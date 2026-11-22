"""
Testes unitários para o os_inspector usando unittest padrão.
"""

import unittest
from unittest.mock import mock_open, patch
from src.os_inspector import OSInspector, SystemContext


class TestOSInspector(unittest.TestCase):

    def test_system_context_is_debian_based(self):
        ctx = SystemContext(
            distro_name="Pop!_OS",
            distro_version="24.04 LTS",
            distro_id="pop",
            id_like=["ubuntu", "debian", "pop"],
        )
        self.assertTrue(ctx.is_debian_based())

        ctx_arch = SystemContext(
            distro_name="Arch Linux",
            distro_version="",
            distro_id="arch",
            id_like=["arch"],
        )
        self.assertFalse(ctx_arch.is_debian_based())

    def test_os_inspector_parse_mock(self):
        mock_content = """
NAME="Ubuntu"
VERSION="22.04.4 LTS (Jammy Jellyfish)"
ID=ubuntu
ID_LIKE=debian
VERSION_ID="22.04"
"""
        with patch("os.path.isfile", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_content)):
                data = OSInspector._parse_os_release()
                self.assertEqual(data["NAME"], "Ubuntu")
                self.assertEqual(data["ID"], "ubuntu")
                self.assertEqual(data["ID_LIKE"], "debian")
                self.assertEqual(data["VERSION_ID"], "22.04")


if __name__ == "__main__":
    unittest.main()
