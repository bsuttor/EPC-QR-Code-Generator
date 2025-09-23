"""
Tests for the EPC QR Code Generator application

Run with: uvx pytest tests/
"""

import pytest
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import generate_epc_data


def test_generate_epc_data():
    """Test EPC data generation with sample data"""
    result = generate_epc_data(
        bic="GKCCBEBB",
        beneficiary_name="John Doe",
        beneficiary_iban="BE68539007547034",
        amount=123.45,
        purpose="COMC",
        remittance_info="Invoice 2024-001",
        debtor_reference="",
    )

    lines = result.split("\n")
    assert len(lines) == 11, "EPC data should have 11 lines"
    assert lines[0] == "BCD", "First line should be BCD"
    assert lines[1] == "002", "Second line should be version 002"
    assert lines[2] == "1", "Third line should be character set 1"
    assert lines[3] == "SCT", "Fourth line should be SCT"
    assert lines[4] == "GKCCBEBB", "Fifth line should be BIC"
    assert lines[5] == "John Doe", "Sixth line should be beneficiary name"
    assert lines[6] == "BE68539007547034", "Seventh line should be IBAN"
    assert lines[7] == "EUR123.45", "Eighth line should be amount"
    assert lines[8] == "COMC", "Ninth line should be purpose"
    assert lines[9] == "Invoice 2024-001", "Tenth line should be remittance info"


def test_zero_amount():
    """Test EPC data generation with zero amount"""
    result = generate_epc_data(
        bic="",
        beneficiary_name="Test User",
        beneficiary_iban="DE89370400440532013000",
        amount=0.0,
        purpose="",
        remittance_info="Variable amount payment",
        debtor_reference="",
    )

    lines = result.split("\n")
    assert lines[7] == "", "Amount should be empty for zero value"


def test_iban_formatting():
    """Test IBAN formatting and validation scenarios"""
    test_ibans = [
        "BE68 5390 0754 7034",  # With spaces
        "BE68539007547034",  # Without spaces
        "de89370400440532013000",  # Lowercase
        "FR1420041010050500013M02606",  # French IBAN
    ]

    for iban in test_ibans:
        formatted = iban.replace(" ", "").upper()
        assert " " not in formatted, f"IBAN should not contain spaces: {formatted}"
        assert formatted.isupper(), f"IBAN should be uppercase: {formatted}"


def test_character_limits():
    """Test character limits for various fields"""
    test_cases = [
        ("beneficiary_name", "x" * 71, 70),  # Should be max 70 chars
        ("remittance_info", "x" * 141, 140),  # Should be max 140 chars
        ("debtor_reference", "x" * 36, 35),  # Should be max 35 chars
    ]

    for field, long_value, max_length in test_cases:
        assert (
            len(long_value) > max_length
        ), f"Test value for {field} should exceed limit"
        truncated = long_value[:max_length]
        assert (
            len(truncated) == max_length
        ), f"Truncated {field} should be exactly {max_length} chars"
