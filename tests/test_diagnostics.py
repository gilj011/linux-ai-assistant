"""
Testes unitarios para o modulo de sondas e motor de diagnostico.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.diagnostics import DiagnosticEngine, DiagnosticReport
from src.probes import ProbeResult, SystemProbes


class TestDiagnostics(unittest.TestCase):

    @patch("shutil.which", return_value=None)
    def test_probe_binary_not_found(self, mock_which):
        res = SystemProbes._run_safe_command("Teste Inexistente", ["comando_fantasma_xyz"])
        self.assertFalse(res.success)
        self.assertIn("nao encontrado", res.error)

    @patch("shutil.which", return_value="/bin/free")
    @patch("subprocess.run")
    def test_probe_successful_execution(self, mock_run, mock_which):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Mem: 16Gi total"
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc

        res = SystemProbes.probe_memory_usage()
        self.assertTrue(res.success)
        self.assertEqual(res.output, "Mem: 16Gi total")
        self.assertIsNone(res.error)

    def test_diagnostic_report_formatting(self):
        item = ProbeResult(
            name="Sonda de Teste",
            command="free -m",
            success=True,
            output="Mem: 16384 total",
        )
        report = DiagnosticReport(target="Teste Unitario", results=[item])
        prompt_text = report.to_prompt_context()

        self.assertIn("RELATORIO DE EVIDENCIAS DO SISTEMA", prompt_text)
        self.assertIn("Sonda de Teste", prompt_text)
        self.assertIn("free -m", prompt_text)
        self.assertIn("EXECUCAO BEM-SUCEDIDA", prompt_text)

    @patch.object(SystemProbes, "probe_memory_usage")
    @patch.object(SystemProbes, "probe_disk_space")
    @patch.object(SystemProbes, "probe_failed_services")
    @patch.object(SystemProbes, "probe_recent_critical_logs")
    @patch.object(SystemProbes, "probe_network_interfaces")
    def test_run_health_check_collects_all_probes(
        self, mock_net, mock_logs, mock_services, mock_disk, mock_mem
    ):
        mock_mem.return_value = ProbeResult("Memoria", "free", True, "ok")
        mock_disk.return_value = ProbeResult("Disco", "df", True, "ok")
        mock_services.return_value = ProbeResult("Servicos", "systemctl", True, "ok")
        mock_logs.return_value = ProbeResult("Logs", "journalctl", True, "ok")
        mock_net.return_value = ProbeResult("Rede", "ip", True, "ok")

        report = DiagnosticEngine.run_health_check()
        self.assertEqual(len(report.results), 5)
        self.assertEqual(report.target, "Saude Geral do Sistema")


if __name__ == "__main__":
    unittest.main()
