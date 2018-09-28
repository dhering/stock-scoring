from libs.model import Stock


def rate_roi(roi):
    if roi > 20: return 1
    if roi < 10: return -1
    return 0


def rate_ebit(ebit_margin):
    if ebit_margin > 12: return 1
    if ebit_margin < 6: return -1
    return 0


def rate_equity_ratio(equity_ratio):
    if equity_ratio > 25: return 1
    if equity_ratio < 15: return -1
    return 0


def rate_per(per):
    if per < 12: return 1
    if per > 16: return -1
    return 0


def rate_eps(eps_last_year, eps_current_year):
    changing = eps_current_year / eps_last_year - 1

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
    performance = 0

    for idx, stockClosing in enumerate(stockClosings):
        indexClosing = indexClosings[idx]

        if stockClosing > indexClosing:
            performance += 1
        if stockClosing < indexClosing:
            performance += -1

    if performance > 0: return 1
    if performance < 0: return -1
    return 0


def rate_ratings(ratings):

    count = ratings.buy + ratings.hold + ratings.sell
    sum = ratings.buy + ratings.hold * 2 + ratings.sell * 3

    rating = round(sum / count, 1)

    if rating <= 1.5: return 1
    if rating >= 2.5: return -1
    return 0


def rate(stock: Stock, print_overview = False):

    roi = rate_roi(stock.roi)
    ebit = rate_ebit(stock.ebit_margin)
    equity_ratio = rate_equity_ratio(stock.equity_ratio)
    per_5_years = rate_per(stock.per_5_years)
    per = rate_per(stock.per)
    ratings = rate_ratings(stock.ratings)
    quarterly_figures = 0
    profit_revision = 0

    performance_6_month = rate_performance(stock.history.performance_6_month(),
                                           stock.indexGroup.history.performance_6_month())

    performance_1_year = rate_performance(stock.history.performance_1_year(),
                                          stock.indexGroup.history.performance_1_year())
    price_momentum = rate_price_momentum(performance_6_month, performance_1_year)
    month_closings = rate_monthClosings(stock.monthClosings.calculate_performance(),
                                  stock.indexGroup.monthClosings.calculate_performance())
    eps = rate_eps(stock.eps_last_year, stock.eps_current_year)

    all_ratings = [roi, ebit, equity_ratio, per_5_years, per, ratings, quarterly_figures, profit_revision,
    performance_6_month, performance_1_year, price_momentum, month_closings, eps]

    if print_overview:
        print("1. Eigenkapitalrendite 2017: \t%i" % roi)
        print("2. EBIT-Marge 2017\t\t\t\t%i" % ebit)
        print("3. Eigenkapitalquote 2017\t\t%i" % equity_ratio)
        print("4. KGV 5 Jahre\t\t\t\t\t%i" % per_5_years)
        print("5. KGV 2018e\t\t\t\t\t%i" % per)
        print("6. Analystenmeinungen:\t\t\t%i" % ratings)
        print("7. Reaktion auf Quartalszahlen\t%i" % quarterly_figures)
        print("8. Gewinnrevision\t\t\t\t%i" % profit_revision)
        print("9. Performance 6 Monaten\t\t%i" % performance_6_month)
        print("10. Performance 1 Jahr\t\t\t%i" % performance_1_year)

        print("11. Kursmomentum steigend\t\t%i" % price_momentum)

        print("12. Dreimonatsreversal\t\t\t%i" % month_closings)

        print("13. EPS \t\t\t\t\t\t%i" % eps)

    print("Bewertung: %s - %i" % (stock.name, sum(all_ratings)))
