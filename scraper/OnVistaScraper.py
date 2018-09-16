from bs4 import BeautifulSoup
from datetime import datetime, timedelta

DUMP_FOLDER = "dump/"


def asFloat(txt):
    return float(txt.replace("%", "").replace(",", "."))


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


def scrap(stock_id, stock_name):
    with open(DUMP_FOLDER + stock_name + ".fundamental.html", mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        last_year = get_last_year()
        current_year = get_current_year()
        next_year = get_next_year()

        fundamentals = scrap_fundamentals(soup)

        roi = asFloat(fundamentals["Rentabilität"]["Eigenkapitalrendite"][last_year])
        print("1. Eigenkapitalrendite 2017: " + str(roi))

        ebit_margin = asFloat(fundamentals["Rentabilität"]["EBIT-Marge"][last_year])
        print("2. EBIT-Marge 2017: " + str(ebit_margin))

        equity_ratio = asFloat(fundamentals["Bilanz"]["Eigenkapitalquote"][last_year])
        print("3. Eigenkapitalquote 2017: " + str(equity_ratio))

        per_5_years = calc_per_5_years(current_year, fundamentals)
        print("4. KGV 5 Jahre: " + str(per_5_years))

        per = asFloat(fundamentals["Gewinn"]["KGV"][current_year])
        print("5. KGV 2018e: " + str(per))

        eps_current_year = asFloat(fundamentals["Gewinn"]["Gewinn pro Aktie in EUR"][current_year])
        print("13a. EPS 2018e: " + str(eps_current_year))
        eps_last_year = asFloat(fundamentals["Gewinn"]["Gewinn pro Aktie in EUR"][next_year])
        print("13b. EPS 2019e: " + str(eps_last_year))
