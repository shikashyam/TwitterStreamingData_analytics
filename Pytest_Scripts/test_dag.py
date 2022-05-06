from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pytest
from DAG_Streaming import DAG
from HitAPI import CallAPI
from CleanData import CleanData

def test_python_operator():
    test = PythonOperator(task_id="CallTwitterAPI", python_callable=CallAPI) 
    result = test.execute(context={})
    assert result == None

def test_python_operator2():
    test = PythonOperator(task_id="CleanData", python_callable=CleanData) 
    result = test.execute(context={})
    assert result == 'Job Triggered' or 'Extract job completed. Triggering Dataflow job'