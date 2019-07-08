import requests

from classes.ad_exchange.abstract_ad_exchange_client import AbstractAdExchangeClient
from classes.ad_exchange.ad_network_stat_item import AdNetworkStatItem


class AdNetworkXClient(AbstractAdExchangeClient):

    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        self.connection = requests.Session()
        return self.connection

    def get_stats(self, date_from, date_to):

        response = self.connection.get(
            url='http://{host}:{port}/get_stats'.format(
                host=self.host,
                port=self.port
            )
        )

        resp = response.json()
        stat_items_list = [AdNetworkStatItem(x['date'], x['revenue']) for x in resp]

        return stat_items_list