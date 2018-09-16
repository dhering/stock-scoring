from downloader import OnVistaDownloader as downloader
from scraper import OnVistaScraper as scraper
from model.Stock import Stock

task_download = False
task_scrap = True

stocks = [
    Stock("747206", "wirecard"),
    Stock("519000", "bmw"),
    Stock("865985", "apple"),
    Stock("870747", "microsoft")
]

stocks = [
    Stock("DE0007472060", "wirecard")
]

for stock in stocks:
    if (task_download):
        downloader.dump_stock(stock.stock_id, stock.name)

    if (task_scrap):
        scraper.scrap(stock.stock_id, stock.name)