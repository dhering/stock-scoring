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

        try:
            blob = self.load_blob(path)
            return blob.download_as_text()

        except NotFound:
            return None

    def load_binary(self, path: str):

        try:
            blob = self.load_blob(path)
            return blob.download_as_bytes()

        except NotFound:
            return None

    def delete(self, path: str):

        blob = self.load_blob(path)
        blob.delete()


    def list(self, prefix: str):

        storage_client = storage.Client()
        blobs = storage_client.list_blobs(self.bucket_name, prefix=prefix, delimiter="/")

        file_list = list(map(lambda b: b.name.split("/")[-1], blobs))

        return file_list

    def load_blob(self, path: str):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket_name)

        return bucket.blob(path)

    def has_content(self, path: str):
        content = self.load(path)

        return content and len(content) > 0
