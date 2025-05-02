import os

# Configuration settings for the anomaly detection process

class Config:
    KAFKA_BROKER = "localhost:9092"
    KAFKA_TOPIC = "alerts"
    DELTA_LAKE_PATH = "/mnt/delta/alerts"
    ALERT_THRESHOLD = 10  # Number of spikes to trigger an alert
    CHECK_INTERVAL = 60  # Time in seconds to check for anomalies

    @staticmethod
    def get_kafka_config():
        return {
            "bootstrap.servers": Config.KAFKA_BROKER,
            "group.id": "anomaly_detector",
            "auto.offset.reset": "latest"
        }

    # Spark and Delta Lake configuration
    DELTA_BRONZE_PATH = os.getenv("DELTA_BRONZE_PATH", "/data/delta/bronze/narratives")
    DELTA_SILVER_PATH = os.getenv("DELTA_SILVER_PATH", "/data/delta/silver/narratives")
    DELTA_GOLD_PATH = os.getenv("DELTA_GOLD_PATH", "/data/delta/gold/alerts")
    
    # Anomaly detection parameters
    ANOMALY_LOOKBACK_DAYS = int(os.getenv("ANOMALY_LOOKBACK_DAYS", "30"))
    ZSCORE_THRESHOLD = float(os.getenv("ZSCORE_THRESHOLD", "2.5"))
    MIN_VOLUME = int(os.getenv("MIN_VOLUME", "5"))
    
    # Notification settings
    ENABLE_WEBHOOK = os.getenv("ENABLE_WEBHOOK", "true").lower() == "true"
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    
    ENABLE_EMAIL = os.getenv("ENABLE_EMAIL", "false").lower() == "true"
    EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",") if os.getenv("EMAIL_RECIPIENTS") else []
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "alphaphage@example.com")
    
    # SMTP settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # API settings
    API_HOST = os.getenv("API_HOST", "api")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_BASE_URL = os.getenv("API_BASE_URL", f"http://{API_HOST}:{API_PORT}")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Scheduling
    DETECTION_INTERVAL_MINUTES = int(os.getenv("DETECTION_INTERVAL_MINUTES", "60"))
    NOTIFICATION_INTERVAL_MINUTES = int(os.getenv("NOTIFICATION_INTERVAL_MINUTES", "15"))