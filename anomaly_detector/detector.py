import logging
import json
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, sum, avg, stddev
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        self.spark = self._create_spark_session()
        
    def _create_spark_session(self):
        """Create and configure Spark session"""
        spark = (SparkSession.builder
                .appName("AlphaPhage-AnomalyDetector")
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                .getOrCreate())
        
        logger.info(json.dumps({"event": "spark_session_created"}))
        return spark
        
    def detect_volume_anomalies(self):
        """Detect anomalies in topic volume using DBSCAN clustering"""
        try:
            logger.info(json.dumps({"event": "starting_anomaly_detection"}))
            
            # Read silver data with topics
            silver_df = self.spark.read.format("delta").load(Config.DELTA_SILVER_PATH)
            
            # Calculate daily topic volumes for the last 30 days
            today = datetime.now()
            thirty_days_ago = today - timedelta(days=30)
            
            # Filter for relevant time period and aggregate by date and topic
            daily_volumes = (silver_df
                             .filter(col("timestamp") >= thirty_days_ago.isoformat())
                             .groupBy("topic_id", "topic_label", 
                                     self.spark.sql("date_trunc('day', timestamp)").alias("date"))
                             .agg(count("*").alias("volume")))
            
            # Convert to pandas for scikit-learn processing
            pandas_df = daily_volumes.toPandas()
            
            # Process each topic separately
            anomalies = []
            
            # Get unique topics
            topics = pandas_df["topic_id"].unique()
            
            for topic_id in topics:
                topic_data = pandas_df[pandas_df["topic_id"] == topic_id]
                
                if len(topic_data) < 3:  # Skip topics with too little data
                    continue
                    
                # Extract topic info
                topic_label = topic_data["topic_label"].iloc[0]
                
                # Get volume time series
                volumes = topic_data["volume"].values.reshape(-1, 1)
                
                # Standardize the volumes
                scaled_volumes = StandardScaler().fit_transform(volumes)
                
                # Apply DBSCAN to detect anomalies
                dbscan = DBSCAN(eps=0.5, min_samples=3)
                clusters = dbscan.fit_predict(scaled_volumes)
                
                # Points labeled as -1 are anomalies
                anomaly_indices = np.where(clusters == -1)[0]
                
                # If anomalies found, add to results
                for idx in anomaly_indices:
                    anomaly_date = topic_data["date"].iloc[idx]
                    anomaly_volume = topic_data["volume"].iloc[idx]
                    
                    # Calculate Z-score to determine significance
                    mean_volume = topic_data["volume"].mean()
                    std_volume = topic_data["volume"].std() if topic_data["volume"].std() > 0 else 1
                    z_score = (anomaly_volume - mean_volume) / std_volume
                    
                    # Only consider significant anomalies (high Z-score)
                    if z_score > 2.0:  # Threshold for significance
                        anomalies.append({
                            "topic_id": int(topic_id),
                            "topic_label": topic_label,
                            "date": anomaly_date,
                            "volume": int(anomaly_volume),
                            "expected_volume": float(mean_volume),
                            "z_score": float(z_score),
                            "detection_time": datetime.now().isoformat(),
                        })
            
            logger.info(json.dumps({
                "event": "anomaly_detection_complete", 
                "anomalies_found": len(anomalies)
            }))
            
            # Convert anomalies back to a Spark dataframe
            if anomalies:
                anomalies_df = self.spark.createDataFrame(anomalies)
                return anomalies_df
            else:
                # Return empty dataframe with correct schema
                schema = StructType([
                    StructField("topic_id", IntegerType(), True),
                    StructField("topic_label", StringType(), True),
                    StructField("date", TimestampType(), True),
                    StructField("volume", IntegerType(), True),
                    StructField("expected_volume", IntegerType(), True),
                    StructField("z_score", IntegerType(), True),
                    StructField("detection_time", TimestampType(), True),
                ])
                return self.spark.createDataFrame([], schema)
                
        except Exception as e:
            logger.error(json.dumps({"event": "anomaly_detection_error", "error": str(e)}))
            raise

    def detect_rolling_average_anomalies(self):
        """Detect anomalies using rolling average technique"""
        try:
            logger.info(json.dumps({"event": "starting_rolling_avg_detection"}))
            
            # Read silver data with topics
            silver_df = self.spark.read.format("delta").load(Config.DELTA_SILVER_PATH)
            
            # Calculate daily topic volumes
            daily_volumes = (silver_df
                             .groupBy("topic_id", "topic_label", 
                                     self.spark.sql("date_trunc('day', timestamp)").alias("date"))
                             .agg(count("*").alias("volume")))
            
            # Define window spec for 7-day rolling average
            from pyspark.sql.window import Window
            import pyspark.sql.functions as F
            
            window_spec = (Window
                          .partitionBy("topic_id")
                          .orderBy("date")
                          .rangeBetween(-6, 0))  # 7-day window including current day
            
            # Calculate rolling metrics
            volumes_with_stats = (daily_volumes
                                 .withColumn("rolling_avg", F.avg("volume").over(window_spec))
                                 .withColumn("rolling_stddev", F.stddev("volume").over(window_spec))
                                 .withColumn("is_anomaly", 
                                            (F.col("volume") > (F.col("rolling_avg") + 3 * F.col("rolling_stddev"))))
                                 .withColumn("z_score", 
                                            (F.col("volume") - F.col("rolling_avg")) / F.col("rolling_stddev")))
            
            # Filter to include only anomalies
            anomalies_df = volumes_with_stats.filter(col("is_anomaly") == True)
            
            logger.info(json.dumps({
                "event": "rolling_avg_detection_complete", 
                "anomalies_found": anomalies_df.count()
            }))
            
            return anomalies_df
            
        except Exception as e:
            logger.error(json.dumps({"event": "rolling_avg_detection_error", "error": str(e)}))
            raise

    def write_alerts_to_gold(self, anomalies_df):
        """Write detected anomalies to the gold Delta table"""
        try:
            if anomalies_df.count() > 0:
                # Enrich with additional alert information
                alerts_df = (anomalies_df
                            .withColumn("alert_id", self.spark.sql("uuid()"))
                            .withColumn("alert_time", self.spark.sql("current_timestamp()"))
                            .withColumn("alert_message", 
                                       self.spark.sql("concat('Anomaly detected in topic: ', topic_label)"))
                            .withColumn("severity", 
                                       self.spark.sql("case when z_score > 5 then 'HIGH' " +
                                                     "when z_score > 3 then 'MEDIUM' else 'LOW' end")))
                
                # Write to gold table
                alerts_df.write.format("delta").mode("append").save(Config.DELTA_GOLD_PATH)
                
                logger.info(json.dumps({
                    "event": "alerts_written_to_gold", 
                    "count": alerts_df.count()
                }))
                
                return True
            else:
                logger.info(json.dumps({"event": "no_alerts_to_write"}))
                return False
                
        except Exception as e:
            logger.error(json.dumps({"event": "write_alerts_error", "error": str(e)}))
            return False

def main():
    detector = AnomalyDetector()
    
    try:
        # Detect anomalies using DBSCAN
        anomalies_df = detector.detect_volume_anomalies()
        
        # If no anomalies found with DBSCAN, try rolling average method
        if anomalies_df.count() == 0:
            anomalies_df = detector.detect_rolling_average_anomalies()
        
        # Write alerts to gold table
        detector.write_alerts_to_gold(anomalies_df)
        
    except Exception as e:
        logger.error(json.dumps({"event": "main_error", "error": str(e)}))
    finally:
        if detector.spark:
            detector.spark.stop()
            logger.info(json.dumps({"event": "spark_session_stopped"}))

if __name__ == "__main__":
    main()