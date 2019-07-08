import logging
from typing import List

from airflow.models import TaskInstance

from classes.ad_exchange.ad_network_stat_item import AdNetworkStatItem
from classes.app_store.app_store_stat_item import AppStoreStatItem


def transform_json_data_callback(ds, **kwargs):
    task_instance: TaskInstance = kwargs['task_instance']
    task = kwargs['task']

    logging.info(task_instance)
    logging.info(task)
    prev_tasks = task.upstream_task_ids

    results = []

    for prev_task in prev_tasks:
        prev_task_result = task_instance.xcom_pull(task_ids=prev_task)
        logging.info(prev_task_result)
        results += prev_task_result

    return results