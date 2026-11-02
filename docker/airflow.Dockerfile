FROM apache/airflow:2.11.2-python3.11

USER airflow

COPY docker/airflow-requirements.txt /tmp/airflow-requirements.txt

RUN pip install --no-cache-dir \
    "apache-airflow==2.11.2" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.11.2/constraints-3.11.txt" \
    -r /tmp/airflow-requirements.txt

RUN python -m venv /opt/airflow/dbt-venv \
    && /opt/airflow/dbt-venv/bin/pip install --no-cache-dir \
    "dbt-duckdb==1.11.0"