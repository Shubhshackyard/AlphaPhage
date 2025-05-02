import logging
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications about alerts"""
    
    @staticmethod
    def send_email_notification(alert):
        """Send an email notification for a high severity alert"""
        if not Config.EMAIL_TO:
            logger.info(json.dumps({"event": "email_notification_skipped", "reason": "No recipients configured"}))
            return False
            
        try:
            # Create email content
            msg = MIMEMultipart()
            msg['Subject'] = f"AlphaPhage Alert: {alert['severity']} - {alert['topic_label']}"
            msg['From'] = Config.EMAIL_FROM
            msg['To'] = ", ".join(Config.EMAIL_TO)
            
            # Create HTML content
            html = f"""
            <html>
              <head>
                <style>
                  body {{ font-family: Arial, sans-serif; }}
                  .alert-header {{ background-color: #f8d7da; padding: 15px; border-radius: 5px 5px 0 0; }}
                  .alert-content {{ padding: 15px; background-color: #f8f9fa; border-radius: 0 0 5px 5px; }}
                  .high {{ color: #721c24; font-weight: bold; }}
                  .medium {{ color: #856404; }}
                  .low {{ color: #0c5460; }}
                </style>
              </head>
              <body>
                <div class="alert-header">
                  <h2>AlphaPhage Alert - <span class="{alert['severity'].lower()}">{alert['severity']}</span></h2>
                </div>
                <div class="alert-content">
                  <p><strong>Topic:</strong> {alert['topic_label']}</p>
                  <p><strong>Message:</strong> {alert['alert_message']}</p>
                  <hr>
                  <p><strong>Volume:</strong> {alert['volume']}</p>
                  <p><strong>Expected Volume:</strong> {alert['expected_volume']:.1f}</p>
                  <p><strong>Z-Score:</strong> {alert['z_score']:.2f}</p>
                  <hr>
                  <p><em>Alert generated at {alert['alert_time']}</em></p>
                </div>
              </body>
            </html>
            """
            
            # Attach HTML content
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                if Config.SMTP_USERNAME and Config.SMTP_PASSWORD:
                    server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(json.dumps({
                "event": "email_notification_sent", 
                "recipients": Config.EMAIL_TO,
                "alert_id": alert.get("alert_id", "unknown")
            }))
            
            return True
            
        except Exception as e:
            logger.error(json.dumps({"event": "email_notification_error", "error": str(e)}))
            return False
    
    @staticmethod
    def send_webhook_notification(alert):
        """Send a webhook notification for an alert"""
        if not Config.WEBHOOK_URL:
            logger.info(json.dumps({"event": "webhook_notification_skipped", "reason": "No webhook URL configured"}))
            return False
            
        try:
            # Format the alert for Slack/Discord webhook
            message = {
                "text": f"*AlphaPhage Alert: {alert['severity']} - {alert['topic_label']}*",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"Alert: {alert['severity']} - {alert['topic_label']}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Message:* {alert['alert_message']}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Volume:* {alert['volume']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Expected:* {alert['expected_volume']:.1f}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Z-Score:* {alert['z_score']:.2f}"
                            }
                        ]
                    }
                ]
            }
            
            # Send webhook
            response = requests.post(
                Config.WEBHOOK_URL,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in (200, 201, 202, 204):
                logger.info(json.dumps({
                    "event": "webhook_notification_sent", 
                    "status_code": response.status_code,
                    "alert_id": alert.get("alert_id", "unknown")
                }))
                return True
            else:
                logger.error(json.dumps({
                    "event": "webhook_notification_error", 
                    "status_code": response.status_code,
                    "response": response.text,
                    "alert_id": alert.get("alert_id", "unknown")
                }))
                return False
                
        except Exception as e:
            logger.error(json.dumps({"event": "webhook_notification_error", "error": str(e)}))
            return False