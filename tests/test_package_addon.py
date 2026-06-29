from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.package_addon import _include


class PackageAddonTest(unittest.TestCase):
    def test_excludes_dotfiles_and_python_cache_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_file = root / ".env"
            pycache_file = root / "__pycache__" / "module.pyc"
            source_file = root / "addon.py"
            env_file.write_text("OPENROUTER_API_KEY=secret", encoding="utf-8")
            pycache_file.parent.mkdir()
            pycache_file.write_bytes(b"cache")
            source_file.write_text("print('ok')", encoding="utf-8")

            self.assertFalse(_include(env_file))
            self.assertFalse(_include(pycache_file))
            self.assertTrue(_include(source_file))


if __name__ == "__main__":
    unittest.main()
