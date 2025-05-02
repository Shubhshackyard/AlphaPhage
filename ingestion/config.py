import os

class Config:
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    # Twitter scraper configuration
    TWITTER_TOPICS = [
        "bitcoin", 
        "ethereum", 
        "tesla stock", 
        "apple stock", 
        "nvidia stock",
        "interest rates",
        "federal reserve",
        "inflation"
    ]
    SCRAPING_INTERVAL = 300  # seconds

    # Kafka configuration
    KAFKA_BROKER = "kafka:9092"
    KAFKA_TOPIC = "raw-narratives"