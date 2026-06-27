from __future__ import annotations

import unittest

from content_text import clean_card_text


class ContentTextTest(unittest.TestCase):
    def test_strips_basic_html_and_collapses_whitespace(self) -> None:
        text = clean_card_text("<div>Aortic<br>regurgitation</div>\n\n<b>murmur</b>")

        self.assertEqual(text, "Aortic regurgitation murmur")

    def test_decodes_entities_and_splits_fields(self) -> None:
        text = clean_card_text("Na&lt;sup&gt;+&lt;/sup&gt;\x1fHigh &amp; low")

        self.assertEqual(text, "Na + High & low")


if __name__ == "__main__":
    unittest.main()
