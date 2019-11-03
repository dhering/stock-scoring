from collections import namedtuple
from datetime import datetime

from libs import IndexGroupFactory
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

downloader.dump_index(indexGroup, index_storage)

scraper.read_stocks(indexGroup, index_storage)

# indexGroup.add_stock("DE0006069008", "FROSTA-AG", "")

'''
indexGroup.add_stock("JP3125800007", "ARIAKE-JAPAN", "")
indexGroup.add_stock("AU000000BAL8", "BELLAMYS-AUSTRALIA-LIMITED", "")
indexGroup.add_stock("AU000000BKL7", "BLACKMORES", "")
indexGroup.add_stock("US12545M2070", "CHRISTIAN-HANSEN-HOLDING", "")
indexGroup.add_stock("US2423702032", "DEAN-FOODS-CO", "")
indexGroup.add_stock("US4052171000", "HAIN-CELESTIAL", "")
indexGroup.add_stock("US61174X1090", "MONSTER-BEVERAGE-CORP", "")
indexGroup.add_stock("US63888U1088", "NATURAL-GROCERS-BY-VITAMIN-COTTAGE-INC", "")
indexGroup.add_stock("US85208M1027", "SPROUTS-FARMERS-MARKET", "")
indexGroup.add_stock("CA8676EP1086", "SUNOPTA", "")
indexGroup.add_stock("US9111631035", "UNITED-NATURAL-FOODS", "")
indexGroup.add_stock("NL0000395317", "KONINKLIJKE-WESSANEN-N-V", "")
indexGroup.add_stock("SE0000470395", "BIOGAIA", "")
indexGroup.add_stock("US8000131040", "SANDERSON-FARMS", "")
'''

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

