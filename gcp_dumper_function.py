import os
import base64
import json
import logging
from datetime import datetime

from libs import IndexGroupFactory
from libs.downloader import DownloaderFactory
from libs.repository.S3Repository import S3Repository
from libs.scraper import ScraperFactory
from libs.storage import IndexStorage, StockStorage
from libs.model import IndexGroup, Stock
from google.cloud import pubsub_v1


PROJECT_ID = "stock-scoring"
STOCK_DUMP_TOPIC_ID = "stock-dump"
DUMP_FOLDER = "dump"
BUCKET_NAME = "stock-scoring.appspot.com"

logging.basicConfig(level=logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")))


def dump_index(event: dict, context):
    data = decode_pubsub_data(event)

    source = data["source"]
    index = data["index"]
    date = date_or_now(data)
d    scrap_stocks = should_scrap_stocks(data)

    print("Dump index for '{}' from '{}' on ".format(index, source, date))

    index_group = IndexGroupFactory.createFor(source, index)

    index_storage = IndexStorage(DUMP_FOLDER, index_group, date=date, storage_repository=S3Repository(BUCKET_NAME))

    downloader = DownloaderFactory.create(source)
    downloader.dump_index(index_group, index_storage)

    scraper = ScraperFactory.create(source)
    scraper.read_stocks(index_group, index_storage)
    scraper.scrap_index(index_group, index_storage)

    if scrap_stocks:
        send_scrap_messages(index_group, date)
    else:
        logging.info("don't scape stocks because of pub/sub message")


def send_scrap_messages(index_group: IndexGroup, date: datetime):

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, STOCK_DUMP_TOPIC_ID)

    for stock in index_group.stocks:

        data = json.dumps({
            "source": index_group.source,
            "index_group": index_group.as_dict(),
            "stock": stock.as_dict(),
            "date": date.isoformat()
        }).encode("utf-8")

        logging.info("publish data: {}".format(data))

        future = publisher.publish(topic_path, data)

        # noinspection PyBroadException
        try:
            future.result()
            logging.info("publish {} to pub/sup: {}".format(STOCK_DUMP_TOPIC_ID, stock.name))
        except Exception:
            logging.exception("unable to publish {} to pub/sup: {}".format(STOCK_DUMP_TOPIC_ID, stock.name))


def dump_stock(event: dict, context):
    data = decode_pubsub_data(event)

    logging.info("data: {}".format(data))

    source = data["source"]
    index_group = new_index_group(data["index_group"])
    stock = new_stock(data["stock"], index_group)
    date = date_or_now(data)

    logging.info("source: {}".format(source))
    logging.info("index_group: {}".format(index_group))
    logging.info("stock: {}".format(stock))
    logging.info("date: {}".format(date))

    index_storage = IndexStorage(DUMP_FOLDER, index_group, date=date, storage_repository=S3Repository(BUCKET_NAME))
    stock_storage = StockStorage(index_storage, stock, storage_repository=S3Repository(BUCKET_NAME))

    downloader = DownloaderFactory.create(source)
    downloader.dump_stock(stock, stock_storage)

    scraper = ScraperFactory.create(source)
    scraper.scrap(stock, stock_storage)
    stock_storage.store()


def new_index_group(data):
    return IndexGroup(data["isin"], data["name"], data["sourceId"], data["source"])


def new_stock(data, index_group):
    stock = Stock(data["stock_id"], data["name"], index_group)
    stock.field = data["field"]

    return stock


def decode_pubsub_data(event: dict) -> dict:
    data = base64.b64decode(event['data']).decode('utf-8')

    return json.loads(data)


def date_or_now(data) -> datetime:
    if 'date' in dict.keys(data):
        date = datetime.fromisoformat(data["date"])
    else:
        date = datetime.now()

    return date


def should_scrap_stocks(data):
    if 'scrape_stocks' in dict.keys(data) and data["scrape_stocks"]:
        return not data["scrape_stocks"].lower() == "false"
    else:
        return True
