import unittest

from libs.Rating import *
from libs.model import Ratings


class MyTestCase(unittest.TestCase):

    def test_rate_roi(self):
        self.assertEqual(1, rate_roi(21))
        self.assertEqual(0, rate_roi(20))
        self.assertEqual(0, rate_roi(10))
        self.assertEqual(-1, rate_roi(9))

    def test_rate_ebit(self):
        self.assertEqual(1, rate_ebit(13))
        self.assertEqual(0, rate_ebit(12))
        self.assertEqual(0, rate_ebit(6))
        self.assertEqual(-1, rate_ebit(5))

    def test_rate_equity_ratio(self):
        self.assertEqual(1, rate_equity_ratio(26))
        self.assertEqual(0, rate_equity_ratio(25))
        self.assertEqual(0, rate_equity_ratio(15))
        self.assertEqual(-1, rate_equity_ratio(14))

    def test_rate_per(self):
        self.assertEqual(1, rate_per(11))
        self.assertEqual(0, rate_per(12))
        self.assertEqual(0, rate_per(16))
        self.assertEqual(-1, rate_per(17))

    def test_rate_eps(self):
        self.assertEqual(1, rate_eps(100, 105))
        self.assertEqual(0, rate_eps(100, 104))
        self.assertEqual(0, rate_eps(100, 96))
        self.assertEqual(-1, rate_eps(100, 95))


    def test_rate_performance(self):
        self.assertEqual(1, rate_performance(0.06, 0))
        self.assertEqual(0, rate_performance(0.05, 0))
        self.assertEqual(0, rate_performance(0, 0.05))
        self.assertEqual(-1, rate_performance(0, 0.06))


    def test_rate_price_momentum(self):
        self.assertEqual(0, rate_price_momentum(1, 1))
        self.assertEqual(1, rate_price_momentum(1, 0))
        self.assertEqual(1, rate_price_momentum(1, -1))
        self.assertEqual(0, rate_price_momentum(0, 1))
        self.assertEqual(0, rate_price_momentum(0, 0))
        self.assertEqual(0, rate_price_momentum(0, -1))
        self.assertEqual(-1, rate_price_momentum(-1, 1))
        self.assertEqual(-1, rate_price_momentum(-1, 0))
        self.assertEqual(0, rate_price_momentum(-1, -1))


    def test_rate_monthClosings(self):
        self.assertEqual(-1, rate_monthClosings([5], [4]))
        self.assertEqual(0, rate_monthClosings([5,4,5], [4,4,4]))
        self.assertEqual(0, rate_monthClosings([4,4,4], [4,4,4]))
        self.assertEqual(0, rate_monthClosings([4,4,4], [5,4,4]))
        self.assertEqual(1, rate_monthClosings([4,4,4], [5,5,5]))


    def test_rate_ratings(self):
        self.assertEqual(-1, rate_ratings(Ratings(1,1,0)))
        self.assertEqual(0, rate_ratings(Ratings(1,0,1)))
        self.assertEqual(1, rate_ratings(Ratings(0,1,1)))



if __name__ == '__main__':
    unittest.main()
