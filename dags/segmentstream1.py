"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
import logging
import os
import pymongo
from decimal import Decimal
from typing import List

import requests
from airflow import DAG
from airflow.hooks.base_hook import BaseHook
from airflow.models import TaskInstance, Connection
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta, date, time

import sys

from pymongo.errors import DuplicateKeyError

from classes.app_store.app_store_stat_item import AppStoreStatItem
from classes.python_dag_callbacks.transform_json_data import transform_json_data_callback

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

dag2 = DAG("segmentstream_demo1", default_args=default_args, schedule_interval=None)

extract_from_ad_service = PythonOperator(
    task_id="extract_from_ad_service",
    python_callable=extract_from_ad_service_callback,
    provide_context=True,
    dag=dag2
)

transform_table_data = PythonOperator(
    task_id="transform_table_data",
    python_callable=transform_table_data_callback,
    provide_context=True,
    dag=dag2
)

transform_table_data.set_upstream(task_or_task_list=extract_from_ad_service)

# Following code is not a copy paste cause in real scenario this steps may be completely different.
extract_from_app_store_1_service = PythonOperator(
    task_id="extract_from_app_store_1_service",
    provide_context=True,
    op_kwargs={'store_id': '1'},
    python_callable=extract_from_app_store_callback,
    dag=dag2
)

extract_from_app_store_2_service = PythonOperator(
    task_id="extract_from_app_store_2_service",
    provide_context=True,
    op_kwargs={'store_id': '2'},
    python_callable=extract_from_app_store_callback,
    dag=dag2
)

extract_from_app_store_3_service = PythonOperator(
    task_id="extract_from_app_store_3_service",
    provide_context=True,
    op_kwargs={'store_id': '3'},
    python_callable=extract_from_app_store_callback,
    dag=dag2
)


def check_currency_response(response: requests.Response):
    data = response.json()
    # print(data
    logging.info(data)
    if data:
        return True
    return False

wait_for_currency_rates_service = HttpSensor(
    task_id="wait_for_currency_rates_service",
    dag=dag2,
    http_conn_id='currency_service',
    method='GET',
    endpoint='get_rates',
    headers={"Content-Type": "application/json"},
    request_params={'date': datetime.now().strftime('%d.%m.%Y')},
    response_check=check_currency_response,
)

transform_json_data = PythonOperator(task_id="transform_json_data", python_callable=transform_json_data_callback, provide_context=True, dag=dag2)
transform_json_data.set_upstream(
    task_or_task_list=[
        extract_from_app_store_1_service,
        extract_from_app_store_2_service,
        extract_from_app_store_3_service
    ]
)


def get_daily_conversion_rates_callback(ds, **kwargs):
    if kwargs.get('test_mode'):
        connection = Connection(host='0.0.0.0', port=9093)
    else:
        connection = BaseHook.get_connection("currency_service")

    response = requests.get(
        url="http://{host}:{port}/get_rates?date={date}".format(host=connection.host, port=connection.port, date=datetime.now().strftime('%d.%m.%Y'))
    )

    return response.json()


get_daily_conversion_rates = PythonOperator(
    task_id='get_daily_conversion_rates',
    python_callable=get_daily_conversion_rates_callback,
    provide_context=True,
    dag=dag2
)

get_daily_conversion_rates.set_upstream(task_or_task_list=wait_for_currency_rates_service)


def perform_currency_conversions_callback(ds, **kwargs):
    task_instance = kwargs['task_instance']
    app_store_data = task_instance.xcom_pull(task_ids='transform_json_data')
    currency_conversion_rates = task_instance.xcom_pull(task_ids='get_daily_conversion_rates')

    # apply currency exchange rates here

    return app_store_data


perform_currency_conversions = PythonOperator(
    task_id="perform_currency_conversions",
    provide_context=True,
    python_callable=perform_currency_conversions_callback,
    dag=dag2
)



perform_currency_conversions.set_upstream(task_or_task_list=[transform_json_data, get_daily_conversion_rates])


def get_mongo_connection(kwargs):
    if kwargs.get('test_mode'):
        connection = Connection(host='0.0.0.0', port=27017)
    else:
        connection = BaseHook.get_connection("my_mongo_db")


    client = pymongo.MongoClient(host=connection.host, port=connection.port)
    return client


def combine_and_append_datasources_callback(ds, **kwargs):
    task_instance = kwargs['task_instance']

    app_store_stats: List[AppStoreStatItem] = task_instance.xcom_pull(task_ids='perform_currency_conversions')
    ad_exchange_stats = task_instance.xcom_pull(task_ids='transform_table_data')

    out = []

    for item in app_store_stats:
        out.append({'date': item.date, 'value': item.revenue})

    for item in ad_exchange_stats:
        out.append({'date': item['date'], 'value': item['revenue']})

    # maybe sum is what we need

    daily_sum = Decimal(0)
    for item in out:
        daily_sum += Decimal(item['value'])

    # write to mongo

    sum = str(daily_sum)


    client = get_mongo_connection(kwargs)
    db = client.get_database(name='ss_stats')
    coll = db.get_collection('revenue')
    coll.create_index(keys=[('date', pymongo.ASCENDING)], unique=True)

    try:
        today = datetime.combine(date.today(), time())
        coll.insert({'date': today, 'revenue': sum})
    except DuplicateKeyError as e:
        logging.exception(e)

    return sum

combine_and_append_datasources = PythonOperator(
    task_id='combine_and_append_datasources',
    python_callable=combine_and_append_datasources_callback,
    provide_context=True,
    dag=dag2
)

combine_and_append_datasources.set_upstream(task_or_task_list=[perform_currency_conversions, transform_table_data])


def check_weekly_historical_data_callback(ds, **kwargs):

    client = get_mongo_connection(kwargs)
    db = client.get_database(name='ss_stats')
    coll = db.get_collection('revenue')

    period_start = datetime.now() - timedelta(days=7)
    period_end = datetime.now()

    try:
        data = []
        cursor = coll.find({"date": {"$gte": period_start, "$lte": period_end}})
        for doc in cursor:
            data.append(doc)

    except Exception as e:
        logging.exception(e)

    return data

check_weekly_historical_data = PythonOperator(
    task_id='check_weekly_historical_data',
    python_callable=check_weekly_historical_data_callback,
    provide_context=True,
    dag=dag2
)

check_weekly_historical_data.set_upstream(task_or_task_list=combine_and_append_datasources)

def make_next_day_prediction_callback(ds, **kwargs):
    if kwargs.get('test_mode'):
        connection = Connection(host='0.0.0.0', port=9094)
    else:
        connection = BaseHook.get_connection("prediction_service")

    date_for_prediction = datetime.now() + timedelta(1)

    response = requests.get(
        url="http://{host}:{port}/make_prediction?date={date}".format(host=connection.host, port=connection.port,
                                                                date=(date_for_prediction).strftime('%d.%m.%Y'))
    )

    prediction = response.json()

    client = get_mongo_connection(kwargs)
    db = client.get_database(name='ss_stats')
    coll = db.get_collection('revenue_predictions')

    coll.insert(
        {
            'date': date_for_prediction,
            'revenue': prediction['revenue'],
            'accuracy': prediction['accuracy']
        }
    )

    return prediction

make_next_day_prediction = PythonOperator(
    task_id='make_next_day_prediction',
    python_callable=make_next_day_prediction_callback,
    provide_context=True,
    dag=dag2
)
make_next_day_prediction.set_upstream(task_or_task_list=check_weekly_historical_data)
