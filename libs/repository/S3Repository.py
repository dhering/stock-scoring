import time

from google.cloud import storage
from google.cloud.exceptions import NotFound


class S3Repository:

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    def store(self, path: str, content):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket_name)

        blob = bucket.blob(path)
        blob.upload_from_string(content)

        time.sleep(5)

    def load(self, path: str):

        blob = self.load_blob(path)

        return blob.download_as_text()

    def load_blob(self, path: str):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket_name)

        return bucket.blob(path)

    def has_content(self, path: str):

        try:
            blob = self.load_blob(path)
            content = blob.download_as_text()

            if content and len(content) > 0:
                return True

        except NotFound:
            return False