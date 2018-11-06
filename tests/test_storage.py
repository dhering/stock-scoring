import unittest
from datetime import datetime

from libs.model import IndexGroup, Stock
from libs.storage import IndexStorage, StockStorage


class TestStorage(unittest.TestCase):

    def test_base_path_of_index(self):
        # given:
        index_group = IndexGroup("index_id", "index_name")
        date = datetime.strptime("2018-01-01", "%Y-%m-%d")

        # when:
        index_storage = IndexStorage("/tests/dump", index_group, date, get_history=False)
        base_path = index_storage.getDatedPath()

        # then:
        self.assertEqual("/tests/dump/index_name/2018-01-01/", base_path)

    def test_storage_path_of_index(self):
        # given:
        index_group = IndexGroup("index_id", "index_name")
        date = datetime.strptime("2018-01-01", "%Y-%m-%d")

        # when:
        index_storage = IndexStorage("/tests/dump", index_group, date, get_history=False)
        storage_path = index_storage.getStoragePath("profile", "html")

        # then:
        self.assertEqual("/tests/dump/index_name/2018-01-01/index_name.profile.html", storage_path)

    def test_base_path_of_stock(self):
        # given:
        index_group = IndexGroup("index_id", "index_name")
        stock = Stock("stock_id", "stock_name", index_group)
        date = datetime.strptime("2018-01-01", "%Y-%m-%d")

        index_storage = IndexStorage("/tests/dump", index_group, date, get_history=False)

        # when:
        stock_storage = StockStorage(index_storage, stock)
        base_path = stock_storage.getDatedPath()

        # then:
        self.assertEqual("/tests/dump/index_name/2018-01-01/", base_path)

    def test_storage_path_of_stock(self):
        # given:
        index_group = IndexGroup("index_id", "index_name")
        stock = Stock("stock_id", "stock_name", index_group)
        date = datetime.strptime("2018-01-01", "%Y-%m-%d")

        index_storage = IndexStorage("/tests/dump", index_group, date, get_history=False)

        # when:
        stock_storage = StockStorage(index_storage, stock)
        storage_path = stock_storage.getStoragePath("profile", "html")

        # then:
        self.assertEqual("/tests/dump/index_name/2018-01-01/stock_name.profile.html", storage_path)


if __name__ == '__main__':
    unittest.main()
