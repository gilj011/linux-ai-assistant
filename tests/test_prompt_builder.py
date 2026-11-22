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


if __name__ == "__main__":
    unittest.main()
