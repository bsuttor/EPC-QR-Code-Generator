"""
Internationalization (i18n) module for EPC QR Code Generator
"""

import json
import os
from typing import Dict, Any
import streamlit as st


class I18n:
    """Internationalization handler"""

    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = locales_dir
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._supported_languages = []
        self._load_translations()

    def _load_translations(self):
        """Load all translation files from the locales directory"""
        if not os.path.exists(self.locales_dir):
            print(f"Warning: Locales directory '{self.locales_dir}' not found")
            return

        for filename in os.listdir(self.locales_dir):
            if filename.endswith(".json"):
                lang_code = filename[:-5]  # Remove .json extension
                filepath = os.path.join(self.locales_dir, filename)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        translations = json.load(f)
                        self._translations[lang_code] = translations
                        self._supported_languages.append(lang_code)
                        print(f"Loaded translations for '{lang_code}' from {filename}")
                except Exception as e:
                    print(f"Error loading translations from {filename}: {e}")

    def get_supported_languages(self) -> list:
        """Get list of supported language codes"""
        return self._supported_languages.copy()

    def get_language_display_name(self, lang_code: str) -> str:
        """Get display name for language code"""
        display_names = {
            "en": "🇬🇧 English",
            "fr": "🇫🇷 Français",
            "de": "🇩🇪 Deutsch",
            "es": "🇪🇸 Español",
            "it": "🇮🇹 Italiano",
            "nl": "🇳🇱 Nederlands",
            "pt": "🇵🇹 Português",
            "pl": "🇵🇱 Polski",
            "sv": "🇸🇪 Svenska",
            "da": "🇩🇰 Dansk",
            "no": "🇳🇴 Norsk",
            "fi": "🇫🇮 Suomi",
        }
        return display_names.get(lang_code, f"{lang_code.upper()}")

    def get(self, key: str, lang: str = "en", **kwargs) -> str:
        """
        Get translated text for a given key and language

        Args:
            key: Translation key (supports nested keys with dots, e.g., 'purpose_codes.COMC')
            lang: Language code
            **kwargs: Variables to format into the translation string

        Returns:
            Translated text or the key if translation not found
        """
        if lang not in self._translations:
            lang = "fr"  # Fallback to English

        translations = self._translations.get(lang, {})

        # Handle nested keys (e.g., 'purpose_codes.COMC')
        if "." in key:
            keys = key.split(".")
            value = translations
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    value = None
                    break
        else:
            value = translations.get(key)

        # Fallback to English if not found in requested language
        if value is None and lang != "en":
            return self.get(key, "en", **kwargs)

        # Return the key itself if no translation found
        if value is None:
            return key

        # Format the string with provided kwargs
        if kwargs and isinstance(value, str):
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value

        return value

    def get_purpose_codes(self, lang: str = "fr") -> Dict[str, str]:
        """Get purpose codes dictionary for the given language"""
        return self.get("purpose_codes", lang) or {}


# Global i18n instance
_i18n = I18n()


def get_text(key: str, lang: str = "fr", **kwargs) -> str:
    """Convenience function to get translated text"""
    return _i18n.get(key, lang, **kwargs)


def get_purpose_options(lang: str = "fr") -> Dict[str, str]:
    """Get purpose options translated"""
    return _i18n.get_purpose_codes(lang)


def get_supported_languages() -> list:
    """Get list of supported language codes"""
    return _i18n.get_supported_languages()


def get_language_display_name(lang_code: str) -> str:
    """Get display name for language code"""
    return _i18n.get_language_display_name(lang_code)


def set_streamlit_language():
    """Set up language selection in Streamlit sidebar"""
    languages = get_supported_languages()

    if not languages:
        return "en"

    with st.sidebar:
        st.markdown("### 🌍 Language")
        selected_lang = st.selectbox(
            "",
            languages,
            format_func=get_language_display_name,
            key="language_selector",
            label_visibility="collapsed",
        )

        # Show translation completeness info
        if st.checkbox("Show translation info", False):
            for lang in languages:
                translations = _i18n._translations.get(lang, {})
                total_keys = len(translations)
                st.write(f"{get_language_display_name(lang)}: {total_keys} keys")

    return selected_lang


# Initialize on import
if __name__ != "__main__":
    # Auto-load translations when imported
    pass
