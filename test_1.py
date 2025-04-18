import unittest
import math
import time
from calculator import Calculator, ParserError, EvaluationError

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
        self.calc_deg = Calculator(angle_unit='degree')

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

    def test_functions(self):
        self.assertAlmostEqual(self.calc.calculate("sin(0)"), 0)
        self.assertAlmostEqual(self.calc.calculate("cos(0)"), 1)
        self.assertAlmostEqual(self.calc.calculate("sqrt(4)"), 2)
        self.assertAlmostEqual(self.calc.calculate("ln(e)"), 1)
        self.assertAlmostEqual(self.calc.calculate("exp(0)"), 1)
        self.assertAlmostEqual(self.calc.calculate("sin(pi/2)"), 1)
        self.assertAlmostEqual(self.calc_deg.calculate("sin(90)"), 1)

    def test_constants(self):
        self.assertAlmostEqual(self.calc.calculate("pi"), math.pi)
        self.assertAlmostEqual(self.calc.calculate("e"), math.e)

    def test_errors(self):
        with self.assertRaises(EvaluationError):
            self.calc.calculate("1/0")
        with self.assertRaises(EvaluationError):
            self.calc.calculate("ln(-1)")
        with self.assertRaises(EvaluationError):
            self.calc.calculate("sqrt(-1)")
        with self.assertRaises(ParserError):
            self.calc.calculate("2/")
        with self.assertRaises(ParserError):
            self.calc.calculate("sin(")
        with self.assertRaises(ParserError):
            self.calc.calculate("1 + (2 * 3")

    def test_complex_expressions(self):
        self.assertAlmostEqual(self.calc.calculate("3.375e+09^(1/3)"), 1500)


class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def test_long_expression(self):

        start = time.time()
        result = self.calc.calculate("1" + "+1" * 1023)  
        end = time.time()
        self.assertEqual(result, 1024)
        self.assertLess(end - start, 0.2)
    
    def test_large_numbers(self):
        start = time.time()
        result = self.calc.calculate("1e300 + 1e30000")
        end = time.time()
        self.assertAlmostEqual(result, 1e300 + 1e30000)
        self.assertLess(end - start, 0.1)
    
    def test_power_large_exponent(self):
        start = time.time()
        result = self.calc.calculate("1 ^ 36893488147419103232")
        end = time.time()
        self.assertEqual(result, 1)
        self.assertLess(end - start, 0.1)

if __name__ == '__main__':
    unittest.main()
