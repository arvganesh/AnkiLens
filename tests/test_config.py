from __future__ import annotations

import unittest

from config import load_config


class BonsaiConfigTest(unittest.TestCase):
    def test_uses_safe_defaults_without_config(self) -> None:
        config = load_config(None)

        self.assertEqual(config.minimum_misses, 2)
        self.assertEqual(config.result_limit, 20)
        self.assertEqual(config.lookback_days, 90)
        self.assertEqual(config.debrief_lookback_days, 1)
        self.assertFalse(config.llm_summary_enabled)
        self.assertEqual(config.llm_model, "openrouter/free")
        self.assertEqual(config.llm_api_url, "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(config.llm_api_key_env, "OPENROUTER_API_KEY")
        self.assertEqual(config.llm_max_cards, 40)
        self.assertEqual(config.llm_max_chars, 12000)
        self.assertEqual(config.llm_timeout_seconds, 20)

    def test_accepts_valid_config_values(self) -> None:
        config = load_config(
            {
                "minimum_misses": "3",
                "result_limit": 50,
                "lookback_days": "30",
                "debrief_lookback_days": "2",
                "llm_summary_enabled": True,
                "llm_model": "anthropic/claude-sonnet-4",
                "llm_api_url": "https://example.test/chat",
                "llm_api_key_env": "BONSAI_LLM_KEY",
                "llm_max_cards": 60,
                "llm_max_chars": 15000,
                "llm_timeout_seconds": 30,
            }
        )

        self.assertEqual(config.minimum_misses, 3)
        self.assertEqual(config.result_limit, 50)
        self.assertEqual(config.lookback_days, 30)
        self.assertEqual(config.debrief_lookback_days, 2)
        self.assertTrue(config.llm_summary_enabled)
        self.assertEqual(config.llm_model, "anthropic/claude-sonnet-4")
        self.assertEqual(config.llm_api_url, "https://example.test/chat")
        self.assertEqual(config.llm_api_key_env, "BONSAI_LLM_KEY")
        self.assertEqual(config.llm_max_cards, 60)
        self.assertEqual(config.llm_max_chars, 15000)
        self.assertEqual(config.llm_timeout_seconds, 30)

    def test_bounds_config_values(self) -> None:
        config = load_config(
            {
                "minimum_misses": 0,
                "result_limit": 999,
                "lookback_days": 99999,
                "debrief_lookback_days": 99,
                "llm_max_cards": 999,
                "llm_max_chars": 999999,
                "llm_timeout_seconds": 999,
            }
        )

        self.assertEqual(config.minimum_misses, 1)
        self.assertEqual(config.result_limit, 200)
        self.assertEqual(config.lookback_days, 3650)
        self.assertEqual(config.debrief_lookback_days, 30)
        self.assertEqual(config.llm_max_cards, 200)
        self.assertEqual(config.llm_max_chars, 60000)
        self.assertEqual(config.llm_timeout_seconds, 90)

    def test_ignores_bool_and_invalid_values(self) -> None:
        config = load_config(
            {
                "minimum_misses": True,
                "result_limit": "many",
                "lookback_days": False,
                "debrief_lookback_days": "soon",
                "llm_summary_enabled": "yes",
                "llm_model": "",
                "llm_api_url": "",
                "llm_api_key_env": "",
            }
        )

        self.assertEqual(config.minimum_misses, 2)
        self.assertEqual(config.result_limit, 20)
        self.assertEqual(config.lookback_days, 90)
        self.assertEqual(config.debrief_lookback_days, 1)
        self.assertFalse(config.llm_summary_enabled)
        self.assertEqual(config.llm_model, "openrouter/free")
        self.assertEqual(config.llm_api_url, "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(config.llm_api_key_env, "OPENROUTER_API_KEY")


if __name__ == "__main__":
    unittest.main()
