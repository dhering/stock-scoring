import re
from collections import namedtuple
from datetime import datetime
from os.path import isfile

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from functional import seq

from libs.downloader import AbstractDownloader as dl
from libs.model import IndexGroup, Stock
from libs.storage import IndexStorage, StockStorage

WEBSITE = "https://www.onvista.de"

StockExchangeOpt = namedtuple('StockExchangeOpt', 'option volume')


def get_notation(file) -> str:
    """
    example:
        <article typeof="schema:Product">
            <meta property="schema:url" content="https://www.onvista.de/index/NASDAQ-Index-325104">

    :param file: file to load and scrap
    :return: notation, extracted from the URL. Could be None.
    """

    with open(file, mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        article = soup.find("article", {"typeof": "schema:Product"})
        url = article.find("meta", {"property": "schema:url"}).get("content")

        matches = re.search("https:\/\/www.onvista.de\/index\/.*-Index-(\d+)", url)

        return matches.group(1)

    return None


def get_links(main_file):
    links = {}

    with open(main_file, mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        subnavis = soup.find("nav", {"class": "NAVI_SNAPSHOT"}).findAll("li")

        for subnavi in subnavis:
            for link in subnavi.findAll("a", recursive=False):
                if link.get('href') and link.get('href').startswith("/"):
                    links[link.get_text().strip()] = link.get('href')

    return links


def download_history_for_interval(notation, month, filename):
    if month == 0:
        dateStart = datetime.now()
    else:
        dateStart = datetime.now() - relativedelta(months=month)

    dateStart = dateStart.replace(day=1).strftime("%#d.%#m.%Y")

    url = "https://www.onvista.de/onvista/boxes/historicalquote/export.csv" \
          + "?notationId=" + notation + "&dateStart=" + dateStart + "&interval=M1"

    dl.download(url, filename)


def download_history(stock_name: str, stockStorage: StockStorage):
    with open(stockStorage.getStoragePath("history", "html"), mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')
        selectbox = soup.find("div", {"id": "exchangesLayerHs"})

        if not selectbox:
            return


        options = selectbox.findAll("a")

        seo = seq(options) \
            .map(
            lambda opt: StockExchangeOpt(option=opt, volume=opt.find("span").get_text().strip().replace(" Stk.", ""))) \
            .filter(lambda se: se.volume != "") \
            .map(lambda se: StockExchangeOpt(se.option, int(se.volume.replace(".", "")))) \
            .sorted(lambda se: se.volume, reverse=True) \
            .first()

        if seo:
            option = seo.option
            notation = option.get('href').split("=")[1]

            option.span.decompose()
            stockExchange = option.get_text().strip()

            print("download history for '{}' from '{}' stock exchange".format(stock_name, stockExchange))
            download_history_by_notation(notation, stockStorage)
        else:
            print("unable to find notation for stock {}".format(stock_name))


def download_history_by_notation(notation, storage):
    download_history_for_interval(notation, 0, storage.getStoragePath("history-0", "csv"))
    download_history_for_interval(notation, 1, storage.getStoragePath("history-1", "csv"))
    download_history_for_interval(notation, 2, storage.getStoragePath("history-2", "csv"))
    download_history_for_interval(notation, 3, storage.getStoragePath("history-3", "csv"))
    download_history_for_interval(notation, 4, storage.getStoragePath("history-4", "csv"))
    download_history_for_interval(notation, 6, storage.getStoragePath("history-6", "csv"))
    download_history_for_interval(notation, 12, storage.getStoragePath("history-12", "csv"))


def download_ratings(stock_id: str, stockStorage: StockStorage):
    url = "https://www.onvista.de/news/boxes/aggregated-analyses" \
          "?timespan=-1+month&assetType=Stock&assetId=" + stock_id + "&showAllAnalyzesLink=0"

    dl.download(url, stockStorage.getStoragePath("ratings", "html"))


def dump_stock(stock: Stock, stockStorage: StockStorage):
    main_file = stockStorage.getStoragePath("profil", "html")

    dl.download(WEBSITE + "/aktien/" + stock.stock_id, main_file)

    links = get_links(main_file)
    dl.download(WEBSITE + links["Fundamental"], stockStorage.getStoragePath("fundamental", "html"))
    dl.download(WEBSITE + links["T&S/Historie"], stockStorage.getStoragePath("history", "html"))
    dl.download(WEBSITE + links["Profil/Termine"], stockStorage.getStoragePath("company-and-appointments", "html"))

    download_history(stock.name, stockStorage)

    download_ratings(stock.stock_id, stockStorage)


def dump_index(indexGroup: IndexGroup, indexStorage: IndexStorage):
    main_file = indexStorage.getStoragePath("profil", "html")

    dl.download(WEBSITE + "/index/" + indexGroup.index, main_file)

    notation = get_notation(main_file)

    download_history_by_notation(notation, indexStorage)

    links = get_links(main_file)

    dl.download(WEBSITE + links["Einzelwerte"], indexStorage.getStoragePath("list", "html"))
