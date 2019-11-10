import os

from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import csv
import re

from libs.DateUtils import toRevertStr, sameDay, toRevertMonthStr
from libs.model import History, IndexGroup, Stock, MonthClosings, AnalystRatings, ReactionToQuarterlyNumbers
from libs.scraper.OnVistaDateUtil import OnVistaDateUtil
from libs.storage import StockStorage, IndexStorage

from libs.scraper.AbstractScraper import asFloat

DUMP_FOLDER = "dump/"


def scrap_price(soup):
    quotebox = soup.find("div", {"class": "row quotebox"}).find("div")
    quotebox.span.decompose()

    return quotebox.get_text().strip()

def scrap_currencies(soup):
    quoteboxes = soup.findAll("div", {"class": "row quotebox"})

    currencies = []

    for quotebox in quoteboxes:
        currency = quotebox.div.span.get_text().strip()
        currencies.append(currency)



    return currencies


def scrap_fundamentals(soup: BeautifulSoup):
    h3s = soup.findAll("h3", {"class": "box-headline"})

    for h3 in h3s:
        headline = h3.get_text().strip()

        if headline.startswith("Kennzahlen ") and headline.endswith(" Aktie"):
            box = h3.parent
            table = box.find("table")

            fundamentals = scrap_annual_table(table)

            table = box.parent.parent.find("div", {"class": "box"}, recursive=False).div.table

            for row in table.findAll("tr"):
                for index, column in enumerate(row.findAll("td")):

                    if index % 2 == 0:
                        key = column.get_text().strip()
                    else:
                        fundamentals[key] = column.get_text().strip()

            return fundamentals

    return {}

def scrap_company_details(soup: BeautifulSoup):
    h3s = soup.findAll("h3", {"class": "box-headline"})

    for h3 in h3s:
        headline = h3.get_text().strip()

        if headline.startswith("Zum Unternehmen "):
            box = h3.parent
            table = box.find("table")

            details = {}

            for row in table.findAll("tr"):
                for index, column in enumerate(row.findAll("td")):

                    if index % 2 == 0:
                        key = column.get_text().strip()
                    else:
                        details[key] = column.get_text().strip()

            return details

    return {}


def scrap_bilanz_guv(soup):
    quotes = soup.findAll("div", {"class": "box table-quotes"})

    bilanz_guv = {}

    for quote in quotes:
        tablename = quote.find("h2").get_text().strip()

        if ":" in tablename:
            tablename = tablename.split(":")[1].strip()

        table = quote.find("table")

        header = []
        data = {}
        for index, column in enumerate(table.thead.findAll("th")):

            year = column.get_text().strip()

            if index > 1 and year != "":
                header.append(year)
                data[year] = {}

        for row in table.findAll("tr"):
            for index, column in enumerate(row.findAll("td")):
                if index == 1:
                    column_name = column.get_text()\
                        .strip()\
                        .replace(" (in EUR)", "")\
                        .replace(" (in USD)", "")
                    if (column_name == ""):
                        break
                    data[column_name] = {}
                elif index > 1 and header[index - 2]:
                    data[column_name][header[index - 2]] = column.get_text().strip()

        bilanz_guv[tablename] = data

    return bilanz_guv


def scrap_schaetzung(soup):
    quotes = soup.findAll("div", {"class": "box table-quotes"})

    for quote in quotes:
        headline = quote.find("h1")

        if headline is None:
            continue

        tablename = headline.get_text().strip()

        if "Schätzungen* zu " not in tablename:
            continue

        table = quote.find("table")

        return scrap_annual_table(table)

    return None


def scrap_annual_table(table):
    header = []
    content = {}
    for index, column in enumerate(table.thead.findAll("th")):

        year = column.get_text().strip().replace("e", "")

        if index > 0 and year != "":
            header.append(year)

    for row in table.findAll("tr"):
        for index, column in enumerate(row.findAll("td")):
            if index == 0:
                column_name = column.get_text().strip()
                if column_name == "":
                    break
                content[column_name] = {}
            elif header[index - 1]:
                value = column.get_text().strip() \
                    .replace(" EUR", "") \
                    .replace(" %", "")

                if value != "-":
                    content[column_name][header[index - 1]] = value

    return content


def scrap_analysen(soup: BeautifulSoup):
    h3s = soup.findAll("h3", {"class": "box-headline"})

    for h3 in h3s:
        headline = h3.get_text().strip()

        if headline.startswith("Kursziele ") and headline.endswith(" Aktie"):

            ratings = {}

            ratingLegend = h3.parent.find("div", {"class": "ratingLegend"})
            rows = ratingLegend.findAll("div", {"class": "clearfix"})

            for row in rows:
                row_content = row.get_text().strip().split(": ")

                if len(row_content) == 2:
                    ratings[row_content[0]] = row_content[1]


            return AnalystRatings(int(ratings["Buy"]), int(ratings["Hold"]), int(ratings["Sell"]))

    return None



def scrap(stock: Stock, stock_storage: StockStorage, util: OnVistaDateUtil = OnVistaDateUtil()):
    with open(stock_storage.getStoragePath("profil", "html"), mode="r") as f:
        soup = BeautifulSoup(f, 'html.parser')

        currencies = scrap_currencies(soup)

        price = scrap_price(soup)
        fundamentals = scrap_fundamentals(soup)
        company_details = scrap_company_details(soup)

    with open(stock_storage.getStoragePath("bilanz_guv", "html"), mode="r") as f:
        soup = BeautifulSoup(f, 'html.parser')

        bilanz_guv = scrap_bilanz_guv(soup)

    with open(stock_storage.getStoragePath("schaetzungen", "html"), mode="r") as f:
        soup = BeautifulSoup(f, 'html.parser')

        schaetzung = scrap_schaetzung(soup)

    with open(stock_storage.getStoragePath("analysen", "html"), mode="r") as f:
        soup = BeautifulSoup(f, 'html.parser')

        stock.ratings = scrap_analysen(soup)

    last_year = util.get_last_year()
    current_year = util.get_current_year(estimated=False)
    next_year = util.get_next_year(estimated=False)

    stock.price = asFloat(price)

    stock.field = company_details["Branchen"]

    for c in currencies:
        if f"GuV (in Mio. {c})" in bilanz_guv:
            currency = c

    gewinn = asFloat(bilanz_guv[f"GuV (in Mio. {currency})"]["Ergebnis nach Steuer"][last_year])
    ebit = asFloat(bilanz_guv[f"GuV (in Mio. {currency})"]["Ergebnis vor Steuern"][last_year])
    erloes = asFloat(bilanz_guv[f"GuV (in Mio. {currency})"]["Umsatzerlöse"][last_year])
    eigenkapital = asFloat(bilanz_guv[f"Bilanz (in Mio. {currency})"]["Eigenkapital"][last_year])

    stock.roi = gewinn / eigenkapital * 100
    stock.ebit_margin = ebit / erloes * 100

    stock.equity_ratio = asFloat(bilanz_guv[f"Unternehmenskennzahlen (in {currency})"]["Eigenkapitalquote in %"][last_year])

    stock.per = asFloat(schaetzung["KGV"][current_year])

    hist_pers = bilanz_guv[f"Unternehmenskennzahlen (in {currency})"]["KGV (Jahresendkurs)"]

    per_5_years = stock.per
    number_of_year = 1

    for year in list(hist_pers.keys())[-4:]:
        if hist_pers[year] != "-":
            per_5_years += asFloat(hist_pers[year])
            number_of_year += 1

    stock.per_5_years = (per_5_years / number_of_year)

    stock.eps_current_year = asFloat(schaetzung["Ergebnis/Aktie (reported)"][current_year])
    stock.eps_next_year = asFloat(schaetzung["Ergebnis/Aktie (reported)"][next_year])

    stock.per_fallback = stock.price / stock.eps_current_year if stock.eps_current_year != 0 else 0

    stock.market_capitalization = asFloat(fundamentals[f"Marktkapitalisierung in Mrd. EUR"]) * 1000000000

    stock.eps_next_year = 0
    stock.eps_current_year = 0

    stock_price_today = 0
    stock_price_6month = 0
    stock_price_1year = 0

    stock.history = History(stock_price_today, stock_price_6month, stock_price_1year)

    stock.monthClosings = MonthClosings()

    stock.eps_current_year = asFloat(schaetzung["Ergebnis/Aktie"]["2019"])
    stock.eps_next_year = asFloat(schaetzung["Ergebnis/Aktie"]["2020"])

    stock.historical_eps_current_year = 0
    stock.historical_eps_date = 0
    stock.historical_eps_next_year = 0

    stock.reaction_to_quarterly_numbers = ReactionToQuarterlyNumbers(0, 0, 0, 0, "")

    return stock


'''


        date = stock_storage.indexStorage.date

        if sameDay(date, datetime.now()):
            date = date - relativedelta(days=1)

        stock_price_today = get_historical_price(stock_storage, date)
        stock_price_6month = get_historical_price(stock_storage, (date - relativedelta(months=6)))
        stock_price_1year = get_historical_price(stock_storage, (date - relativedelta(months=12)))

        stock.history = History(stock_price_today, stock_price_6month, stock_price_1year)

        stock.monthClosings = get_month_closings(stock_storage)
'''


#    stock = scrap_ratings(stock, stock_storage)

#    add_historical_eps(stock, stock_storage)

#    add_reaction_to_quarterly_numbers(stock, stock_storage)

#    return stock


def calc_per_5_years(pers, ref_year):
    counter = 0
    per_sum = 0.0
    for key in pers.keys():
        if key <= ref_year and pers[key].strip() != "-":
            counter += 1
            per_sum += asFloat(pers[key])

    if counter == 0:
        return 0

    return per_sum / counter


def find_existing_column(values, col_names: []):
    for name in col_names:
        if name in values:
            return name

    return None


def read_stocks(indexGroup, index_storage: IndexStorage):
    with open(index_storage.getStoragePath("list", "html"), mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        article = soup.find("div", {"id": "index-list-container"})
        table = article.find("table")

        for row in table.findAll("tr"):
            columns = row.findAll("td")

            if len(columns) == 0:
                continue

            firstCol = columns[0]

            link = firstCol.find("a")

            if link is not None and link.get("href") and link.get("href").startswith("/"):
                matches = re.search(r'\/aktien\/(.*)-aktie', link.get("href"))
                name = matches.group(1)

                stock_id = firstCol.get_text().strip().split("\n")[1]

                indexGroup.add_stock(stock_id, name)
