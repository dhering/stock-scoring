import os
from bs4 import BeautifulSoup

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

def scrap(stock_id, stock_name):

    with open(DUMP_FOLDER +  stock_name + ".fundamental.html", mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        fundamentals = scrap_fundamentals(soup)

        roi = asFloat(fundamentals["Rentabilität"]["Eigenkapitalrendite"]["2017"])
        print("1. Eigenkapitalrendite 2017: " + str(roi))

        ebit_margin = asFloat(fundamentals["Rentabilität"]["EBIT-Marge"]["2017"])
        print("2. EBIT-Marge 2017: " + str(ebit_margin))

        equity_ratio = asFloat(fundamentals["Bilanz"]["Eigenkapitalquote"]["2017"])
        print("3. Eigenkapitalquote 2017: " + str(equity_ratio))

        #per_5_years = asFloat()
        print("4. KGV 5 Jahre: " + fundamentals["Gewinn"]["KGV"]["2017"] + " " + fundamentals["Gewinn"]["KGV"]["2016"]+ " " + fundamentals["Gewinn"]["KGV"]["2015"]+ " " + fundamentals["Gewinn"]["KGV"]["2014"])

        per = asFloat(fundamentals["Gewinn"]["KGV"]["2018e"])
        print("5. KGV 2018e: " + str(per))

        eps_current_year = asFloat(fundamentals["Gewinn"]["Gewinn pro Aktie in EUR"]["2018e"])
        print("13a. EPS 2018e: " + str(eps_current_year))
        eps_last_year = asFloat(fundamentals["Gewinn"]["Gewinn pro Aktie in EUR"]["2017"])
        print("13b. EPS 2017: " + str(eps_last_year))