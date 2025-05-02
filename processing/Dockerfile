FROM apache/spark-py:latest

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["spark-submit", "--master", "local[*]", "spark_streaming.py"]