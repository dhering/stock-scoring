from lib.downloader import OnVistaDownloader as downloader
from lib.scraper import OnVistaScraper as scraper
from lib.model.Model import IndexGroup

task_download_index = False
task_download = False
task_scrap = True

indexGroup = IndexGroup("20735", "DAX")
indexGroup.add_stock("DE0007472060", "wirecard")

if task_download_index:
    downloader.dump_index(indexGroup)

if (task_scrap):
    scraper.scrap_index(indexGroup)

for stock in indexGroup.stocks:
    if (task_download):
        downloader.dump_stock(stock)

    if (task_scrap):
        scraper.scrap(stock)