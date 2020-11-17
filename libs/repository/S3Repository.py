import time

from google.cloud import storage

class S3Repository:

    def __init__(self, bucket_name:str):
        self.bucket_name = bucket_name

    def store(self, path: str, content):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket_name)

        blob = bucket.blob(path)
        blob.upload_from_string(content)

        time.sleep(5)

    def load(self, path: str):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.bucket_name)

        blob = bucket.blob(path)

        return blob.download_as_string()