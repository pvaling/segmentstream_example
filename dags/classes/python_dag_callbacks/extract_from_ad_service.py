from airflow.hooks.base_hook import BaseHook
from airflow.models import Connection

from classes.ad_exchange.ad_network_x_client import AdNetworkXClient


def extract_from_ad_service(ds, **kwargs):
    if kwargs.get('test_mode'):
        # connection = Connection(host='docker.for.mac.localhost', port=9092)
        connection = Connection(host='0.0.0.0', port=9092)
    else:
        connection = BaseHook.get_connection("ad_network_x")


    ad_service_client = AdNetworkXClient(host=connection.host, port=connection.port)

    stats = ad_service_client.get_stats(date_from=ds, date_to=ds)

    #need_put_data_into_external_storage

    return stats