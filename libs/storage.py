import json
from datetime import datetime

from libs.model import Stock, IndexGroup, History, MonthClosings, AnalystRatings


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

    def toJson(self) -> str:
        return json.dumps(self.stock.asDict())

    def store(self):

        with open(self.getStoragePath("stock", "json"), "w") as f:
            f.write(self.toJson())

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
                stock.monthClosings.calculate_performance = stock_json["monthClosings"]
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
