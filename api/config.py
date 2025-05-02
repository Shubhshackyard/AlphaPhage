# Configuration settings for the API service

import os

class Config:
    # API Settings
    API_VERSION = "v1"
    HOST = os.getenv("API_HOST", "0.0.0.0")
    PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS Settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Delta Lake paths
    DELTA_BRONZE_PATH = os.getenv("DELTA_BRONZE_PATH", "/data/delta/bronze/narratives")
    DELTA_SILVER_PATH = os.getenv("DELTA_SILVER_PATH", "/data/delta/silver/narratives")
    DELTA_GOLD_PATH = os.getenv("DELTA_GOLD_PATH", "/data/delta/gold/alerts")
    
    # Notification settings
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "alphaphage@example.com")
    EMAIL_TO = os.getenv("EMAIL_TO", "").split(",")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

class ProductionConfig(Config):
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alerts.db")
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

# You can add more configurations as needed for testing or staging environments.