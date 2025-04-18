import unittest
import math
import time
from calc_1 import Calculator, ParserError, EvaluationError

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
        self.calc_deg = Calculator()

    def test_basic_arithmetic(self):
        self.assertAlmostEqual(self.calc.calculate("2+3"), 5)
        self.assertAlmostEqual(self.calc.calculate("5-2"), 3)
        self.assertAlmostEqual(self.calc.calculate("3*4"), 12)
        self.assertAlmostEqual(self.calc.calculate("10/2"), 5)
        self.assertAlmostEqual(self.calc.calculate("2^3"), 8)
        self.assertAlmostEqual(self.calc.calculate("2+3*4"), 14)
        self.assertAlmostEqual(self.calc.calculate("(2+3)*4"), 20)
        self.assertAlmostEqual(self.calc.calculate("2*-3"), -6)
        self.assertAlmostEqual(self.calc.calculate("8^(1/3)"), 2)

    def test_floats_and_scientific(self):
        self.assertAlmostEqual(self.calc.calculate("3.14"), 3.14)
        self.assertAlmostEqual(self.calc.calculate("1e5"), 1e5)
        self.assertAlmostEqual(self.calc.calculate("1.25e+09"), 1.25e+09)
        self.assertAlmostEqual(self.calc.calculate("-5"), -5)


    def test_errors(self):
        with self.assertRaises(EvaluationError):
            self.calc.calculate("1/0")
        with self.assertRaises(ParserError):
            self.calc.calculate("2/")
        with self.assertRaises(ParserError):
            self.calc.calculate("1 + (2 * 3")


class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def test_long_expression(self):

        start = time.time()
        result = self.calc.calculate("1" + "+1" * 1023)  
        end = time.time()
        self.assertEqual(result, 1024)
        self.assertLess(end - start, 0.2)

    


if __name__ == '__main__':
    unittest.main()
