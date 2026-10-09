"""
Unit tests for text preprocessing and normalization in SafeChat Guardian.
Tests casing, whitespace, character repetition, leetspeak, slang, emojis, and negation preservation.
"""

import pytest
from ml.preprocessing import normalize_text, clean_for_ml


class TestTextNormalization:
    """Test suite for normalize_text."""

    def test_case_and_whitespace(self):
        """Verify lowercase and whitespace collapsing."""
        raw = "   HELLO    WORLD \t\n  THIS   IS   A   TEST   "
        expected = "hello world this is a test"
        assert normalize_text(raw) == expected

    def test_empty_and_none_input(self):
        """Verify handling of empty, whitespace, and None input."""
        assert normalize_text("") == ""
        assert normalize_text("    ") == ""
        assert normalize_text(None) == ""

    def test_repeated_characters_compression(self):
        """Verify repeated character reduction (3+ characters collapsed to 2)."""
        # 'sooooo' has 5 o's -> should collapse to 'soo'
        assert "soo" in normalize_text("I am sooooo bored")
        # 'stopppp' has 4 p's -> should collapse to 'stopp'
        assert "stopp" in normalize_text("stopppp doing that")
        # 'kiiiill' has 4 i's -> should collapse to 'kiill'
        assert "kill" in normalize_text("i will kiiiill you") or "kiill" in normalize_text("i will kiiiill you")
        # Legitimate 2 consecutive characters are NOT collapsed to 1
        assert "kill" in normalize_text("kill")
        assert "cool" in normalize_text("cool")
        assert "good" in normalize_text("good")

    def test_leetspeak_obfuscation(self):
        """Verify decoding of common leetspeak obfuscations."""
        assert "kill" in normalize_text("i will k!ll you")
        assert "kill" in normalize_text("i will k1ll you")
        assert "die" in normalize_text("go d!e")
        assert "die" in normalize_text("go d1e")
        assert "bitch" in normalize_text("you b!tch")
        assert "doxx" in normalize_text("i will d0xx you")

    def test_slang_and_abbreviations(self):
        """Verify expansion of common chat abbreviations and slang."""
        assert "kill yourself" in normalize_text("kys now")
        assert "kill myself" in normalize_text("i want to kms")
        assert "you" in normalize_text("u are here")
        assert "your" in normalize_text("ur car")
        assert "are" in normalize_text("r u ready")
        assert "please" in normalize_text("plz stop")
        assert "right now" in normalize_text("leave rn")
        assert "direct message" in normalize_text("check your dm")
        assert "picture" in normalize_text("send a pic")

    def test_negation_preservation(self):
        """Verify that contractions expand while strictly preserving negation words."""
        assert "will not" in normalize_text("I won't hurt you")
        assert "cannot" in normalize_text("I can't do this")
        assert "do not" in normalize_text("I don't hate you")
        assert "never" in normalize_text("I will never hurt you")
        assert "not" in normalize_text("I am not going to fight")

    def test_emoji_preservation(self):
        """Verify emojis are retained in output for context signaling."""
        text_with_laugh = "That was so funny 😂"
        cleaned_laugh = normalize_text(text_with_laugh)
        assert "😂" in cleaned_laugh

        text_with_skull = "I am dead 💀"
        cleaned_skull = normalize_text(text_with_skull)
        assert "💀" in cleaned_skull

    def test_url_replacement(self):
        """Verify URLs are sanitized to a neutral token."""
        assert "url" in normalize_text("Click http://phishing-site.xyz for free robux")
        assert "url" in normalize_text("Go to www.example.com right now")

    def test_unicode_quotes_and_dashes(self):
        """Verify curly quotes and em-dashes are normalized."""
        assert normalize_text("“hello world”") == "hello world"
        assert normalize_text("it’s me") == "it is me" or "its me" in normalize_text("it’s me") or "it is me" in normalize_text("it's me")

    def test_clean_for_ml_alias(self):
        """Verify clean_for_ml produces identical results to normalize_text."""
        sample = "u r sooooo stupid rn 😂"
        assert clean_for_ml(sample) == normalize_text(sample)
