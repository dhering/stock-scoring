from libs.scraper import OnVistaScraper, FinanzenNetScraper

scrapperOptions = {
    "onvista": OnVistaScraper,
    "finanzen.net": FinanzenNetScraper
}


def create(source: str):
    return scrapperOptions.get(source)
