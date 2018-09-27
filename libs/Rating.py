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


def rate(stock: Stock):
    print("1. Eigenkapitalrendite 2017: \t%i" % rate_roi(stock.roi))
    print("2. EBIT-Marge 2017\t\t\t\t%i" % rate_ebit(stock.ebit_margin))
    print("3. Eigenkapitalquote 2017\t\t%i" % rate_equity_ratio(stock.equity_ratio))
    print("4. KGV 5 Jahre\t\t\t\t\t%i" % rate_per(stock.per_5_years))
    print("5. KGV 2018e\t\t\t\t\t%i" % rate_per(stock.per))
    # print("6. Analystenmeinungen:\t\t\t" + str(self.ratings))
    # print("7. Reaktion auf Quartalszahlen")
    # print("8. Gewinnrevision")
    # print("9. Performance 6 Monaten\t\t%0.3f%% (Referenzindex %s %0.3f%%)" % (
    #     self.history.performance_6_month() * 100, self.indexGroup.name,
    #     self.indexGroup.history.performance_6_month() * 100))
    # print("10. Performance 1 Jahr\t\t\t%0.3f%% (Referenzindex %s %0.3f%%)" % (
    #     self.history.performance_1_year() * 100, self.indexGroup.name,
    #     self.indexGroup.history.performance_1_year() * 100))
    # print("11. Kursmomentum steigend\t\t(abhängig von 9. und 10.)")
    # print("12. Dreimonatsreversal\t\t\tPerformance für 3 Monate " + str(
    #     self.monthClosings.calculate_performance()) + " (Referenz " + self.indexGroup.name + " " + str(
    #     self.indexGroup.monthClosings.calculate_performance()) + ")")
    print("13. EPS \t\t\t\t\t\t%i" % rate_eps(stock.eps_last_year, stock.eps_current_year))
