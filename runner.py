from libs.HtmlReport import write_stock_report
from libs.downloader import OnVistaDownloader as downloader
from libs.scraper import OnVistaScraper as scraper
from libs.model import IndexGroup
from libs.Rating import Rating
from libs.storage import IndexStorage, StockStorage

task_download_index = True
task_download = True
task_scrap = True
print_full = True
skip_underrated = False

indexGroup = IndexGroup("DE0008469008", "DAX")
# indexGroup = IndexGroup("DE0008467416", "MDAX")
# indexGroup = IndexGroup("DE0007203275", "TecDAX")
# indexGroup = IndexGroup("DE0009653386", "SDAX")
#indexGroup = IndexGroup("EU0009658145", "EURO-STOXX-50")
# indexGroup = IndexGroup("AT0000999982", "ATX")
# indexGroup = IndexGroup("CH0009980894", "SMI")
# indexGroup = IndexGroup("US2605661048", "Dow-Jones")
# indexGroup = IndexGroup("US6311011026", "NASDAQ")

index_storage = IndexStorage("dump", indexGroup, source="onvista")

if task_download_index:
    downloader.dump_index(indexGroup, index_storage)

# scraper.read_stocks(indexGroup, index_storage)
indexGroup.add_stock("DE0007664039", "Volkswagen-VZ", "Kraftfahrzeuge")

if task_scrap:
    scraper.scrap_index(indexGroup, index_storage)

for stock in indexGroup.stocks:
    stock_storage = StockStorage(index_storage, stock)

    if task_download:
        downloader.dump_stock(stock, stock_storage)

    if task_scrap:
        stock = scraper.scrap(stock, stock_storage)
        stock_storage.store()
        # stock_storage.compress()

    if task_scrap:
        rating = Rating(stock)
        result = rating.rate()

        write_stock_report(stock, stock_storage, rating)

        if rating.is_small:
            stock_type = "S"
        elif rating.is_medium:
            stock_type = "M"
        else:
            stock_type = "L"

        if rating.is_finance:
            stock_type += ", F"

        buy_signal = rating.buy_signal

        if print_full:
            print("- Kennzahlen")
            stock.print_report()
            print(f"Datenqualität: {rating.rate_quality() * 100:0.0f}%")
            print("- Einzelbewertung")
            rating.print_overview()

            rating.is_small

        print("Bewertung: %s %s (%s)\t[%i]\t%s" % (stock.stock_id, stock.name, stock_type, result, buy_signal))
        if print_full:
            print("---")
