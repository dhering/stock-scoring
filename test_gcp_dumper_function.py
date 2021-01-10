import base64
import json
import unittest
from datetime import datetime

from gcp_dumper_function import dump_index, dump_stock, date_or_now, should_scrap_stocks
from model import IndexGroup, Stock
from storage import IndexStorage, StockStorage


class TestGcpDumperFunction(unittest.TestCase):

    def test_dump_index(self):
        # given:
        SOURCE = "TEST-SOURCE"
        INDEX = "TEST-INDEX"

        event = create_event({
            "source": SOURCE,
            "index": INDEX,
            "scrape_stocks": "false"
        })

        index_group_factory = MockIndexGroupFactory()
        downloader_factory = MockDownloaderFactory()
        scraper_factory = MockScraperFactory()

        # when:
        dump_index(event, None, index_group_factory, downloader_factory, scraper_factory)

        # then:
        self.assertEqual(index_group_factory.calls, 1)
        self.assertEqual(index_group_factory.source, SOURCE)
        self.assertEqual(index_group_factory.index, INDEX)

        self.assertEqual(downloader_factory.calls, 1)
        self.assertEqual(downloader_factory.source, SOURCE)
        self.assertEqual(downloader_factory.downloader.calls_dump_index, 1)
        self.assertEqual(downloader_factory.downloader.calls_dump_stock, 0)
        self.assertIsNotNone(downloader_factory.downloader.index_group)
        self.assertEqual(downloader_factory.downloader.index_group.source, SOURCE)
        self.assertEqual(downloader_factory.downloader.index_group.name, INDEX)
        self.assertIsNotNone(downloader_factory.downloader.index_storage)
        self.assertEqual(downloader_factory.downloader.index_storage.source, SOURCE)

        self.assertEqual(scraper_factory.calls, 1)
        self.assertEqual(scraper_factory.scraper.calls_scrap_index, 1)
        self.assertEqual(scraper_factory.scraper.calls_read_stock, 1)
        self.assertEqual(scraper_factory.source, SOURCE)

    def test_dump_stock(self):
        # given:
        SOURCE = "TEST-SOURCE"
        INDEX = "TEST-INDEX"

        event = create_event({
            "source": SOURCE,
            "index": INDEX,
            "scrape_stocks": "false"
        })

        index_group_factory = MockIndexGroupFactory()
        downloader_factory = MockDownloaderFactory()
        scraper_factory = MockScraperFactory()

        # when:
        dump_stock(event, None, index_group_factory, downloader_factory, scraper_factory)

    def test_date_or_now_with_given_date(self):
        # given:
        test_data = {"date": "2021-01-01"}

        # when:
        date = date_or_now(test_data)

        # then:
        self.assertEquals(date, datetime.fromisoformat("2021-01-01"))

    def test_date_or_now_with_fallback_to_now(self):
        # given:
        test_data = {}

        # when:
        date = date_or_now(test_data)

        # then:
        self.assertEquals(date, datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))

    def test_should_scrap_stocks(self):
        self.assertTrue(should_scrap_stocks({}))
        self.assertTrue(should_scrap_stocks({"scrape_stocks": None}))
        self.assertTrue(should_scrap_stocks({"scrape_stocks": "foo"}))
        self.assertTrue(should_scrap_stocks({"scrape_stocks": "true"}))
        self.assertTrue(should_scrap_stocks({"scrape_stocks": "True"}))

        self.assertFalse(should_scrap_stocks({"scrape_stocks": "false"}))
        self.assertFalse(should_scrap_stocks({"scrape_stocks": "False"}))


def create_event(data):
    json_data = json.dumps(data)

    return {
        "data": base64.b64encode(json_data.encode('utf-8'))
    }


class MockIndexGroupFactory:

    def __init__(self):
        self.calls = 0
        self.source = 0
        self.index = 0

    def createFor(self, source, index):
        self.calls += 1
        self.source = source
        self.index = index
        return IndexGroup("1234", index, "TEST-SOURCE-ID", source)


class MockDownloaderFactory:

    def __init__(self):
        self.calls = 0
        self.downloader = MockDownloader()
        self.source = None

    def create(self, source: str):
        self.calls += 1
        self.source = source
        return self.downloader


class MockDownloader:

    def __init__(self):
        self.calls_dump_index = 0
        self.calls_dump_stock = 0
        self.index_group: IndexGroup = None
        self.index_storage: IndexStorage = None
        self.stock: Stock = None
        self.stock_storage: StockStorage = None

    def dump_index(self, index_group: IndexGroup, index_storage: IndexStorage):
        self.calls_dump_index += 1
        self.index_group = index_group
        self.index_storage = index_storage
        pass

    def dump_stock(self, stock: Stock, stock_storage: StockStorage):
        self.calls_dump_stock += 1
        self.stock = stock
        self.stock_storage = stock_storage
        pass


class MockScraperFactory:

    def __init__(self):
        self.calls = 0
        self.scraper = MockScraper()
        self.source = None

    def create(self, source: str):
        self.calls += 1
        self.source = source
        return self.scraper


class MockScraper:

    def __init__(self):
        self.calls_read_stock = 0
        self.calls_scrap_index = 0

    def read_stocks(self, index_group, index_storage):
        self.calls_read_stock += 1
        pass

    def scrap_index(self, index_group, index_storage):
        self.calls_scrap_index += 1
        pass
