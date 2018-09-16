import os
import requests
from bs4 import BeautifulSoup

DUMP_FOLDER = "dump/"


def get_links(main_file):
    links = {}

    with open(DUMP_FOLDER + main_file, mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        subnavis = soup.find("nav", {"class": "NAVI_SNAPSHOT"}).findAll("li")

        for subnavi in subnavis:
            for link in subnavi.findAll("a", recursive=False):
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


def dump_stock(stock_id, stock_name):
    main_file = stock_name + ".profil.html"

    download("https://www.onvista.de/aktien/" + stock_id, main_file)

    links = get_links(main_file)

    download("https://www.onvista.de" + links["Fundamental"], stock_name + ".fundamental.html")