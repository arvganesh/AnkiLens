from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseConfigTest(unittest.TestCase):
    def test_demo_data_is_off_by_default(self) -> None:
        config = json.loads((ROOT / "addon" / "config.json").read_text(encoding="utf-8"))

        self.assertIs(config["demo_data_enabled"], False)

    def test_manifest_has_publishable_metadata(self) -> None:
        manifest = json.loads((ROOT / "addon" / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["package"], "ankilens")
        self.assertEqual(manifest["name"], "AnkiLens")
        self.assertIn("github.com/arvganesh/AnkiLens", manifest["homepage"])
        self.assertNotIn("example.invalid", json.dumps(manifest))


if __name__ == "__main__":
    unittest.main()
