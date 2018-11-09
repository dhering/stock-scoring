from collections import namedtuple
from datetime import datetime

from libs.HtmlReport import write_stock_report, write_index_report
from libs.Rating import Rating
from libs.downloader import OnVistaDownloader as downloader
from libs.model import IndexGroup
from libs.scraper import OnVistaScraper as scraper
from libs.storage import IndexStorage, StockStorage

task_download_index = True
task_download = True
task_scrap = True
print_full = True
skip_underrated = True

indexGroup = IndexGroup("DE0008469008", "DAX")
# indexGroup = IndexGroup("DE0008467416", "MDAX")
# indexGroup = IndexGroup("DE0007203275", "TecDAX")
# indexGroup = IndexGroup("DE0009653386", "SDAX")
# indexGroup = IndexGroup("EU0009658145", "EURO-STOXX-50")
indexGroup = IndexGroup("EU0009658202", "EURO-STOXX-600")
# indexGroup = IndexGroup("AT0000999982", "ATX")
# indexGroup = IndexGroup("CH0009980894", "SMI")
# indexGroup = IndexGroup("US2605661048", "Dow-Jones")
# indexGroup = IndexGroup("US6311011026", "NASDAQ")
# indexGroup = IndexGroup("JP9010C00002", "Nikkei")
# indexGroup = IndexGroup("HK0000004322", "Hang-Seng")
# indexGroup = IndexGroup("XC0009695252", "S&P-TSX-Composite")
# indexGroup = IndexGroup("NL0000000107", "AEX")
# indexGroup = IndexGroup("NO0000000021", "OBX")
# indexGroup = IndexGroup("AT0000999677", "PTX")
# indexGroup = IndexGroup("SE0000337842", "OMXS-30")
# indexGroup = IndexGroup("ES0SI0000005", "IBEX-35")


# date = datetime.strptime("06.11.2018", "%d.%m.%Y")
date = datetime.now()
index_storage = IndexStorage("dump", indexGroup, source="onvista", date=date)

downloader.dump_index(indexGroup, index_storage)

scraper.read_stocks(indexGroup, index_storage)
scraper.scrap_index(indexGroup, index_storage)

RatingEntity = namedtuple('RatingEntity', 'stock, rating')

rating_entities = []

for stock in indexGroup.stocks:
    stock_storage = StockStorage(index_storage, stock)

    try:
        stock_storage.load()
    except FileNotFoundError:
        print("could not load stock date for " + stock.name)
        continue

    stock = stock_storage.stock

    rating = Rating(stock)
    result = rating.rate()

    rating_entities.append(RatingEntity(stock, rating))

    write_stock_report(stock, stock_storage, rating)

write_index_report(indexGroup, index_storage, rating_entities)

