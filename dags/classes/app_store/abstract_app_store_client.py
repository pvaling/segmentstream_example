from abc import ABC
from typing import List

from classes.app_store.app_store_stat_item import AppStoreStatItem


class AbstractAppStoreClient(ABC):

    connection = None

    def get_stats(self, date_from, date_to) -> List[AppStoreStatItem]:
        raise NotImplementedError()

    def connect(self):
        raise NotImplementedError()
