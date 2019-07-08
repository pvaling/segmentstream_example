import random


class AdNetworkStatItem:
    date = None
    revenue = None

    def __init__(self, date, revenue):
        self.date = date
        self.revenue = revenue  # USD
        self.some_field = random.randint(100, 1000)  # odd field to remove during table formatting stage (demo purpose)

    def __str__(self):
        return 'AdNetworkStatItem ({} - {})'.format(self.date, self.revenue)

    def __repr__(self):
        return str(self)