from abc import ABC
from typing import List

from classes.ad_exchange.ad_network_stat_item import AdNetworkStatItem


class AbstractAdExchangeClient(ABC):

    connection = None

    def get_stats(self, date_from, date_to) -> List[AdNetworkStatItem]:
        raise NotImplementedError()

    def connect(self):
        raise NotImplementedError()
