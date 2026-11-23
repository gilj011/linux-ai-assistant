"""
Parser de acoes estruturadas propostas pelo modelo.
Permite identificar intencoes de criacao de arquivos e execucao de comandos.
"""

from dataclasses import dataclass
import json
import re
from typing import List, Optional, Tuple


@dataclass
class ProposedAction:
    """Representa uma acao proposta pelo kored sujeita a autorizacao humana."""

    action_type: str  # "write_file" ou "run_command"
    path: Optional[str] = None
    content: Optional[str] = None
    command: Optional[str] = None
    explanation: Optional[str] = None

    def summary(self) -> str:
        """Retorna resumo textual da acao para exibicao no terminal."""
        if self.action_type == "write_file":
            preview = (self.content[:100] + "...") if self.content and len(self.content) > 100 else (self.content or "")
            return (
                f"Tipo: Criacao/Edicao de Arquivo\n"
                f"Destino: {self.path}\n"
                f"Previa do conteudo:\n{preview}"
            )
        elif self.action_type == "run_command":
            return (
                f"Tipo: Execucao de Comando de Sistema\n"
                f"Comando: {self.command}\n"
                f"Objetivo: {self.explanation or 'Nao informado'}"
            )
        return f"Acao: {self.action_type}"


class ActionParser:
    """Extrai e sanitiza blocos de acoes kored-action."""

    # Captura blocos com backticks: ```kored-action { ... } ```
    ACTION_BLOCK_PATTERN = re.compile(r"```(?:kored-action|json:action)\s*(\{.*?\})\s*```", re.DOTALL)

    # Captura JSON puro sem backticks: { "action": "run_command", ... } ou { "action": "write_file", ... }
    # Usado apenas para strip (nao para extracao de acoes, evitando falso positivo em exemplos de texto)
    BARE_JSON_ACTION_PATTERN = re.compile(
        r'\{\s*"action"\s*:\s*"(?:run_command|write_file)".*?\}',
        re.DOTALL,
    )

    @classmethod
    def extract_actions(cls, text: str) -> List[ProposedAction]:
        """Extrai todas as acoes validas encontradas no texto gerado (somente blocos com backticks)."""
        actions: List[ProposedAction] = []
        matches = cls.ACTION_BLOCK_PATTERN.findall(text)

        for match in matches:
            try:
                data = json.loads(match.strip())
                action_type = data.get("action", "")

                if action_type == "write_file" and data.get("path"):
                    actions.append(
                        ProposedAction(
                            action_type="write_file",
                            path=data.get("path"),
                            content=data.get("content", ""),
                            explanation=data.get("explanation"),
                        )
                    )
                elif action_type == "run_command" and data.get("command"):
                    actions.append(
                        ProposedAction(
                            action_type="run_command",
                            command=data.get("command"),
                            explanation=data.get("explanation"),
                        )
                    )
            except Exception:
                continue

        return actions

    @classmethod
    def strip_action_blocks(cls, text: str) -> str:
        """Remove blocos tecnicos de acao (com e sem backticks) para visualizacao limpa no terminal."""
        # Remove blocos com backtick primeiro
        cleaned = cls.ACTION_BLOCK_PATTERN.sub("", text)
        # Remove JSON puro sem backticks que o modelo as vezes emite no follow-up
        cleaned = cls.BARE_JSON_ACTION_PATTERN.sub("", cleaned)
        return cleaned.strip()
