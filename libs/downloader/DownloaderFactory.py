from libs.downloader import OnVistaDownloader

downloader = {
    "onvista": OnVistaDownloader
}


def create(source: str):
    return downloader.get(source)
