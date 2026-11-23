"""
Cliente HTTP para comunicação com o Ollama local com suporte a streaming.
"""

import json
import os
from typing import Any, Dict, Generator, List, Optional, Tuple
import requests


class OllamaClient:
    """Cliente para a API HTTP do Ollama rodando localmente."""

    DEFAULT_OPTIONS: Dict[str, Any] = {
        "temperature": 0.6,
        "top_p": 0.9,
        "repeat_penalty": 1.15,
        "repeat_last_n": 64,
    }

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: str = "qwen2.5:7b",
        timeout: int = 180,
        options: Optional[Dict[str, Any]] = None,
    ):
        self.base_url = (base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.model = model
        self.timeout = timeout
        self.options = dict(self.DEFAULT_OPTIONS)
        if options:
            self.options.update(options)

    def check_connection(self) -> Tuple[bool, str]:
        """
        Verifica se o servidor Ollama está acessível.
        Retorna (True, 'versão') ou (False, 'mensagem de erro amigável').
        """
        try:
            resp = requests.get(f"{self.base_url}/api/version", timeout=3)
            if resp.status_code == 200:
                version = resp.json().get("version", "desconhecida")
                return True, f"Ollama ativo (versão {version})"
            return False, f"Ollama respondeu com código HTTP {resp.status_code}."
        except requests.exceptions.ConnectionError:
            return False, (
                "Não foi possível conectar ao Ollama em "
                f"{self.base_url}.\n"
                "Certifique-se de que o Ollama está instalado e em execução ('ollama serve')."
            )
        except Exception as e:
            return False, f"Erro ao verificar conexão com o Ollama: {str(e)}"

    def list_installed_models(self) -> List[str]:
        """Retorna a lista de nomes dos modelos instalados localmente."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("models", [])
                return [m.get("name", "") for m in models if m.get("name")]
            return []
        except Exception:
            return []

    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """
        Gera resposta em tempo real via streaming de tokens.
        Gera (yield) cada pedaço de texto assim que recebido do modelo.
        """
        target_model = model or self.model
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": True,
            "options": self.options,
        }
        if system_prompt:
            payload["system"] = system_prompt

        url = f"{self.base_url}/api/generate"

        try:
            with requests.post(url, json=payload, stream=True, timeout=self.timeout) as response:
                if response.status_code != 200:
                    yield f"\n[Erro do Ollama HTTP {response.status_code}]: {response.text}"
                    return

                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        token = chunk.get("response", "")
                        yield token
                        if chunk.get("done", False):
                            break
        except requests.exceptions.ConnectionError:
            yield (
                "\n\n[Erro]: Conexão perdida com o Ollama local. "
                "Verifique se o processo do Ollama continua ativo."
            )
        except Exception as e:
            yield f"\n\n[Erro inesperado na geração]: {str(e)}"

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """
        Gera resposta em tempo real via endpoint /api/chat do Ollama,
        mantendo o histórico completo da conversa (multi-turn).
        """
        target_model = model or self.model
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": True,
            "options": self.options,
        }

        url = f"{self.base_url}/api/chat"

        try:
            with requests.post(url, json=payload, stream=True, timeout=self.timeout) as response:
                if response.status_code != 200:
                    yield f"\n[Erro do Ollama HTTP {response.status_code}]: {response.text}"
                    return

                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        msg = chunk.get("message", {})
                        token = msg.get("content", "")
                        if token:
                            yield token
                        if chunk.get("done", False):
                            break
        except requests.exceptions.ConnectionError:
            yield (
                "\n\n[Erro]: Conexão perdida com o Ollama local. "
                "Verifique se o processo do Ollama continua ativo."
            )
        except Exception as e:
            yield f"\n\n[Erro inesperado no chat]: {str(e)}"
