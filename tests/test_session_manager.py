"""
Testes unitarios para o gerenciador de sessoes persistentes (SessionManager).
"""

from pathlib import Path
import tempfile
import unittest

from src.session_manager import SessionData, SessionManager


class TestSessionManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sessions_dir = Path(self.temp_dir.name)
        self.manager = SessionManager(sessions_dir=self.sessions_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_load_session(self):
        session = self.manager.create_session(
            mode="readonly",
            model="qwen2.5:7b",
            system_prompt="prompt teste",
            title="Sessao de Teste",
        )
        self.assertIsNotNone(session.id)
        self.assertEqual(session.title, "Sessao de Teste")
        self.assertEqual(len(session.messages), 1)

        loaded = self.manager.load_session(session.id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, session.id)
        self.assertEqual(loaded.model, "qwen2.5:7b")

    def test_auto_title_from_user_message(self):
        session = self.manager.create_session(
            mode="assisted",
            model="qwen2.5:7b",
            system_prompt="sys",
        )
        session.messages.append({"role": "user", "content": "como verificar portas abertas com ss?"})
        self.manager.save_session(session)

        loaded = self.manager.load_session(session.id)
        self.assertEqual(loaded.title, "como verificar portas abertas com ss?")

    def test_list_and_get_latest_session(self):
        s1 = self.manager.create_session(mode="readonly", model="qwen2.5:7b", system_prompt="s1", title="Primeira")
        s2 = self.manager.create_session(mode="assisted", model="qwen2.5:7b", system_prompt="s2", title="Segunda")

        sessions = self.manager.list_sessions()
        self.assertEqual(len(sessions), 2)
        # Mais recente primeiro
        self.assertEqual(sessions[0]["id"], s2.id)

        latest = self.manager.get_latest_session()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.id, s2.id)

    def test_delete_session(self):
        session = self.manager.create_session(mode="readonly", model="m", system_prompt="s")
        self.assertTrue(self.manager.delete_session(session.id))
        self.assertIsNone(self.manager.load_session(session.id))


if __name__ == "__main__":
    unittest.main()
