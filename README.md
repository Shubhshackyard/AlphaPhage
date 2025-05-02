# AlphaPhage – Real-Time Narrative Mining for Financial Signals

## Overview
AlphaPhage is a modular pipeline designed for real-time narrative mining of financial signals from public data sources, specifically Twitter. The project leverages various technologies including Apache Kafka, Spark Structured Streaming, Delta Lake, HuggingFace transformers, FastAPI, and React to provide a comprehensive solution for monitoring and analyzing financial trends.

## Project Structure
The project is organized into several key components:

- **Ingestion**: Responsible for scraping Twitter data and publishing it to Kafka.
- **Processing**: Consumes Kafka streams and processes the data, writing it to Delta Lake.
- **NLP Service**: Enriches the data with NLP embeddings and topic assignments.
- **Anomaly Detector**: Detects anomalies in topic volumes and generates alerts.
- **API**: Exposes a REST API for fetching alerts and topics.
- **Dashboard**: A React-based dashboard for visualizing trends and alerts.
- **Infrastructure**: Contains Docker and Kubernetes configurations for deployment.
- **Documentation**: Provides architecture diagrams and setup instructions.

## Technologies Used
- **Python**: For backend services and data processing.
- **Apache Kafka**: For real-time data streaming.
- **Spark**: For processing large datasets in real-time.
- **Delta Lake**: For reliable data storage and management.
- **HuggingFace Transformers**: For natural language processing tasks.
- **FastAPI**: For building the REST API.
- **React**: For the frontend dashboard.
- **Docker**: For containerization of services.
- **Kubernetes**: For orchestration and deployment.

## Setup Instructions
1. **Clone the Repository**:
   ```
   git clone <repository-url>
   cd alphaphage
   ```

2. **Install Dependencies**:
   Each service has its own `requirements.txt` file. Install the dependencies for each service as needed.

3. **Run the Ingestion Service**:
   Navigate to the `ingestion` directory and build the Docker image:
   ```
   cd ingestion
   docker build -t alphaphage-ingestion .
   ```

4. **Run the Processing Service**:
   Navigate to the `processing` directory and build the Docker image:
   ```
   cd processing
   docker build -t alphaphage-processing .
   ```

5. **Run the NLP Service**:
   Navigate to the `nlp_service` directory and build the Docker image:
   ```
   cd nlp_service
   docker build -t alphaphage-nlp-service .
   ```

6. **Run the Anomaly Detector**:
   Navigate to the `anomaly_detector` directory and build the Docker image:
   ```
   cd anomaly_detector
   docker build -t alphaphage-anomaly-detector .
   ```

7. **Run the API Service**:
   Navigate to the `api` directory and build the Docker image:
   ```
   cd api
   docker build -t alphaphage-api .
   ```

8. **Run the Dashboard**:
   Navigate to the `dashboard` directory and build the Docker image:
   ```
   cd dashboard
   docker build -t alphaphage-dashboard .
   ```

9. **Deploy with Kubernetes**:
   Use the provided Kubernetes manifests in the `infra/kubernetes` directory to deploy the services.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.