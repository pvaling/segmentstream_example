"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
import os

from airflow import DAG
from datetime import datetime, timedelta

import sys

from airflow.operators.dummy_operator import DummyOperator
from classes.python_dag_callbacks.callbacks import check_weekly_historical_data_callback, \
    combine_and_append_datasources_callback, perform_currency_conversions_callback, make_next_day_prediction_callback, \
    get_daily_conversion_rates_callback, check_currency_response
from classes.python_dag_callbacks.transform_json_data import transform_json_data_callback
from classes.python_dag_callbacks.user_config import get_config

sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

from airflow.operators.python_operator import PythonOperator
from airflow.operators.sensors import HttpSensor
from classes.python_dag_callbacks.extract_from_ad_service import extract_from_ad_service as extract_from_ad_service_callback
from classes.python_dag_callbacks.transform_table_data import transform_table_data as transform_table_data_callback
from classes.python_dag_callbacks.extract_from_app_store import extract_from_app_store as extract_from_app_store_callback

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

dag_x = DAG("segmentstream_demo", default_args=default_args, schedule_interval=None)

initial_task = DummyOperator(task_id='start', dag=dag_x)

wait_for_currency_rates_service = HttpSensor(
    task_id="wait_for_currency_rates_service",
    dag=dag_x,
    http_conn_id='currency_service',
    method='GET',
    endpoint='get_rates',
    headers={"Content-Type": "application/json"},
    request_params={'date': datetime.now().strftime('%d.%m.%Y')},
    response_check=check_currency_response,
)
wait_for_currency_rates_service << initial_task


get_daily_conversion_rates = PythonOperator(
    task_id="get_daily_conversion_rates",
    python_callable=get_daily_conversion_rates_callback,
    provide_context=True,
    dag=dag_x
)

get_daily_conversion_rates.set_upstream(task_or_task_list=wait_for_currency_rates_service)

configs = get_config()

for conf_item in configs:
    task_prefix = conf_item.get('user', 'XYZ')
    dummy_start_task = DummyOperator(task_id='{user_id}'.format(user_id=task_prefix), dag=dag_x)
    dummy_start_task << initial_task

    extract_from_ad_service = PythonOperator(
        task_id=f"{task_prefix}_extract_from_ad_service",
        python_callable=extract_from_ad_service_callback,
        provide_context=True,
        dag=dag_x
    )

    extract_from_ad_service.set_upstream(dummy_start_task)

    transform_table_data = PythonOperator(
        task_id=f"{task_prefix}_transform_table_data",
        python_callable=transform_table_data_callback,
        provide_context=True,
        dag=dag_x
    )

    transform_table_data.set_upstream(task_or_task_list=extract_from_ad_service)

    # Following code is not a copy paste cause in real scenario this steps may be completely different.
    enabled_user_shops = conf_item.get('params', {}).get('shops', [])


    app_store_jobs = []
    if 1 in enabled_user_shops:
        extract_from_app_store_1_service = PythonOperator(
            task_id=f"{task_prefix}_extract_from_app_store_1_service",
            provide_context=True,
            op_kwargs={'store_id': '1'},
            python_callable=extract_from_app_store_callback,
            dag=dag_x
        )
        extract_from_app_store_1_service << dummy_start_task
        app_store_jobs.append(extract_from_app_store_1_service)

    if 2 in enabled_user_shops:
        extract_from_app_store_2_service = PythonOperator(
            task_id=f"{task_prefix}_extract_from_app_store_2_service",
            provide_context=True,
            op_kwargs={'store_id': '2'},
            python_callable=extract_from_app_store_callback,
            dag=dag_x
        )
        extract_from_app_store_2_service << dummy_start_task
        app_store_jobs.append(extract_from_app_store_2_service)


    if 3 in enabled_user_shops:
        extract_from_app_store_3_service = PythonOperator(
            task_id=f"{task_prefix}_extract_from_app_store_3_service",
            provide_context=True,
            op_kwargs={'store_id': '3'},
            python_callable=extract_from_app_store_callback,
            dag=dag_x
        )
        extract_from_app_store_3_service << dummy_start_task
        app_store_jobs.append(extract_from_app_store_3_service)


    transform_json_data = PythonOperator(
        task_id=f"{task_prefix}_transform_json_data",
        python_callable=transform_json_data_callback,
        provide_context=True, dag=dag_x)

    transform_json_data.set_upstream(
        task_or_task_list=app_store_jobs
    )

    need_to_make_conversion = conf_item.get('params', {}).get('conversion', False)

    if need_to_make_conversion:
        perform_currency_conversions = PythonOperator(
            task_id=f"{task_prefix}_perform_currency_conversions",
            provide_context=True,
            python_callable=perform_currency_conversions_callback,
            dag=dag_x
        )

        perform_currency_conversions.set_upstream(task_or_task_list=[transform_json_data, get_daily_conversion_rates])


    combine_and_append_datasources = PythonOperator(
        task_id=f"{task_prefix}_combine_and_append_datasources",
        python_callable=combine_and_append_datasources_callback,
        provide_context=True,
        dag=dag_x
    )


    if need_to_make_conversion:
        next_tasks = [perform_currency_conversions, transform_table_data]
    else:
        next_tasks = [transform_json_data, transform_table_data]

    combine_and_append_datasources.set_upstream(task_or_task_list=next_tasks)


    check_weekly_historical_data = PythonOperator(
        task_id=f"{task_prefix}_check_weekly_historical_data",
        python_callable=check_weekly_historical_data_callback,
        provide_context=True,
        dag=dag_x
    )

    check_weekly_historical_data.set_upstream(task_or_task_list=combine_and_append_datasources)


    make_next_day_prediction = PythonOperator(
        task_id=f"{task_prefix}_make_next_day_prediction",
        python_callable=make_next_day_prediction_callback,
        provide_context=True,
        queue='hearvy_tasks',
        dag=dag_x
    )
    make_next_day_prediction.set_upstream(task_or_task_list=check_weekly_historical_data)
