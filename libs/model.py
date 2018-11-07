import inspect


class IndexGroup:
    def __init__(self, index: str, name: str):
        self.index: str = index
        self.name: str = name
        self.stocks = []

        self.history: History = None
        self.monthClosings: MonthClosings = None

    def add_stock(self, id, name, field = ""):
        stock = Stock(id, name, self)
        stock.field = field

        self.stocks.append(stock)


class Stock:

    def __init__(self, stock_id: str, name: str, indexGroup: IndexGroup):
        self.stock_id: str = stock_id
        self.name: str = name
        self.indexGroup = indexGroup

        self.field = ""

        self.history: History = None
        self.monthClosings: MonthClosings = None
        self.ratings: AnalystRatings = None

        self.roi = None
        self.ebit_margin = None
        self.equity_ratio = None
        self.per = None
        self.per_5_years = None
        self.reaction_to_quarterly_numbers = None
        self.eps_current_year = None
        self.eps_next_year = None
        self.market_capitalization = None

        self.historical_eps_current_year = None
        self.historical_eps_next_year = None
        self.historical_eps_date = None

    def asDict(self):
        props = {}
        for name in dir(self):
            value = getattr(self, name)
            if name == "history" or name == "monthClosings" or name == "ratings":
                props[name] = value.asDict()
            elif not name.startswith('__') and not name.startswith('indexGroup') and not inspect.ismethod(value):
                props[name] = value
        return props

    def rating(self):
        return 0

    def print_report(self):
        print("Marktkapitalisierung in EURO: \t%0.0f" % self.market_capitalization)
        print("Branche:\t\t\t\t\t\t%s" % self.field)
        print("1. Eigenkapitalrendite 2017: \t%0.2f%%" % self.roi)
        print("2. EBIT-Marge 2017\t\t\t\t%0.2f%%" % self.ebit_margin)
        print("3. Eigenkapitalquote 2017\t\t%0.2f%%" % self.equity_ratio)
        print("4. KGV 5 Jahre\t\t\t\t\t%0.2f" % self.per_5_years)
        print("5. KGV 2018e\t\t\t\t\t%0.2f" % self.per)
        print("6. Analystenmeinungen:\t\t\t" + str(self.ratings))
        print("7. Reaktion auf Quartalszahlen")
        print("8. Gewinnrevision\t\t\t\tEPS Entwicklung dieses Jahr %0.2f vs. %0.2f am %s\n"
              "\t\t\t\t\t\t\t\tEPS Entwicklung kommendes Jahr %0.2f vs. %0.2f am %s"
              % (self.eps_current_year, self.historical_eps_current_year, self.historical_eps_date, self.eps_next_year, self.historical_eps_next_year, self.historical_eps_date))
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

    def asDict(self):
        return {
            "today": self.today,
            "half_a_year": self.half_a_year,
            "one_year": self.one_year
        }

    def performance_6_month(self):
        if self.half_a_year == 0:
            return 0
        return round((self.today / self.half_a_year) - 1, 4)

    def performance_1_year(self):
        if self.one_year == 0:
            return 0
        return round((self.today / self.one_year) - 1, 4)


class MonthClosings:

    def __init__(self):
        self.closings = [0, 0, 0, 0, ]

    def asDict(self) -> dict:
        return {
            "closings": self.closings
        }

    def calculate_performance(self):

        performance = []

        if self.closings and len(self.closings) > 1:
            for index, closing in enumerate(self.closings):
                if index == 0:
                    last = closing
                elif last == 0:
                    performance.append(0.0)
                else:
                    performance.append(round((closing / last) - 1, 4))

        return performance


class AnalystRatings:

    def __init__(self, buy: int, hold: int, sell: int):
        self.buy = buy
        self.hold = hold
        self.sell = sell

    def __str__(self) -> str:
        return "[buy {}, hold {}, sell {}]".format(self.buy, self.hold, self.sell)

    def asDict(self) -> dict:
        return {
            "buy": self.buy,
            "hold": self.hold,
            "sell": self.sell
        }

    def count(self) -> int:
        return self.buy + self.hold + self.sell

    def sum_weight(self) -> int:
        return self.buy + self.hold * 2 + self.sell * 3