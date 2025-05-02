# AlphaPhage Setup Instructions

## Prerequisites
Before you begin, ensure you have the following installed on your machine:

- Python 3.8 or higher
- Docker
- Docker Compose
- Kubernetes (Minikube or any other local setup)
- Apache Kafka
- Spark (with Delta Lake support)
- Node.js and npm (for the React dashboard)

## Project Structure
The project is organized into several directories, each responsible for a specific part of the pipeline:

- **ingestion/**: Contains the Twitter scraper and Kafka producer.
- **processing/**: Contains Spark Structured Streaming jobs for processing data.
- **nlp_service/**: Contains the FastAPI service for NLP tasks.
- **anomaly_detector/**: Contains the batch job for anomaly detection.
- **api/**: Contains the FastAPI REST API for fetching alerts.
- **dashboard/**: Contains the React application for displaying alerts and trends.
- **infra/**: Contains Docker and Kubernetes configurations.
- **docs/**: Contains documentation and architecture diagrams.

## Setup Instructions

### Step 1: Clone the Repository
Clone the repository to your local machine:
```bash
git clone <repository-url>
cd alphaphage
```

### Step 2: Set Up Ingestion Service
1. Navigate to the ingestion directory:
   ```bash
   cd ingestion
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Build the Docker image:
   ```bash
   docker build -t alphaphage-ingestion .
   ```

### Step 3: Set Up Processing Service
1. Navigate to the processing directory:
   ```bash
   cd ../processing
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Build the Docker image:
   ```bash
   docker build -t alphaphage-processing .
   ```

### Step 4: Set Up NLP Service
1. Navigate to the nlp_service directory:
   ```bash
   cd ../nlp_service
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Build the Docker image:
   ```bash
   docker build -t alphaphage-nlp-service .
   ```

### Step 5: Set Up Anomaly Detector
1. Navigate to the anomaly_detector directory:
   ```bash
   cd ../anomaly_detector
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Build the Docker image:
   ```bash
   docker build -t alphaphage-anomaly-detector .
   ```

### Step 6: Set Up API Service
1. Navigate to the api directory:
   ```bash
   cd ../api
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Build the Docker image:
   ```bash
   docker build -t alphaphage-api .
   ```

### Step 7: Set Up Dashboard
1. Navigate to the dashboard directory:
   ```bash
   cd ../dashboard
   ```
2. Install the required dependencies:
   ```bash
   npm install
   ```
3. Build the Docker image:
   ```bash
   docker build -t alphaphage-dashboard .
   ```

### Step 8: Run the Services
You can use Docker Compose to run all services together. Navigate to the infra directory and run:
```bash
cd ../infra
docker-compose up
```

### Step 9: Deploy to Kubernetes
If you want to deploy the services to a Kubernetes cluster, apply the Kubernetes manifests:
```bash
kubectl apply -f kubernetes/
```

### Step 10: Access the Dashboard
Once all services are running, you can access the React dashboard at `http://localhost:3000`.

## Conclusion
You have successfully set up the AlphaPhage project. For further details on each component, refer to the respective directories and documentation.