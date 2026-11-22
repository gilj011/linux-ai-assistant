"""
Módulo de inspeção do sistema operacional.
Realiza leitura estritamente segura (read-only) do ambiente local para contextualizar a IA.
"""

from dataclasses import dataclass, field
import os
import platform
import shutil
from typing import Dict, List, Optional


@dataclass
class SystemContext:
    distro_name: str
    distro_version: str
    distro_id: str
    id_like: List[str] = field(default_factory=list)
    kernel: str = ""
    arch: str = ""
    available_package_managers: List[str] = field(default_factory=list)

    def is_debian_based(self) -> bool:
        """Verifica se a distribuição é derivada de Debian."""
        identifiers = {self.distro_id.lower()} | {item.lower() for item in self.id_like}
        return bool(identifiers & {"debian", "ubuntu", "pop", "mint", "elementary", "zorin"})

    def to_prompt_context(self) -> str:
        """Formata o contexto do sistema para injeção no prompt da IA."""
        pkg_managers = ", ".join(self.available_package_managers) if self.available_package_managers else "apt"
        base_info = f"Distribuição: {self.distro_name} {self.distro_version}".strip()
        return (
            f"- {base_info}\n"
            f"- Base: {', '.join(self.id_like) if self.id_like else self.distro_id}\n"
            f"- Kernel: {self.kernel} ({self.arch})\n"
            f"- Gerenciadores de pacotes detectados: {pkg_managers}"
        )


class OSInspector:
    """Coletor seguro de informações do sistema operacional."""

    OS_RELEASE_PATH = "/etc/os-release"

    @classmethod
    def get_system_context(cls) -> SystemContext:
        """Obtém o contexto consolidado do sistema."""
        raw_os_release = cls._parse_os_release()
        
        distro_name = raw_os_release.get("NAME", platform.system())
        distro_version = raw_os_release.get("VERSION", raw_os_release.get("VERSION_ID", ""))
        distro_id = raw_os_release.get("ID", "unknown")
        
        id_like_str = raw_os_release.get("ID_LIKE", "")
        id_like = [item.strip() for item in id_like_str.split()] if id_like_str else []
        if distro_id and distro_id not in id_like:
            id_like.append(distro_id)

        uname_info = platform.uname()
        kernel = uname_info.release or platform.release()
        arch = uname_info.machine or platform.machine()

        package_managers = cls._detect_package_managers()

        return SystemContext(
            distro_name=distro_name,
            distro_version=distro_version,
            distro_id=distro_id,
            id_like=id_like,
            kernel=kernel,
            arch=arch,
            available_package_managers=package_managers,
        )

    @classmethod
    def _parse_os_release(cls) -> Dict[str, str]:
        """Lê e analisa o arquivo /etc/os-release sem invocar shells."""
        data: Dict[str, str] = {}
        if not os.path.isfile(cls.OS_RELEASE_PATH):
            return data

        try:
            with open(cls.OS_RELEASE_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip('"').strip("'")
                        data[key] = val
        except Exception:
            pass

        return data

    @classmethod
    def _detect_package_managers(cls) -> List[str]:
        """Detecta quais ferramentas de pacotes comuns estão disponíveis no PATH."""
        candidates = ["apt", "dpkg", "flatpak", "snap"]
        detected: List[str] = []
        for cmd in candidates:
            if shutil.which(cmd):
                detected.append(cmd)
        return detected


if __name__ == "__main__":
    ctx = OSInspector.get_system_context()
    print("=== Contexto do Sistema Detectado ===")
    print(ctx.to_prompt_context())
    print(f"Base Debian? {'Sim' if ctx.is_debian_based() else 'Não'}")
