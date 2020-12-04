import re
from collections import namedtuple

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from functional import seq

from libs.DateUtils import toRevertMonthStr
from libs.downloader import AbstractDownloader as dl
from libs.model import IndexGroup, Stock
from libs.storage import IndexStorage, StockStorage

WEBSITE = "https://www.finanzen.net"

def dump_stock(stock: Stock, stockStorage: StockStorage):
    main_file = stockStorage.getStoragePath("profil", "html")
    storage_repository = stockStorage.storage_repository

    dl.download(WEBSITE + "/aktien/" + stock.name, main_file, storage_repository)

    dl.download(f"%s/bilanz_guv/%s" % (WEBSITE, stock.name), stockStorage.getStoragePath("bilanz_guv", "html"), storage_repository)
    dl.download(f"%s/schaetzungen/%s" % (WEBSITE, stock.name), stockStorage.getStoragePath("schaetzungen", "html"), storage_repository)
    dl.download(f"%s/termine/%s" % (WEBSITE, stock.name), stockStorage.getStoragePath("termine", "html"), storage_repository)
    dl.download(f"%s/analysen/%s-analysen" % (WEBSITE, stock.name), stockStorage.getStoragePath("analysen", "html"), storage_repository)

    download_history(stockStorage)


def download_history(storage):
    download_history_for_delta(0, storage)
    download_history_for_delta(1, storage)
    download_history_for_delta(2, storage)
    download_history_for_delta(3, storage)
    download_history_for_delta(4, storage)
    download_history_for_delta(6, storage)
    download_history_for_delta(12, storage)


def download_history_for_delta(delta: int, storage):
    if (isinstance(storage, IndexStorage)):
        runDate = storage.date
    elif (isinstance(storage, StockStorage)):
        runDate = storage.indexStorage.date

    storage_repository = storage.storage_repository

    dateStart = runDate.replace(day=1)

    if delta == 0:
        dateEnd = runDate
    else:
        dateStart = dateStart - relativedelta(months=delta)
        dateEnd = dateStart + relativedelta(months=1) - relativedelta(days=1)

    params = {
        "inTag1": dateStart.strftime("%#d"),
        "inMonat1": dateStart.strftime("%#m"),
        "inJahr1": dateStart.strftime("%Y"),
        "inTag2": dateEnd.strftime("%#d"),
        "inMonat2": dateEnd.strftime("%#m"),
        "inJahr2": dateEnd.strftime("%Y"),
        "strBoerse": "XETRA"
    }

    url = f"%s/historische-kurse/%s" % (WEBSITE, storage.stock.name)

    if delta == 0:
        dl.downloadByPost(url, params, storage.getStoragePath("prices", "csv"), storage_repository, retry=True)
    else:
        dl.downloadByPost(url, params, storage.getStoragePath(f"prices.{toRevertMonthStr(dateStart)}", "csv"), storage_repository, retry=True)


def dump_index(indexGroup: IndexGroup, indexStorage: IndexStorage):
    main_file = indexStorage.getStoragePath("profil", "html")
    storage_repository = indexStorage.storage_repository

    dl.download(f"%s/index/%s" % (WEBSITE, indexGroup.sourceId), main_file, storage_repository)
    dl.download(f"%s/index/%s/werte" % (WEBSITE, indexGroup.sourceId), indexStorage.getStoragePath("list", "html"), storage_repository)
