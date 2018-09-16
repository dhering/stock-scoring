import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import monthdelta
from dateutil.relativedelta import relativedelta

WEBSITE = "https://www.onvista.de"
DUMP_FOLDER = "dump/"


def get_links(main_file):
    links = {}

    with open(DUMP_FOLDER + main_file, mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        subnavis = soup.find("nav", {"class": "NAVI_SNAPSHOT"}).findAll("li")

        for subnavi in subnavis:
            for link in subnavi.findAll("a", recursive=False):
                if link.get('href') and link.get('href').startswith("/"):
                    links[link.get_text().strip()] = link.get('href')

    return links


def write_file_from_response(res, filename):
    path = DUMP_FOLDER + filename

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(res.content)


def download(url, filename):
    r = requests.get(url, allow_redirects=True)
    print("download into " + filename + ": " + r.url)

    write_file_from_response(r, filename)


def download_history_for_interval(notation, month, filename):

    if month == 0:
        dateStart = datetime.now()
    else:
        dateStart = datetime.now() - relativedelta(months=month)

    dateStart = dateStart.replace(day=1).strftime("%#d.%#m.%Y")

    url = "https://www.onvista.de/onvista/boxes/historicalquote/export.csv" \
          + "?notationId=" + notation + "&dateStart=" + dateStart + "&interval=M1"

    download(url, filename)


def download_history(stock_name):

    with open(DUMP_FOLDER + stock_name + ".history.html", mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        for option in soup.find("div", {"id": "exchangesLayerHs"}).findAll("a"):
            if option.get_text().strip().startswith("Xetra"):
                href = option.get('href')
                notation = href.split("=")[1]
                print(notation)

    download_history_for_interval(notation, 1, stock_name + ".history-0.csv")
    download_history_for_interval(notation, 1, stock_name + ".history-1.csv")
    download_history_for_interval(notation, 2, stock_name + ".history-2.csv")
    download_history_for_interval(notation, 3, stock_name + ".history-3.csv")
    download_history_for_interval(notation, 6, stock_name + ".history-6.csv")
    download_history_for_interval(notation, 12, stock_name + ".history-12.csv")


def dump_stock(stock_id, stock_name):
    main_file = stock_name + ".profil.html"

    download(WEBSITE + "/aktien/" + stock_id, main_file)

    links = get_links(main_file)
    download(WEBSITE + links["Fundamental"], stock_name + ".fundamental.html")
    download(WEBSITE + links["T&S/Historie"], stock_name + ".history.html")

    download_history(stock_name)
