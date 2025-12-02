import os
import sys
import unittest
from unittest.mock import patch, MagicMock

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_DIR)

from services.pdf_extraction import extract_data  # noqa: E402


class TestPdfExtraction(unittest.TestCase):
    @patch("services.pdf_extraction.PdfReader")
    def test_extract_data(self, mock_reader_cls):
        # Configura mock do PdfReader
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = " - JOAO SILVA     123.456.789-10 ... 1.234,56\n - MARIA  111.222.333-44 ... 2.000,00"
        mock_reader.pages = [mock_page]
        mock_reader_cls.return_value = mock_reader

        data = extract_data("fake.pdf")
        self.assertIn("JOAO SILVA", data)
        self.assertIn("MARIA", data)
        self.assertEqual(data["JOAO SILVA"]["cpf"], "123.456.789-10")
        self.assertAlmostEqual(data["JOAO SILVA"]["valor"], 1234.56)
        self.assertAlmostEqual(data["MARIA"]["valor"], 2000.00)


if __name__ == "__main__":
    unittest.main()
