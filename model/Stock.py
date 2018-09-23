class IndexGroup:
    def __init__(self, stock_id, name):
        self.stock_id = stock_id
        self.name = name

        self.roi = None

class Stock:

    def __init__(self, stock_id, name):
        self.stock_id = stock_id
        self.name = name

        self.roi = None

    def rating(self):
        return 0

class LargCap(Stock):

    def rating(self):
        return 0


class MidSmallCap(Stock):

    def rating(self):
        return 0