#!/usr/bin/env python3
"""
Test runner script for EPC QR Code Generator

This script can run all tests or specific test suites using pytest
"""

import sys
import os
import subprocess
from pathlib import Path


def check_pytest_available():
    """Check if pytest is available"""
    try:
        subprocess.run(
            [sys.executable, "-c", "import pytest"], check=True, capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def run_with_uvx(args):
    """Run pytest using uvx with all required dependencies"""
    cmd = [
        "uvx",
        "--with",
        "pytest",
        "--with",
        "streamlit",
        "--with",
        "qrcode[pil]",
        "--with",
        "pillow",
        "--with",
        "ipdb",
        "pytest",
        "--pdb",
        "-s",
    ] + args
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd)


def run_with_python(args):
    """Run pytest with python -m pytest"""
    cmd = [sys.executable, "-m", "pytest"] + args
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd)


def main():
    """Main test runner"""
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Parse arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else ["tests/"]

    # Add verbose flag if not specified
    if not any(arg.startswith("-v") for arg in args):
        args.append("-v")

    print("🧪 EPC QR Code Generator - Test Runner")
    print("=" * 50)

    print("📦 Using uvx to run pytest")
    result = run_with_uvx(args)

    # Print summary
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
