"""
Modulo de Auditoria e Persistencia de Relatorios do kored.
Registra de forma segura todas as operacoes, comandos autorizados e diagnosticos.
"""

from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditLogger:
    """Gerenciador de logs de auditoria e relatorios de diagnostico."""

    DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "kored"

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or self.DEFAULT_DATA_DIR
        self.audit_file = self.base_dir / "audit.log"
        self.reports_dir = self.base_dir / "reports"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Garante que as pastas de armazenamento local existam."""
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            os.makedirs(self.reports_dir, exist_ok=True)
        except Exception:
            pass

    def log_action(
        self,
        action_type: str,
        target: str,
        status: str,
        details: Optional[str] = None,
        user_approved: bool = True,
    ) -> None:
        """
        Registra uma acao ou comando no arquivo de auditoria.
        status: 'EXECUTADO_SUCESSO', 'FALHA_EXECUCAO', 'CANCELADO_PELO_USUARIO', 'BLOQUEADO_SEGURANCA'
        """
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action_type": action_type,
            "target": target,
            "user_approved": user_approved,
            "status": status,
            "details": details or "",
        }

        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def save_diagnostic_report(self, target: str, prompt_context: str) -> Optional[Path]:
        """Salva uma copia do relatorio de evidencias no disco para consulta historica."""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target = "".join(c if c.isalnum() else "_" for c in target).strip("_").lower()
        filename = f"diag_{safe_target}_{timestamp_str}.log"
        target_path = self.reports_dir / filename

        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(prompt_context)
            return target_path
        except Exception:
            return None

    def get_recent_actions(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Recupera as acoes mais recentes do arquivo de auditoria."""
        if not os.path.isfile(self.audit_file):
            return []

        entries: List[Dict[str, Any]] = []
        try:
            with open(self.audit_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except Exception:
                            continue
        except Exception:
            return []

        return entries[-limit:]

    def list_saved_reports(self, limit: int = 10) -> List[Path]:
        """Lista os relatorios de diagnostico salvos mais recentes."""
        if not os.path.isdir(self.reports_dir):
            return []

        try:
            files = sorted(
                self.reports_dir.glob("diag_*.log"),
                key=os.path.getmtime,
                reverse=True,
            )
            return files[:limit]
        except Exception:
            return []
