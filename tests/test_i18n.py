"""
Tests for the i18n (internationalization) system

Tests translation loading, key lookups, and language support
"""

import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import get_text, get_supported_languages, get_language_display_name, I18n


class TestI18nSystem:
    """Test suite for the internationalization system"""

    def test_supported_languages(self):
        """Test that all expected languages are supported"""
        languages = get_supported_languages()
        expected_languages = {"en", "fr", "de", "es"}

        assert (
            len(languages) >= 4
        ), f"Expected at least 4 languages, got {len(languages)}"
        assert expected_languages.issubset(
            set(languages)
        ), f"Missing expected languages. Got: {languages}"

    def test_language_display_names(self):
        """Test that all supported languages have display names"""
        languages = get_supported_languages()

        for lang in languages:
            display_name = get_language_display_name(lang)
            assert (
                display_name != lang
            ), f"Display name for {lang} should be different from code"
            assert (
                len(display_name) > 2
            ), f"Display name for {lang} should be descriptive"

    def test_basic_translations(self):
        """Test basic translation functionality"""
        test_keys = [
            "main_title",
            "subtitle",
            "beneficiary_name",
            "amount",
            "beneficiary_iban",
        ]

        languages = get_supported_languages()

        for key in test_keys:
            for lang in languages:
                translation = get_text(key, lang)
                assert (
                    translation is not None
                ), f"Translation for {key} in {lang} should not be None"
                assert (
                    len(translation) > 0
                ), f"Translation for {key} in {lang} should not be empty"
                # Should not return the key itself (unless it's fallback)
                if lang == "en":
                    assert (
                        translation != key
                    ), f"English translation for {key} should not be the key itself"

    def test_nested_translations(self):
        """Test nested translation keys like purpose_codes.CBFF"""
        purpose_codes = ["CBFF", "CHAR", "COMC", "CPKC", "DIVI"]
        languages = get_supported_languages()

        for code in purpose_codes:
            nested_key = f"purpose_codes.{code}"
            for lang in languages:
                translation = get_text(nested_key, lang)
                assert (
                    translation is not None
                ), f"Purpose code {code} should have translation in {lang}"
                assert (
                    len(translation) > 2
                ), f"Purpose code {code} translation in {lang} should be descriptive"
                assert (
                    translation != code
                ), f"Translation should not be the same as code {code}"

    def test_fallback_to_english(self):
        """Test fallback behavior when translation is missing"""
        # Test with a key that might not exist in all languages
        test_key = "main_title"  # This should exist in all languages

        # Get English version first
        english_translation = get_text(test_key, "en")
        assert english_translation is not None

        # Test other languages
        for lang in get_supported_languages():
            translation = get_text(test_key, lang)
            assert (
                translation is not None
            ), f"Should get translation or fallback for {lang}"

    def test_missing_key_fallback(self):
        """Test behavior with completely missing keys"""
        missing_key = "this_key_does_not_exist_anywhere"

        # Should return the key itself as fallback
        result = get_text(missing_key, "en")
        assert result == missing_key, f"Missing key should return the key itself"

    def test_i18n_class_initialization(self):
        """Test I18n class can be instantiated properly"""
        i18n = I18n()

        # Test that translations are loaded
        languages = i18n.get_supported_languages()
        assert len(languages) >= 4, "I18n should load multiple languages"

        # Test basic functionality
        text = i18n.get("main_title", "en")
        assert (
            text is not None and len(text) > 0
        ), "I18n should return valid translations"

    def test_translation_consistency(self):
        """Test that all languages have the same set of basic keys"""
        basic_keys = [
            "main_title",
            "subtitle",
            "beneficiary_name",
            "beneficiary_iban",
            "amount",
        ]

        languages = get_supported_languages()
        english_keys_work = True

        # First verify English has all keys
        for key in basic_keys:
            english_text = get_text(key, "en")
            if english_text == key:  # Key not found, returned itself
                english_keys_work = False
                break

        assert english_keys_work, "English translations should exist for basic keys"

        # Test other languages have translations (may fallback to English)
        for lang in languages:
            if lang == "en":
                continue
            for key in basic_keys:
                translation = get_text(key, lang)
                assert (
                    translation is not None
                ), f"Should have translation or fallback for {key} in {lang}"
                assert (
                    len(translation) > 0
                ), f"Translation for {key} in {lang} should not be empty"

    @pytest.mark.parametrize("language", ["en", "fr", "de", "es"])
    def test_specific_language_translations(self, language):
        """Test that specific languages have proper translations"""
        # Test main title translation
        main_title = get_text("main_title", language)
        assert (
            "QR" in main_title or "qr" in main_title.lower()
        ), f"Main title in {language} should mention QR"

        # Test amount field
        amount_text = get_text("amount", language)
        assert "EUR" in amount_text, f"Amount field in {language} should mention EUR"

    def test_purpose_codes_completeness(self):
        """Test that purpose codes are complete across all languages"""
        # Standard EPC purpose codes that should be available
        required_purpose_codes = [
            "CBFF",
            "CHAR",
            "COMC",
            "CPKC",
            "DIVI",
            "GOVI",
            "INST",
            "INTC",
            "LIMA",
            "OTHR",
        ]
        languages = get_supported_languages()

        for code in required_purpose_codes:
            for lang in languages:
                translation = get_text(f"purpose_codes.{code}", lang)
                assert (
                    translation != f"purpose_codes.{code}"
                ), f"Purpose code {code} should have translation in {lang}"
                assert (
                    len(translation) > 3
                ), f"Purpose code {code} translation in {lang} should be descriptive"
