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


def scrap_fundamentals(soup):
    fundamental = soup.find("article", {"class": "KENNZAHLEN"})

    data_fundamental = {}

    for table in fundamental.findAll("table"):
        name = table.find("th")

        name.em.decompose()
        name.span.decompose()

        tablename = name.get_text().strip()

        header = list(map(lambda th: th.get_text().strip(), table.findAll("th")))

        data = {}
        for index, year in enumerate(header):
            if index > 0 and year != "":
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


def get_for_year(values, col_names: [], fallback: str = "0"):
    col_name = find_existing_column(values, col_names)

    if (col_name is None) or col_name not in values:
        return fallback

    return values[col_name]


def find_existing_column(values, col_names: []):
    for name in col_names:
        if name in values:
            return name

    return None


def calc_per_5_years(fundamentals, col_names: []):
    pers = fundamentals["Gewinn"]["KGV"]

    ref_year = find_existing_column(pers, col_names)

    if ref_year is None:
        return 0

    counter = 0
    per_sum = 0.0
    for key in pers.keys():
        if key <= ref_year and pers[key].strip() != "-":
            counter += 1
            per_sum += asFloat(pers[key])

    if counter == 0:
        return 0

    return per_sum / counter


def get_path_to_historical_prices(storage, historical_date) -> str:
    historical_month = toRevertMonthStr(historical_date)

    ref_date = get_reference_date(storage)

    filename = None

    if toRevertMonthStr(ref_date) == historical_month:
        filename = storage.getStoragePath("prices", "csv")

        if not os.path.isfile(filename):
            filename = None

    if filename is None:
        filename = storage.getHistoryPath(f"prices.{historical_month}", "csv")

    return filename


def read_price_from_csv(filename: str, date_for_price):
    if not os.path.isfile(filename):
        return 0

    with open(filename, mode="r", encoding="utf-8") as f:
        history = csv.DictReader(f, delimiter=';')
        last_price = None

        for day in history:
            if day["Datum"].strip() == "":
                continue

            date = datetime.strptime(day["Datum"].strip(), "%d.%m.%Y")

            if date > date_for_price and last_price is not None:
                break

            if day["Schluss"]:
                last_price = day["Schluss"]

        if last_price is None:
            return 0

        return asFloat(last_price)


def get_latest_price(storage, date):

    filename = storage.getStoragePath("prices", "csv")

    price = read_price_from_csv(filename, date)

    if price > 0:
        return price
    else:
        last_day_last_month = (date - relativedelta(days=date.day))
        historical_month = toRevertMonthStr(last_day_last_month)

        filename = storage.getHistoryPath(f"prices.{historical_month}", "csv")

        return read_price_from_csv(filename, last_day_last_month)


def get_historical_price(storage, historical_date):
    historical_month = toRevertMonthStr(historical_date)

    filename = storage.getHistoryPath(f"prices.{historical_month}", "csv")

    return read_price_from_csv(filename, historical_date)


def scrap_ratings(stock, stock_storage: StockStorage):
    filename = stock_storage.getStoragePath("ratings", "html")
    ratings = {
        "kaufen": 0,
        "halten": 0,
        "verkaufen": 0
    }

    if os.path.isfile(filename):
        with open(filename, mode="r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, 'html.parser')

            for row in soup.findAll("tr"):
                columns = row.findAll("td")

                type = columns[0].get_text().strip()
                count = columns[1]

                count.div.decompose()

                ratings[type] = int(count.get_text().strip())

    stock.ratings = AnalystRatings(ratings["kaufen"], ratings["halten"], ratings["verkaufen"])

    return stock


def get_market_capitalization(fundamentals, last_year, last_cross_year):
    market_capitalization = asFloat(
        get_for_year(fundamentals["Marktkapitalisierung"]["Marktkapitalisierung in Mio. EUR"], [last_year,
                                                                                                last_cross_year]))
    if market_capitalization > 0:
        market_capitalization = market_capitalization * 1000000

    return market_capitalization


def add_reaction_to_quarterly_numbers(stock, stock_storage):
    appointments = read_existing_appointments(stock_storage)

    scrap_appointments(appointments, stock_storage)

    write_appointments(appointments, stock_storage)

    from_date = toRevertStr(stock_storage.indexStorage.date - relativedelta(months=3))
    to_date = toRevertStr(stock_storage.indexStorage.date)

    newest_appointments = {k: v for k, v in appointments.items() if from_date <= k <= to_date}

    if len(newest_appointments) > 0:
        last_appointment = max(newest_appointments.keys())

        last_appointment_date = (datetime.strptime(last_appointment, "%Y-%m-%d"))
        before_appointment_date = (last_appointment_date - relativedelta(days=1))

        price_before = get_historical_price(stock_storage, before_appointment_date)
        price = get_historical_price(stock_storage, last_appointment_date)

        index_price_before = get_historical_price(stock_storage.indexStorage, before_appointment_date)
        index_price = get_historical_price(stock_storage.indexStorage, last_appointment_date)

        stock.reaction_to_quarterly_numbers = ReactionToQuarterlyNumbers(price, price_before, index_price,
                                                                         index_price_before, last_appointment)


def read_existing_appointments(stock_storage: StockStorage):
    appointments = {}

    path = stock_storage.indexStorage.getAppointmentsPath()
    csv_file = path + stock_storage.getFilename("company-and-appointments", "csv")

    if os.path.isfile(csv_file):
        with open(csv_file, mode="r", encoding="utf-8") as f:
            rows = csv.DictReader(f, delimiter=';')

            for row in rows:
                date = row["Date"].strip()
                topic = row["Topic"].strip()

                appointments[date] = topic

    return appointments


def write_appointments(appointments, stock_storage: StockStorage):
    if len(appointments) > 0:

        path = stock_storage.indexStorage.getAppointmentsPath()
        csv_file = path + stock_storage.getFilename("company-and-appointments", "csv")

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(csv_file, 'w', encoding="utf-8") as f:

            f.write("Date;Topic;\n")

            for key, value in appointments.items():
                f.write("%s;%s;\n" % (key, value))


def scrap_appointments(appointments, stock_storage):
    def scrap(soup):
        article = soup.find("article", {"class": "TERMINE"})
        table = article.find("table")

        for row in table.findAll("tr"):
            columns = row.findAll("td")

            if len(columns) < 2:
                continue

            date = columns[0].get_text().strip()
            topic = columns[1].get_text().strip()

            matches = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', date)
            if matches is not None:
                date = "%s-%s-%s" % (matches.group(3), matches.group(2), matches.group(1))

            if date in appointments:
                continue

            if "Bericht" in topic or "Jahresbericht" in topic:
                appointments[date] = topic

    path = stock_storage.getStoragePath("company-and-appointments", "html")

    if os.path.isfile(path):
        try:
            with open(path, mode="r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, 'html.parser')
                scrap(soup)
        except UnicodeDecodeError:
            print(f"Could not scrap appointments for {stock_storage.stock.name}, retry without UTF-8 encoding.")
            try:
                with open(path, mode="r") as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    scrap(soup)
            except UnicodeDecodeError:
                print(f"Failed to scrap appointments for {stock_storage.stock.name}.")
                pass


def scrap(stock: Stock, stock_storage: StockStorage, util: OnVistaDateUtil = OnVistaDateUtil()):
    with open(stock_storage.getStoragePath("fundamental", "html"), mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        fundamentals = scrap_fundamentals(soup)

        last_year_est = util.get_last_year(estimated=True)
        last_cross_year_est = util.get_last_cross_year(estimated=True)

        fallback_to_last_year_values = last_year_est in fundamentals["Rentabilität"][
            "Eigenkapitalrendite"] or last_cross_year_est in fundamentals["Rentabilität"]["Eigenkapitalrendite"]

        if fallback_to_last_year_values:
            last_year = util.get_last_year(min_years=2)
            last_cross_year = util.get_last_cross_year(min_years=2)
            current_year = util.get_last_year(estimated=True)
            current_cross_year = util.get_last_cross_year()
            current_cross_year_est = util.get_last_cross_year(estimated=True)
            next_year = util.get_current_year()
            next_cross_year = util.get_current_cross_year()
        else:
            last_year = util.get_last_year()
            last_cross_year = util.get_last_cross_year()
            current_year = util.get_current_year()
            current_cross_year = util.get_current_cross_year(estimated=False)
            current_cross_year_est = util.get_current_cross_year()
            next_year = util.get_next_year()
            next_cross_year = util.get_next_cross_year()

        stock.price = asFloat(soup.find("ul", {"class": "KURSDATEN"}).find("li").find("span").get_text().strip())

        stock.roi = asFloat(
            get_for_year(fundamentals["Rentabilität"]["Eigenkapitalrendite"], [last_year, last_cross_year]))
        stock.ebit_margin = asFloat(
            get_for_year(fundamentals["Rentabilität"]["EBIT-Marge"], [last_year, last_cross_year]))

        stock.equity_ratio = asFloat(
            get_for_year(fundamentals["Bilanz"]["Eigenkapitalquote"], [last_year, last_cross_year]))

        stock.per_5_years = calc_per_5_years(fundamentals, [current_year, current_cross_year_est, current_cross_year])

        stock.per = asFloat(get_for_year(fundamentals["Gewinn"]["KGV"], [current_year, current_cross_year_est, current_cross_year]))

        date = stock_storage.indexStorage.date

        if sameDay(date, datetime.now()):
            date = date - relativedelta(days=1)

        stock_price_today = get_latest_price(stock_storage, date)

        stock_price_6month = get_historical_price(stock_storage, (date - relativedelta(months=6)))
        stock_price_1year = get_historical_price(stock_storage, (date - relativedelta(months=12)))

        stock.history = History(stock_price_today, stock_price_6month, stock_price_1year)

        stock.monthClosings = get_month_closings(stock_storage)

        stock.eps_current_year = asFloat(
            get_for_year(fundamentals["Gewinn"]["Gewinn pro Aktie in EUR"],
                         [current_year, current_cross_year_est, current_cross_year]))

        stock.per_fallback = stock.price / stock.eps_current_year if stock.eps_current_year != 0 else 0

        stock.eps_next_year = asFloat(
            get_for_year(fundamentals["Gewinn"]["Gewinn pro Aktie in EUR"], [next_year, next_cross_year]))

        stock.market_capitalization = get_market_capitalization(fundamentals, last_year, last_cross_year)

    stock = scrap_ratings(stock, stock_storage)

    add_historical_eps(stock, stock_storage)

    add_reaction_to_quarterly_numbers(stock, stock_storage)

    return stock


def add_historical_eps(stock: Stock, stock_storage: StockStorage):
    if not stock_storage.indexStorage.historicalStorage:
        stock.historical_eps_current_year = 0
        stock.historical_eps_next_year = 0
        return

    historical_storage = StockStorage(stock_storage.indexStorage.historicalStorage, stock)

    stock.historical_eps_date = historical_storage.indexStorage.date_str

    try:
        historical_storage.load()
        historical_stock = historical_storage.stock

        stock.historical_eps_current_year = historical_stock.eps_current_year
        stock.historical_eps_next_year = historical_stock.eps_next_year

    except FileNotFoundError:
        stock.historical_eps_current_year = 0
        stock.historical_eps_next_year = 0


def scrap_index(indexGroup: IndexGroup, index_storage: IndexStorage):
    date = index_storage.date

    if sameDay(date, datetime.now()):
        date = date - relativedelta(days=1)

    index_price_today = get_latest_price(index_storage, date)

    index_price_6month = get_historical_price(index_storage, (date - relativedelta(months=6)))

    index_price_1year = get_historical_price(index_storage, (date - relativedelta(months=12)))

    indexGroup.history = History(index_price_today, index_price_6month, index_price_1year)

    indexGroup.monthClosings = get_month_closings(index_storage)


def get_month_closings(storage):
    closings = MonthClosings()

    closings.closings = [
        get_closing_price(storage, 4),
        get_closing_price(storage, 3),
        get_closing_price(storage, 2),
        get_closing_price(storage, 1)
    ]

    return closings


def get_reference_date(storage):
    if (isinstance(storage, IndexStorage)):
        date_ref = storage.date
    elif (isinstance(storage, StockStorage)):
        date_ref = storage.indexStorage.date
    else:
        date_ref = datetime.now()

    return (date_ref - timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0)


def get_closing_price(storage, month):
    ref_month = get_reference_date(storage) - relativedelta(months=month)

    filename = get_path_to_historical_prices(storage, ref_month)

    if not os.path.isfile(filename):
        return 0

    with open(filename, mode="r", encoding="utf-8") as f:
        history = csv.DictReader(f, delimiter=';')

        last_price = "0"

        first_day_next_month = (ref_month + relativedelta(months=1)).replace(day=1)

        for day in history:
            date_str = day["Datum"].strip()
            if date_str == "":
                continue
            if datetime.strptime(date_str, "%d.%m.%Y") >= first_day_next_month:
                break
            if day["Schluss"]:
                last_price = day["Schluss"]

        return asFloat(last_price)


def read_stocks(indexGroup, index_storage: IndexStorage):
    with open(index_storage.getStoragePath("list", "html"), mode="r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

        article = soup.find("article", {"class": "top-flop-box"})
        table = article.find("table")

        for row in table.findAll("tr"):
            columns = row.findAll("td")

            if len(columns) == 0:
                continue

            firstCol = columns[0]

            link = firstCol.find("a")

            if link is not None and link.get("href") and link.get("href").startswith("/"):
                matches = re.search(r'\/aktien\/(.*)-Aktie-(.*)', link.get("href"))
                name = matches.group(1)
                stock_id = matches.group(2)

                field = firstCol.find("span").get_text().strip()

                indexGroup.add_stock(stock_id, name, field)
