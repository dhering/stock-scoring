from downloader import OnVistaDownloader as downloader
from scraper import OnVistaScraper as scraper
from model.Stock import Stock, LargCap
from model.Definition import IndexGroup

task_download_index = False
task_download = False
task_scrap = True

stocks = [
    Stock("747206", "wirecard"),
    Stock("519000", "bmw"),
    Stock("865985", "apple"),
    Stock("870747", "microsoft")
]

stocks = [
    LargCap("DE0007472060", "wirecard")
]

indexGroup = IndexGroup("20735", "DAX", stocks)

if task_download_index:
    downloader.dump_index(indexGroup.index, indexGroup.name)

for stock in indexGroup.stocks:
    if (task_download):
        downloader.dump_stock(stock.stock_id, stock.name)

    if (task_scrap):
        scraper.scrap(stock.stock_id, stock.name)