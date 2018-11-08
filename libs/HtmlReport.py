from datetime import datetime

from libs.Rating import Rating
from libs.model import Stock, IndexGroup
from libs.storage import StockStorage, IndexStorage
from mako.template import Template


def write_stock_report(stock: Stock, stock_storage: StockStorage, rating: Rating):
    template = Template(filename="libs/templates/stock-rating.html")

    report = template.render(stock=stock, rating=rating, source=stock_storage.indexStorage.source, report_date=stock_storage.indexStorage.date_str)

    with open(stock_storage.getStoragePath("", "html"), "w", encoding="utf-8") as f:
        f.write(report)
