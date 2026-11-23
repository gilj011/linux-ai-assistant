"""
Testes unitarios para o controlador CLI, gerenciamento de historico e sessoes persistentes.
"""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.cli import KoredCLI
from src.config import KoredConfig
from src.session_manager import SessionManager


class TestKoredCLI(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sessions_dir = Path(self.temp_dir.name) / "sessions"
        self.config_file = Path(self.temp_dir.name) / "config.yaml"
        self.config = KoredConfig(clear_on_start=False)
        self.cli = KoredCLI(
            model="qwen2.5:7b",
            sessions_dir=self.sessions_dir,
            config=self.config,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_conversation_history(self):
        self.assertEqual(len(self.cli.conversation_history), 1)
        self.assertEqual(self.cli.conversation_history[0]["role"], "system")
        self.assertIn("kored", self.cli.conversation_history[0]["content"])
        self.assertIsNotNone(self.cli.current_session)

    def test_reset_conversation(self):
        self.cli.conversation_history.append({"role": "user", "content": "ola"})
        self.cli.conversation_history.append({"role": "assistant", "content": "ola!"})
        self.assertEqual(len(self.cli.conversation_history), 3)

        self.cli.reset_conversation()
        self.assertEqual(len(self.cli.conversation_history), 1)
        self.assertEqual(self.cli.conversation_history[0]["role"], "system")

    def test_trim_history_if_needed(self):
        # Enche o historico alem do limite configurado (20)
        for i in range(25):
            self.cli.conversation_history.append({"role": "user", "content": f"msg {i}"})

        self.cli._trim_history_if_needed()
        # Mantem o prompt de sistema + mensagens recentes dentro do limite
        self.assertTrue(len(self.cli.conversation_history) <= 20)
        self.assertEqual(self.cli.conversation_history[0]["role"], "system")

    @patch("src.ollama_client.OllamaClient.stream_chat")
    def test_ask_streaming_stores_assistant_response_and_persists_session(self, mock_stream):
        mock_stream.return_value = iter(["Para apagar logs, ", "use truncate..."])

        self.cli.ask_streaming("como apagar logs do docker?")

        # Historico deve ter: system, user, assistant
        self.assertEqual(len(self.cli.conversation_history), 3)
        self.assertEqual(self.cli.conversation_history[1]["role"], "user")
        self.assertEqual(self.cli.conversation_history[1]["content"], "como apagar logs do docker?")
        self.assertEqual(self.cli.conversation_history[2]["role"], "assistant")
        self.assertEqual(self.cli.conversation_history[2]["content"], "Para apagar logs, use truncate...")

        # Verifica se a sessao foi persistida no session_manager
        saved_session = self.cli.session_manager.load_session(self.cli.current_session.id)
        self.assertIsNotNone(saved_session)
        self.assertEqual(len(saved_session.messages), 3)
        self.assertEqual(saved_session.title, "como apagar logs do docker?")

    def test_resume_latest_session(self):
        # Cria uma sessao com pergunta
        self.cli.conversation_history.append({"role": "user", "content": "duvida sobre iptables"})
        self.cli.conversation_history.append({"role": "assistant", "content": "iptables gerencia pacotes..."})
        self.cli._sync_session()

        session_id = self.cli.current_session.id

        # Nova instancia de CLI com resume_latest=True
        cli_resumed = KoredCLI(
            sessions_dir=self.sessions_dir,
            config=self.config,
            resume_latest=True,
        )
        self.assertEqual(cli_resumed.current_session.id, session_id)
        self.assertEqual(len(cli_resumed.conversation_history), 3)
        self.assertEqual(cli_resumed.conversation_history[1]["content"], "duvida sobre iptables")

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

    @patch("src.cli.console.clear")
    @patch("src.cli.Prompt.ask")
    @patch("src.cli.KoredCLI.check_ollama_status")
    def test_run_interactive_clear_and_exit(self, mock_status, mock_prompt, mock_clear):
        mock_status.return_value = True
        mock_prompt.side_effect = ["limpar", "sair"]

        self.cli.config.clear_on_start = True
        self.cli.run_interactive()

        # console.clear deve ser chamado na inicializacao e ao receber 'limpar'
        self.assertEqual(mock_clear.call_count, 2)

    def test_show_config_and_sessions(self):
        # Nao deve lancar excecoes
        self.cli.show_config()
        self.cli.show_sessions()

    @patch("src.ollama_client.OllamaClient.stream_chat")
    def test_fix_command_with_explicit_command_and_error(self, mock_stream):
        mock_stream.return_value = iter(["Causa: a porta 80 ja esta ocupada. ", "Execute ss -tulpn para verificar."])

        self.cli.fix_command(
            command="docker run -p 80:80 nginx",
            error_output="Error response from daemon: driver failed: bind: address already in use",
        )

        self.assertEqual(len(self.cli.conversation_history), 3)
        self.assertIn("docker run -p 80:80 nginx", self.cli.conversation_history[1]["content"])
        self.assertIn("bind: address already in use", self.cli.conversation_history[1]["content"])
        self.assertIn("porta 80 ja esta ocupada", self.cli.conversation_history[2]["content"])

    @patch("src.shell_inspector.ShellInspector.get_last_command")
    def test_fix_command_not_found_handling(self, mock_last_cmd):
        mock_last_cmd.return_value = None
        # Nao deve levantar excecoes e nem adicionar mensagens
        self.cli.fix_command()
        self.assertEqual(len(self.cli.conversation_history), 1)


if __name__ == "__main__":
    unittest.main()
