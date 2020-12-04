import os


class FileSystemRepository:

    def __init__(self):
        return

    def store(self, path: str, content):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        mode = "w" if isinstance(content, str) else "wb"

        with open(path, mode) as f:
            f.write(content)

    def load(self, path: str):

        with open(path, "r") as f:
            return f.read()

    def has_content(self, path: str):

        if os.path.isfile(path):
            return os.path.getsize(path) > 0
        else:
            return False
