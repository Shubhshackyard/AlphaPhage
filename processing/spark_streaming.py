from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from delta.tables import DeltaTable
import logging
import json
from config import KAFKA_BROKER, KAFKA_TOPIC, DELTA_BRONZE_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create and configure Spark session with Delta Lake support"""
    builder = (SparkSession.builder
               .appName("AlphaPhage-NarrativesProcessor")
               .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
               .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
               .config("spark.sql.warehouse.dir", "spark-warehouse"))
    
    spark = builder.getOrCreate()
    logger.info(json.dumps({"event": "spark_session_created"}))
    return spark

def define_schema():
    """Define schema for the ingested Twitter data"""
    return StructType([
        StructField("source", StringType(), True),
        StructField("topic", StringType(), True),
        StructField("text", StringType(), True),
        StructField("username", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("scrape_time", TimestampType(), True)
    ])

def process_stream(spark):
    """Process Kafka stream and write to Delta Lake bronze table"""
    schema = define_schema()
    
    # Read from Kafka
    df = (spark
          .readStream
          .format("kafka")
          .option("kafka.bootstrap.servers", KAFKA_BROKER)
          .option("subscribe", KAFKA_TOPIC)
          .option("startingOffsets", "latest")
          .load())
    
    # Parse JSON payload
    parsed_df = (df
                .select(from_json(col("value").cast("string"), schema).alias("data"))
                .select("data.*"))
    
    # Add processing timestamp
    enriched_df = parsed_df.withColumn("processing_time", col("current_timestamp"))
    
    # Write to Delta Lake bronze table
    query = (enriched_df
             .writeStream
             .format("delta")
             .outputMode("append")
             .option("checkpointLocation", f"{DELTA_BRONZE_PATH}/_checkpoints")
             .start(DELTA_BRONZE_PATH))
    
    logger.info(json.dumps({"event": "streaming_query_started", "table": "bronze_narratives"}))
    
    return query

def main():
    try:
        spark = create_spark_session()
        query = process_stream(spark)
        
        # Keep the streaming query running until terminated
        query.awaitTermination()
    except Exception as e:
        logger.error(json.dumps({"event": "streaming_error", "error": str(e)}))
    finally:
        logger.info(json.dumps({"event": "stream_processing_terminated"}))

if __name__ == "__main__":
    main()