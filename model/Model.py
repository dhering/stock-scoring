class IndexGroup:
    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.stocks = []

        self.history = None

    def add_stock(self, id, name):
        self.stocks.append(Stock(id, name, self))


class History:
    def __init__(self, today, half_a_year, one_year):
        self.today = today
        self.half_a_year = half_a_year
        self.one_year = one_year

    def performance_6_month(self):
        return round((self.today / self.half_a_year) - 1, 4)
        self.one_year = one_year

    def performance_1_year(self):
        return round((self.today / self.one_year) - 1, 4)

class Stock:

    def __init__(self, stock_id, name, indexGroup):
        self.stock_id = stock_id
        self.name = name
        self.indexGroup = indexGroup

        self.roi = None

    def rating(self):
        return 0


class LargCap(Stock):

    def rating(self):
        return 0


class MidSmallCap(Stock):

    def rating(self):
        return 0
