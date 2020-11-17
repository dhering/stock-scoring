from datetime import datetime

from libs.Rating import Rating
from libs.model import Stock, IndexGroup
from libs.storage import StockStorage, IndexStorage
from mako.template import Template


def find_stock_next_to(ref_stock: Stock, all_stocks):

    before_ref = True

    stock_before = None
    stock_after = None

    for stock in all_stocks:

        if stock.stock_id == ref_stock.stock_id:
            before_ref = False
        elif before_ref:
            stock_before = stock
        else:
            stock_after = stock
            break

    return stock_before, stock_after


def write_stock_report(stock: Stock, stock_storage: StockStorage, rating: Rating):
    template = Template(filename="libs/templates/stock-rating.html")

    stock_before, stock_after = find_stock_next_to(stock, stock.indexGroup.stocks)

    report = template.render(stock=stock, rating=rating, source=stock_storage.indexStorage.source,
                             report_date=stock_storage.indexStorage.date_str, stock_before=stock_before,
                             stock_after=stock_after)

    with open(stock_storage.getStoragePath("", "html"), "w", encoding="utf-8") as f:
        f.write(report)


def write_index_report(index_group: IndexGroup, index_storage: IndexStorage, rating_entities: []):
    template = Template(filename="libs/templates/index-rating-overview.html")

    report = template.render(index_group=index_group, rating_entities=rating_entities, source=index_storage.source,
                             report_date=index_storage.date_str)

    with open(index_storage.getStoragePath("", "html"), "w", encoding="utf-8") as f:
        f.write(report)
