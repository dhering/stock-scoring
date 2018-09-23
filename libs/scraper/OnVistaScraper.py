from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import csv

from libs.Model import History, IndexGroup, Stock

DUMP_FOLDER = "dump/"


def asFloat(txt):
    return float(txt.replace("%", "").replace(".", "").replace(",", "."))


def scrap_fundamentals(soup):
    fundamental = soup.find("article", {"class": "KENNZAHLEN"})

    print("Scraping: " + fundamental.find("h2", {"class": "BOX_HEADLINE"}).get_text())

    data_fundamental = {}

    for table in fundamental.findAll("table"):
        name = table.find("th")

        name.em.decompose()
        name.span.decompose()

        tablename = name.get_text().strip()

        header = list(map(lambda th: th.get_text().strip(), table.findAll("th")))

        data = {}
        for index, year in enumerate(header):
            if (index > 0 and year != ""):
                data[year] = {}

        for row in table.tbody.findAll("tr"):
            for index, column in enumerate(row.findAll("td")):
                if (index == 0):
                    column_name = column.get_text().strip()
                    if (column_name == ""):
                        break
                    data[column_name] = {}
                elif (header[index]):
                    data[column_name][header[index]] = column.get_text().strip()

        data_fundamental[tablename] = data

    return data_fundamental


def get_last_year():
    return str(datetime.now().year - 1)


def get_current_year():
    return str(datetime.now().year) + "e"


def get_next_year():
    return str(datetime.now().year + 1) + "e"


def calc_per_5_years(current_year, fundamentals):
    pers = fundamentals["Gewinn"]["KGV"]
    counter = 0
    per_sum = 0.0
    for key in pers.keys():
        if key <= current_year:
            counter += 1
            per_sum += asFloat(pers[key])

    if counter == 0:
        return 0

    return per_sum / counter


def get_historical_price(stock_name, month):

    with open(DUMP_FOLDER + stock_name + ".history-" + str(month) + ".csv", mode="r", encoding="utf-8") as f:
        history = csv.DictReader(f, delimiter=';')
        date_ref = (datetime.now() - timedelta(1))
        if month != 0:
            date_ref = date_ref - relativedelta(months=month)

        for day in history:
            if day["Datum"].strip() == "":
                continue

            date = datetime.strptime(day["Datum"].strip(), "%d.%m.%Y")

            if date > date_ref:
                break

            last_price = day["Schluss"]

        return asFloat(last_price)


def scrap(stock: Stock):
    with open(DUMP_FOLDER + stock.name + ".fundamental.html", mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        last_year = get_last_year()
        current_year = get_current_year()
        next_year = get_next_year()

        fundamentals = scrap_fundamentals(soup)

        stock.roi = asFloat(fundamentals["Rentabilität"]["Eigenkapitalrendite"][last_year])

        stock.ebit_margin = asFloat(fundamentals["Rentabilität"]["EBIT-Marge"][last_year])

        stock.equity_ratio = asFloat(fundamentals["Bilanz"]["Eigenkapitalquote"][last_year])

        stock.per_5_years = calc_per_5_years(current_year, fundamentals)

        stock.per = asFloat(fundamentals["Gewinn"]["KGV"][current_year])

        stock_price_today = get_historical_price(stock.name, 0)
        stock_price_6month = get_historical_price(stock.name, 6)
        stock_price_1year = get_historical_price(stock.name, 12)

        stock.history = History(stock_price_today, stock_price_6month, stock_price_1year)

        stock.eps_current_year = asFloat(fundamentals["Gewinn"]["Gewinn pro Aktie in EUR"][current_year])

        stock.eps_last_year = asFloat(fundamentals["Gewinn"]["Gewinn pro Aktie in EUR"][next_year])

        stock.print_report()

def scrap_index(indexGroup: IndexGroup):
    index_price_today = get_historical_price(indexGroup.name, 0)

    index_price_6month = get_historical_price(indexGroup.name, 6)

    index_price_1year = get_historical_price(indexGroup.name, 12)

    indexGroup.history = History(index_price_today, index_price_6month, index_price_1year)