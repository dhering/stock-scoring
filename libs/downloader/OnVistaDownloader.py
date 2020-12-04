import re
from collections import namedtuple

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from functional import seq

from libs.DateUtils import toRevertMonthStr
from libs.downloader import AbstractDownloader as dl
from libs.model import IndexGroup, Stock
from libs.storage import IndexStorage, StockStorage

WEBSITE = "https://www.onvista.de"

StockExchangeOpt = namedtuple('StockExchangeOpt', 'option name notation volume')


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


def download_history_for_delta(notation: str, delta: int, storage):
    if (isinstance(storage, IndexStorage)):
        dateStart = storage.date
    elif (isinstance(storage, StockStorage)):
        dateStart = storage.indexStorage.date

    storage_repository = storage.storage_repository

    if delta != 0:
        dateStart = dateStart - relativedelta(months=delta)

    dateStart_str = dateStart.replace(day=1).strftime("%#d.%#m.%Y")

    url = f"https://www.onvista.de/onvista/boxes/historicalquote/export.csv" \
          f"?notationId={notation}&dateStart={dateStart_str}&interval=M1"

    if delta == 0:
        dl.download(url, storage.getStoragePath("prices", "csv"), storage_repository, retry=True)
    else:
        dl.download(url, storage.getHistoryPath(f"prices.{toRevertMonthStr(dateStart)}", "csv"), storage_repository, retry=True)


def download_history(stock_name: str, stockStorage: StockStorage):
    with open(stockStorage.getStoragePath("history", "html"), mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')
        selectbox = soup.find("div", {"id": "exchangesLayerHs"})

        if not selectbox:
            return

        options = selectbox.findAll("a")

        if options is None:
            print("unable to find historical data for stock {}".format(stock_name))

        def create_StockExchangeOpt(opt):
            volume = opt.find("span").get_text().strip()
            volume = volume.replace(" Stk.", "")
            volume = "0" if volume is None or volume == "" else volume
            volume = volume.replace(".", "")

            notation = opt.get('href').split("=")[1]

            opt.find("span").decompose()
            name = opt.get_text().strip()

            return StockExchangeOpt(option=opt, name=name, notation=notation, volume=int(volume))

        def is_valid_exchange_option(opt: StockExchangeOpt, ref_index: str) -> bool:
            if ref_index == "TecDAX":
                return opt.name != "Swiss Exchange"

            return True

        ref_index = stockStorage.stock.indexGroup.name

        seo = seq(options) \
            .map(create_StockExchangeOpt) \
            .filter(lambda se: is_valid_exchange_option(se, ref_index)) \
            .sorted(lambda se: se.volume, reverse=True) \
            .first()

        if seo:
            print("download history for '{}' from '{}' stock exchange (volumne: {})"
                  .format(stock_name, seo.name, seo.volume))

            download_history_by_notation(seo.notation, stockStorage)
        else:
            print("unable to find notation for stock {}".format(stock_name))


def download_history_by_notation(notation, storage):
    download_history_for_delta(notation, 0, storage)
    download_history_for_delta(notation, 1, storage)
    download_history_for_delta(notation, 2, storage)
    download_history_for_delta(notation, 3, storage)
    download_history_for_delta(notation, 4, storage)
    download_history_for_delta(notation, 6, storage)
    download_history_for_delta(notation, 12, storage)


def download_ratings(stock_id: str, stockStorage: StockStorage):
    url = "https://www.onvista.de/news/boxes/aggregated-analyses" \
          "?timespan=-1+month&assetType=Stock&assetId=" + stock_id + "&showAllAnalyzesLink=0"

    dl.download(url, stockStorage.getStoragePath("ratings", "html"), stockStorage.storage_repository)


def dump_stock(stock: Stock, stockStorage: StockStorage):
    main_file = stockStorage.getStoragePath("profil", "html")

    storage_repository = stockStorage.storage_repository

    dl.download(WEBSITE + "/aktien/" + stock.stock_id, main_file, storage_repository)

    links = get_links(main_file)
    dl.download(WEBSITE + links["Fundamental"], stockStorage.getStoragePath("fundamental", "html"), storage_repository)
    dl.download(WEBSITE + links["T&S/Historie"], stockStorage.getStoragePath("history", "html"), storage_repository, retry=True)
    dl.download(WEBSITE + links["Profil/Termine"], stockStorage.getStoragePath("company-and-appointments", "html"), storage_repository)

    download_history(stock.name, stockStorage)

    download_ratings(stock.stock_id, stockStorage)


def dump_index(indexGroup: IndexGroup, indexStorage: IndexStorage):
    main_file = indexStorage.getStoragePath("profil", "html")
    storage_repository = indexStorage.storage_repository

    dl.download(WEBSITE + "/index/" + indexGroup.isin, main_file, storage_repository)

    notation = get_notation(main_file)

    download_history_by_notation(notation, indexStorage)

    links = get_links(main_file)

    dl.download(WEBSITE + links["Einzelwerte"], indexStorage.getStoragePath("list", "html"), storage_repository)
