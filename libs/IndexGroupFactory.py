import csv
import os

from libs.model import IndexGroup


def createFor(source: str, indexName: str, confFile: str = "indexGroup-by-provider.csv") -> IndexGroup:
    if not os.path.isfile(confFile):
        raise ValueError(f"Config file %s not found" % confFile)

    with open(confFile, mode="r", encoding="utf-8") as f:
        indexConfig = csv.DictReader(f)

        for index in indexConfig:
            if index["name"] == indexName and source in index and index[source] is not None  and index[source] != "":
                isin = index["isin"]
                sourceId = index[source]
                return IndexGroup(isin, indexName, sourceId, source)

    raise ValueError(f"Unable to find configuration for index %s from source %s" % (indexName, source))