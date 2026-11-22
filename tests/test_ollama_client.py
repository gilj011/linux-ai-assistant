"""
Testes unitários para o OllamaClient usando mocks de rede.
"""

import json
import unittest
from unittest.mock import MagicMock, patch
from src.ollama_client import OllamaClient


class TestOllamaClient(unittest.TestCase):

    def setUp(self):
        self.client = OllamaClient(base_url="http://localhost:11434", model="qwen2.5:7b")

    @patch("requests.get")
    def test_check_connection_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"version": "0.3.14"}
        mock_get.return_value = mock_resp

        ok, msg = self.client.check_connection()
        self.assertTrue(ok)
        self.assertIn("0.3.14", msg)

    @patch("requests.get")
    def test_list_installed_models(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [{"name": "qwen2.5:7b"}, {"name": "llama3.2:3b"}]
        }
        mock_get.return_value = mock_resp

        models = self.client.list_installed_models()
        self.assertEqual(models, ["qwen2.5:7b", "llama3.2:3b"])

    @patch("requests.post")
    def test_stream_generate(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = None

        chunks = [
            json.dumps({"response": "Olá! ", "done": False}).encode("utf-8"),
            json.dumps({"response": "Como posso ajudar?", "done": True}).encode("utf-8"),
        ]
        mock_resp.iter_lines.return_value = chunks
        mock_post.return_value = mock_resp

        output = list(self.client.stream_generate(prompt="Oi"))
        self.assertEqual("".join(output), "Olá! Como posso ajudar?")


if __name__ == "__main__":
    unittest.main()
