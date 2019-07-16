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
from airflow.hooks.base_hook import BaseHook
from airflow.models import Connection
from datetime import datetime, timedelta, date, time

import sys

from pymongo.errors import DuplicateKeyError

from classes.app_store.app_store_stat_item import AppStoreStatItem

sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))


def get_mongo_connection(kwargs):
    if kwargs.get('test_mode'):
        connection = Connection(host='0.0.0.0', port=27017)
    else:
        connection = BaseHook.get_connection("my_mongo_db")

    client = pymongo.MongoClient(host=connection.host, port=connection.port)
    return client

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


def combine_and_append_datasources_callback(ds, **kwargs):
    task_instance = kwargs['task_instance']

    app_store_stats: List[AppStoreStatItem] = task_instance.xcom_pull(task_ids='perform_currency_conversions')
    ad_exchange_stats = task_instance.xcom_pull(task_ids='transform_table_data')

    out = []
    if app_store_stats:
        for item in app_store_stats:
            out.append({'date': item.date, 'value': item.revenue})

    if ad_exchange_stats:
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


def perform_currency_conversions_callback(ds, **kwargs):
    task_instance = kwargs['task_instance']
    app_store_data = task_instance.xcom_pull(task_ids='transform_json_data')
    currency_conversion_rates = task_instance.xcom_pull(task_ids='get_daily_conversion_rates')

    # apply currency exchange rates here

    return app_store_data


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


def get_daily_conversion_rates_callback(ds, **kwargs):
    if kwargs.get('test_mode'):
        connection = Connection(host='0.0.0.0', port=9093)
    else:
        connection = BaseHook.get_connection("currency_service")

    response = requests.get(
        url="http://{host}:{port}/get_rates?date={date}".format(host=connection.host, port=connection.port,
                                                                date=datetime.now().strftime('%d.%m.%Y'))
    )

    return response.json()


def check_currency_response(response: requests.Response):
    data = response.json()
    # print(data
    logging.info(data)
    if data:
        return True
    return False