"""
Testes unitários para o controlador CLI e gerenciamento de histórico.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.cli import KoredCLI


class TestKoredCLI(unittest.TestCase):

    def setUp(self):
        self.cli = KoredCLI(model="qwen2.5:7b")

    def test_initial_conversation_history(self):
        self.assertEqual(len(self.cli.conversation_history), 1)
        self.assertEqual(self.cli.conversation_history[0]["role"], "system")
        self.assertIn("kored", self.cli.conversation_history[0]["content"])

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

    @patch("src.ollama_client.OllamaClient.stream_chat")
    @patch("src.diagnostics.DiagnosticEngine.run_health_check")
    def test_run_diagnostics(self, mock_health, mock_stream):
        from src.diagnostics import DiagnosticReport
        from src.probes import ProbeResult

        mock_health.return_value = DiagnosticReport(
            target="Saude Geral",
            results=[ProbeResult("Memoria", "free", True, "ok")],
        )
        mock_stream.return_value = iter(["Analise: ", "sistema estavel."])

        self.cli.run_diagnostics()
        self.assertIn("RELATORIO DE EVIDENCIAS", self.cli.conversation_history[-2]["content"])
        self.assertEqual(self.cli.conversation_history[-1]["content"], "Analise: sistema estavel.")

    def test_mode_toggle(self):
        from src.executor import ExecutionMode
        self.assertEqual(self.cli.mode, ExecutionMode.READONLY)
        self.cli.set_mode(ExecutionMode.ASSISTED)
        self.assertEqual(self.cli.mode, ExecutionMode.ASSISTED)
        self.assertIn("MODO ASSISTIDO", self.cli.system_prompt)


if __name__ == "__main__":
    unittest.main()
