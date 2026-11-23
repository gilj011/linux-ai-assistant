"""
Testes unitarios para o AuditLogger e persistencia de relatorios.
"""

from pathlib import Path
import tempfile
import unittest

from src.audit import AuditLogger


class TestAuditLogger(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.tmpdir.name)
        self.logger = AuditLogger(base_dir=self.base_dir)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_log_action_appends_entry(self):
        self.logger.log_action(
            action_type="write_file",
            target="/tmp/teste.txt",
            status="EXECUTADO_SUCESSO",
            details="Arquivo criado",
            user_approved=True,
        )

        entries = self.logger.get_recent_actions(limit=5)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action_type"], "write_file")
        self.assertEqual(entries[0]["target"], "/tmp/teste.txt")
        self.assertEqual(entries[0]["status"], "EXECUTADO_SUCESSO")
        self.assertTrue(entries[0]["user_approved"])

    def test_save_diagnostic_report(self):
        report_text = "EVIDENCIAS COLETADAS DO SISTEMA TESTE"
        saved_path = self.logger.save_diagnostic_report("Saude Geral", report_text)

        self.assertIsNotNone(saved_path)
        self.assertTrue(saved_path.is_file())
        with open(saved_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), report_text)

        reports = self.logger.list_saved_reports()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0], saved_path)


if __name__ == "__main__":
    unittest.main()
