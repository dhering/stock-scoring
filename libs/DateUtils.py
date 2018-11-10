from datetime import datetime, date


def toRevertStr(date: datetime) -> str:
    return "{:04d}-{:02d}-{:02d}".format(date.year, date.month, date.day)


def toRevertMonthStr(date: datetime) -> str:
    return "{:04d}-{:02d}".format(date.year, date.month)
