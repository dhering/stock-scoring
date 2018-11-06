import json
import zipfile
from datetime import datetime
from os import listdir, remove, path

from dateutil.relativedelta import relativedelta

from libs.model import Stock, IndexGroup, History, MonthClosings, AnalystRatings


class IndexStorage:
    def __init__(self, base_folder: str, indexGroup: IndexGroup, date: datetime = datetime.now(),
                 source: str = "", get_history=True):
        self.base_folder = base_folder if base_folder.endswith("/") else base_folder + "/"
        self.indexGroup = indexGroup
        self.date = date
        self.date_str = datetime.strftime(date, "%Y-%m-%d")
        self.source = source

        if get_history:
            self.historicalStorage = self.getHistoricalStorage()
        else:
            self.historicalStorage = None

    def getBasePath(self) -> str:
        return self.base_folder + self.indexGroup.name + "/"

    def getDatedPath(self) -> str:
        return self.getBasePath() + self.date_str + "/"

    def getStoragePath(self, appending: str, suffix: str):
        return self.getDatedPath() + self.indexGroup.name + append(self.source) \
               + append(appending) + "." + suffix

    def getHistoricalStorage(self, maxMonth: int = 3):

        fromDate = self.date - relativedelta(months=maxMonth)
        fromDate = "{:04d}-{:02d}-{:02d}".format(fromDate.year, fromDate.month, fromDate.day)

        dateFolders = listdir(self.getBasePath())
        dateFolders = [f for f in dateFolders if fromDate <= f < self.date_str]

        if not dateFolders:
            return None

        oldestFolder = min(dateFolders)

        storage_date = datetime.strptime(oldestFolder, "%Y-%m-%d")

        return IndexStorage(self.base_folder, self.indexGroup, storage_date, self.source, False)


class StockStorage:
    def __init__(self, indexStorage: IndexStorage, stock: Stock):
        self.indexStorage = indexStorage
        self.stock = stock

    def getDatedPath(self) -> str:
        return self.indexStorage.getDatedPath()

    def getStoragePath(self, appending: str, suffix: str):

        return self.getDatedPath() + self.stock.name + append(self.indexStorage.source) \
               + append(appending) + "." + suffix

    def toJson(self) -> str:
        return json.dumps(self.stock.asDict())

    def store(self):

        with open(self.getStoragePath("stock", "json"), "w") as f:
            f.write(self.toJson())

    def load(self):

        with open(self.getStoragePath("stock", "json"), "r") as f:
            indexGroup = self.stock.indexGroup

            self.stock = self.fromJson(f.read())
            self.stock.indexGroup = indexGroup

    def compress(self):

        stock_prefix = self.stock.name + "." + self.indexStorage.source + "."
        stock_files = [file for file in listdir(self.getDatedPath()) if
                       file.startswith(stock_prefix) and (file.endswith(".html") or file.endswith(".csv"))]

        with zipfile.ZipFile(self.getStoragePath("", "zip"), 'w', compression=zipfile.ZIP_DEFLATED) as zip:
            for file in stock_files:
                zip.write(self.getDatedPath() + file, file)
                remove(self.getDatedPath() + file)

    def uncompress(self):

        archive = self.getStoragePath("", "zip")

        if path.isfile(archive):
            with zipfile.ZipFile(archive, 'r', compression=zipfile.ZIP_DEFLATED) as zip:
                zip.extractall(self.getDatedPath())

    def fromJson(self, json_str: str) -> Stock:
        stock_json = json.loads(json_str)

        stock = Stock(stock_json["stock_id"], stock_json["name"], None)

        for attr in stock_json.keys():
            if attr == "stock_id" or attr == "stock_name":
                continue

            if attr == "history":
                history = stock_json["history"]
                stock.history = History(history["today"], history["half_a_year"], history["one_year"])
            elif attr == "monthClosings":
                stock.monthClosings = MonthClosings()
                stock.monthClosings.closings = stock_json["monthClosings"].get("closings")
            elif attr == "ratings":
                ratings = stock_json["ratings"]
                stock.ratings = AnalystRatings(ratings["buy"], ratings["hold"], ratings["sell"])
            else:
                stock.__setattr__(attr, stock_json[attr])

        return stock


def append(appending: str):
    if appending is None or appending == "":
        return ""

    if not appending.startswith(("-", "_", ".")):
        appending = "." + appending

    return appending
