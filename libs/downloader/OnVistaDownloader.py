from datetime import datetime
from os.path import isfile

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from libs.downloader import AbstractDownloader as dl
from libs.model import IndexGroup, Stock

WEBSITE = "https://www.onvista.de"


def getPath(filename):
    return "dump/" + filename


dl.getPath = getPath


def get_links(main_file):
    links = {}

    with open(getPath(main_file), mode="r", encoding="utf-8") as f:
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


def download_history(stock_name):
    with open(getPath(stock_name + ".history.html"), mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        for option in soup.find("div", {"id": "exchangesLayerHs"}).findAll("a"):
            if option.get_text().strip().startswith("Xetra"):
                href = option.get('href')
                notation = href.split("=")[1]

    download_history_by_notation(notation, stock_name)


def download_history_by_notation(notation, stock_name):
    download_history_for_interval(notation, 0, stock_name + ".history-0.csv")
    download_history_for_interval(notation, 1, stock_name + ".history-1.csv")
    download_history_for_interval(notation, 2, stock_name + ".history-2.csv")
    download_history_for_interval(notation, 3, stock_name + ".history-3.csv")
    download_history_for_interval(notation, 4, stock_name + ".history-4.csv")
    download_history_for_interval(notation, 6, stock_name + ".history-6.csv")
    download_history_for_interval(notation, 12, stock_name + ".history-12.csv")


def download_ratings(stock_id, stock_name):
    url = "https://www.onvista.de/news/boxes/aggregated-analyses" \
          "?timespan=-1+month&assetType=Stock&assetId=" + stock_id + "&showAllAnalyzesLink=0"

    dl.download(url, stock_name + ".ratings.html")


def dump_stock(stock: Stock):
    base_folder = stock.indexGroup.name + "/"
    main_file = base_folder +stock.name + ".profil.html"

    if isfile(getPath(main_file)):
        return # avoid downloading files a second time

    dl.download(WEBSITE + "/aktien/" + stock.stock_id, main_file)

    links = get_links(main_file)
    dl.download(WEBSITE + links["Fundamental"], base_folder + stock.name + ".fundamental.html")
    dl.download(WEBSITE + links["T&S/Historie"], base_folder + stock.name + ".history.html")

    download_history(base_folder + stock.name)

    download_ratings(stock.stock_id, base_folder + stock.name)


def dump_index(indexGroup: IndexGroup):
    base_folder = indexGroup.name + "/"
    main_file = base_folder + indexGroup.name + ".profil.html"

    dl.download(WEBSITE + "/index/" + indexGroup.index, main_file)
    download_history_by_notation(indexGroup.index, base_folder + indexGroup.name)

    links = get_links(main_file)

    dl.download(WEBSITE + links["Einzelwerte"], base_folder + indexGroup.name + ".list.html")