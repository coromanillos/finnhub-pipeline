FROM apache/airflow:2.9.1-python3.11

# Switch to root only to copy project files with correct ownership
USER root

WORKDIR /opt/airflow

# Copy your pipeline source code into the image
COPY --chown=airflow:root base_pipeline.py .
COPY --chown=airflow:root config.py .
COPY --chown=airflow:root pipelines/ ./pipelines/
COPY --chown=airflow:root requirements.txt .

# Switch back to airflow user for pip install (required by the base image)
USER airflow

RUN pip install --no-cache-dir -r requirements.txt