"""Regression tests for inline media and the unchanged card transport gates."""
import base64
import json
import random
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

import validate_bundle as validator


def png_bytes():
    """Build a valid PNG large enough to exercise the former URL-size defect."""
    width, height = 160, 80
    rng = random.Random(17)
    pixels = b"".join(b"\x00" + rng.randbytes(width * 3) for _ in range(height))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


def fixture_card(url=None, mime_type="image/png", placement="explanation"):
    card = {
        "question": "What is the source of power in this transport fixture?",
        "answer": "The fixture's vehicle supply.",
        "explanation": "The fixture specifies a supply feeding its module.",
        "evidence": "The fixture's vehicle supply feeds its module.",
        "source": {"sourceTitle": "Transport validation fixture"},
        "cardType": "qa", "confidence": 0.96,
        "idempotencyKey": "fixture:transport:power-source",
    }
    if url is not None:
        card["media"] = [{"title": "Fixture PNG", "mimeType": mime_type,
                          "url": url, "placement": placement}]
    return card


class MediaTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = png_bytes()
        cls.uri = "data:image/png;base64," + base64.b64encode(cls.raw).decode("ascii")

    def check_card(self, card):
        return validator.validate_card(card, 1, set(), set(), set(), True)

    def test_original_bytes_larger_than_short_url_limit_survive(self):
        self.assertGreater(len(self.uri), 8000)
        self.assertTrue(self.check_card(fixture_card(self.uri)))
        self.assertEqual(base64.b64decode(self.uri.split(",", 1)[1]), self.raw)

    def test_cli_accepts_an_image_bearing_strict_bundle(self):
        with tempfile.TemporaryDirectory(prefix="flashcard-transport-") as directory:
            root = Path(directory)
            (root / "cards.jsonl").write_text(json.dumps(fixture_card(self.uri)) + "\n", encoding="utf-8")
            (root / "manifest.json").write_text(json.dumps({
                "format": "hub-flashcards-v1", "version": 1,
                "deckName": "Transport fixture", "cardsFile": "cards.jsonl",
                "generator": {"workflow": "deep-flashcards-v2"},
            }), encoding="utf-8")
            result = subprocess.run([sys.executable, str(Path(validator.__file__)), "--strict", str(root / "manifest.json")],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("OK: 1 cards", result.stdout)

    def test_bad_base64_is_rejected(self):
        for payload in ("%%%%", "a", "YWJj$"):
            with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, "malformed Base64"):
                self.check_card(fixture_card("data:image/png;base64," + payload))

    def test_mime_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "MIME type"):
            self.check_card(fixture_card(self.uri, mime_type="image/jpeg"))

    def test_missing_or_empty_data_is_rejected(self):
        for url in ("data:image/png;base64", "data:image/png;base64,", "data:image/png,"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.check_card(fixture_card(url))

    def test_percent_encoded_svg_remains_supported(self):
        self.assertTrue(self.check_card(fixture_card(
            "data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%2F%3E",
            mime_type="image/svg+xml")))

    def test_malformed_percent_encoding_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "percent-encoded"):
            self.check_card(fixture_card("data:image/svg+xml,%XZ", mime_type="image/svg+xml"))

    def test_inline_payload_keeps_file_size_ceiling(self):
        with self.assertRaisesRegex(ValueError, "16 MB"):
            validator.validate_media_url("data:image/png;base64," + "a" * validator.MAX_BYTES, "image/png", "fixture")

    def test_short_locators_remain_supported(self):
        for url in ("https://example.test/image.png", "http://example.test/image.png",
                    "hub-media://transport-fixture", "craft-media://transport-fixture"):
            with self.subTest(url=url):
                self.assertTrue(self.check_card(fixture_card(url)))

    def test_oversized_reference_and_file_url_are_rejected(self):
        for url in ("https://example.test/" + "x" * 8000, "file:///fixture.png"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.check_card(fixture_card(url))

    def test_placement_gate_still_applies(self):
        with self.assertRaisesRegex(ValueError, "placement"):
            self.check_card(fixture_card(self.uri, placement="front"))

    def test_text_only_cards_remain_supported(self):
        self.assertTrue(self.check_card(fixture_card()))


if __name__ == "__main__":
    unittest.main()
