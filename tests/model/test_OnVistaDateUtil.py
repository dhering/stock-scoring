import unittest
from datetime import datetime

from libs.scraper.OnVistaDateUtil import OnVistaDateUtil


class MyTestCase(unittest.TestCase):
    onVistaDateUtil = OnVistaDateUtil(datetime.strptime('2017-03-01', '%Y-%m-%d'))

    def test_get_last_year(self):
        self.assertEqual("2016", self.onVistaDateUtil.get_last_year())

    def test_get_current_year(self):
        self.assertEqual("2017e", self.onVistaDateUtil.get_current_year())

    def test_get_next_year(self):
        self.assertEqual("2018e", self.onVistaDateUtil.get_next_year())

    def test_get_last_cross_year(self):
        self.assertEqual("15/16", self.onVistaDateUtil.get_last_cross_year())

    def test_get_current_cross_year(self):
        self.assertEqual("16/17e", self.onVistaDateUtil.get_current_cross_year())

    def test_get_next_cross_year(self):
        self.assertEqual("17/18e", self.onVistaDateUtil.get_next_cross_year())


if __name__ == '__main__':
    unittest.main()
