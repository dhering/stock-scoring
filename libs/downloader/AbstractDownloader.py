import requests
import time


def download(url: str, filename: str, storage_repository, checkFile: bool = True, retry: bool = False, sleep: int = 0,
             maxSleep: int = 64):
    if checkFile and storage_repository.has_content(filename):
        print("file still exists: " + filename)
    else:

        if sleep > 0:
            time.sleep(sleep)

        r = requests.get(url, allow_redirects=True)
        print("download into " + filename + ": " + r.url)

        storage_repository.store(filename, r.content)

        if retry and not storage_repository.has_content(filename):

            retryTime = sleep * 2 if sleep > 0 else 1

            if retryTime <= maxSleep:
                print(f"download has been blocked, retry in %is: %s: %s" % (retryTime, filename, r.url))
                download(url, filename, storage_repository, checkFile=False, retry=retry, sleep=retryTime,
                         maxSleep=maxSleep)
            else:
                print(f"ERROR: unable to download after retries %s: %s" % (filename, r.url))


def downloadByPost(url: str, data: dict, filename: str, storage_repository, checkFile: bool = True, retry: bool = False,
                   sleep: int = 0, maxSleep: int = 64):
    if checkFile and storage_repository.has_content(filename):
        print("file still exists: " + filename)
    else:

        if sleep > 0:
            time.sleep(sleep)

        r = requests.post(url, data, allow_redirects=True)
        print("download POST into " + filename + ": " + r.url)

        storage_repository.store(filename, r.content)

        if retry and not storage_repository.has_content(filename):

            retryTime = sleep * 2 if sleep > 0 else 1

            if retryTime <= maxSleep:
                print(f"download has been blocked, retry in %is: %s: %s" % (retryTime, filename, r.url))
                downloadByPost(url, data, filename, storage_repository, checkFile=False, retry=retry, sleep=retryTime,
                               maxSleep=maxSleep)
            else:
                print(f"ERROR: unable to download after retries %s: %s" % (filename, r.url))
