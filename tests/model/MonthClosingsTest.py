import unittest

from libs.model import MonthClosings


class MyTestCase(unittest.TestCase):

    def test_closing_performance(self):

        #given:
        closings = MonthClosings()
        closings.closings = [100, 100, 105]

        #when:
        performance = closings.calculate_performance()

        #then:
        self.assertEqual(2, len(performance))
        self.assertEqual(0, performance[0])
        self.assertEqual(0.05, performance[1])


if __name__ == '__main__':
    unittest.main()
