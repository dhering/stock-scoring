import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

DUMP_FOLDER = "dump/"

def get_links(main_file):
    links = {}

    with open(DUMP_FOLDER + main_file, mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        subnavis = soup.findAll("ul", {"class": "detailnavigation_ul hidden-xs"})

        for subnavi in subnavis:
            for link in subnavi.findAll("a"):
                if link.get('href') and link.get('href').startswith("/"):
                    links[link.get_text()] = link.get('href')

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


def date_rage(days):
    to_date = datetime.today() - timedelta(days=days)
    from_date = to_date - timedelta(days=5)

    return from_date.strftime("%#d.%#m.%Y") + "_" + to_date.strftime("%#d.%#m.%Y")


def download_history(uri, days, filename):
    stock_name = uri.split("/")[3].lower()

    r = requests.get("https://www.boerse-online.de" + uri, allow_redirects=True)
    soup = BeautifulSoup(r.content, 'html.parser')

    __atts = soup.findAll('input', {'name': '__atts'})[-1].get('value')
    __ath = soup.findAll('input', {'name': '__ath'})[-1].get('value')
    __atcrv = soup.findAll('input', {'name': '__atcrv'})[-1].get('value')

    headers = {"__atts": __atts, "__ath": __ath, "__atcrv": str(eval(__atcrv))}

    ajax = requests.post(
        "https://www.boerse-online.de/Ajax/SharesController_HistoricPriceList/" + stock_name + "/XETRA/" + date_rage(
            days), headers=headers)

    print("download into " + filename + ": " + ajax.url)

    write_file_from_response(ajax, filename)


def dump_stock(stock_id, stock_name):
    main_file = stock_name + ".Profil.html"

    download("https://www.boerse-online.de/suchergebnisse?_search=" + stock_id, main_file)

    links = get_links(main_file)

    download("https://www.boerse-online.de" + links["Kursziele"], stock_name + ".Kursziele.html")
    download("https://www.boerse-online.de" + links["Bilanz/GuV"], stock_name + ".Bilanz_GuV.html")
    download("https://www.boerse-online.de" + links["Schätzungen"], stock_name + ".Schätzungen.html")

    download_history(links["Historisch"], 0, stock_name + ".Historisch.today.html")
    download_history(links["Historisch"], 30, stock_name + ".Historisch.30.html")
    download_history(links["Historisch"], 180, stock_name + ".Historisch.180.html")
