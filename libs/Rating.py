from libs.model import Stock, AnalystRatings, ReactionToQuarterlyNumbers


class Rating:

    def __init__(self, stock: Stock):
        self.stock = stock
        self.is_medium = check_for_medium_stock(stock)
        self.is_small = check_for_small_stock(stock)
        self.is_finance = check_for_finance(stock)

        self.roi = 0
        self.ebit = 0
        self.equity_ratio = 0
        self.per_5_years = 0
        self.per = 0
        self.per_fallback = 0
        self.ratings = 0
        self.quarterly_numbers = 0
        self.profit_revision = 0
        self.performance_6_month = 0
        self.performance_1_year = 0
        self.price_momentum = 0
        self.month_closings = 0
        self.eps = 0

        self.buy_signal = "-"

        self.result = 0

    def rate(self):

        self.roi = rate_roi(self.stock.roi)

        if self.is_finance:
            self.ebit = 0
        else:
            self.ebit = rate_ebit(self.stock.ebit_margin)

        if self.is_finance:
            self.equity_ratio = rate_equity_ratio_finance(self.stock.equity_ratio)
        else:
            self.equity_ratio = rate_equity_ratio(self.stock.equity_ratio)

        self.per_5_years = rate_per(self.stock.per_5_years)
        self.per = rate_per(self.stock.per) if self.stock.per != 0 else rate_per(self.stock.per_fallback)

        if (self.is_small and self.stock.ratings.count() <= 5):
            self.ratings = rate_small_ratings(self.stock.ratings)
        else:
            self.ratings = rate_ratings(self.stock.ratings)

        self.quarterly_numbers = rate_quarterly_numbers(self.stock.reaction_to_quarterly_numbers)
        self.profit_revision = rate_profit_revision(self.stock)

        self.performance_6_month = rate_performance(self.stock.history.performance_6_month(),
                                                    self.stock.indexGroup.history.performance_6_month())

        self.performance_1_year = rate_performance(self.stock.history.performance_1_year(),
                                                   self.stock.indexGroup.history.performance_1_year())
        self.price_momentum = rate_price_momentum(self.performance_6_month, self.performance_1_year)

        if (self.is_medium or self.is_small):
            self.month_closings = 0
        else:
            self.month_closings = rate_monthClosings(self.stock.monthClosings.calculate_performance(),
                                                     self.stock.indexGroup.monthClosings.calculate_performance())

        self.eps = rate_eps(self.stock.eps_current_year, self.stock.eps_next_year)

        all_ratings = [self.roi, self.ebit, self.equity_ratio, self.per_5_years, self.per, self.ratings,
                       self.quarterly_numbers, self.profit_revision, self.performance_6_month,
                       self.performance_1_year, self.price_momentum, self.month_closings, self.eps]

        self.result = sum(all_ratings)

        self.rate_buy_signal()

        return self.result

    def print_overview(self):
        print("1. Eigenkapitalrendite 2017: \t%i" % self.roi)
        print("2. EBIT-Marge 2017\t\t\t\t%i" % self.ebit)
        print("3. Eigenkapitalquote 2017\t\t%i" % self.equity_ratio)
        print("4. KGV 5 Jahre\t\t\t\t\t%i" % self.per_5_years)
        print("5. KGV 2018e\t\t\t\t\t%i" % self.per)
        print("6. Analystenmeinungen:\t\t\t%i" % self.ratings)
        print("7. Reaktion auf Quartalszahlen\t%i" % self.quarterly_numbers)
        print("8. Gewinnrevision\t\t\t\t%i" % self.profit_revision)
        print("9. Performance 6 Monaten\t\t%i" % self.performance_6_month)
        print("10. Performance 1 Jahr\t\t\t%i" % self.performance_1_year)

        print("11. Kursmomentum steigend\t\t%i" % self.price_momentum)

        print("12. Dreimonatsreversal\t\t\t%i" % self.month_closings)

        print("13. Gewinnwachstum \t\t\t\t%i" % self.eps)

    def rate_quality(self):
        valid_results = [
            self.stock.roi != 0,
            self.is_finance or self.stock.ebit_margin != 0,
            self.stock.equity_ratio != 0,
            self.stock.per_5_years != 0,
            self.stock.per != 0,
            self.stock.ratings is not None and (
                        self.stock.ratings.buy != 0 or self.stock.ratings.hold != 0 or self.stock.ratings.sell != 0),
            self.stock.reaction_to_quarterly_numbers is not None and self.stock.reaction_to_quarterly_numbers.calc_growth() != 0,
            self.stock.eps_current_year != 0 and self.stock.historical_eps_current_year != 0 and self.stock.eps_next_year != 0 and self.stock.historical_eps_next_year != 0,
            self.stock.history.performance_6_month() != 0 and self.stock.indexGroup.history.performance_6_month() != 0,
            self.stock.history.performance_1_year() != 0 and self.stock.indexGroup.history.performance_1_year() != 0,
            self.is_small or self.is_medium or (self.stock.monthClosings.calculate_performance() != 0 and self.stock.indexGroup.monthClosings.calculate_performance() != 0),
            self.stock.eps_current_year != 0 and self.stock.eps_next_year != 0
        ]

        return round(sum(valid_results) / len(valid_results), 2)

    def rate_buy_signal(self):

        if self.is_small or self.is_medium:
            if self.result == 7:
                self.buy_signal = "+"
            elif self.result > 7:
                self.buy_signal = "++"
            else:
                self.buy_signal = "-"
        else:
            if self.result == 4:
                self.buy_signal = "+"
            elif self.result > 4:
                self.buy_signal = "++"
            else:
                self.buy_signal = "-"


def check_for_small_stock(stock: Stock):
    return stock.market_capitalization < 2000000000 if stock.market_capitalization is not None else False


def check_for_medium_stock(stock: Stock):
    return 5000000000 > stock.market_capitalization >= 2000000000 if stock.market_capitalization is not None else False


def check_for_finance(stock):
    return stock.field == "Finanzsektor"


def rate_roi(roi):
    if roi == 0: return 0
    if roi > 20: return 1
    if roi < 10: return -1
    return 0


def rate_ebit(ebit_margin):
    if ebit_margin == 0: return 0
    if ebit_margin > 12: return 1
    if ebit_margin < 6: return -1
    return 0


def rate_equity_ratio(equity_ratio):
    if equity_ratio == 0: return 0
    if equity_ratio > 25: return 1
    if equity_ratio < 15: return -1
    return 0


def rate_equity_ratio_finance(equity_ratio):
    if equity_ratio == 0: return 0
    if equity_ratio > 10: return 1
    if equity_ratio < 5: return -1
    return 0


def rate_per(per):
    if per == 0: return 0
    if per <= 0: return -1
    if per > 0 and per < 12: return 1
    if per > 16: return -1
    return 0


def rate_eps(eps_current_year, eps_next_year):
    if eps_current_year == 0:
        return 0

    changing = eps_next_year / eps_current_year - 1

    if changing > 0.05: return 1
    if changing < -0.05: return -1
    return 0


def rate_performance(stock, index):
    performance = stock - index

    if performance > 0.05: return 1
    if performance < -0.05: return -1
    return 0


def rate_price_momentum(performance_6_month, performance_1_year):
    if performance_6_month == 1 and performance_1_year != 1: return 1
    if performance_6_month == -1 and performance_1_year != -1: return -1
    return 0


def rate_monthClosings(stockClosings, indexClosings):
    def compare_closing(stockClosing, indexClosing):
        if stockClosing > indexClosing:
            return 1
        elif stockClosing < indexClosing:
            return -1
        else:
            return 0

    performance = sum(map(compare_closing, stockClosings, indexClosings))

    if performance == len(stockClosings): return -1
    if performance * -1 == len(stockClosings): return 1
    return 0


def rate_ratings(ratings: AnalystRatings):
    count = ratings.count()
    sum = ratings.sum_weight()

    if count == 0:
        return -1

    rating = round(sum / count, 1)

    if rating <= 1.5: return -1
    if rating >= 2.5: return 1
    return 0


def rate_quarterly_numbers(reaction_to_quarterly_numbers: ReactionToQuarterlyNumbers):
    if reaction_to_quarterly_numbers is None:
        return 0

    growth = reaction_to_quarterly_numbers.calc_growth()

    if growth > 0.01:
        return 1
    elif growth < -0.01:
        return -1

    return 0


def rate_profit_revision(stock: Stock):
    if stock.eps_next_year > 0:
        next_year_growth = stock.historical_eps_next_year / stock.eps_next_year - 1
    else:
        next_year_growth = 0

    if stock.eps_current_year > 0:
        current_year_growth = stock.historical_eps_current_year / stock.eps_current_year - 1
    else:
        current_year_growth = 0

    if next_year_growth <= - 0.05 and current_year_growth <= -0.05:
        return -1

    if next_year_growth >= 0.05 and current_year_growth >= 0.05:
        return 1

    return 0


def rate_small_ratings(ratings: AnalystRatings):
    count = ratings.count()
    sum = ratings.sum_weight()

    if count == 0:
        return -1

    rating = round(sum / count, 1)

    if rating <= 1.5: return 1
    if rating >= 2.5: return -1
    return 0
