import os
import sys
import unittest

# Ajusta o path para importar módulos do pacote 'ret'
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_DIR)

from utils.formatting import format_currency  # noqa: E402


class TestFormatting(unittest.TestCase):
    def test_format_currency(self):
        self.assertEqual(format_currency(0), "0,00")
        self.assertEqual(format_currency(1), "1,00")
        self.assertEqual(format_currency(12.3), "12,30")
        self.assertEqual(format_currency(1234.56), "1.234,56")
        self.assertEqual(format_currency(1234567.89), "1.234.567,89")


if __name__ == "__main__":
    unittest.main()
