from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2019, 7, 6),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}


dag_y = DAG("task_race", default_args=default_args, schedule_interval=None)


task1 = DummyOperator(task_id='task1', dag=dag_y)
task2 = DummyOperator(task_id='task2', dag=dag_y)
task3 = DummyOperator(task_id='task3', dag=dag_y)

task1 >> task2 >> task3
