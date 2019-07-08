import logging
from typing import List

from classes.ad_exchange.ad_network_stat_item import AdNetworkStatItem


def transform_table_data(ds, **kwargs):
    task_instance = kwargs['task_instance']
    data: List[AdNetworkStatItem] = task_instance.xcom_pull(task_ids='extract_from_ad_service')

    new_data = []
    for item in data:
        new_data.append({
            'source': 'ad_exchange',  # feature for prediction model
            'date': item.date,
            'revenue': item.revenue
        })

    logging.info(data)
    logging.info(new_data)

    return new_data