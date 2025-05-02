# Configuration settings for the NLP service

import os

class Config:
    # Model and service configuration
    MODEL_PATH = os.getenv("MODEL_PATH", "/data/models")
    MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-nli-stsb-mean-tokens")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Processing limits
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 512))
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 768))
    TOPIC_THRESHOLD = int(os.getenv("TOPIC_THRESHOLD", 10))
    
    # Service settings
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
    MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", 100))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # BERTopic settings
    MIN_TOPIC_SIZE = int(os.getenv("MIN_TOPIC_SIZE", 10))
    
    # Database settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME", "alphaphage")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")