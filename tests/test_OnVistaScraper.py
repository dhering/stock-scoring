from datetime import datetime
import unittest

from libs.model import IndexGroup, Stock
from libs.storage import StockStorage, IndexStorage
from libs.scraper import OnVistaScraper as scraper


def get_vw_stock_storage(get_history=False):
    indexGroup = IndexGroup("DE0008469008", "DAX")
    index_storage = IndexStorage("resources", indexGroup, source="onvista",
                                 date=datetime.strptime("06.11.2018", "%d.%m.%Y"),
                                 get_history=get_history)
    stock = Stock("DE0007664039", "Volkswagen-VZ", indexGroup)

    return StockStorage(index_storage, stock)


class OnVistaScraperCase(unittest.TestCase):

    def test_get_for_year(self):
        self.assertEqual("15", scraper.get_for_year({"2018": "15"}, "2018", "17/18"))

    def test_get_for_crossyear(self):
        self.assertEqual("15", scraper.get_for_year({"17/18": "15"}, "2018", "17/18"))

    def test_get_for_unknown_year(self):
        self.assertEqual("0", scraper.get_for_year({}, "2018", "17/18"))

    def test_calc_per_5_years(self):
        fundamentals = {"Gewinn": {"KGV": {"2019": "4", "2018": "1,3", "2017": "1,5", "2016": "2,2", "2015": "1"}}}

        self.assertEqual(1.5, scraper.calc_per_5_years("2018", "17/18", fundamentals))

    def test_calc_per_5_crossyears(self):
        fundamentals = {"Gewinn": {"KGV": {"18/19": "4", "17/18": "1,3", "16/17": "1,5", "15/16": "2,2", "14/15": "1"}}}

        self.assertEqual(1.5, scraper.calc_per_5_years("2018", "17/18", fundamentals))

    def test_get_historical_price(self):
        # given:
        stock_storage = get_vw_stock_storage()
        today = datetime.strptime("15.11.2018", "%d.%m.%Y")

        # when:
        historical_price = scraper.get_historical_price(stock_storage, 1, today=today)

        # then:
        self.assertEqual(140.16, historical_price)

    def test_get_cloasing_price(self):
        # given:
        stock_storage = get_vw_stock_storage()

        # when:
        cloasing_price = scraper.get_cloasing_price(stock_storage, 4)

        # then:
        self.assertEqual(152.22, cloasing_price)

    def test_get_month_closings(self):
        # given:
        stock_storage = get_vw_stock_storage()

        # when:
        month_closings = scraper.get_month_closings(stock_storage)

        # then:
        self.assertEqual([152.22, 140.84, 151.60, 148.76], month_closings.closings)

    def test_get_reference_date_from_stock_storage(self):
        # given:
        stock_storage = get_vw_stock_storage()

        # when:
        date = scraper.get_reference_date(stock_storage)

        # then:
        self.assertEqual("2018-11-05", datetime.strftime(date, "%Y-%m-%d"))

    def test_get_reference_date_from_stock_storage(self):
        # given:
        stock_storage = get_vw_stock_storage()
        index_storage = stock_storage.indexStorage

        # when:
        date = scraper.get_reference_date(index_storage)

        # then:
        self.assertEqual("2018-11-05", datetime.strftime(date, "%Y-%m-%d"))

    def test(self):
        # given:
        stock_storage = get_vw_stock_storage(get_history=True)
        stock = stock_storage.stock

        # when:
        scraper.add_reaction_to_quarterly_numbers(stock, stock_storage)

        # then:
        self.assertEqual(1.42, round(stock.reaction_to_quarterly_numbers.calc_growth() * 100, 2))

    def test_file_reading(self):
        # given:
        stock_storage = get_vw_stock_storage(get_history=True)
        stock = stock_storage.stock

        # when:
        scraper.scrap(stock, stock_storage)

        # then:
        self.assertEqual(10.40, stock.roi, "Eigenkapitalrendite")
        self.assertEqual(6.03, stock.ebit_margin, "EBIT - Marge")
        self.assertEqual(25.83, stock.equity_ratio, "Eigenkapitalquote")
        self.assertEqual(8.8275, stock.per_5_years, "KGV 5 Jahre")
        self.assertEqual(6.08, stock.per, "KGV")
        self.assertEqual(1.42, round(stock.reaction_to_quarterly_numbers.calc_growth() * 100, 2), "Reaktion auf Quartalszahlen")

        self.assertEqual(155.44, stock.history.today, "Preis heute")
        self.assertEqual(172.72, stock.history.half_a_year, "Preis vor 6 Monaten")
        self.assertEqual(162.95, stock.history.one_year, "Preis vor einem Jahr")

        self.assertEqual([152.22, 140.84, 151.60, 148.76], stock.monthClosings.closings, "Schlusskurse")

        self.assertEqual(25.38, stock.eps_current_year, "Gewinn pro Aktie in EUR (dieses Jahr)")
        self.assertEqual(28.48, stock.eps_next_year, "Gewinn pro Aktie in EUR (nächstes Jahr)")

        self.assertEqual(84104500000, stock.market_capitalization, "Marktkapitalisierung")

        self.assertEqual((24, 4, 1), (stock.ratings.buy, stock.ratings.hold, stock.ratings.sell), "Analystenmeinungen")

        self.assertEqual(25.61, stock.historical_eps_current_year,
                         "Gewinn pro Aktie in EUR (dieses Jahr, Vergleich mit 28.10.18)")
        self.assertEqual(28.53, stock.historical_eps_next_year,
                         "Gewinn pro Aktie in EUR (nächstes Jahr, Vergleich mit 28.10.18)")


if __name__ == '__main__':
    unittest.main()
