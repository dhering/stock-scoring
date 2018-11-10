import json
import zipfile
from datetime import datetime
from os import listdir, remove, path

from dateutil.relativedelta import relativedelta

from libs.DateUtils import toRevertStr
from libs.model import Stock, IndexGroup, History, MonthClosings, AnalystRatings, ReactionToQuarterlyNumbers


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

    def getAppointmentsPath(self) -> str:
        return self.getBasePath() + "appointments/"

    def getHistoryPath(self, appending: str = None, suffix: str = None) -> str:

        historyPath = self.getBasePath() + "history/"

        if(appending or suffix):
            return historyPath + self.getFilename(appending, suffix)
        else:
            return historyPath

    def getStoragePath(self, appending: str, suffix: str):
        return self.getDatedPath() + self.getFilename(appending, suffix)

    def getFilename(self, appending: str, suffix: str):
        return self.indexGroup.name + append(self.source) \
               + append(appending) + "." + suffix

    def getHistoricalStorage(self, maxMonth: int = 3):

        fromDate = toRevertStr(self.date - relativedelta(months=maxMonth))

        if path.isdir(self.getBasePath()):
            dateFolders = listdir(self.getBasePath())
            dateFolders = [f for f in dateFolders if fromDate <= f < self.date_str]

            if not dateFolders:
                return None

            oldestFolder = min(dateFolders)

            storage_date = datetime.strptime(oldestFolder, "%Y-%m-%d")

            return IndexStorage(self.base_folder, self.indexGroup, storage_date, self.source, False)

        return None

class StockStorage:
    def __init__(self, indexStorage: IndexStorage, stock: Stock):
        self.indexStorage = indexStorage
        self.stock = stock

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

        with open(self.getStoragePath("stock", "json"), "w") as f:
            f.write(self.toJson())

    def load(self):

        with open(self.getStoragePath("stock", "json"), "r") as f:
            indexGroup = self.stock.indexGroup

            self.stock = self.fromJson(f.read())
            self.stock.indexGroup = indexGroup

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
                    ReactionToQuarterlyNumbers(reaction["price"], reaction["price_before"], reaction["index_price"], reaction["index_price_before"], reaction["date"])
            else:
                stock.__setattr__(attr, stock_json[attr])

        return stock


def append(appending: str):
    if appending is None or appending == "":
        return ""

    if not appending.startswith(("-", "_", ".")):
        appending = "." + appending

    return appending
