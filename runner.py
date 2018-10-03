from libs.downloader import OnVistaDownloader as downloader
from libs.scraper import OnVistaScraper as scraper
from libs.model import IndexGroup
from libs.Rating import Rating

task_download_index = False
task_download = False
task_scrap = False
print_full = False

indexGroup = IndexGroup("DE0008467416", "DAX")

if task_download_index:
    downloader.dump_index(indexGroup)

scraper.read_stocks(indexGroup)

if task_scrap:
    scraper.scrap_index(indexGroup)

for stock in indexGroup.stocks:
    if task_download:
        downloader.dump_stock(stock)

for stock in indexGroup.stocks:
    if task_scrap:
        stock = scraper.scrap(stock)

    if print_full:
        stock.print_report()

    if task_scrap:
        rating = Rating(stock)
        result = rating.rate()

        if print_full:
            rating.print_overview()

        print("Bewertung: %s  [%i]" % (stock.name, result))
