from airflow.hooks.base_hook import BaseHook
from airflow.models import Connection

from classes.ad_exchange.ad_network_x_client import AdNetworkXClient
from classes.app_store.app_store_x_client import AppStoreXClient


def extract_from_app_store(ds, **kwargs):
    if kwargs.get('test_mode'):
        # connection = Connection(host='docker.for.mac.localhost', port=9092)
        connection = Connection(host='0.0.0.0', port=9092)
    else:
        store_code = kwargs.get('store_id')
        connection = BaseHook.get_connection("app_store_{store_code}".format(store_code=store_code))


    app_store_client = AppStoreXClient(host=connection.host, port=connection.port, store_code=store_code)

    stats = app_store_client.get_stats(date_from=ds, date_to=ds)

    #need_put_data_into_external_storage

    return stats