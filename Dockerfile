FROM python:3.10-slim

LABEL maintainer='trinome_data_engineering'
LABEL description='Pipeline ETL Mobile Money CI'
LABEL version='1.0.0'

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY dags/ ./dags/
COPY data/ ./data/

RUN mkdir -p /data/raw /data/clean /data/output /logs

EXPOSE 8080

CMD ["python", "dags/dag_pipeline_mobile_money.py"]
