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


class ExecutionMode(str, Enum):
    READONLY = "readonly"      # Modo Seguro: apenas consulta e diagnostico; nenhuma acao executada
    ASSISTED = "assisted"      # Modo Assistido: IA pode propor acoes, mas cada uma exige aprovacao humana


class ControlledExecutor:
    """Validador e executor controlado de acoes no sistema."""

    DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "allowed_commands.yaml"

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
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
                return False, f"Comando bloqueado pelas diretrizes de seguranca (padrao proibido: '{pattern}')."

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
                return True, combined or "[Comando executado com sucesso sem saida no terminal]"
            else:
                return False, f"Codigo de erro {res.returncode}:\n{combined}"
        except subprocess.TimeoutExpired:
            return False, f"Tempo limite de execucao ({timeout}s) esgotado."
        except Exception as e:
            return False, f"Falha na execucao do comando: {str(e)}"

    def write_file(self, target_path: str, content: str) -> Tuple[bool, str]:
        """Cria ou atualiza um arquivo de forma controlada."""
        try:
            # Expande ~ para a pasta home real do usuario
            expanded_path = os.path.abspath(os.path.expanduser(target_path.strip()))
            
            # Garante que diretorios pais existam
            parent_dir = os.path.dirname(expanded_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            with open(expanded_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True, f"Arquivo criado com sucesso: {expanded_path}"
        except PermissionError:
            return False, f"Permissao negada para escrever em: {target_path}. Requer privilegios elevados."
        except Exception as e:
            return False, f"Falha ao escrever arquivo: {str(e)}"
