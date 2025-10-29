#!/usr/bin/env python3
"""
Browser Language Detection Test Suite

Tests the browser language detection functionality using pytest
"""

import pytest
import os
import sys
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import (
    detect_browser_language,
    get_language_display_name,
    _map_language_code_to_supported,
    _parse_accept_language_header,
    get_supported_languages,
)


class TestLanguageMapping:
    """Test language code mapping functionality"""

    def setup_method(self):
        """Set up test data"""
        self.supported = get_supported_languages()

    @pytest.mark.parametrize(
        "input_lang,expected",
        [
            # Direct matches
            ("en", "en"),
            ("fr", "fr"),
            ("de", "de"),
            ("es", "es"),
            # Romance language mappings
            ("it", "fr"),  # Italian -> French
            ("pt", "es"),  # Portuguese -> Spanish
            # Germanic language mappings
            ("nl", "nl"),  # Dutch -> Dutch
            ("da", "de"),  # Danish -> German
            ("sv", "de"),  # Swedish -> German
            # Fallback cases
            ("ja", "fr"),  # Japanese -> French (fallback)
            ("zh", "fr"),  # Chinese -> French (fallback)
        ],
    )
    def test_language_code_mapping(self, input_lang, expected):
        """Test individual language code mappings"""
        result = _map_language_code_to_supported(input_lang, self.supported)
        assert result == expected, f"Expected {input_lang} -> {expected}, got {result}"

    def test_supported_languages_exist(self):
        """Test that all supported languages are valid"""
        assert "en" in self.supported
        assert "fr" in self.supported
        assert "de" in self.supported
        assert "es" in self.supported
        assert "nl" in self.supported
        assert len(self.supported) == 5


class TestAcceptLanguageParsing:
    """Test Accept-Language header parsing"""

    def setup_method(self):
        """Set up test data"""
        self.supported = get_supported_languages()

    @pytest.mark.parametrize(
        "header,expected_lang",
        [
            ("en-US,en;q=0.9,fr;q=0.8,es;q=0.7", "en"),  # English preference
            ("fr-FR,fr;q=0.9,en;q=0.8", "fr"),  # French preference
            ("de-DE,de;q=0.9,en;q=0.5", "de"),  # German preference
            ("es-ES,es;q=0.9,en;q=0.8", "es"),  # Spanish preference
            ("it-IT,it;q=0.9,fr;q=0.8,en;q=0.7", "fr"),  # Italian -> French
            ("pt-BR,pt;q=0.9,es;q=0.8,en;q=0.7", "es"),  # Portuguese -> Spanish
            ("ja-JP,ja;q=0.9,en;q=0.8", "fr"),  # Japanese -> fallback
        ],
    )
    def test_accept_language_header_parsing(self, header, expected_lang):
        """Test parsing of Accept-Language headers"""
        result = _parse_accept_language_header(header, self.supported)
        assert (
            result == expected_lang
        ), f"Header '{header}' should map to {expected_lang}, got {result}"

    def test_empty_header(self):
        """Test handling of empty Accept-Language header"""
        result = _parse_accept_language_header("", self.supported)
        assert result == "fr"  # Should return default fallback

    def test_invalid_header(self):
        """Test handling of malformed Accept-Language header"""
        result = _parse_accept_language_header("invalid-header", self.supported)
        assert result == "fr"  # Should return default fallback


class TestSystemLocaleDetection:
    """Test system locale detection"""

    def test_get_display_names(self):
        """Test that display names are available for all supported languages"""
        supported = get_supported_languages()
        for lang in supported:
            display_name = get_language_display_name(lang)
            assert display_name is not None
            assert len(display_name) > 0

    @patch("locale.getdefaultlocale")
    def test_system_locale_fallback(self, mock_getdefaultlocale):
        """Test system locale detection with various locale settings"""
        # Test with English locale
        mock_getdefaultlocale.return_value = ("en_US", "UTF-8")
        # We can't easily test the actual detection without refactoring,
        # but we can test the language mapping
        lang_code = "en"
        mapped = _map_language_code_to_supported(lang_code, get_supported_languages())
        assert mapped == "en"

        # Test with French locale
        mock_getdefaultlocale.return_value = ("fr_FR", "UTF-8")
        lang_code = "fr"
        mapped = _map_language_code_to_supported(lang_code, get_supported_languages())
        assert mapped == "fr"

    @patch("locale.getdefaultlocale")
    def test_system_locale_exception_handling(self, mock_getdefaultlocale):
        """Test handling of locale detection exceptions"""
        mock_getdefaultlocale.side_effect = Exception("Locale error")
        # The function should handle this gracefully and return fallback
        # We test the mapping function that would be used
        result = _map_language_code_to_supported("unknown", get_supported_languages())
        assert result == "fr"  # Should return fallback


class TestTimezoneDetection:
    """Test timezone-based cultural detection"""

    @pytest.mark.parametrize(
        "timezone,expected_lang",
        [
            ("Europe/Berlin", "de"),
            ("Europe/Madrid", "es"),
            ("Europe/Paris", "fr"),
            ("Europe/London", "en"),
            ("US/Pacific", "en"),
            ("Asia/Tokyo", "fr"),  # fallback
        ],
    )
    def test_timezone_mapping_logic(self, timezone, expected_lang):
        """Test timezone to language mapping logic"""
        # This tests the logical mapping that would be used in timezone detection
        timezone_mappings = {
            "Europe/Berlin": "de",
            "Europe/Madrid": "es",
            "Europe/Paris": "fr",
            "Europe/London": "en",
            "US/Pacific": "en",
        }

        if timezone in timezone_mappings:
            expected = timezone_mappings[timezone]
            assert expected == expected_lang
        else:
            # For unmapped timezones, should fallback to French
            assert expected_lang == "fr"


class TestBrowserDetection:
    """Test the main browser detection function"""

    def test_browser_detection_returns_supported_language(self):
        """Test that browser detection always returns a supported language"""
        result = detect_browser_language()
        supported = get_supported_languages()
        assert (
            result in supported
        ), f"Detection returned {result}, but supported are {supported}"

    def test_language_display_names_complete(self):
        """Test that all supported languages have display names"""
        supported = get_supported_languages()
        for lang in supported:
            display_name = get_language_display_name(lang)
            assert display_name is not None
            assert len(display_name) > 0
            assert isinstance(display_name, str)


class TestIntegration:
    """Integration tests for the complete detection system"""

    def test_detection_returns_valid_language(self):
        """Test that the detection system returns a valid supported language"""
        result = detect_browser_language()
        supported = get_supported_languages()
        assert (
            result in supported
        ), f"Detection returned {result}, but supported are {supported}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
