#!/usr/bin/env python3
"""
Translation management scripts for EPC QR Code Generator
"""

import json
import os
import re
import sys


def validate_translations():
    """Validate JSON syntax in all translation files"""
    print("🔍 Validating JSON syntax in translation files...")

    locales_dir = "locales"
    if not os.path.exists(locales_dir):
        print("❌ locales directory not found")
        return False

    files = [f for f in os.listdir(locales_dir) if f.endswith(".json")]
    valid_count = 0
    total_count = len(files)

    for file in files:
        file_path = os.path.join(locales_dir, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)
            print(f"✅ {file}: Valid JSON")
            valid_count += 1
        except json.JSONDecodeError as e:
            print(f"❌ {file}: Invalid JSON - Line {e.lineno}: {e.msg}")
        except Exception as e:
            print(f"❌ {file}: Error - {e}")

    if valid_count == total_count:
        print(f"🎉 All {total_count} translation files are valid!")
        return True
    else:
        print(f"❌ {valid_count}/{total_count} files are valid")
        return False


def check_translation_consistency():
    """Check translation key consistency across languages"""
    print("🌍 Checking translation consistency...")

    locales_dir = "locales"
    if not os.path.exists(locales_dir):
        print("❌ locales directory not found")
        return False

    files = [f for f in os.listdir(locales_dir) if f.endswith(".json")]
    if not files:
        print("❌ No translation files found")
        return False

    print(f"Found {len(files)} translation files: {files}")

    # Load all translations
    translations = {}
    for file in files:
        lang = file.replace(".json", "")
        try:
            with open(os.path.join(locales_dir, file), "r", encoding="utf-8") as f:
                translations[lang] = json.load(f)
            print(f"✅ {file}: Loaded {len(translations[lang])} keys")
        except json.JSONDecodeError as e:
            print(f"❌ {file}: Invalid JSON - {e}")
            return False
        except Exception as e:
            print(f"❌ {file}: Error - {e}")
            return False

    # Check key consistency
    if len(translations) < 2:
        print("⚠️  Only one translation file found, cannot check consistency")
        return True

    base_lang = list(translations.keys())[0]
    base_keys = set(translations[base_lang].keys())

    all_consistent = True
    for lang, trans in translations.items():
        if lang == base_lang:
            continue

        lang_keys = set(trans.keys())
        missing = base_keys - lang_keys
        extra = lang_keys - base_keys

        if missing:
            print(f"❌ {lang}.json missing keys: {sorted(missing)}")
            all_consistent = False
        if extra:
            print(f"⚠️  {lang}.json extra keys: {sorted(extra)}")

        if not missing and not extra:
            print(f"✅ {lang}.json: All keys consistent")

    if all_consistent:
        print("🎉 Translation check completed successfully!")
    else:
        print("❌ Translation check failed!")

    return all_consistent


def show_translation_stats():
    """Show translation statistics and coverage"""
    print("📊 Translation statistics...")

    locales_dir = "locales"
    if not os.path.exists(locales_dir):
        print("❌ locales directory not found")
        return False

    files = [f for f in os.listdir(locales_dir) if f.endswith(".json")]
    files.sort()

    print("Translation Coverage Report")
    print("=" * 30)

    translations = {}
    for file in files:
        lang = file.replace(".json", "")
        try:
            with open(os.path.join(locales_dir, file), "r", encoding="utf-8") as f:
                translations[lang] = json.load(f)
        except Exception:
            print(f"❌ Could not load {file}")
            continue

    if not translations:
        print("❌ No valid translation files found")
        return False

    # Stats per language
    total_keys = max(len(trans) for trans in translations.values())
    print(f"Total unique keys: {total_keys}")
    print()

    for lang, trans in translations.items():
        key_count = len(trans)
        coverage = (key_count / total_keys * 100) if total_keys > 0 else 0
        flag = {"en": "🇬🇧", "fr": "🇫🇷", "de": "🇩🇪", "es": "🇪🇸"}.get(lang, "🌍")
        print(f"{flag} {lang.upper()}: {key_count:3d} keys ({coverage:5.1f}% coverage)")

    # Find missing keys
    if len(translations) > 1:
        all_keys = set()
        for trans in translations.values():
            all_keys.update(trans.keys())

        print()
        print("Missing Keys Analysis:")
        print("-" * 22)
        for key in sorted(all_keys):
            missing_in = []
            for lang, trans in translations.items():
                if key not in trans:
                    missing_in.append(lang)
            if missing_in:
                print(f"❌ {key}: missing in {missing_in}")

    return True


def sync_translation_keys():
    """Sync translation keys across all languages"""
    print("🔄 Syncing translation keys across languages...")
    print("Note: This will add [TODO: ...] placeholders for missing keys")

    locales_dir = "locales"
    if not os.path.exists(locales_dir):
        print("❌ locales directory not found")
        return False

    files = [f for f in os.listdir(locales_dir) if f.endswith(".json")]
    if not files:
        print("❌ No translation files found")
        return False

    # Load all translations
    translations = {}
    for file in files:
        lang = file.replace(".json", "")
        file_path = os.path.join(locales_dir, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                translations[lang] = json.load(f)
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")
            return False

    # Collect all unique keys
    all_keys = set()
    for trans in translations.values():
        all_keys.update(trans.keys())

    print(f"Found {len(all_keys)} unique keys across {len(translations)} languages")

    # Add missing keys with placeholder values
    changes_made = False
    for lang, trans in translations.items():
        missing_keys = all_keys - set(trans.keys())
        if missing_keys:
            print(f"Adding {len(missing_keys)} missing keys to {lang}.json")
            for key in sorted(missing_keys):
                # Use English as reference if available, otherwise use key name
                if "en" in translations and key in translations["en"]:
                    trans[key] = f'[TODO: {translations["en"][key]}]'
                else:
                    trans[key] = f"[TODO: {key}]"
            changes_made = True

    if changes_made:
        # Write back the updated files
        for lang, trans in translations.items():
            file_path = os.path.join(locales_dir, f"{lang}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(trans, f, ensure_ascii=False, indent=2)
            print(f"✅ Updated {lang}.json")
        print("🎉 Translation sync completed!")
    else:
        print("✅ All translation files are already in sync!")

    return True


def extract_translation_keys():
    """Extract translatable strings from code"""
    print("🔍 Extracting translatable strings from code...")

    # Search for get_text() calls in Python files
    pattern = r'get_text\(["\']([^"\']+)["\']'
    keys = set()

    for root, dirs, files in os.walk("."):
        # Skip hidden directories and common exclude patterns
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in ["__pycache__", "node_modules"]
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = re.findall(pattern, content)
                        for match in matches:
                            keys.add(match)

                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")

    if not keys:
        print("❌ No translation keys found in code")
        return False

    extracted_keys = sorted(keys)
    print(f"Found {len(extracted_keys)} translation keys in code:")
    print()

    # Check against existing translations
    locales_dir = "locales"
    existing_keys = set()

    if os.path.exists(locales_dir):
        try:
            with open(os.path.join(locales_dir, "en.json"), "r", encoding="utf-8") as f:
                existing_translations = json.load(f)
                existing_keys = set(existing_translations.keys())
        except Exception:
            pass

    # Show status of each key
    for key in extracted_keys:
        status = "✅" if key in existing_keys else "❌"
        print(f"{status} {key}")

    missing_keys = set(extracted_keys) - existing_keys
    if missing_keys:
        print(f"\n❌ {len(missing_keys)} keys missing from translations:")
        for key in sorted(missing_keys):
            print(f"  - {key}")
        return False
    else:
        print(f"\n🎉 All {len(extracted_keys)} keys are present in translations!")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 i18n_tools.py <command>")
        print("Commands: validate, check, stats, sync, extract")
        sys.exit(1)

    command = sys.argv[1]
    success = False

    if command == "validate":
        success = validate_translations()
    elif command == "check":
        success = check_translation_consistency()
    elif command == "stats":
        success = show_translation_stats()
    elif command == "sync":
        success = sync_translation_keys()
    elif command == "extract":
        success = extract_translation_keys()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: validate, check, stats, sync, extract")
        sys.exit(1)

    sys.exit(0 if success else 1)
