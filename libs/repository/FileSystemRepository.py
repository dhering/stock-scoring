class FileSystemRepository:
    def store(self, path: str, content):
        with open(path, "w") as f:
            f.write(content)


    def load(self, path: str):
        with open(path, "r") as f:
            return f.read()

        return None