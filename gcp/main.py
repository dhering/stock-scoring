import base64
import json
from datetime import datetime

import IndexGroupFactory
from downloader import DownloaderFactory
from repository.S3Repository import S3Repository
from scraper import ScraperFactory
from storage import IndexStorage


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
    bucket_name = "gs://stock-scoring.appspot.com"

    if 'date' in dict.keys():
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