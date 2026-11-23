"""
Testes unitários para o PromptBuilder.
"""

import unittest
from src.os_inspector import SystemContext
from src.prompt_builder import PromptBuilder


class TestPromptBuilder(unittest.TestCase):

    def test_build_system_prompt_includes_context(self):
        ctx = SystemContext(
            distro_name="Pop!_OS",
            distro_version="24.04 LTS",
            distro_id="pop",
            id_like=["ubuntu", "debian"],
            kernel="7.2.15",
            arch="x86_64",
            available_package_managers=["apt", "flatpak"],
        )
        prompt = PromptBuilder.build_system_prompt(ctx)

        self.assertIn("Pop!_OS", prompt)
        self.assertIn("apt, flatpak", prompt)
        self.assertIn("Português do Brasil", prompt)
        self.assertIn("kored", prompt)

    def test_build_explain_command_prompt(self):
        prompt = PromptBuilder.build_explain_command_prompt("tar -xzvf archive.tar.gz")
        self.assertIn("tar -xzvf archive.tar.gz", prompt)
        self.assertIn("mecânica", prompt)

    def test_build_system_prompt_assisted_mode_includes_fewshot(self):
        from src.executor import ExecutionMode
        ctx = SystemContext(
            distro_name="Pop!_OS",
            distro_version="24.04",
            distro_id="pop",
            id_like=["ubuntu"],
            kernel="7.2.15",
            arch="x86_64",
            available_package_managers=["apt"],
        )
        prompt = PromptBuilder.build_system_prompt(ctx, mode=ExecutionMode.ASSISTED)
        self.assertIn("MODO ASSISTIDO", prompt)
        self.assertIn("kored-action", prompt)
        self.assertIn("which brave-browser", prompt)
        self.assertIn("run_command", prompt)

    def test_build_fix_prompt(self):
        prompt = PromptBuilder.build_fix_prompt("docker run -p 80:80 nginx", "address already in use")
        self.assertIn("docker run -p 80:80 nginx", prompt)
        self.assertIn("address already in use", prompt)
        self.assertIn("Diagnostico do Erro", prompt)


if __name__ == "__main__":
    unittest.main()
