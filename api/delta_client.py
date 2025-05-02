import json
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_json, struct, desc
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class DeltaClient:
    """Client for reading data from Delta tables"""
    
    def __init__(self):
        self.spark = self._create_spark_session()
        
    def _create_spark_session(self):
        """Create a Spark session configured for Delta Lake"""
        try:
            builder = (SparkSession.builder
                      .appName("AlphaPhage-API")
                      .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                      .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                      .config("spark.databricks.delta.schema.autoMerge.enabled", "true")
                      .config("spark.sql.warehouse.dir", "spark-warehouse"))
            
            spark = builder.getOrCreate()
            logger.info(json.dumps({"event": "spark_session_created"}))
            return spark
            
        except Exception as e:
            logger.error(json.dumps({"event": "spark_session_error", "error": str(e)}))
            raise
    
    def get_alerts(self, limit=20, severity=None, days=7):
        """Fetch alerts from the gold Delta table"""
        try:
            # Read from Delta gold table
            df = self.spark.read.format("delta").load(Config.DELTA_GOLD_PATH)
            
            # Filter by severity if provided
            if severity:
                df = df.filter(col("severity") == severity.upper())
            
            # Filter for recent alerts
            if days:
                df = df.filter(col("alert_time") >= f"current_timestamp() - interval {days} days")
                
            # Order by alert_time descending (newest first)
            df = df.orderBy(desc("alert_time")).limit(limit)
            
            # Convert to JSON format
            alerts = df.select(to_json(struct("*")).alias("json")).collect()
            
            # Parse JSON strings to Python dictionaries
            result = [json.loads(row.json) for row in alerts]
            
            logger.info(json.dumps({"event": "alerts_fetched", "count": len(result)}))
            return result
            
        except Exception as e:
            logger.error(json.dumps({"event": "get_alerts_error", "error": str(e)}))
            return []
    
    def get_trending_topics(self, limit=10, days=2):
        """Fetch trending topics from the silver Delta table"""
        try:
            # Read from silver table with topics
            silver_df = self.spark.read.format("delta").load(Config.DELTA_SILVER_PATH)
            
            # Filter for recent records
            if days:
                silver_df = silver_df.filter(col("timestamp") >= f"current_timestamp() - interval {days} days")
            
            # Group by topic and count volume
            trending = (silver_df
                        .groupBy("topic_id", "topic_label")
                        .count()
                        .orderBy(desc("count"))
                        .limit(limit))
            
            # Convert to JSON format
            topics = trending.select(
                col("topic_id"),
                col("topic_label"),
                col("count").alias("volume"),
                col("current_timestamp()").alias("last_updated")
            ).select(to_json(struct("*")).alias("json")).collect()
            
            # Parse JSON strings to Python dictionaries
            result = [json.loads(row.json) for row in topics]
            
            logger.info(json.dumps({"event": "trending_topics_fetched", "count": len(result)}))
            return result
            
        except Exception as e:
            logger.error(json.dumps({"event": "get_trending_topics_error", "error": str(e)}))
            return []
    
    def close(self):
        """Close the Spark session"""
        if self.spark:
            self.spark.stop()
            logger.info(json.dumps({"event": "spark_session_closed"}))