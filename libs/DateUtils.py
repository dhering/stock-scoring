from datetime import datetime, date


def toRevertStr(date: datetime) -> str:
    return "{:04d}-{:02d}-{:02d}".format(date.year, date.month, date.day)


def toRevertMonthStr(date: datetime) -> str:
    return "{:04d}-{:02d}".format(date.year, date.month)


def sameDay(d1: datetime, d2: datetime):
    return d1.day == d2.day and d1.month == d2.month and d1.year == d2.year
