import os
import sys
import tempfile
import unittest

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_DIR)

from utils.ret_file import alterar_extensao_para_txt  # noqa: E402


class TestRetFile(unittest.TestCase):
    def test_alterar_extensao_para_txt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ret_path = os.path.join(tmpdir, "exemplo.ret")
            with open(ret_path, "w", encoding="utf-8") as f:
                f.write("conteudo")
            txt_path = alterar_extensao_para_txt(ret_path)
            self.assertIsNotNone(txt_path)
            self.assertTrue(txt_path.endswith(".txt"))
            self.assertTrue(os.path.exists(txt_path))
            self.assertFalse(os.path.exists(ret_path))

    def test_alterar_extensao_para_txt_nao_ret(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "exemplo.outro")
            with open(path, "w", encoding="utf-8") as f:
                f.write("conteudo")
            result = alterar_extensao_para_txt(path)
            self.assertIsNone(result)
            self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
