"""
Tests for QR code generation functionality

Tests QR code creation, logo embedding, and image processing
"""

import sys
import os
from io import BytesIO

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_qr_code, generate_epc_data


class TestQRCodeGeneration:
    """Test suite for QR code generation functionality"""

    def test_basic_qr_generation(self):
        """Test basic QR code generation without logo"""
        # Generate test EPC data
        epc_data = generate_epc_data(
            bic="GKCCBEBB",
            beneficiary_name="Test User",
            beneficiary_iban="BE68539007547034",
            amount=100.50,
            purpose="COMC",
            remittance_info="Test payment",
            debtor_reference="",
        )

        # Generate QR code
        qr_image = create_qr_code(epc_data)

        # Verify image properties
        assert qr_image is not None, "QR code image should not be None"
        assert hasattr(qr_image, "size"), "QR image should have size attribute"
        assert qr_image.size[0] > 0, "QR image width should be positive"
        assert qr_image.size[1] > 0, "QR image height should be positive"

    def test_qr_with_logo(self):
        """Test QR code generation with logo"""
        # Create a simple test logo
        from PIL import Image

        # Create a small test image (red square)
        logo = Image.new("RGB", (50, 50), color="red")

        # Generate test EPC data
        epc_data = generate_epc_data(
            bic="GKCCBEBB",
            beneficiary_name="Test User",
            beneficiary_iban="BE68539007547034",
            amount=100.50,
            purpose="COMC",
            remittance_info="Test payment",
            debtor_reference="",
        )

        # Generate QR code with logo
        qr_image = create_qr_code(epc_data, logo)

        # Verify image properties
        assert qr_image is not None, "QR code with logo should not be None"
        assert qr_image.size[0] > 0, "QR image with logo width should be positive"
        assert qr_image.size[1] > 0, "QR image with logo height should be positive"

    def test_qr_data_length(self):
        """Test QR code with various data lengths"""
        test_cases = [
            # Short data
            {"beneficiary_name": "A", "remittance_info": "Test", "amount": 1.00},
            # Medium data
            {
                "beneficiary_name": "John Doe Company Ltd",
                "remittance_info": "Invoice 2024-001 for services rendered",
                "amount": 1234.56,
            },
            # Longer data (but within limits)
            {
                "beneficiary_name": "Very Long Company Name International Limited Corporation",
                "remittance_info": "Very detailed payment reference with lots of information about the transaction",
                "amount": 99999.99,
            },
        ]

        for case in test_cases:
            epc_data = generate_epc_data(
                bic="GKCCBEBB",
                beneficiary_name=case["beneficiary_name"],
                beneficiary_iban="BE68539007547034",
                amount=case["amount"],
                purpose="COMC",
                remittance_info=case["remittance_info"],
                debtor_reference="",
            )

            qr_image = create_qr_code(epc_data)
            assert qr_image is not None, f"QR generation failed for case: {case}"

    def test_qr_image_format(self):
        """Test that QR code images can be saved in different formats"""
        # Generate test data and QR code
        epc_data = generate_epc_data(
            bic="GKCCBEBB",
            beneficiary_name="Test User",
            beneficiary_iban="BE68539007547034",
            amount=100.50,
            purpose="COMC",
            remittance_info="Test payment",
            debtor_reference="",
        )

        qr_image = create_qr_code(epc_data)

        # Test saving as PNG
        png_buffer = BytesIO()
        qr_image.save(png_buffer, format="PNG")
        png_data = png_buffer.getvalue()

        assert len(png_data) > 0, "PNG data should not be empty"
        assert png_data.startswith(b"\x89PNG"), "Should be valid PNG format"

        # Test saving as JPEG
        # Convert to RGB if needed for JPEG
        if qr_image.mode != "RGB":
            qr_image = qr_image.convert("RGB")

        jpeg_buffer = BytesIO()
        qr_image.save(jpeg_buffer, format="JPEG")
        jpeg_data = jpeg_buffer.getvalue()

        assert len(jpeg_data) > 0, "JPEG data should not be empty"
        assert jpeg_data.startswith(b"\xff\xd8"), "Should be valid JPEG format"

    def test_zero_amount_qr(self):
        """Test QR code generation with zero amount (variable payment)"""
        epc_data = generate_epc_data(
            bic="GKCCBEBB",
            beneficiary_name="Test User",
            beneficiary_iban="BE68539007547034",
            amount=0.0,  # Variable amount
            purpose="COMC",
            remittance_info="Variable amount payment",
            debtor_reference="",
        )

        qr_image = create_qr_code(epc_data)
        assert qr_image is not None, "QR generation with zero amount should work"

    def test_empty_optional_fields_qr(self):
        """Test QR code generation with empty optional fields"""
        epc_data = generate_epc_data(
            bic="",  # Optional for SEPA
            beneficiary_name="Test User",
            beneficiary_iban="BE68539007547034",
            amount=100.50,
            purpose="",  # Optional
            remittance_info="",  # Can be empty
            debtor_reference="",  # Optional
        )

        qr_image = create_qr_code(epc_data)
        assert (
            qr_image is not None
        ), "QR generation with empty optional fields should work"

    def test_qr_code_consistency(self):
        """Test that same data generates consistent QR codes"""
        epc_data = generate_epc_data(
            bic="GKCCBEBB",
            beneficiary_name="Test User",
            beneficiary_iban="BE68539007547034",
            amount=100.50,
            purpose="COMC",
            remittance_info="Test payment",
            debtor_reference="",
        )

        # Generate two QR codes with same data
        qr1 = create_qr_code(epc_data)
        qr2 = create_qr_code(epc_data)

        # Convert to bytes for comparison
        buffer1 = BytesIO()
        buffer2 = BytesIO()

        qr1.save(buffer1, format="PNG")
        qr2.save(buffer2, format="PNG")

        assert (
            buffer1.getvalue() == buffer2.getvalue()
        ), "Same data should generate identical QR codes"
