from downloader import BoerseOnlineDownloader as downloader
from model.Stock import Stock

stocks = [
    Stock("747206", "wirecard"),
    Stock("519000", "bmw"),
    Stock("865985", "apple"),
    Stock("870747", "microsoft")
]

for stock in stocks:
    downloader.dump_stock(stock.stock_id, stock.name)


