import os
import sys
import tempfile
import unittest

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_DIR)

from services.ret_processing import parse_ret_txt_files, buscar_no_banco  # noqa: E402
from services.db import save_data_to_json  # noqa: E402


class TestRetProcessing(unittest.TestCase):
    def test_parse_ret_txt_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Cria dois .txt com linhas formatadas
            p1 = os.path.join(tmpdir, "a.txt")
            p2 = os.path.join(tmpdir, "b.txt")
            with open(p1, "w", encoding="latin-1") as f:
                f.write("header1\nheader2\nJOAO SILVA\nXX\nMARIA JOSE\nYY\nfooter1\nfooter2\n")
            with open(p2, "w", encoding="latin-1") as f:
                f.write("header1\nheader2\nJOSE ALMEIDA\nXX\nfooter1\nfooter2\n")

            nomes, total, por_arq = parse_ret_txt_files(tmpdir)
            self.assertTrue({"JOAO SILVA", "MARIA JOSE", "JOSE ALMEIDA"}.issubset(set(nomes)))
            self.assertEqual(total, por_arq["a.txt"] + por_arq["b.txt"])

    def test_buscar_no_banco(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            banco_path = os.path.join(tmpdir, "db.json")
            banco = {
                "arquivo1.pdf": {
                    "JOAO SILVA": {"cpf": "123.456.789-10", "valor": 100.0},
                    "MARIA JOSE": {"cpf": "111.222.333-44", "valor": 200.0},
                }
            }
            save_data_to_json(banco, banco_path)
            nomes = ["JOAO SILVA", "MARIA", "DESCONHECIDO"]
            results, total_val, por_arquivo = buscar_no_banco(nomes, banco_path, incluir_valores=True)
            # Deve somar 100 (JOAO) + 200 (para MARIA via parcial) = 300
            self.assertAlmostEqual(total_val, 300.0)
            # Deve conter registros para "Não Encontrado" também
            self.assertIn("Não Encontrado", por_arquivo)


if __name__ == "__main__":
    unittest.main()
