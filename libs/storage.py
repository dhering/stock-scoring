from datetime import datetime

from libs.model import Stock, IndexGroup


class IndexStorage:
    def __init__(self, base_folder: str, indexGroup: IndexGroup, date: datetime = datetime.now(), source: str = ""):
        self.base_folder = base_folder if base_folder.endswith("/") else base_folder + "/"
        self.indexGroup = indexGroup
        self.date = date
        self.date_str = datetime.strftime(date, "%Y-%m-%d")
        self.source = source

    def getBasePath(self) -> str:
        return self.base_folder + self.indexGroup.name + "/" + self.date_str + "/"

    def getStoragePath(self, appending: str, suffix: str):

        return self.getBasePath() + self.indexGroup.name + append(self.source) \
            + append(appending) + "." + suffix


class StockStorage:
    def __init__(self, indexStorage: IndexStorage, stock: Stock):
        self.indexStorage = indexStorage
        self.stock = stock

    def getBasePath(self) -> str:
        return self.indexStorage.getBasePath()

    def getStoragePath(self, appending: str, suffix: str):

        return self.getBasePath() + self.stock.name + append(self.indexStorage.source) \
               + append(appending) + "." + suffix


def append(appending: str):

    if appending is None or appending == "":
        return ""

    if not appending.startswith(("-", "_", ".")):
        appending = "." + appending

    return appending
