# Configuration settings for the processing jobs

class Config:
    SPARK_MASTER = "local[*]"

    # Kafka configuration
    KAFKA_BROKER = "kafka:9092"
    KAFKA_TOPIC = "raw-narratives"

    # Delta Lake paths
    DELTA_BRONZE_PATH = "/data/delta/bronze/narratives"
    DELTA_SILVER_PATH = "/data/delta/silver/narratives"
    DELTA_GOLD_PATH = "/data/delta/gold/alerts"

    # Checkpoint locations
    CHECKPOINT_LOCATION = "/mnt/checkpoints"
    BRONZE_CHECKPOINT = f"{CHECKPOINT_LOCATION}/bronze"
    SILVER_CHECKPOINT = f"{CHECKPOINT_LOCATION}/silver"
    
    # Batch intervals
    BATCH_INTERVAL = "10 seconds"
    
    # NLP Service connection
    NLP_SERVICE_HOST = "nlp-service"
    NLP_SERVICE_PORT = 8000
    
    # Processing settings
    MAX_RETRIES = 3
    RETRY_INTERVAL = 10  # seconds