from __future__ import annotations

import unittest

from debrief import SessionHabits
from session_context import session_context_text


class DebriefDialogTest(unittest.TestCase):
    def test_session_context_is_hidden_for_tiny_windows(self) -> None:
        context = session_context_text(SessionHabits(4, 1, 0.25, "Evening"))

        self.assertEqual(context, "")

    def test_session_context_omits_unreliable_timing(self) -> None:
        context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 1, 7.0, 7.0))

        self.assertEqual(context, "Context: 10 reviews · 20% Again · evening")

    def test_session_context_includes_timing_when_most_reviews_are_timed(self) -> None:
        context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 8, 60.0, 7.5))

        self.assertEqual(context, "Context: 10 reviews · 20% Again · evening · 7.5s/card")


if __name__ == "__main__":
    unittest.main()
