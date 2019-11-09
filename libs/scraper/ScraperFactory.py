from libs.scraper import OnVistaScraper, FinanzenNetScraper

downloader = {
    "onvista": OnVistaScraper,
    "finanzen.net": FinanzenNetScraper
}


def create(source: str):
    return downloader.get(source)
