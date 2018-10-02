class IndexGroup:
    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.stocks = []

        self.history: History = None
        self.monthClosings: MonthClosings = None

    def add_stock(self, id, name):
        self.stocks.append(Stock(id, name, self))


class Stock:

    def __init__(self, stock_id, name, indexGroup: IndexGroup):
        self.stock_id = stock_id
        self.name = name
        self.indexGroup = indexGroup

        self.history: History = None
        self.monthClosings: MonthClosings = None
        self.ratings: AnalystRatings = None

        self.roi = None
        self.ebit_margin = None
        self.equity_ratio = None
        self.per = None
        self.per_5_years = None
        self.eps_current_year = None
        self.eps_next_year = None
        self.market_capitalization = None

    def rating(self):
        return 0

    def print_report(self):
        print("Marktkapitalisierung in EURO: \t%0.0f" % self.market_capitalization)
        print("1. Eigenkapitalrendite 2017: \t%0.2f%%" % self.roi)
        print("2. EBIT-Marge 2017\t\t\t\t%0.2f%%" % self.ebit_margin)
        print("3. Eigenkapitalquote 2017\t\t%0.2f%%" % self.equity_ratio)
        print("4. KGV 5 Jahre\t\t\t\t\t%0.2f" % self.per_5_years)
        print("5. KGV 2018e\t\t\t\t\t%0.2f" % self.per)
        print("6. Analystenmeinungen:\t\t\t" + str(self.ratings))
        print("7. Reaktion auf Quartalszahlen")
        print("8. Gewinnrevision")
        print("9. Performance 6 Monaten\t\t%0.3f%% (Referenzindex %s %0.3f%%)" % (
            self.history.performance_6_month() * 100, self.indexGroup.name,
            self.indexGroup.history.performance_6_month() * 100))
        print("10. Performance 1 Jahr\t\t\t%0.3f%% (Referenzindex %s %0.3f%%)" % (
            self.history.performance_1_year() * 100, self.indexGroup.name,
            self.indexGroup.history.performance_1_year() * 100))
        print("11. Kursmomentum steigend\t\t(abhängig von 9. und 10.)")
        print("12. Dreimonatsreversal\t\t\tPerformance für 3 Monate " + str(
            self.monthClosings.calculate_performance()) + " (Referenz " + self.indexGroup.name + " " + str(
            self.indexGroup.monthClosings.calculate_performance()) + ")")
        print("13a. EPS 2018e\t\t\t\t\t%0.3f" % self.eps_current_year)
        print("13b. EPS 2019e\t\t\t\t\t%0.3f" % self.eps_next_year)


class LargCap(Stock):

    def rating(self):
        return 0


class MidSmallCap(Stock):

    def rating(self):
        return 0


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


class MonthClosings:

    def __init__(self):
        self.closings = [0, 0, 0, 0, ]

    def calculate_performance(self):

        performance = []

        if self.closings and len(self.closings) > 1:
            for index, cloasing in enumerate(self.closings):
                if (index == 0):
                    last = cloasing
                else:
                    performance.append(round((cloasing / last) - 1, 4))

        return performance


class AnalystRatings:

    def __init__(self, buy: int, hold: int, sell: int):
        self.buy = buy
        self.hold = hold
        self.sell = sell

    def __str__(self) -> str:
        return "[buy {}, hold {}, sell {}]".format(self.buy, self.hold, self.sell)

    def count(self) -> int:
        return self.buy + self.hold + self.sell

    def sum_weight(self) -> int:
        return self.buy + self.hold * 2 + self.sell * 3