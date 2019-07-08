import random


class AppStoreStatItem:
    date = None
    revenue = None

    def __init__(self, date, revenue):
        self.date = date
        self.revenue = revenue
        self.attrs = {'attr1': 'a', 'attr2': 'b'} #  to highlight json nature of data
        self.some_field = random.randint(100, 1000)  # odd field to remove during table formatting stage (demo purpose)

    def __str__(self):
        return 'AppStoreStatItem ({} - {})'.format(self.date, self.revenue)

    def __repr__(self):
        return str(self)