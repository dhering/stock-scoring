from libs.scraper import OnVistaScraper

downloader = {
    "onvista": OnVistaScraper
}


def create(source: str):
    return downloader.get(source)
