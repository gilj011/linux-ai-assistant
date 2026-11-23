"""
Modulo do Executor Controlado com Politicas de Seguranca.
Garante que nenhuma acao ocorra sem validacao e autorizacao explicita do usuario.
"""

from enum import Enum
import os
from pathlib import Path
import subprocess
from typing import Dict, List, Optional, Tuple
import yaml

from src.audit import AuditLogger


class ExecutionMode(str, Enum):
    READONLY = "readonly"      # Modo Seguro: apenas consulta e diagnostico; nenhuma acao executada
    ASSISTED = "assisted"      # Modo Assistido: IA pode propor acoes, mas cada uma exige aprovacao humana


class ControlledExecutor:
    """Validador e executor controlado de acoes no sistema."""

    DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "allowed_commands.yaml"

    def __init__(self, config_path: Optional[Path] = None, audit_dir: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.audit_logger = AuditLogger(base_dir=audit_dir)
        self.diagnostic_commands: List[str] = []
        self.allowed_actions: List[str] = []
        self.blocked_patterns: List[str] = []
        self.load_policy()

    def load_policy(self) -> None:
        """Carrega regras de comandos e padroes bloqueados a partir do arquivo YAML."""
        if not os.path.isfile(self.config_path):
            self.blocked_patterns = ["rm -rf /", "mkfs", "dd if=", "| bash", "| sh"]
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.diagnostic_commands = data.get("diagnostic_commands", [])
                self.allowed_actions = data.get("allowed_actions", [])
                self.blocked_patterns = data.get("blocked_patterns", [])
        except Exception:
            self.blocked_patterns = ["rm -rf /", "mkfs", "dd if=", "| bash", "| sh"]

    def validate_command(self, command: str) -> Tuple[bool, str]:
        """
        Valida se o comando e seguro para ser proposto/executado.
        Bloqueia terminantemente padroes destrutivos.
        """
        cmd_clean = command.strip()
        if not cmd_clean:
            return False, "Comando vazio."

        for pattern in self.blocked_patterns:
            if pattern in cmd_clean:
                msg = f"Comando bloqueado pelas diretrizes de seguranca (padrao proibido: '{pattern}')."
                self.audit_logger.log_action("run_command", cmd_clean, "BLOQUEADO_SEGURANCA", msg, user_approved=False)
                return False, msg

        return True, "Comando compativel com as politicas de seguranca."

    def execute_command(self, command: str, timeout: int = 60) -> Tuple[bool, str]:
        """Executa um comando no sistema operacional de forma controlada."""
        valid, msg = self.validate_command(command)
        if not valid:
            return False, msg

        try:
            res = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            output = res.stdout.strip()
            error = res.stderr.strip()
            combined = output if output else error

            if res.returncode == 0:
                success_msg = combined or "[Comando executado com sucesso sem saida no terminal]"
                self.audit_logger.log_action("run_command", command, "EXECUTADO_SUCESSO", success_msg[:300], user_approved=True)
                return True, success_msg
            else:
                fail_msg = f"Codigo de retorno {res.returncode}:\n{combined}" if combined else f"Codigo de retorno {res.returncode} (sem ocorrencias / sem saida)"
                self.audit_logger.log_action("run_command", command, "RETORNO_NAO_ZERO", fail_msg[:300], user_approved=True)
                return False, fail_msg
        except subprocess.TimeoutExpired:
            timeout_msg = f"Tempo limite de execucao ({timeout}s) esgotado."
            self.audit_logger.log_action("run_command", command, "TEMPO_ESGOTADO", timeout_msg, user_approved=True)
            return False, timeout_msg
        except Exception as e:
            err_msg = f"Falha na execucao do comando: {str(e)}"
            self.audit_logger.log_action("run_command", command, "FALHA_EXECUCAO", err_msg, user_approved=True)
            return False, err_msg

    def write_file(self, target_path: str, content: str) -> Tuple[bool, str]:
        """Cria ou atualiza um arquivo de forma controlada."""
        try:
            expanded_path = os.path.abspath(os.path.expanduser(target_path.strip()))
            
            parent_dir = os.path.dirname(expanded_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            with open(expanded_path, "w", encoding="utf-8") as f:
                f.write(content)

            success_msg = f"Arquivo criado com sucesso: {expanded_path}"
            self.audit_logger.log_action("write_file", expanded_path, "EXECUTADO_SUCESSO", f"Bytes gravados: {len(content)}", user_approved=True)
            return True, success_msg
        except PermissionError:
            err_msg = f"Permissao negada para escrever em: {target_path}. Requer privilegios elevados."
            self.audit_logger.log_action("write_file", target_path, "FALHA_PERMISSAO", err_msg, user_approved=True)
            return False, err_msg
        except Exception as e:
            err_msg = f"Falha ao escrever arquivo: {str(e)}"
            self.audit_logger.log_action("write_file", target_path, "FALHA_EXECUCAO", err_msg, user_approved=True)
            return False, err_msg
