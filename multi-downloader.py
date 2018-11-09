from datetime import datetime
from queue import Queue
from threading import Thread

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
# indexGroup = IndexGroup("RU000A0JPEB3", "RTS")
# indexGroup = IndexGroup("SE0000337842", "OMXS-30")
# indexGroup = IndexGroup("ES0SI0000005", "IBEX-35")

# date = datetime.strptime("06.11.2018", "%d.%m.%Y")
date = datetime.now()
index_storage = IndexStorage("dump", indexGroup, source="onvista", date=date)

downloader.dump_index(indexGroup, index_storage)

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


workers = 8
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
