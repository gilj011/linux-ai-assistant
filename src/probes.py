"""
Modulo de sondas seguras de diagnostico (read-only).
Executa comandos de inspecao de estado do sistema com limites de tempo e tamanho.
"""

from dataclasses import dataclass
import shutil
import subprocess
from typing import List, Optional


@dataclass
class ProbeResult:
    name: str
    command: str
    success: bool
    output: str
    error: Optional[str] = None


class SystemProbes:
    """Conjunto de sondas de leitura segura do sistema operacional."""

    MAX_OUTPUT_CHARS = 4000
    DEFAULT_TIMEOUT_SECONDS = 5

    @classmethod
    def _run_safe_command(cls, name: str, cmd_args: List[str], timeout: Optional[int] = None) -> ProbeResult:
        """Executa um comando somente de leitura de maneira isolada e segura."""
        binary = cmd_args[0]
        if not shutil.which(binary):
            return ProbeResult(
                name=name,
                command=" ".join(cmd_args),
                success=False,
                output="",
                error=f"Utilitario '{binary}' nao encontrado no sistema.",
            )

        try:
            res = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=timeout or cls.DEFAULT_TIMEOUT_SECONDS,
                check=False,
            )
            raw_output = res.stdout.strip() or res.stderr.strip()
            # Limita tamanho para evitar sobrecarga no contexto da IA
            truncated_output = raw_output[: cls.MAX_OUTPUT_CHARS]
            if len(raw_output) > cls.MAX_OUTPUT_CHARS:
                truncated_output += "\n... [saida truncada por limite de tamanho]"

            return ProbeResult(
                name=name,
                command=" ".join(cmd_args),
                success=(res.returncode == 0),
                output=truncated_output,
                error=None if res.returncode == 0 else f"Codigo de saida: {res.returncode}",
            )
        except subprocess.TimeoutExpired:
            return ProbeResult(
                name=name,
                command=" ".join(cmd_args),
                success=False,
                output="",
                error="Tempo limite de execucao esgotado.",
            )
        except Exception as e:
            return ProbeResult(
                name=name,
                command=" ".join(cmd_args),
                success=False,
                output="",
                error=str(e),
            )

    @classmethod
    def probe_failed_services(cls) -> ProbeResult:
        """Verifica servicos em estado de falha via systemctl."""
        return cls._run_safe_command(
            name="Servicos com Falha",
            cmd_args=["systemctl", "--failed", "--no-pager", "--plain"],
        )

    @classmethod
    def probe_recent_critical_logs(cls, lines: int = 25) -> ProbeResult:
        """Coleta logs de erro recentes (prioridade err / crit) via journalctl."""
        return cls._run_safe_command(
            name="Logs Recentes de Erro",
            cmd_args=["journalctl", "-p", "3", "-xb", "-n", str(lines), "--no-pager"],
        )

    @classmethod
    def probe_memory_usage(cls) -> ProbeResult:
        """Coleta informacoes de utilizacao de memoria RAM e Swap."""
        return cls._run_safe_command(
            name="Consumo de Memoria",
            cmd_args=["free", "-h"],
        )

    @classmethod
    def probe_disk_space(cls) -> ProbeResult:
        """Coleta utilizacao das particoes de disco montadas."""
        return cls._run_safe_command(
            name="Espaco em Disco",
            cmd_args=["df", "-h", "-x", "tmpfs", "-x", "devtmpfs", "-x", "squashfs"],
        )

    @classmethod
    def probe_network_interfaces(cls) -> ProbeResult:
        """Verifica o estado das interfaces de rede."""
        return cls._run_safe_command(
            name="Interfaces de Rede",
            cmd_args=["ip", "-br", "a"],
        )

    @classmethod
    def probe_service_status(cls, service_name: str) -> ProbeResult:
        """Inspeciona o estado detalhado de um servico especifico."""
        # Sanitizacao basica do nome do servico
        clean_name = service_name.strip().split()[0]
        return cls._run_safe_command(
            name=f"Status do Servico '{clean_name}'",
            cmd_args=["systemctl", "status", clean_name, "-n", "30", "--no-pager"],
        )
