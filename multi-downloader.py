from datetime import datetime
from queue import Queue
from threading import Thread

from libs import IndexGroupFactory
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
indexGroup = IndexGroupFactory.createFor(SOURCE, "MDAX")
indexGroup = IndexGroupFactory.createFor(SOURCE, "TecDAX")
indexGroup = IndexGroupFactory.createFor(SOURCE, "SDAX")
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


# date = datetime.strptime("01.11.2020", "%d.%m.%Y")
date = datetime.now()
index_storage = IndexStorage("dump", indexGroup, date=date)

downloader = DownloaderFactory.create(SOURCE)
downloader.dump_index(indexGroup, index_storage)

scraper = ScraperFactory.create(SOURCE)
scraper.read_stocks(indexGroup, index_storage)
scraper.scrap_index(indexGroup, index_storage)


def thread_body(queue: Queue):
    while True:
        payload = queue.get()

        stock = payload[0]
        stock_storage = payload[1]

        try:

            print("download %s" % stock.name)

            stock_storage.uncompress()

            downloader.dump_stock(stock, stock_storage)

            scraper.scrap(stock, stock_storage)
            stock_storage.store()
            stock_storage.compress()
        except:
            print(f"error while downloading {stock.name} - {stock.stock_id}")

        queue.task_done()


workers = 10
stock_queue = Queue()

for i in range(workers):
    worker = Thread(target=thread_body, args=(stock_queue,))
    worker.setDaemon(True)
    worker.start()

for stock in indexGroup.stocks:
    stock_storage = StockStorage(index_storage, stock)
    stock_queue.put((stock, stock_storage))

print('## Start downloading')
stock_queue.join()
print('## Finished downloading')
