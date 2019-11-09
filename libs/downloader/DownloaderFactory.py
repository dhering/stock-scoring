from libs.downloader import OnVistaDownloader, FinanzenNetDownloader

downloader = {
    "onvista": OnVistaDownloader,
    "finanzen.net": FinanzenNetDownloader
}


def create(source: str):
    return downloader.get(source)
