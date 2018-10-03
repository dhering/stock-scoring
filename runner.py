from libs.downloader import OnVistaDownloader as downloader
from libs.scraper import OnVistaScraper as scraper
from libs.model import IndexGroup
from libs.Rating import Rating

task_download_index = False
task_download = False
task_scrap = True
print_full = False

#indexGroup = IndexGroup("DE0008469008", "DAX")
#indexGroup = IndexGroup("DE0008467416", "MDAX")
#indexGroup = IndexGroup("DE0007203275", "TecDAX")
indexGroup = IndexGroup("DE0009653386", "SDAX")

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

        if rating.is_small:
            stock_type = "S"
        elif rating.is_medium:
            stock_type = "M"
        else:
            stock_type = "L"

        if rating.is_finance:
            stock_type += ", F"

        buy_signal = ""
        if (rating.is_small or rating.is_medium):
            if result == 7:
                buy_signal = "+"
            if result > 7:
                buy_signal = "++"
        else:
            if result == 4:
                buy_signal = "+"
            if result > 4:
                buy_signal = "++"



        print("Bewertung: %s (%s)\t[%i]\t%s" % (stock.name, stock_type, result, buy_signal))
