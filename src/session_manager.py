"""
Gerenciador de persistencia de sessoes do kored.
Permite salvar, listar e retomar conversas continuas em ~/.local/share/kored/sessions/.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class SessionData:
    """Representacao estruturada de uma sessao de conversa do kored."""

    id: str
    title: str
    created_at: str
    updated_at: str
    mode: str
    model: str
    messages: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", "Sessao sem titulo"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            mode=data.get("mode", "readonly"),
            model=data.get("model", "qwen2.5:7b"),
            messages=data.get("messages", []),
        )


class SessionManager:
    """Gerencia o ciclo de vida e a persistencia das sessoes no disco."""

    def __init__(self, sessions_dir: Optional[Path] = None):
        if sessions_dir:
            self.sessions_dir = sessions_dir
        else:
            xdg_data = os.getenv("XDG_DATA_HOME")
            base_dir = Path(xdg_data) if xdg_data else (Path.home() / ".local" / "share")
            self.sessions_dir = base_dir / "kored" / "sessions"

        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Garante a existencia do diretorio de sessoes com fallback seguro."""
        try:
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Fallback para diretorio alternativo caso .local/share seja read-only
            fallback = Path("/tmp") / f"kored_{os.getuid()}" / "sessions"
            try:
                fallback.mkdir(parents=True, exist_ok=True)
                self.sessions_dir = fallback
            except Exception:
                pass

    def create_session(
        self,
        mode: str,
        model: str,
        system_prompt: str,
        title: str = "Nova sessao",
        save_now: bool = True,
    ) -> SessionData:
        """Cria e registra uma nova sessao com a mensagem de sistema inicial."""
        now_str = datetime.now().isoformat()
        session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        session = SessionData(
            id=session_id,
            title=title,
            created_at=now_str,
            updated_at=now_str,
            mode=mode,
            model=model,
            messages=[{"role": "system", "content": system_prompt}],
        )
        if save_now:
            self.save_session(session)
        return session

    def _get_session_path(self, session_id: str) -> Path:
        clean_id = session_id.replace(".json", "")
        return self.sessions_dir / f"session_{clean_id}.json"

    def save_session(self, session: SessionData) -> bool:
        """Salva ou atualiza a sessao em arquivo JSON."""
        session.updated_at = datetime.now().isoformat()

        # Atualiza o titulo com base na primeira pergunta do usuario se ainda tiver o titulo padrao
        if session.title in ["Nova sessao", "Sessao sem titulo"]:
            for msg in session.messages:
                if msg.get("role") == "user":
                    first_line = msg.get("content", "").strip().split("\n")[0]
                    if first_line:
                        session.title = first_line[:50]
                    break

        file_path = self._get_session_path(session.id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_session(self, session_id: str) -> Optional[SessionData]:
        """Carrega uma sessao especifica pelo seu identificador."""
        file_path = self._get_session_path(session_id)
        if not file_path.exists():
            # Tenta busca exata pelo nome do arquivo
            direct_path = self.sessions_dir / session_id
            if direct_path.exists() and direct_path.is_file():
                file_path = direct_path
            else:
                return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SessionData.from_dict(data)
        except Exception:
            return None

    def get_latest_session(self) -> Optional[SessionData]:
        """Retorna a sessao modificada mais recentemente."""
        files = list(self.sessions_dir.glob("session_*.json"))
        if not files:
            return None

        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return self.load_session(files[0].stem.replace("session_", ""))

    def list_sessions(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Lista as sessoes gravadas ordenadas das mais recentes para as mais antigas."""
        files = list(self.sessions_dir.glob("session_*.json"))
        if not files:
            return []

        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        results = []

        for f in files[:limit]:
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                turns = (len(data.get("messages", [])) - 1) // 2
                results.append({
                    "id": data.get("id", f.stem.replace("session_", "")),
                    "title": data.get("title", "Sem titulo"),
                    "updated_at": data.get("updated_at", ""),
                    "mode": data.get("mode", "readonly"),
                    "turns": max(0, turns),
                    "model": data.get("model", ""),
                })
            except Exception:
                continue

        return results

    def delete_session(self, session_id: str) -> bool:
        """Remove o arquivo de uma sessao."""
        file_path = self._get_session_path(session_id)
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception:
                return False
        return False
