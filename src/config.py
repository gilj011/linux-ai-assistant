"""
Gerenciamento de configuracao persistente do kored.
Carrega e valida parametros em ~/.config/kored/config.yaml respeitando XDG_CONFIG_HOME.
"""

from dataclasses import asdict, dataclass
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass
class KoredConfig:
    """Estrutura de configuracao do usuario para o kored."""

    model: str = "qwen2.5:7b"
    ollama_host: str = "http://localhost:11434"
    default_mode: str = "readonly"  # 'readonly' ou 'assisted'
    timeout: int = 180
    clear_on_start: bool = True
    history_limit: int = 20

    @classmethod
    def default_config_path(cls) -> Path:
        """Retorna o caminho padrao para o arquivo de configuracao."""
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        if xdg_config:
            base_dir = Path(xdg_config)
        else:
            base_dir = Path.home() / ".config"
        return base_dir / "kored" / "config.yaml"

    @classmethod
    def load(cls, custom_path: Optional[Path] = None) -> "KoredConfig":
        """
        Carrega configuracoes do arquivo YAML.
        Cria o arquivo com os valores padrao caso nao exista.
        """
        config_path = custom_path or cls.default_config_path()

        if not config_path.exists():
            config = cls()
            config.save(config_path)
            return config

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            if not isinstance(data, dict):
                return cls()

            return cls(
                model=str(data.get("model", "qwen2.5:7b")),
                ollama_host=str(data.get("ollama_host", os.getenv("OLLAMA_HOST", "http://localhost:11434"))),
                default_mode=str(data.get("default_mode", "readonly")).lower(),
                timeout=int(data.get("timeout", 180)),
                clear_on_start=bool(data.get("clear_on_start", True)),
                history_limit=int(data.get("history_limit", 20)),
            )
        except Exception:
            return cls()

    def save(self, custom_path: Optional[Path] = None) -> bool:
        """Salva a configuracao atual no caminho especificado."""
        config_path = custom_path or self.default_config_path()
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            content = {
                "model": self.model,
                "ollama_host": self.ollama_host,
                "default_mode": self.default_mode,
                "timeout": self.timeout,
                "clear_on_start": self.clear_on_start,
                "history_limit": self.history_limit,
            }
            raw_yaml = yaml.dump(content, default_flow_style=False, sort_keys=False)
            header = (
                "# kored — Arquivo de Configuracao do Usuario\n"
                "# Localizacao: ~/.config/kored/config.yaml\n\n"
            )
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(header + raw_yaml)
            return True
        except (OSError, Exception):
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Converte a configuracao em dicionario."""
        return asdict(self)
