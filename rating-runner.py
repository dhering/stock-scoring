from collections import namedtuple
from datetime import datetime

from libs import IndexGroupFactory
from libs.HtmlReport import write_stock_report, write_index_report
from libs.Rating import Rating
from libs.downloader import DownloaderFactory
from libs.scraper import ScraperFactory
from libs.storage import IndexStorage, StockStorage

task_download_index = True
task_download = True
task_scrap = True
print_full = True
skip_underrated = True


SOURCE = "onvista"

indexGroup = IndexGroupFactory.createFor(SOURCE, "DAX")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "MDAX")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "TecDAX")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "SDAX")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "Stoxx Europe 50")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "Stoxx Europe 600")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "ATX")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "SMI")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "Dow-Jones")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "NASDAQ")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "S&P 500")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "Nikkei")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "Hang-Seng")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "S&P-TSX-Composite")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "AEX")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "OBX")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "PTX")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "RTS")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "OMXS-30")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "IBEX-35")
# indexGroup = IndexGroupFactory.createFor(SOURCE, "SOLACTIVE-ORGANIC-FOOD")



# date = datetime.strptime("03.03.2019", "%d.%m.%Y")
date = datetime.now()
index_storage = IndexStorage("dump", indexGroup, date=date)

downloader = DownloaderFactory.create(SOURCE)
downloader.dump_index(indexGroup, index_storage)

scraper = ScraperFactory.create(SOURCE)
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

