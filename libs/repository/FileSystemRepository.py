import os
from os import listdir


class FileSystemRepository:

    def __init__(self):
        return

    def store(self, path: str, content):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        mode = "w" if isinstance(content, str) else "wb"

        with open(path, mode) as f:
            f.write(content)

    def load(self, path: str, encoding: str = "utf-8"):

        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except FileNotFoundError:
            return None
        except UnicodeDecodeError:
            if encoding == "utf-8":
                return self.load(path, None)
            else:
                return None

    def load_binary(self, path: str):

        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def delete(self, path: str):

        os.remove(path)

    def list(self, prefix: str):

        parts = prefix.split("/")

        directory_path = "/".join(parts[: -1])
        file_prefix = parts[-1]

        file_list = [file for file in listdir(directory_path) if file.startswith(file_prefix)]

        return file_list

    def has_content(self, path: str):

        if os.path.isfile(path):
            return os.path.getsize(path) > 0
        else:
            return False
