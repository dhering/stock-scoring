import json
import zipfile
from datetime import datetime
from os import listdir, remove, path

import dateutil.relativedelta

from libs.DateUtils import toRevertStr
from libs.model import Stock, IndexGroup, History, MonthClosings, AnalystRatings, ReactionToQuarterlyNumbers
from libs.repository.FileSystemRepository import FileSystemRepository

class IndexStorage:
    def __init__(self, base_folder: str, indexGroup: IndexGroup, date: datetime = datetime.now(), get_history=True, storage_repository:any=FileSystemRepository()):
        self.base_folder = base_folder if base_folder.endswith("/") else base_folder + "/"
        self.indexGroup = indexGroup
        self.date = date
        self.date_str = datetime.strftime(date, "%Y-%m-%d")
        self.source = indexGroup.source

        if get_history:
            self.historicalStorage = self.getHistoricalStorage()
        else:
            self.historicalStorage = None

        self.storage_repository = storage_repository

    def getBasePath(self) -> str:
        return self.base_folder + self.indexGroup.name + "/"

    def getDatedPath(self) -> str:
        return self.getBasePath() + self.date_str + "/"

    def getAppointmentsPath(self) -> str:
        return self.getBasePath() + "appointments/"

    def getHistoryPath(self, appending: str = None, suffix: str = None) -> str:

        historyPath = self.getBasePath() + "history/"

        if (appending or suffix):
            return historyPath + self.getFilename(appending, suffix)
        else:
            return historyPath

    def getStoragePath(self, appending: str, suffix: str):
        return self.getDatedPath() + self.getFilename(appending, suffix)

    def getFilename(self, appending: str, suffix: str):
        return self.indexGroup.name + append(self.source) \
               + append(appending) + "." + suffix

    def getHistoricalStorage(self, maxMonth: int = 3):

        fromDate = toRevertStr(self.date - dateutil.relativedelta.relativedelta(months=maxMonth))

        if path.isdir(self.getBasePath()):
            dateFolders = listdir(self.getBasePath())
            dateFolders = [f for f in dateFolders if fromDate <= f < self.date_str]

            if not dateFolders:
                return None

            oldestFolder = min(dateFolders)

            storage_date = datetime.strptime(oldestFolder, "%Y-%m-%d")

            return IndexStorage(self.base_folder, self.indexGroup, storage_date, False)

        return None

    def toJson(self):

        index = self.indexGroup

        return {
            "isin": index.index,
            "name": index.name,
            "sourceId": index.sourceId,
            "source": index.source,
            "stocks": list(map(lambda s: {"id": s.stock_id, "name": s.name}, index.stocks)),
            "history": index.history.asDict(),
            "monthClosings": index.monthClosings.asDict()
        }

    def fromJson(self, json_str: str) -> IndexGroup:

        index_json = json.loads(json_str)

        # backward compatibilities
        isin = index_json["isin"] if "isin" in index_json else index_json["index"]
        name = index_json["name"]
        sourceID = index_json["sourceId"] if "sourceId" in index_json else name
        source = index_json["source"] if "source" in index_json else "onvista"

        indexGroup = IndexGroup(isin, name, sourceID, source)

        history = index_json["history"]
        indexGroup.history = History(history["today"], history["half_a_year"], history["one_year"])

        indexGroup.monthClosings = MonthClosings()
        indexGroup.monthClosings.closings = index_json["monthClosings"].get("closings")

        indexGroup.stocks = list(map(lambda s: Stock(s.id, s.name, indexGroup)), index_json["stocks"])

        return indexGroup

    def store(self):

        self.storage_repository.store(self.getStoragePath("", "json"), self.toJson())

    def load(self):

        content = self.storage_repository.load(self.getStoragePath("", "json"))
        self.indexGroup = self.fromJson(content)

        return self.indexGroup



class StockStorage:
    def __init__(self, indexStorage: IndexStorage, stock: Stock, storage_repository=FileSystemRepository()):
        self.indexStorage = indexStorage
        self.stock = stock
        self.storage_repository = storage_repository

    def getDatedPath(self) -> str:
        return self.indexStorage.getDatedPath()

    def getStoragePath(self, appending: str, suffix: str):

        return self.getDatedPath() + self.getFilename(appending, suffix)

    def getFilename(self, appending: str, suffix: str):
        return self.stock.name + append(self.indexStorage.source) \
               + append(appending) + "." + suffix

    def getHistoryPath(self, appending: str, suffix: str) -> str:
        return f"{self.indexStorage.getHistoryPath()}{self.stock.name}/{self.getFilename(appending, suffix)}"

    def toJson(self) -> str:
        return json.dumps(self.stock.asDict())

    def store(self):

        self.storage_repository.store(self.getStoragePath("stock", "json"), self.toJson())

    def load(self):

        index_group = self.stock.indexGroup
        path = self.getStoragePath("stock", "json")
        content = self.storage_repository.load(path)

        self.stock = self.fromJson(content)
        self.stock.indexGroup = index_group

        return self.stock

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
            try:
                with zipfile.ZipFile(archive, 'r', compression=zipfile.ZIP_DEFLATED) as zip:
                    zip.extractall(self.getDatedPath())
            except zipfile.BadZipFile:
                print(f"remove broken zip file {archive}")
                remove(archive)

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
            elif attr == "reaction_to_quarterly_numbers":
                reaction = stock_json["reaction_to_quarterly_numbers"]
                stock.reaction_to_quarterly_numbers = \
                    ReactionToQuarterlyNumbers(reaction["price"], reaction["price_before"], reaction["index_price"],
                                               reaction["index_price_before"], reaction["date"])
            else:
                stock.__setattr__(attr, stock_json[attr])

        return stock


def append(appending: str):
    if appending is None or appending == "":
        return ""

    if not appending.startswith(("-", "_", ".")):
        appending = "." + appending

    return appending
