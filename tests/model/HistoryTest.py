import unittest

from model.Model import History


class MyTestCase(unittest.TestCase):
    def test_6_month_performance_calculation(self):

        #given:
        history = History(105, 100, 100)

        #when:
        performance = history.performance_6_month()

        #then:
        self.assertEqual(0.05, performance, "performance of 5%")


if __name__ == '__main__':
    unittest.main()
