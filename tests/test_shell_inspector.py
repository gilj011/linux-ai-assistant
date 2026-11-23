"""
Testes unitarios para o modulo de inspecao do shell (ShellInspector).
"""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.shell_inspector import ShellInspector


class TestShellInspector(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_file = Path(self.temp_dir.name) / "test_history"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_detect_shell(self):
        with patch.dict(os.environ, {"SHELL": "/usr/bin/zsh"}):
            self.assertEqual(ShellInspector.detect_shell(), "zsh")

        with patch.dict(os.environ, {"SHELL": "/bin/bash"}):
            self.assertEqual(ShellInspector.detect_shell(), "bash")

    def test_clean_history_line_bash(self):
        raw = "   sudo apt update && sudo apt upgrade -y   "
        self.assertEqual(
            ShellInspector.clean_history_line(raw),
            "sudo apt update && sudo apt upgrade -y",
        )

    def test_clean_history_line_zsh_extended(self):
        raw = ": 1699999999:0;docker compose up -d"
        self.assertEqual(
            ShellInspector.clean_history_line(raw),
            "docker compose up -d",
        )

    def test_get_last_command_skips_kored_and_empty(self):
        lines = [
            "ls -la\n",
            "sudo systemctl restart nginx\n",
            "\n",
            "kored 'como listar portas'\n",
            "./kored fix\n",
            "   \n",
        ]
        with open(self.history_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        last_cmd = ShellInspector.get_last_command(custom_path=self.history_file)
        self.assertEqual(last_cmd, "sudo systemctl restart nginx")

    def test_get_last_command_empty_file_returns_none(self):
        self.history_file.touch()
        last_cmd = ShellInspector.get_last_command(custom_path=self.history_file)
        self.assertIsNone(last_cmd)

    @patch("sys.stdin.isatty")
    def test_read_stdin_tty_returns_none(self, mock_isatty):
        mock_isatty.return_value = True
        self.assertIsNone(ShellInspector.read_stdin_if_available())


if __name__ == "__main__":
    unittest.main()
