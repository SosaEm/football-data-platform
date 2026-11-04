FROM apache/airflow:3.3.2

USER root
RUN mkdir -p /opt/project/data && chown -R airflow:0 /opt/project/data

USER airflow
RUN python -m venv /home/airflow/dbt_venv \
    && /home/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-core dbt-postgres