from libs.downloader import OnVistaDownloader as downloader
from libs.scraper import OnVistaScraper as scraper
from libs.model import IndexGroup
from libs.Rating import Rating

task_download_index = False
task_download = True
task_scrap = True
print_full = False

indexGroup = IndexGroup("20735", "DAX")
indexGroup.add_stock("DE000A1EWWW0", "Adidas")
indexGroup.add_stock("DE0008404005", "Allianz")
indexGroup.add_stock("DE000BASF111", "BASF")
indexGroup.add_stock("DE0005190003", "BMW")
indexGroup.add_stock("DE000BAY0017", "Bayer")
indexGroup.add_stock("DE0005200000", "Beiersdorf")
indexGroup.add_stock("DE0005439004", "Continental")
indexGroup.add_stock("DE0006062144", "COVESTRO-AG")
indexGroup.add_stock("DE0007100000", "Daimler")
indexGroup.add_stock("DE0005140008", "Deutsche-Bank")
indexGroup.add_stock("DE0005810055", "Deutsche-Boerse")
indexGroup.add_stock("DE0005552004", "Deutsche-Post")
indexGroup.add_stock("DE0005557508", "Deutsche-Telekom")
indexGroup.add_stock("DE000ENAG999", "EON")
indexGroup.add_stock("DE0005785802", "Fresenius-Medical-Care")
indexGroup.add_stock("DE0005785604", "Fresenius")
indexGroup.add_stock("DE0006047004", "HeidelbergCement")
indexGroup.add_stock("DE0006048432", "Henkel")
indexGroup.add_stock("DE0006231004", "Infineon")
indexGroup.add_stock("DE000A2E4L75", "LINDE-AG")
indexGroup.add_stock("DE0006599905", "Merck")
indexGroup.add_stock("DE0008430026", "Muenchener-Rueck")
indexGroup.add_stock("DE0007037129", "RWE")
indexGroup.add_stock("DE0007164600", "SAP")
indexGroup.add_stock("DE0007236101", "Siemens")
indexGroup.add_stock("DE0007500001", "ThyssenKrupp")
indexGroup.add_stock("DE0007664039", "Volkswagen-VZ")
indexGroup.add_stock("DE000A1ML7J1", "Vonovia")
indexGroup.add_stock("DE0007472060", "Wirecard")

if task_download_index:
    downloader.dump_index(indexGroup)

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
