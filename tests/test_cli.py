"""
Testes unitários para o controlador CLI e gerenciamento de histórico.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.cli import LinuxAssistantCLI


class TestLinuxAssistantCLI(unittest.TestCase):

    def setUp(self):
        self.cli = LinuxAssistantCLI(model="qwen2.5:7b")

    def test_initial_conversation_history(self):
        self.assertEqual(len(self.cli.conversation_history), 1)
        self.assertEqual(self.cli.conversation_history[0]["role"], "system")
        self.assertIn("Linux AI Assistant", self.cli.conversation_history[0]["content"])

    def test_reset_conversation(self):
        self.cli.conversation_history.append({"role": "user", "content": "olá"})
        self.cli.conversation_history.append({"role": "assistant", "content": "olá!"})
        self.assertEqual(len(self.cli.conversation_history), 3)

        self.cli.reset_conversation()
        self.assertEqual(len(self.cli.conversation_history), 1)
        self.assertEqual(self.cli.conversation_history[0]["role"], "system")

    def test_trim_history_if_needed(self):
        # Enche o histórico além do limite
        for i in range(25):
            self.cli.conversation_history.append({"role": "user", "content": f"msg {i}"})

        self.cli._trim_history_if_needed()
        # Deve manter a mensagem de sistema + 14 mensagens recentes = 15
        self.assertEqual(len(self.cli.conversation_history), 15)
        self.assertEqual(self.cli.conversation_history[0]["role"], "system")
        self.assertEqual(self.cli.conversation_history[-1]["content"], "msg 24")

    @patch("src.ollama_client.OllamaClient.stream_chat")
    def test_ask_streaming_stores_assistant_response(self, mock_stream):
        mock_stream.return_value = iter(["Para apagar logs, ", "use truncate..."])

        self.cli.ask_streaming("como apagar logs do docker?")

        # Histórico deve ter: system, user, assistant
        self.assertEqual(len(self.cli.conversation_history), 3)
        self.assertEqual(self.cli.conversation_history[1]["role"], "user")
        self.assertEqual(self.cli.conversation_history[1]["content"], "como apagar logs do docker?")
        self.assertEqual(self.cli.conversation_history[2]["role"], "assistant")
        self.assertEqual(self.cli.conversation_history[2]["content"], "Para apagar logs, use truncate...")


if __name__ == "__main__":
    unittest.main()
