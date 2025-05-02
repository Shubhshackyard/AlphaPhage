from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from delta import *

def write_to_delta_bronze(spark: SparkSession, input_df):
    delta_table_path = "s3://your-bucket/delta/bronze"

    input_df.write.format("delta").mode("append").save(delta_table_path)

def main():
    spark = SparkSession.builder \
        .appName("DeltaWriter") \
        .config("spark.sql.extensions", "delta.sql.DeltaSparkSessionExtensions") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    # Assuming input_df is the DataFrame you want to write to Delta Lake
    input_df = spark.read.json("path/to/your/input/data")  # Replace with your input source

    write_to_delta_bronze(spark, input_df)

if __name__ == "__main__":
    main()