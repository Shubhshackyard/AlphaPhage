import requests
import json
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, struct, explode, to_json
from pyspark.sql.types import StringType, ArrayType, DoubleType, IntegerType, StructType, StructField
from delta.tables import DeltaTable
from config import Config

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
               .appName("AlphaPhage-BronzeToSilver")
               .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
               .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
               .config("spark.sql.warehouse.dir", "spark-warehouse"))
    
    spark = builder.getOrCreate()
    logger.info(json.dumps({"event": "spark_session_created"}))
    return spark

def enrich_with_nlp(text, nlp_service_url):
    """Call NLP service to enrich a text with embeddings and topic"""
    try:
        # Extract embedding
        embedding_response = requests.post(
            f"{nlp_service_url}/embed",
            json={"text": text}
        )
        embedding_response.raise_for_status()
        embedding_data = embedding_response.json()
        
        # Extract topic
        topic_response = requests.post(
            f"{nlp_service_url}/topic",
            json={"text": text}
        )
        topic_response.raise_for_status()
        topic_data = topic_response.json()
        
        # Combine results
        result = {
            "embedding": embedding_data.get("embedding", []),
            "topic_id": topic_data.get("topic_id", -1),
            "topic_label": topic_data.get("topic_label", ""),
            "topic_confidence": topic_data.get("confidence", 0.0),
            "topic_keywords": topic_data.get("keywords", [])
        }
        
        return json.dumps(result)
    except Exception as e:
        logger.error(json.dumps({"event": "nlp_enrichment_error", "error": str(e), "text": text[:100]}))
        # Return empty JSON structure
        return json.dumps({
            "embedding": [],
            "topic_id": -1,
            "topic_label": "error",
            "topic_confidence": 0.0,
            "topic_keywords": []
        })

def process_bronze_to_silver(spark):
    """Process bronze data, enrich with NLP, and write to silver table"""
    try:
        # Read from bronze table
        bronze_df = spark.read.format("delta").load(Config.DELTA_BRONZE_PATH)
        
        # Register UDF for NLP enrichment
        nlp_service_url = f"http://{Config.NLP_SERVICE_HOST}:{Config.NLP_SERVICE_PORT}"
        enrich_udf = udf(lambda text: enrich_with_nlp(text, nlp_service_url), StringType())
        
        # Define schema for parsed NLP results
        nlp_schema = StructType([
            StructField("embedding", ArrayType(DoubleType()), True),
            StructField("topic_id", IntegerType(), True),
            StructField("topic_label", StringType(), True),
            StructField("topic_confidence", DoubleType(), True),
            StructField("topic_keywords", ArrayType(StringType()), True)
        ])
        
        # Apply NLP enrichment
        enriched_df = bronze_df.withColumn("nlp_enrichment", enrich_udf(col("text")))
        
        # Parse the JSON result and expand columns
        parsed_df = enriched_df.withColumn(
            "nlp_parsed", 
            from_json(col("nlp_enrichment"), nlp_schema)
        ).select(
            "*",
            col("nlp_parsed.embedding").alias("embedding"),
            col("nlp_parsed.topic_id").alias("topic_id"),
            col("nlp_parsed.topic_label").alias("topic_label"),
            col("nlp_parsed.topic_confidence").alias("topic_confidence"),
            col("nlp_parsed.topic_keywords").alias("topic_keywords")
        ).drop("nlp_enrichment", "nlp_parsed")
        
        # Write to silver table
        parsed_df.write.format("delta").mode("overwrite").save(Config.DELTA_SILVER_PATH)
        
        logger.info(json.dumps({
            "event": "bronze_to_silver_complete",
            "records_processed": parsed_df.count()
        }))
    
    except Exception as e:
        logger.error(json.dumps({"event": "bronze_to_silver_error", "error": str(e)}))
        raise
        
def main():
    try:
        spark = create_spark_session()
        process_bronze_to_silver(spark)
    except Exception as e:
        logger.error(json.dumps({"event": "main_error", "error": str(e)}))
    finally:
        logger.info(json.dumps({"event": "bronze_to_silver_job_completed"}))

if __name__ == "__main__":
    main()