import asyncio
import json
import logging
from datetime import datetime
from playwright.async_api import async_playwright
from kafka_producer import KafkaMessageProducer
from config import TWITTER_TOPICS, SCRAPING_INTERVAL, KAFKA_BROKER, KAFKA_TOPIC

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TwitterScraper:
    def __init__(self):
        self.producer = KafkaMessageProducer(KAFKA_BROKER, KAFKA_TOPIC)
        self.topics = TWITTER_TOPICS

    async def initialize_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        logger.info(json.dumps({"event": "browser_initialized"}))

    async def close_browser(self):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
        logger.info(json.dumps({"event": "browser_closed"}))

    async def search_twitter(self, topic):
        search_url = f"https://twitter.com/search?q={topic}&src=typed_query&f=live"
        
        try:
            await self.page.goto(search_url, timeout=60000)
            await self.page.wait_for_load_state("networkidle")
            
            # Wait for tweets to appear
            await self.page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
            
            # Extract tweets
            tweets = await self.page.query_selector_all('article[data-testid="tweet"]')
            
            results = []
            for tweet in tweets[:10]:  # Process first 10 tweets
                try:
                    # Extract tweet text
                    text_element = await tweet.query_selector('div[data-testid="tweetText"]')
                    if text_element:
                        text = await text_element.inner_text()
                    else:
                        continue
                        
                    # Extract username
                    username_element = await tweet.query_selector('div[data-testid="User-Name"] span')
                    username = await username_element.inner_text() if username_element else "unknown"
                    
                    # Extract timestamp
                    time_element = await tweet.query_selector('time')
                    timestamp = await time_element.get_attribute('datetime') if time_element else datetime.now().isoformat()
                    
                    tweet_data = {
                        "source": "twitter",
                        "topic": topic,
                        "text": text,
                        "username": username,
                        "timestamp": timestamp,
                        "scrape_time": datetime.now().isoformat(),
                    }
                    
                    results.append(tweet_data)
                except Exception as e:
                    logger.error(json.dumps({"event": "tweet_extraction_error", "error": str(e)}))
            
            return results
            
        except Exception as e:
            logger.error(json.dumps({"event": "search_error", "topic": topic, "error": str(e)}))
            return []

    async def run_scraping(self):
        await self.initialize_browser()
        
        try:
            while True:
                for topic in self.topics:
                    logger.info(json.dumps({"event": "scraping_topic", "topic": topic}))
                    tweets = await self.search_twitter(topic)
                    
                    for tweet in tweets:
                        await self.producer.send_message(tweet)
                        logger.info(json.dumps({"event": "tweet_sent", "topic": topic}))
                    
                    # Sleep between topics to avoid rate limiting
                    await asyncio.sleep(5)
                
                # Wait for the configured interval before next scraping
                logger.info(json.dumps({"event": "scraping_complete", "next_run": f"in {SCRAPING_INTERVAL} seconds"}))
                await asyncio.sleep(SCRAPING_INTERVAL)
        
        except Exception as e:
            logger.error(json.dumps({"event": "scraping_error", "error": str(e)}))
        
        finally:
            await self.close_browser()
            await self.producer.close()

if __name__ == "__main__":
    scraper = TwitterScraper()
    asyncio.run(scraper.run_scraping())