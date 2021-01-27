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


def get_notation(path: str, repository) -> str:
    """
    example:
        <article typeof="schema:Product">
            <meta property="schema:url" content="https://www.onvista.de/index/NASDAQ-Index-325104">

    :param path: file to load and scrap
    :return: notation, extracted from the URL. Could be None.
    """

    content = repository.load(path)

    if content:
        soup = BeautifulSoup(content, 'html.parser')

        article = soup.find("article", {"typeof": "schema:Product"})
        url = article.find("meta", {"property": "schema:url"}).get("content")

        matches = re.search("https:\/\/www.onvista.de\/index\/.*-Index-(\d+)", url)

        return matches.group(1)

    return None


def get_links(path: str, storage_repository):
    links = {}

    content = storage_repository.load(path)

    if content:
        soup = BeautifulSoup(content, 'html.parser')

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
        dl.download(url, storage.getHistoryPath(f"prices.{toRevertMonthStr(dateStart)}", "csv"),
                    storage_repository, retry=True)


def download_history(stock_name: str, stockStorage: StockStorage):
    path = stockStorage.getStoragePath("history", "html")
    content = stockStorage.storage_repository.load(path)

    if content:
        soup = BeautifulSoup(content, 'html.parser')
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


def dump_stock(stock: Stock, stock_storage: StockStorage):
    main_file = stock_storage.getStoragePath("profil", "html")

    storage_repository = stock_storage.storage_repository

    dl.download(WEBSITE + "/aktien/" + stock.stock_id, main_file, storage_repository)

    links = get_links(main_file, storage_repository)
    dl.download(WEBSITE + links["Fundamental"], stock_storage.getStoragePath("fundamental", "html"),
                storage_repository)
    dl.download(WEBSITE + links["T&S/Historie"], stock_storage.getStoragePath("history", "html"),
                storage_repository, retry=True)
    dl.download(WEBSITE + links["Profil/Termine"], stock_storage.getStoragePath("company-and-appointments", "html"),
                storage_repository)

    download_history(stock.name, stock_storage)

    download_ratings(stock.stock_id, stock_storage)


def dump_index(index_group: IndexGroup, index_storage: IndexStorage):
    main_file = index_storage.getStoragePath("profil", "html")
    storage_repository = index_storage.storage_repository

    dl.download(WEBSITE + "/index/" + index_group.isin, main_file, storage_repository)

    notation = get_notation(main_file, storage_repository)

    download_history_by_notation(notation, index_storage)

    links = get_links(main_file, storage_repository)

    download_stock_list(links["Einzelwerte"], index_storage)


def download_stock_list(next_page, index_storage):
    storage_repository = index_storage.storage_repository
    next_page_count = 0

    while next_page:
        next_page_count += 1
        next_page_path = index_storage.getStoragePath("list.{}".format(next_page_count), "html")

        dl.download(WEBSITE + next_page, next_page_path, storage_repository)
        content = storage_repository.load(next_page_path)

        next_page = get_next_page(content)


def get_next_page(content):
    if content:
        soup = BeautifulSoup(content, 'html.parser')

        navi = soup.find("div", {"class": "BLAETTER_NAVI"})

        if navi:
            next_link = soup.find("div", {"class": "BLAETTER_NAVI"}).find("li", {"class": "WEITER"})
            if next_link:
                return next_link.find("a").get('href')

    return None
