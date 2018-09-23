import os
import requests

def getPath(filename):
    return filename

def write_file_from_response(res, filename):
    path = getPath(filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(res.content)

def download(url, filename):
    r = requests.get(url, allow_redirects=True)
    print("download into " + filename + ": " + r.url)

    write_file_from_response(r, filename)