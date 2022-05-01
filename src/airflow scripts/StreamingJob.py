from airflow import DAG
from airflow.operators import PythonOperator
from CleanData import CleanData
from HitAPI import CallAPI
from datetime import datetime


with DAG(dag_id="TwitterStreaming",
         start_date=datetime(2022, 4, 28),
         schedule_interval="@hourly",
         catchup=False) as dag:

    task1 = PythonOperator(
        task_id="CallTwitterAPI",
        python_callable=CallAPI)

    task2 = PythonOperator(
        task_id="CleanData",
        python_callable=CleanData)


task1 >> task2