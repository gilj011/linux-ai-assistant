"""
Motor de diagnosticos do kored.
Consolida evidencias coletadas pelas sondas para envio ao modelo de IA.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from src.probes import ProbeResult, SystemProbes


@dataclass
class DiagnosticReport:
    """Relatorio consolidado de evidencias do sistema."""

    target: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    results: List[ProbeResult] = field(default_factory=list)

    def to_prompt_context(self) -> str:
        """Formata as evidencias coletadas para inclusao no prompt de analise."""
        lines = [
            f"=== RELATORIO DE EVIDENCIAS DO SISTEMA ({self.target}) ===",
            f"Data/Hora da Coleta: {self.timestamp}\n",
        ]

        for item in self.results:
            status = "EXECUCAO BEM-SUCEDIDA" if item.success else "FALHA NA COLETA"
            lines.append(f"--- [SONDA]: {item.name} ({status}) ---")
            lines.append(f"Comando executado: {item.command}")
            if item.output:
                lines.append(item.output)
            if item.error:
                lines.append(f"Aviso/Erro: {item.error}")
            lines.append("")

        lines.append("=== FIM DAS EVIDENCIAS ===")
        return "\n".join(lines)


class DiagnosticEngine:
    """Orquestrador de diagnósticos e inspeção do sistema."""

    @classmethod
    def run_health_check(cls) -> DiagnosticReport:
        """Executa varredura de saude basica do sistema (recursos, servicos e logs)."""
        report = DiagnosticReport(target="Saude Geral do Sistema")

        # 1. Recursos fundamentais
        report.results.append(SystemProbes.probe_memory_usage())
        report.results.append(SystemProbes.probe_disk_space())

        # 2. Servicos com falha
        report.results.append(SystemProbes.probe_failed_services())

        # 3. Logs criticos recentes
        report.results.append(SystemProbes.probe_recent_critical_logs(lines=20))

        # 4. Interfaces de rede
        report.results.append(SystemProbes.probe_network_interfaces())

        return report

    @classmethod
    def run_service_check(cls, service_name: str) -> DiagnosticReport:
        """Executa diagnostico focado em um servico especifico do systemd."""
        report = DiagnosticReport(target=f"Servico {service_name}")
        report.results.append(SystemProbes.probe_service_status(service_name))
        return report
