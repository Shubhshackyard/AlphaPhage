import json
import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_json, struct
from datetime import datetime, timedelta
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AlertGenerator:
    def __init__(self):
        self.spark = self._create_spark_session()
        
    def _create_spark_session(self):
        """Create and configure Spark session"""
        spark = (SparkSession.builder
                .appName("AlphaPhage-AlertGenerator")
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                .getOrCreate())
        
        logger.info(json.dumps({"event": "spark_session_created"}))
        return spark
    
    def get_recent_alerts(self, hours=24):
        """Get alerts that were generated in the last N hours"""
        try:
            # Read from gold Delta table
            alerts_df = self.spark.read.format("delta").load(Config.DELTA_GOLD_PATH)
            
            # Filter for alerts in the last N hours
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_alerts = alerts_df.filter(col("alert_time") >= cutoff_time.isoformat())
            
            logger.info(json.dumps({
                "event": "recent_alerts_retrieved", 
                "count": recent_alerts.count(),
                "hours": hours
            }))
            
            return recent_alerts
            
        except Exception as e:
            logger.error(json.dumps({"event": "get_recent_alerts_error", "error": str(e)}))
            return None
    
    def send_webhook_notifications(self, alerts_df):
        """Send alerts to a webhook (e.g., Slack)"""
        if not Config.WEBHOOK_URL:
            logger.warning(json.dumps({"event": "webhook_url_not_configured"}))
            return False
        
        try:
            # Convert alerts to JSON format for webhook
            alerts_json = alerts_df.select(
                to_json(struct("*")).alias("json")
            ).collect()
            
            for alert in alerts_json:
                alert_data = json.loads(alert.json)
                
                # Format message for Slack
                message = {
                    "text": f"⚠️ *ALERT*: {alert_data['alert_message']}",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Topic:* {alert_data['topic_label']}"
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Volume:* {alert_data['volume']}"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Expected:* {alert_data['expected_volume']:.1f}"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Z-Score:* {alert_data['z_score']:.2f}"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Severity:* {alert_data['severity']}"
                                }
                            ]
                        }
                    ]
                }
                
                # Send to webhook
                response = requests.post(
                    Config.WEBHOOK_URL,
                    json=message,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    logger.error(json.dumps({
                        "event": "webhook_send_error", 
                        "status_code": response.status_code,
                        "response": response.text
                    }))
                else:
                    logger.info(json.dumps({
                        "event": "webhook_alert_sent", 
                        "topic": alert_data['topic_label'],
                        "severity": alert_data['severity']
                    }))
            
            return True
            
        except Exception as e:
            logger.error(json.dumps({"event": "webhook_notification_error", "error": str(e)}))
            return False
    
    def send_email_notifications(self, alerts_df):
        """Send email notifications for alerts"""
        if not Config.ENABLE_EMAIL or not Config.EMAIL_RECIPIENTS:
            logger.warning(json.dumps({"event": "email_notifications_disabled"}))
            return False
        
        try:
            # Collect alerts to send
            alerts = alerts_df.collect()
            
            if not alerts:
                logger.info(json.dumps({"event": "no_alerts_to_email"}))
                return True
                
            # Create email content
            msg = MIMEMultipart()
            msg['Subject'] = f'AlphaPhage Alert: {len(alerts)} Anomalies Detected'
            msg['From'] = Config.EMAIL_SENDER
            msg['To'] = ', '.join(Config.EMAIL_RECIPIENTS)
            
            # Create HTML content
            html = f"""
            <html>
            <head>
                <style>
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    .high {{
                        color: red;
                        font-weight: bold;
                    }}
                    .medium {{
                        color: orange;
                    }}
                    .low {{
                        color: blue;
                    }}
                </style>
            </head>
            <body>
                <h2>AlphaPhage Alert: {len(alerts)} Anomalies Detected</h2>
                <p>The following topic anomalies were detected:</p>
                <table>
                    <tr>
                        <th>Topic</th>
                        <th>Volume</th>
                        <th>Expected</th>
                        <th>Z-Score</th>
                        <th>Severity</th>
                        <th>Time</th>
                    </tr>
            """
            
            # Add rows for each alert
            for alert in alerts:
                severity_class = alert.severity.lower()
                html += f"""
                    <tr>
                        <td>{alert.topic_label}</td>
                        <td>{alert.volume}</td>
                        <td>{alert.expected_volume:.1f}</td>
                        <td>{alert.z_score:.2f}</td>
                        <td class="{severity_class}">{alert.severity}</td>
                        <td>{alert.alert_time}</td>
                    </tr>
                """
            
            html += """
                </table>
                <p>This is an automated alert from the AlphaPhage system.</p>
            </body>
            </html>
            """
            
            # Attach HTML content
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                if Config.SMTP_USE_TLS:
                    server.starttls()
                if Config.SMTP_USERNAME and Config.SMTP_PASSWORD:
                    server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(json.dumps({
                "event": "email_alert_sent", 
                "recipients": Config.EMAIL_RECIPIENTS,
                "alert_count": len(alerts)
            }))
            
            return True
            
        except Exception as e:
            logger.error(json.dumps({"event": "email_notification_error", "error": str(e)}))
            return False

def main():
    alert_gen = AlertGenerator()
    
    try:
        # Get recent alerts (last 6 hours)
        recent_alerts = alert_gen.get_recent_alerts(hours=6)
        
        if recent_alerts and recent_alerts.count() > 0:
            # Send notifications
            alert_gen.send_webhook_notifications(recent_alerts)
            alert_gen.send_email_notifications(recent_alerts)
        else:
            logger.info(json.dumps({"event": "no_recent_alerts"}))
            
    except Exception as e:
        logger.error(json.dumps({"event": "main_error", "error": str(e)}))
    finally:
        if alert_gen.spark:
            alert_gen.spark.stop()
            logger.info(json.dumps({"event": "spark_session_stopped"}))

if __name__ == "__main__":
    main()