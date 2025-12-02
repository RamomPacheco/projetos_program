import os
import sys
import tempfile
import unittest

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_DIR)

from services.merge import merge_pdfs  # noqa: E402

# Para criar PDFs de teste sem dependências extras, usamos PyPDF2 para gerar páginas em branco.
from PyPDF2 import PdfWriter  # noqa: E402


def _create_blank_pdf(path: str, pages: int = 1) -> None:
    writer = PdfWriter()
    # PdfWriter não cria páginas em branco diretamente, mas podemos anexar um PDF vazio de memória.
    # Alternativa simples: adicionar páginas vazias com dimensões padrão.
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)  # A4 em pontos
    with open(path, "wb") as f:
        writer.write(f)


class TestMergeService(unittest.TestCase):
    def test_merge_pdfs(self):
        with tempfile.TemporaryDirectory() as tmp:
            f1 = os.path.join(tmp, "a.pdf")
            f2 = os.path.join(tmp, "b.pdf")
            out = os.path.join(tmp, "out", "merged.pdf")
            _create_blank_pdf(f1, pages=2)
            _create_blank_pdf(f2, pages=3)

            merge_pdfs([f1, f2], out)
            self.assertTrue(os.path.exists(out))
            # Verifica número de páginas resultante
            from PyPDF2 import PdfReader
            r = PdfReader(out)
            self.assertEqual(len(r.pages), 5)

    def test_merge_pdfs_sem_arquivos(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "merged.pdf")
            with self.assertRaises(ValueError):
                merge_pdfs([], out)


if __name__ == "__main__":
    unittest.main()
