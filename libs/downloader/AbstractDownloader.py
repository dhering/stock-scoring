import os
import requests
from requests import Response
import time


def getPath(filename):
    return filename


def write_file_from_response(res: Response, filename: str):
    path = getPath(filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(res.content)


def download(url: str, filename: str, checkFile: bool = True, retry: bool = False, sleep: int = 0, maxSleep: int = 64):
    if checkFile and os.path.isfile(filename) and os.path.getsize(filename) > 0:
        print("file still exists: " + filename)
    else:

        if sleep > 0:
            time.sleep(sleep)

        r = requests.get(url, allow_redirects=True)
        print("download into " + filename + ": " + r.url)

        write_file_from_response(r, filename)

        if retry and os.path.getsize(filename) == 0:

            retryTime = sleep * 2 if sleep > 0 else 1

            if retryTime <= maxSleep:
                print(f"download has been blocked, retry in %is: %s: %s" % (retryTime, filename, r.url))
                download(url, filename, checkFile=False, retry=retry, sleep=retryTime, maxSleep=maxSleep)
            else:
                print(f"ERROR: unable to download after retries %s: %s" % (filename, r.url))


def downloadByPost(url: str, data: dict, filename: str, checkFile: bool = True, retry: bool = False, sleep: int = 0, maxSleep: int = 64):
    if checkFile and os.path.isfile(filename) and os.path.getsize(filename) > 0:
        print("file still exists: " + filename)
    else:

        if sleep > 0:
            time.sleep(sleep)

        r = requests.post(url, data, allow_redirects=True)
        print("download POST into " + filename + ": " + r.url)

        write_file_from_response(r, filename)

        if retry and os.path.getsize(filename) == 0:

            retryTime = sleep * 2 if sleep > 0 else 1

            if retryTime <= maxSleep:
                print(f"download has been blocked, retry in %is: %s: %s" % (retryTime, filename, r.url))
                download(url, filename, checkFile=False, retry=retry, sleep=retryTime, maxSleep=maxSleep)
            else:
                print(f"ERROR: unable to download after retries %s: %s" % (filename, r.url))