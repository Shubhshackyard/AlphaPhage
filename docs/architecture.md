# Architecture Overview

## System Components

The AlphaPhage project is designed to perform real-time narrative mining for financial signals using a modular architecture. The system consists of several key components:

1. **Ingestion Layer**:
   - **Twitter Scraper**: Utilizes Playwright or Tweepy to scrape tweets in real-time based on specified criteria.
   - **Kafka Producer**: Publishes the scraped tweets to an Apache Kafka topic for further processing.

2. **Processing Layer**:
   - **Spark Structured Streaming**: Consumes the Kafka stream and processes the raw records, writing them into a Delta Lake bronze zone.
   - **Delta Lake Writer**: Responsible for writing processed data into Delta Lake, ensuring data reliability and performance.

3. **NLP Service**:
   - **FastAPI Application**: Handles the generation of NLP embeddings and topic assignments using a HuggingFace transformer model.
   - **Embeddings and Topic Extraction**: Enriches each record with embeddings and assigns topic IDs for further analysis.

4. **Anomaly Detection**:
   - **Batch Job**: Monitors topic volume spikes and generates alerts based on detected anomalies, writing them to a gold Delta Lake table.

5. **API Layer**:
   - **FastAPI REST API**: Exposes endpoints to fetch the latest alerts and trending topics, facilitating interaction with the dashboard.

6. **Dashboard**:
   - **React Application**: Provides a user interface to visualize trending topics and alerts, enhancing user engagement and decision-making.

## Data Flow

1. **Data Ingestion**:
   - The Twitter scraper fetches tweets and sends them to Kafka.
   
2. **Data Processing**:
   - Spark Structured Streaming consumes the tweets from Kafka, processes them, and writes the raw data into Delta Lake.

3. **NLP Enrichment**:
   - The NLP service enriches the processed data with embeddings and topic IDs.

4. **Anomaly Detection**:
   - The anomaly detector monitors the processed data for volume spikes and generates alerts.

5. **API Interaction**:
   - The API provides endpoints for the dashboard to fetch alerts and trending topics.

## Deployment

The entire system is containerized using Docker and orchestrated with Kubernetes. Each microservice has its own Dockerfile and Kubernetes deployment manifest, ensuring scalability and maintainability.

## Security and Data Management

- **Unity Catalog**: Implements IAM to isolate raw and processed data, ensuring data governance and security.
- **Logging and Monitoring**: Each microservice includes structured JSON logging and basic health checks to monitor system performance and reliability.

## Conclusion

The AlphaPhage architecture is designed to be modular, scalable, and efficient, enabling real-time narrative mining for financial signals while ensuring data integrity and security.