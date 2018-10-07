import os
import requests
from requests import Response


def getPath(filename):
    return filename


def write_file_from_response(res: Response, filename: str):
    path = getPath(filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(res.content)


def download(url: str, filename: str, checkFile: bool = True):

    if checkFile and os.path.isfile(filename):
        print("file still exists: " + filename)
    else:
        r = requests.get(url, allow_redirects=True)
        print("download into " + filename + ": " + r.url)

        write_file_from_response(r, filename)
