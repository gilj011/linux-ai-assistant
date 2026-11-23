"""
Testes unitarios para o modulo de configuracao persistente (KoredConfig).
"""

from pathlib import Path
import tempfile
import unittest

from src.config import KoredConfig


class TestKoredConfig(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "test_config.yaml"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_values(self):
        cfg = KoredConfig()
        self.assertEqual(cfg.model, "qwen2.5:7b")
        self.assertEqual(cfg.ollama_host, "http://localhost:11434")
        self.assertEqual(cfg.default_mode, "readonly")
        self.assertEqual(cfg.timeout, 180)
        self.assertTrue(cfg.clear_on_start)
        self.assertEqual(cfg.history_limit, 20)

    def test_save_and_load(self):
        cfg = KoredConfig(
            model="qwen2.5:3b",
            ollama_host="http://192.168.1.100:11434",
            default_mode="assisted",
            timeout=120,
            clear_on_start=False,
            history_limit=30,
        )
        self.assertTrue(cfg.save(self.config_path))
        self.assertTrue(self.config_path.exists())

        loaded = KoredConfig.load(self.config_path)
        self.assertEqual(loaded.model, "qwen2.5:3b")
        self.assertEqual(loaded.ollama_host, "http://192.168.1.100:11434")
        self.assertEqual(loaded.default_mode, "assisted")
        self.assertEqual(loaded.timeout, 120)
        self.assertFalse(loaded.clear_on_start)
        self.assertEqual(loaded.history_limit, 30)

    def test_load_non_existent_creates_default(self):
        self.assertFalse(self.config_path.exists())
        loaded = KoredConfig.load(self.config_path)
        self.assertTrue(self.config_path.exists())
        self.assertEqual(loaded.model, "qwen2.5:7b")

    def test_load_corrupted_file_returns_defaults(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("invalid: [yaml: broken")

        loaded = KoredConfig.load(self.config_path)
        self.assertEqual(loaded.model, "qwen2.5:7b")
        self.assertEqual(loaded.default_mode, "readonly")

    def test_to_dict(self):
        cfg = KoredConfig()
        d = cfg.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("model", d)
        self.assertIn("clear_on_start", d)


if __name__ == "__main__":
    unittest.main()
