import json
import re
import unittest
from pathlib import Path
from collections import Counter


def load_json(path: Path):
    """Read a UTF-8 JSON file and return the parsed data."""
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


class TestScraper(unittest.TestCase):
    """Black-box tests for the web-scraper pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.dell_path = Path(
            "BE/demo/src/main/resources/sample_datasets/dell_sentiment_analysis.json"
        )
        cls.hp_path = Path(
            "BE/demo/src/main/resources/sample_datasets/hp_sentiment_analysis.json"
        )
        cls.dell_data = load_json(cls.dell_path)

    # ---------- B01 ----------
    def test_b01_dell_count(self):
        """Exactly three Dell laptops saved."""
        # checks if there are 3 Dell laptop objects
        self.assertEqual(len(self.dell_data), 3)
        for obj in self.dell_data:
            # checks if "dell" appears in every product title
            self.assertIn("dell", obj["title"].lower())

    # ---------- B02 ----------
    def test_b02_required_keys_non_empty(self):
        """All mandatory keys exist and are populated."""
        required = {
            "title", "product_id", "price", "image_url", "product_url",
            "average_rating", "review_count", "histogram",
            "histogram_reviews_to_scrape", "review",
            "review_summary", "review_sentiments",
        }
        for obj in self.dell_data:
            # checks if all required keys are present
            self.assertTrue(required.issubset(obj))
            for key in required:
                val = obj[key]
                # checks if value is not None
                self.assertIsNotNone(val)
                if isinstance(val, str):
                    # checks if string isn’t empty/whitespace
                    self.assertNotEqual(val.strip(), "")
                elif isinstance(val, (list, dict)):
                    # checks if list/dict contains at least one item
                    self.assertGreater(len(val), 0)

    # ---------- B03 ----------
    def test_b03_price_format(self):
        """Prices follow $999.99 pattern."""
        price_pattern = re.compile(r"^\$\d+\.\d{2}$")
        for prod in self.dell_data:
            # checks if price matches regex $digits.digits
            self.assertRegex(prod["price"], price_pattern)

    # ---------- B04 ----------
    def test_b04_urls_https(self):
        """All URLs start with https://"""
        for prod in self.dell_data:
            # checks if image_url uses https
            self.assertTrue(prod["image_url"].startswith("https://"))
            # checks if product_url uses https
            self.assertTrue(prod["product_url"].startswith("https://"))

    # ---------- B05 ----------
    def test_b05_review_counts_vs_histogram(self):
        """Review list counts match requested histogram numbers."""
        star_re = re.compile(r"^(\d)")

        def bucket(star_str: str) -> str:
            m = star_re.match(star_str.strip())
            return f"{m.group(1)}_star" if m else "unknown"

        for prod in self.dell_data:
            reviews = prod["review"]
            target = prod["histogram_reviews_to_scrape"]

            # checks if total review count equals sum of targets
            self.assertEqual(len(reviews), sum(target.values()))

            observed = Counter(bucket(r["star_rating"]) for r in reviews)
            for bucket_key, expected in target.items():
                # checks if each star bucket count matches target
                self.assertEqual(observed.get(bucket_key, 0), expected)

    # ---------- B06 ----------
    def test_b06_aspect_whitelist(self):
        """Sentiment aspects stay within approved list."""
        allowed = {
            "AUDIO", "BATTERY", "BUILD_QUALITY", "DESIGN",
            "DISPLAY", "PERFORMANCE", "PORTABILITY", "PRICE", "WARRANTY"
        }
        for prod in self.dell_data:
            for aspect_list in prod["review_sentiments"].values():
                for aspect in aspect_list:
                    # checks if aspect belongs to allowed set
                    self.assertIn(aspect, allowed)

    # ---------- B07 ----------
    def test_b07_fallback_hp(self):
        """Unknown brand falls back to HP laptops (titles contain 'hp')."""
        hp_data = load_json(self.hp_path)
        # checks if exactly 3 HP laptops are returned
        self.assertEqual(len(hp_data), 3)
        for prod in hp_data:
            # checks if "hp" appears in every product title
            self.assertIn("hp", prod["title"].lower())


if __name__ == "__main__":
    unittest.main()