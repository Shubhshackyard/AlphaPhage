import json
import logging
import asyncio
from aiokafka import AIOKafkaProducer
import config
import time

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class KafkaMessageProducer:
    def __init__(self, bootstrap_servers, topic):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        
    async def start(self):
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            logger.info(json.dumps({"event": "kafka_producer_started", "broker": self.bootstrap_servers, "topic": self.topic}))
        except Exception as e:
            logger.error(json.dumps({"event": "kafka_producer_start_error", "error": str(e)}))
            raise
            
    async def send_message(self, message):
        if self.producer is None:
            await self.start()
            
        try:
            await self.producer.send_and_wait(self.topic, message)
            return True
        except Exception as e:
            logger.error(json.dumps({"event": "kafka_send_error", "error": str(e)}))
            return False
            
    async def close(self):
        if self.producer:
            await self.producer.stop()
            logger.info(json.dumps({"event": "kafka_producer_closed"}))

async def main():
    kafka_producer = KafkaMessageProducer(config.KAFKA_BROKER, config.KAFKA_TOPIC)
    
    try:
        await kafka_producer.start()
        
        while True:
            # Here you would integrate the Twitter scraper to fetch tweets
            # For demonstration, we'll use a placeholder tweet
            tweet = {
                'user': 'example_user',
                'text': 'This is a sample tweet',
                'timestamp': time.time()
            }
            
            success = await kafka_producer.send_message(tweet)
            if success:
                logger.info(json.dumps({"event": "tweet_published", "tweet": tweet}))
            else:
                logger.error(json.dumps({"event": "tweet_publish_failed", "tweet": tweet}))
            
            await asyncio.sleep(1)  # Adjust the sleep time as needed
    finally:
        await kafka_producer.close()

if __name__ == "__main__":
    asyncio.run(main())