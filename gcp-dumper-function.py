import base64
import json
from datetime import datetime

from libs import IndexGroupFactory
from libs.downloader import DownloaderFactory
from libs.repository.S3Repository import S3Repository
from libs.scraper import ScraperFactory
from libs.storage import IndexStorage
from google.cloud import pubsub_v1


def dump_index(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')

    message = json.loads(pubsub_message)

    source = message["source"]
    index = message["index"]
    bucket_name = "stock-scoring.appspot.com"

    if 'date' in dict.keys(message):
        date = message["date"]
    else:
        date = datetime.now()

    print("Dump index for '{}' from '{}' on ".format(index, source, date))

    index_group = IndexGroupFactory.createFor(source, index)

    index_storage = IndexStorage("dump", index_group, date=date, storage_repository=S3Repository(bucket_name))

    downloader = DownloaderFactory.create(source)
    downloader.dump_index(index_group, index_storage)

    scraper = ScraperFactory.create(source)
    scraper.read_stocks(index_group, index_storage)
    scraper.scrap_index(index_group, index_storage)

    publisher = pubsub_v1.PublisherClient()
    project_id = "stock-scoring"
    topic_id = "stock-dump"
    topic_path = publisher.topic_path(project_id, topic_id)

    for stock in index_group.stocks:
        print("publish to pub/sup: {}".format(stock.name))

        message = json.dumps(stock.asDict()).encode("utf-8")

        future = publisher.publish(topic_path, message)
        print(future.result())
