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

# indexGroup = IndexGroup("DE0008469008", "DAX")
# indexGroup = IndexGroup("DE0008467416", "MDAX")
# indexGroup = IndexGroup("DE0007203275", "TecDAX")
# indexGroup = IndexGroup("DE0009653386", "SDAX")
# indexGroup = IndexGroup("EU0009658145", "EURO-STOXX-50")
# indexGroup = IndexGroup("AT0000999982", "ATX")
# indexGroup = IndexGroup("CH0009980894", "SMI")
indexGroup = IndexGroup("US2605661048", "Dow-Jones")
# indexGroup = IndexGroup("US6311011026", "NASDAQ")

index_storage = IndexStorage("dump", indexGroup, source="onvista")

downloader.dump_index(indexGroup, index_storage)

scraper.read_stocks(indexGroup, index_storage)
scraper.scrap_index(indexGroup, index_storage)


def thread_body(queue: Queue):
    while True:
        payload = queue.get()
        stock = payload[0]
        stock_storage = payload[1]

        print("download %s" % stock.name)

        stock_storage.uncompress()

        downloader.dump_stock(stock, stock_storage)

        scraper.scrap(stock, stock_storage)
        stock_storage.store()
        stock_storage.compress()

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
