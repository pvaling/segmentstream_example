import requests

from classes.ad_exchange.ad_network_stat_item import AdNetworkStatItem
from classes.app_store.abstract_app_store_client import AbstractAppStoreClient
from classes.app_store.app_store_stat_item import AppStoreStatItem


class AppStoreXClient(AbstractAppStoreClient):

    def __init__(self, store_code, host=None, port=None):
        self.host = host
        self.port = port
        self.store_code = store_code
        self._connect()

    def _connect(self):
        self.connection = requests.Session()
        return self.connection

    def get_stats(self, date_from, date_to):

        response = self.connection.get(
            url='http://{host}:{port}/store{store_code}'.format(
                host=self.host,
                port=self.port,
                store_code=self.store_code
            )
        )

        resp = response.json()
        stat_items_list = [AppStoreStatItem(x['date'], x['revenue']) for x in resp]

        return stat_items_list