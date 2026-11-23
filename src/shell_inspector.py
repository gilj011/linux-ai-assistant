"""
Modulo de inspecao do shell do usuario.
Recupera o ultimo comando executado a partir do historico do Bash ou Zsh
e le saidas de erro redirecionadas via stdin.
"""

import os
from pathlib import Path
import re
import select
import sys
from typing import Optional


class ShellInspector:
    """Inspeciona o historico e fluxos de entrada do shell ativo."""

    @staticmethod
    def detect_shell() -> str:
        """Detecta o shell padrao ativo do usuario."""
        shell_env = os.getenv("SHELL", "")
        if "zsh" in shell_env:
            return "zsh"
        elif "bash" in shell_env:
            return "bash"
        return "bash"

    @classmethod
    def get_history_file(cls) -> Optional[Path]:
        """Identifica o arquivo de historico correspondente ao shell ativo."""
        histfile_env = os.getenv("HISTFILE")
        if histfile_env:
            p = Path(histfile_env)
            if p.exists() and p.is_file():
                return p

        home = Path.home()
        candidates = [
            home / ".bash_history",
            home / ".zsh_history",
            home / ".history",
        ]

        # Prioriza o arquivo do shell detectado
        detected = cls.detect_shell()
        if detected == "zsh":
            candidates.insert(0, home / ".zsh_history")
        else:
            candidates.insert(0, home / ".bash_history")

        for cand in candidates:
            if cand.exists() and cand.is_file():
                return cand

        return None

    @staticmethod
    def clean_history_line(raw_line: str) -> str:
        """
        Limpa marcadores de timestamp de shells (ex: ZSH_EXTENDED_HISTORY).
        Formato Zsh: ': 1630000000:0;comando'
        """
        line = raw_line.strip()
        zsh_pattern = r"^:\s*\d+:\d+;(.*)$"
        match = re.match(zsh_pattern, line)
        if match:
            return match.group(1).strip()
        return line

    @classmethod
    def get_last_command(cls, custom_path: Optional[Path] = None) -> Optional[str]:
        """
        Retorna o ultimo comando valido do historico, ignorando
        invocacoes do proprio kored e linhas vazias.
        """
        history_file = custom_path or cls.get_history_file()
        if not history_file or not history_file.exists():
            return None

        try:
            with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return None

        # Percorre as linhas de tras para frente
        for raw in reversed(lines):
            cmd = cls.clean_history_line(raw)
            if not cmd:
                continue

            # Ignora chamadas do proprio kored
            parts = cmd.split()
            first_token = parts[0].lower() if parts else ""
            if first_token in ["kored", "./kored"] or first_token.endswith("/kored"):
                continue

            return cmd

        return None

    @staticmethod
    def read_stdin_if_available(max_bytes: int = 65536) -> Optional[str]:
        """
        Le a saida recebida via pipe (stdin) caso nao seja um terminal TTY interativo.
        Exemplo: docker compose up 2>&1 | kored fix
        """
        if sys.stdin.isatty():
            return None

        try:
            # Verifica se ha dados disponiveis para leitura sem bloquear indefinidamente
            if select.select([sys.stdin], [], [], 0.1)[0]:
                content = sys.stdin.read(max_bytes)
                return content.strip() if content else None
        except Exception:
            pass

        return None
