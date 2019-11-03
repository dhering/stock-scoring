import unittest

from libs import IndexGroupFactory

CONF_FILE = "resources/test-indexGroup-by-provider.csv"


class IndexGroupFactoryCase(unittest.TestCase):

    def test_unknown_file(self):
        with self.assertRaises(ValueError):
            IndexGroupFactory.createFor("a", "b", "unknown.csv")

    def test_valid_onvista(self):
        # when:
        indexGroup = IndexGroupFactory.createFor("onvista", "S&P 500", CONF_FILE)

        # then:
        self.assertEqual("US78378X1072", indexGroup.isin)
        self.assertEqual("S&P 500", indexGroup.name)
        self.assertEqual("S-P-500", indexGroup.sourceId)

    def test_valid_finanzennet(self):
        # when:
        indexGroup = IndexGroupFactory.createFor("finanzen.net", "S&P 500", CONF_FILE)

        # then:
        self.assertEqual("US78378X1072", indexGroup.isin)
        self.assertEqual("S&P 500", indexGroup.name)
        self.assertEqual("s&p_500", indexGroup.sourceId)

    def test_missing_source_id(self):
        with self.assertRaises(ValueError):
            IndexGroupFactory.createFor("finanzen.net", "MDAX", CONF_FILE)

    def test_unknown_index(self):
        with self.assertRaises(ValueError):
            IndexGroupFactory.createFor("finanzen.net", "FOO", CONF_FILE)
