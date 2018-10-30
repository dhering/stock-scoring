import unittest

from libs.Rating import *
from libs.model import AnalystRatings


class MyTestCase(unittest.TestCase):

    def test_rate_roi(self):
        self.assertEqual(1, rate_roi(21), "rate ROI - test 1")
        self.assertEqual(0, rate_roi(20), "rate ROI - test 2")
        self.assertEqual(0, rate_roi(10), "rate ROI - test 3")
        self.assertEqual(-1, rate_roi(9), "rate ROI - test 4")

    def test_rate_ebit(self):
        self.assertEqual(1, rate_ebit(13), "rate EBIT - test 1")
        self.assertEqual(0, rate_ebit(12), "rate EBIT - test 2")
        self.assertEqual(0, rate_ebit(6), "rate EBIT - test 3")
        self.assertEqual(-1, rate_ebit(5), "rate EBIT - test 4")

    def test_rate_equity_ratio(self):
        self.assertEqual(1, rate_equity_ratio(26), "rate equity ratio - test 1")
        self.assertEqual(0, rate_equity_ratio(25), "rate equity ratio - test 2")
        self.assertEqual(0, rate_equity_ratio(15), "rate equity ratio - test 3")
        self.assertEqual(-1, rate_equity_ratio(14), "rate equity ratio - test 4")

    def test_rate_equity_ratio_finance(self):
        self.assertEqual(1, rate_equity_ratio_finance(11), "rate equity ratio finance - test 1")
        self.assertEqual(0, rate_equity_ratio_finance(10), "rate equity ratio finance - test 2")
        self.assertEqual(0, rate_equity_ratio_finance(5), "rate equity ratio finance - test 3")
        self.assertEqual(-1, rate_equity_ratio_finance(4), "rate equity ratio finance - test 4")

    def test_rate_per(self):
        self.assertEqual(1, rate_per(11), "rate PER - test 1")
        self.assertEqual(0, rate_per(12), "rate PER - test 2")
        self.assertEqual(0, rate_per(16), "rate PER - test 3")
        self.assertEqual(-1, rate_per(17), "rate PER - test 4")

    def test_rate_eps(self):
        self.assertEqual(1, rate_eps(100, 105), "rate EPS - test 1")
        self.assertEqual(0, rate_eps(100, 104), "rate EPS - test 2")
        self.assertEqual(0, rate_eps(100, 96), "rate EPS - test 3")
        self.assertEqual(-1, rate_eps(100, 95), "rate EPS - test 4")


    def test_rate_performance(self):
        self.assertEqual(1, rate_performance(0.06, 0), "rate performance - test 1")
        self.assertEqual(0, rate_performance(0.05, 0), "rate performance - test 2")
        self.assertEqual(0, rate_performance(0, 0.05), "rate performance - test 3")
        self.assertEqual(-1, rate_performance(0, 0.06), "rate performance - test 4")


    def test_rate_price_momentum(self):
        self.assertEqual(0, rate_price_momentum(1, 1), "rate price momentum - test 1")
        self.assertEqual(1, rate_price_momentum(1, 0), "rate price momentum - test 2")
        self.assertEqual(1, rate_price_momentum(1, -1), "rate price momentum - test 3")
        self.assertEqual(0, rate_price_momentum(0, 1), "rate price momentum - test 4")
        self.assertEqual(0, rate_price_momentum(0, 0), "rate price momentum - test 5")
        self.assertEqual(0, rate_price_momentum(0, -1), "rate price momentum - test 6")
        self.assertEqual(-1, rate_price_momentum(-1, 1), "rate price momentum - test 7")
        self.assertEqual(-1, rate_price_momentum(-1, 0), "rate price momentum - test 8")
        self.assertEqual(0, rate_price_momentum(-1, -1), "rate price momentum - test 9")


    def test_rate_monthClosings(self):
        self.assertEqual(-1, rate_monthClosings([5], [4]), "rate monthClosings - test 1")
        self.assertEqual(0, rate_monthClosings([5,4,5], [4,4,4]), "rate monthClosings - test 2")
        self.assertEqual(0, rate_monthClosings([4,4,4], [4,4,4]), "rate monthClosings - test 3")
        self.assertEqual(0, rate_monthClosings([4,4,4], [5,4,4]), "rate monthClosings - test 4")
        self.assertEqual(1, rate_monthClosings([4,4,4], [5,5,5]), "rate monthClosings - test 5")


    def test_rate_ratings(self):
        self.assertEqual(-1, rate_ratings(AnalystRatings(1,1,0)), "rate ratings - test 1")
        self.assertEqual(0, rate_ratings(AnalystRatings(1,0,1)), "rate ratings - test 2")
        self.assertEqual(1, rate_ratings(AnalystRatings(0,1,1)), "rate ratings - test 3")

    def test_rate_profit_revision(self):
        #given:
        stock = Stock("test", "test", None)
        stock.eps_next_year = 1
        stock.eps_current_year = 1

        stock.historical_eps_next_year = 1.05
        stock.historical_eps_current_year = 1.05
        self.assertEqual(1, rate_profit_revision(stock), "rate profit revision - test 1")

        stock.historical_eps_next_year = 1.04
        stock.historical_eps_current_year = 1.04
        self.assertEqual(0, rate_profit_revision(stock), "rate profit revision - test 2")

        stock.historical_eps_next_year = 0.96
        stock.historical_eps_current_year = 0.96
        self.assertEqual(0, rate_profit_revision(stock), "rate profit revision - test 3")

        stock.historical_eps_next_year = 0.95
        stock.historical_eps_current_year = 0.95
        self.assertEqual(-1, rate_profit_revision(stock), "rate profit revision - test 4")

        stock.historical_eps_next_year = 1.05
        stock.historical_eps_current_year = 1.04
        self.assertEqual(0, rate_profit_revision(stock), "rate profit revision - test 5")

        stock.historical_eps_next_year = 1.04
        stock.historical_eps_current_year = 1.05
        self.assertEqual(0, rate_profit_revision(stock), "rate profit revision - test 6")

        stock.historical_eps_next_year = 0.95
        stock.historical_eps_current_year = 0.96
        self.assertEqual(0, rate_profit_revision(stock), "rate profit revision - test 7")

        stock.historical_eps_next_year = 0.96
        stock.historical_eps_current_year = 0.95
        self.assertEqual(0, rate_profit_revision(stock), "rate profit revision - test 8")


    def test_rate_small_ratings(self):
        self.assertEqual(1, rate_small_ratings(AnalystRatings(1,1,0)), "rate small ratings - test 1")
        self.assertEqual(0, rate_small_ratings(AnalystRatings(1,0,1)), "rate small ratings - test 2")
        self.assertEqual(-1, rate_small_ratings(AnalystRatings(0,1,1)), "rate small ratings - test 3")



if __name__ == '__main__':
    unittest.main()
