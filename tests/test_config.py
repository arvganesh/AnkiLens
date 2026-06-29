from __future__ import annotations

import unittest

from config import load_config


class AnkiLensConfigTest(unittest.TestCase):
    def test_uses_safe_defaults_without_config(self) -> None:
        config = load_config(None)

        self.assertEqual(config.minimum_misses, 2)
        self.assertEqual(config.result_limit, 20)
        self.assertEqual(config.debrief_lookback_days, 1)
        self.assertFalse(config.llm_summary_enabled)
        self.assertEqual(config.llm_model, "inclusionai/ling-2.6-flash")
        self.assertEqual(config.llm_api_key_env, "OPENROUTER_API_KEY")
        self.assertEqual(config.llm_max_cards, 30)
        self.assertFalse(config.demo_data_enabled)

    def test_accepts_valid_values_and_safely_handles_bad_values(self) -> None:
        valid = load_config(
            {
                "minimum_misses": "3",
                "result_limit": 50,
                "debrief_lookback_days": "2",
                "llm_summary_enabled": True,
                "llm_model": "anthropic/claude-sonnet-4",
                "llm_api_key_env": "ANKILENS_LLM_KEY",
                "llm_max_cards": 60,
                "demo_data_enabled": True,
            }
        )
        bounded = load_config({"minimum_misses": 0, "result_limit": 999, "llm_max_cards": 999})
        invalid = load_config({"minimum_misses": True, "llm_summary_enabled": "yes", "demo_data_enabled": "yes"})

        self.assertEqual(valid.minimum_misses, 3)
        self.assertEqual(valid.result_limit, 50)
        self.assertEqual(valid.debrief_lookback_days, 2)
        self.assertTrue(valid.llm_summary_enabled)
        self.assertEqual(valid.llm_model, "anthropic/claude-sonnet-4")
        self.assertEqual(valid.llm_api_key_env, "ANKILENS_LLM_KEY")
        self.assertEqual(valid.llm_max_cards, 60)
        self.assertTrue(valid.demo_data_enabled)
        self.assertEqual(bounded.minimum_misses, 1)
        self.assertEqual(bounded.result_limit, 200)
        self.assertEqual(bounded.llm_max_cards, 200)
        self.assertEqual(invalid.minimum_misses, 2)
        self.assertFalse(invalid.llm_summary_enabled)
        self.assertFalse(invalid.demo_data_enabled)


if __name__ == "__main__":
    unittest.main()
