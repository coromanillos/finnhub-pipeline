FROM apache/airflow:2.9.1-python3.11

USER root

WORKDIR /opt/airflow

COPY --chown=airflow:root base_pipeline.py .
COPY --chown=airflow:root config.py .
COPY --chown=airflow:root pipelines/ ./pipelines/
COPY --chown=airflow:root models/ ./models/
COPY --chown=airflow:root requirements.txt .

RUN groupadd -g 124 docker && usermod -aG docker airflow

USER airflow

RUN pip install --no-cache-dir -r requirements.txt