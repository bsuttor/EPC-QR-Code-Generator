"""
Internationalization (i18n) module for EPC QR Code Generator
"""

import json
import os
from typing import Dict, Any
import streamlit as st
import streamlit.components.v1 as components


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

    def get(self, key: str, lang: str = "fr", **kwargs) -> str:
        """
        Get translated text for a given key and language

        Args:
            key: Translation key (supports nested keys with dots, e.g., 'purpose_codes.COMC')
            lang: Language code (defaults to French)
            **kwargs: Variables to format into the translation string

        Returns:
            Translated text or the key if translation not found
        """
        # Try the requested language first
        if lang in self._translations:
            translations = self._translations[lang]

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

            if value is not None:
                # Format the string with provided kwargs
                if kwargs and isinstance(value, str):
                    try:
                        return value.format(**kwargs)
                    except (KeyError, ValueError):
                        return value
                return value

        # Fallback chain: requested -> French -> English -> key
        fallback_languages = ["fr", "en"]
        if lang in fallback_languages:
            fallback_languages.remove(lang)  # Don't try the same language again

        for fallback_lang in fallback_languages:
            if fallback_lang in self._translations:
                translations = self._translations[fallback_lang]

                # Handle nested keys
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

                if value is not None:
                    # Format the string with provided kwargs
                    if kwargs and isinstance(value, str):
                        try:
                            return value.format(**kwargs)
                        except (KeyError, ValueError):
                            return value
                    return value

        # Return the key itself if no translation found anywhere
        return key

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


def detect_browser_language():
    """Detect browser language and return best matching supported language"""
    languages = get_supported_languages()

    if not languages:
        return "fr"

    # Use session state to cache the detected language
    if "detected_browser_lang" not in st.session_state:
        detected_lang = "fr"  # Default fallback

        # Try multiple detection methods
        try:
            # Method 1: Check if Streamlit has access to request headers
            # This requires Streamlit >= 1.18.0 with experimental features
            if hasattr(st, "context") and hasattr(st.context, "headers"):
                accept_lang = st.context.headers.get("accept-language", "")
                if accept_lang:
                    # Parse Accept-Language header: "en-US,en;q=0.9,fr;q=0.8"
                    detected_lang = _parse_accept_language_header(
                        accept_lang, languages
                    )
        except Exception:
            pass

        # Method 2: Use system locale as approximation
        if detected_lang == "fr":  # Only if not detected above
            try:
                import locale

                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    lang_code = system_locale.split("_")[0].lower()
                    detected_lang = _map_language_code_to_supported(
                        lang_code, languages
                    )
            except Exception:
                pass

        # Method 3: Check timezone as cultural indicator
        if detected_lang == "fr":  # Only if not detected above
            try:
                import datetime

                # Try to infer from system timezone
                local_tz = str(datetime.datetime.now().astimezone().tzinfo)
                if "Europe/Berlin" in local_tz or "Europe/Zurich" in local_tz:
                    if "de" in languages:
                        detected_lang = "de"
                elif "Europe/Madrid" in local_tz or "Europe/Barcelona" in local_tz:
                    if "es" in languages:
                        detected_lang = "es"
                elif "Europe/London" in local_tz:
                    if "en" in languages:
                        detected_lang = "en"
            except Exception:
                pass

        st.session_state.detected_browser_lang = detected_lang

        # Store detection method for debugging
        st.session_state.detection_method = "system_locale"

    return st.session_state.detected_browser_lang


def _parse_accept_language_header(accept_lang: str, supported_languages: list) -> str:
    """Parse Accept-Language header and return best matching supported language"""
    # Parse "en-US,en;q=0.9,fr;q=0.8,es;q=0.7"
    languages_with_priority = []

    for lang_item in accept_lang.split(","):
        lang_item = lang_item.strip()
        if ";q=" in lang_item:
            lang, priority = lang_item.split(";q=")
            priority = float(priority)
        else:
            lang, priority = lang_item, 1.0

        # Extract language code (e.g., 'en-US' -> 'en')
        lang_code = lang.split("-")[0].lower()
        languages_with_priority.append((lang_code, priority))

    # Sort by priority (highest first)
    languages_with_priority.sort(key=lambda x: x[1], reverse=True)

    # Find first supported language
    for lang_code, _ in languages_with_priority:
        if lang_code in supported_languages:
            return lang_code

        # Try mapping if not direct match
        mapped = _map_language_code_to_supported(lang_code, supported_languages)
        if mapped in supported_languages:
            return mapped

    return "fr"  # fallback


def _map_language_code_to_supported(
    detected_lang: str, supported_languages: list
) -> str:
    """Map detected language code to supported language, with intelligent fallbacks"""
    # Direct match
    if detected_lang in supported_languages:
        return detected_lang

    # Language family mappings
    language_mappings = {
        # Germanic languages -> German or English
        "de": "de",
        "at": "de",
        "ch": "de",  # German, Austrian, Swiss
        "en": "en",
        "us": "en",
        "gb": "en",
        "au": "en",
        "ca": "en",  # English variants
        # Romance languages -> French or Spanish
        "fr": "fr",
        "be": "fr",  # French, Belgian
        "es": "es",
        "mx": "es",
        "ar": "es",
        "co": "es",  # Spanish variants
        "it": "fr",  # Italian -> French (similar Romance language)
        "pt": "es",  # Portuguese -> Spanish (similar Romance language)
        # Other European languages -> closest available
        "nl": "de",  # Dutch -> German
        "da": "de",  # Danish -> German
        "sv": "de",  # Swedish -> German
        "no": "de",  # Norwegian -> German
        "fi": "de",  # Finnish -> German
        "pl": "de",  # Polish -> German
    }

    mapped_lang = language_mappings.get(detected_lang, "fr")  # Default to French
    return mapped_lang if mapped_lang in supported_languages else "fr"


def set_streamlit_language():
    """Set up language selection in Streamlit sidebar with browser language detection"""
    languages = get_supported_languages()

    if not languages:
        return "fr"  # Default to French even if no translations loaded

    # Detect browser language as default
    browser_lang = detect_browser_language()
    default_index = 0
    if browser_lang in languages:
        default_index = languages.index(browser_lang)

    with st.sidebar:
        st.markdown("### 🌍 Language")

        # Show detected language info
        detection_method = st.session_state.get("detection_method", "default")
        if browser_lang != "fr" or detection_method != "default":
            detected_display = get_language_display_name(browser_lang)
            if detection_method == "system_locale":
                st.caption(f"🔍 Auto-detected: {detected_display}")
            else:
                st.caption(f"🌐 Browser: {detected_display}")

        selected_lang = st.selectbox(
            "",
            languages,
            index=default_index,
            format_func=get_language_display_name,
            key="language_selector",
            label_visibility="collapsed",
            help="Language auto-detected from system preferences. You can change it anytime.",
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
