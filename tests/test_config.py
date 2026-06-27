from __future__ import annotations

import unittest

from config import load_config


class BonsaiConfigTest(unittest.TestCase):
    def test_uses_safe_defaults_without_config(self) -> None:
        config = load_config(None)

        self.assertEqual(config.minimum_misses, 2)
        self.assertEqual(config.result_limit, 20)
        self.assertEqual(config.lookback_days, 90)

    def test_accepts_valid_config_values(self) -> None:
        config = load_config({"minimum_misses": "3", "result_limit": 50, "lookback_days": "30"})

        self.assertEqual(config.minimum_misses, 3)
        self.assertEqual(config.result_limit, 50)
        self.assertEqual(config.lookback_days, 30)

    def test_bounds_config_values(self) -> None:
        config = load_config({"minimum_misses": 0, "result_limit": 999, "lookback_days": 99999})

        self.assertEqual(config.minimum_misses, 1)
        self.assertEqual(config.result_limit, 200)
        self.assertEqual(config.lookback_days, 3650)

    def test_ignores_bool_and_invalid_values(self) -> None:
        config = load_config({"minimum_misses": True, "result_limit": "many", "lookback_days": False})

        self.assertEqual(config.minimum_misses, 2)
        self.assertEqual(config.result_limit, 20)
        self.assertEqual(config.lookback_days, 90)


if __name__ == "__main__":
    unittest.main()
