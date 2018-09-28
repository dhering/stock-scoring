from datetime import datetime

def get_last_year():
    return str(datetime.now().year - 1)


def get_current_year():
    return str(datetime.now().year) + "e"


def get_next_year():
    return str(datetime.now().year + 1) + "e"


def get_last_cross_year():
    return str(datetime.now().year - 2)[2:] + "/" + str(datetime.now().year - 1)[2:]


def get_current_cross_year():
    return str(datetime.now().year - 1)[2:] + "/" + str(datetime.now().year)[2:] + "e"


def get_next_cross_year():
    return str(datetime.now().year)[2:] + "/" + str(datetime.now().year + 1)[2:] + "e"
