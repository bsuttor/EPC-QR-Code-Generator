import streamlit as st
import qrcode
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw
import base64


def generate_epc_data(
    bic: str,
    beneficiary_name: str,
    beneficiary_iban: str,
    amount: float,
    purpose: str,
    remittance_info: str,
    debtor_reference: str = "",
):
    """
    Generate EPC QR code data string according to EPC069-12 standard.

    Format:
    BCD
    002
    1
    SCT
    BIC
    Name
    IBAN
    EURAmount
    Purpose
    RemittanceInformation
    DebtorReference
    """
    # Format amount to 2 decimal places
    amount_str = f"EUR{amount:.2f}" if amount > 0 else ""

    # EPC QR code data elements
    epc_data = [
        "BCD",  # Service Tag
        "002",  # Version
        "1",  # Character Set (1 = UTF-8)
        "SCT",  # Identification (SEPA Credit Transfer)
        bic,  # BIC
        beneficiary_name,  # Beneficiary Name
        beneficiary_iban,  # Beneficiary Account (IBAN)
        amount_str,  # Amount
        purpose,  # Purpose
        remittance_info,  # Remittance Information (Unstructured)
        debtor_reference,  # Remittance Information (Structured)
    ]

    return "\n".join(epc_data)


def create_default_logo():
    """Create a simple default logo (Euro symbol)"""
    logo_size = 60
    logo = Image.new("RGBA", (logo_size, logo_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(logo)

    # Create a white circle background
    margin = 5
    draw.ellipse(
        [margin, margin, logo_size - margin, logo_size - margin],
        fill=(255, 255, 255, 255),
        outline=(0, 0, 0, 255),
        width=2,
    )

    # Draw Euro symbol (€)
    # This is a simplified euro symbol
    center_x, center_y = logo_size // 2, logo_size // 2

    # Draw the "C" part of the Euro symbol
    draw.arc(
        [center_x - 15, center_y - 15, center_x + 15, center_y + 15],
        start=45,
        end=315,
        fill=(0, 0, 0, 255),
        width=3,
    )

    # Draw the horizontal lines
    draw.line(
        [center_x - 18, center_y - 5, center_x + 5, center_y - 5],
        fill=(0, 0, 0, 255),
        width=2,
    )
    draw.line(
        [center_x - 18, center_y + 5, center_x + 5, center_y + 5],
        fill=(0, 0, 0, 255),
        width=2,
    )

    return logo


def add_logo_to_qr(qr_img, logo_img=None):
    """Add a logo to the center of the QR code"""
    if logo_img is None:
        logo_img = create_default_logo()

    # Convert QR code to RGBA if it isn't already
    qr_img = qr_img.convert("RGBA")

    # Resize logo to appropriate size (about 1/5 of QR code size)
    qr_width, qr_height = qr_img.size
    logo_size = min(qr_width, qr_height) // 5
    logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Calculate position to center the logo
    pos_x = (qr_width - logo_size) // 2
    pos_y = (qr_height - logo_size) // 2

    # Paste the logo onto the QR code
    qr_img.paste(logo_img, (pos_x, pos_y), logo_img)

    return qr_img


def create_qr_code(data: str, add_logo: bool = True, custom_logo=None):
    """Create QR code from EPC data with optional logo"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction for logo
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Add logo if requested
    if add_logo:
        img = add_logo_to_qr(img, custom_logo)

    return img


def main():
    st.set_page_config(
        page_title="EPC QR Code Generator", page_icon="🏦", layout="wide"
    )

    st.title("🏦 EPC QR Code Generator")
    st.markdown(
        "Generate QR codes for SEPA Credit Transfer according to EPC069-12 standard"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Payment Information")

        # Beneficiary Information
        st.subheader("Beneficiary Details")
        beneficiary_name = st.text_input(
            "Beneficiary Name *",
            placeholder="John Doe",
            max_chars=70,
            help="Maximum 70 characters",
        )

        beneficiary_iban = (
            st.text_input(
                "Beneficiary IBAN *",
                placeholder="BE68539007547034",
                help="International Bank Account Number",
            )
            .replace(" ", "")
            .upper()
        )

        bic = st.text_input(
            "BIC/SWIFT Code",
            placeholder="GKCCBEBB",
            help="Bank Identifier Code (optional for SEPA countries)",
        ).upper()

        # Payment Details
        st.subheader("Payment Details")
        amount = st.number_input(
            "Amount (EUR)",
            min_value=0.0,
            max_value=999999999.99,
            value=0.0,
            step=0.01,
            help="Leave 0.00 for variable amount",
        )

        purpose_options = {
            "": "Not specified",
            "CBFF": "Capital building",
            "CHAR": "Charity payment",
            "COMC": "Commercial payment",
            "CPKC": "Car park charges",
            "DIVI": "Dividend",
            "GOVI": "Government insurance",
            "GSCI": "Government social contribution",
            "INST": "Insurance premium",
            "INTC": "Interest",
            "LIMA": "Liquidity management",
            "OTHR": "Other",
            "RLTI": "Real estate investment",
            "SALA": "Salary",
            "SECU": "Securities",
            "SSBE": "Social security benefit",
            "SUPP": "Supplier payment",
            "TAXS": "Tax payment",
            "TRAD": "Trade",
            "TREA": "Treasury payment",
            "VATX": "VAT payment",
            "WHLD": "Withholding",
        }

        purpose_key = st.selectbox(
            "Purpose Code",
            options=list(purpose_options.keys()),
            format_func=lambda x: (
                f"{x} - {purpose_options[x]}" if x else purpose_options[x]
            ),
            help="ISO 20022 purpose code",
        )

        # Remittance Information
        st.subheader("Remittance Information")
        remittance_info = st.text_area(
            "Remittance Information",
            placeholder="Invoice 2024-001",
            max_chars=140,
            help="Payment reference or description (max 140 characters)",
        )

        debtor_reference = st.text_input(
            "Structured Reference",
            placeholder="RF18539007547034",
            max_chars=35,
            help="Structured creditor reference (max 35 characters)",
        )

        # Logo Options
        st.subheader("QR Code Customization")
        add_logo = st.checkbox(
            "Add logo to QR code center",
            value=True,
            help="Adds a logo in the center of the QR code (uses higher error correction)",
        )

        logo_option = st.radio(
            "Logo type:",
            ["Default (Euro symbol)", "Custom upload"],
            disabled=not add_logo,
            help="Choose between a default Euro symbol or upload your own logo",
        )

        custom_logo = None
        if add_logo and logo_option == "Custom upload":
            uploaded_file = st.file_uploader(
                "Upload your logo",
                type=["png", "jpg", "jpeg"],
                help="Recommended: Square image, transparent background, max 2MB",
            )
            if uploaded_file is not None:
                try:
                    custom_logo = Image.open(uploaded_file).convert("RGBA")
                    # Show preview
                    st.image(custom_logo, caption="Logo preview", width=100)
                except Exception as e:
                    st.error(f"Error loading logo: {str(e)}")
                    custom_logo = None

        # Validation
        is_valid = bool(beneficiary_name and beneficiary_iban)

        if st.button("Generate QR Code", disabled=not is_valid, type="primary"):
            if is_valid:
                try:
                    # Generate EPC data
                    epc_data = generate_epc_data(
                        bic=bic,
                        beneficiary_name=beneficiary_name,
                        beneficiary_iban=beneficiary_iban,
                        amount=amount,
                        purpose=purpose_key,
                        remittance_info=remittance_info,
                        debtor_reference=debtor_reference,
                    )

                    # Create QR code with logo options
                    qr_img = create_qr_code(
                        epc_data, add_logo=add_logo, custom_logo=custom_logo
                    )

                    # Store in session state
                    st.session_state.qr_image = qr_img
                    st.session_state.epc_data = epc_data
                    st.session_state.payment_info = {
                        "beneficiary_name": beneficiary_name,
                        "beneficiary_iban": beneficiary_iban,
                        "bic": bic,
                        "amount": amount,
                        "purpose": purpose_key,
                        "remittance_info": remittance_info,
                        "debtor_reference": debtor_reference,
                    }

                    st.success("QR Code generated successfully!")

                except Exception as e:
                    st.error(f"Error generating QR code: {str(e)}")
            else:
                st.error("Please fill in all required fields (*)")

    with col2:
        st.header("Generated QR Code")

        if hasattr(st.session_state, "qr_image") and st.session_state.qr_image:
            # Convert PIL image to bytes for display
            img_buffer = BytesIO()
            st.session_state.qr_image.save(img_buffer, format="PNG")
            img_bytes = img_buffer.getvalue()

            # Display QR code
            st.image(img_bytes, caption="EPC QR Code", width=300)

            # Download button
            st.download_button(
                label="Download QR Code",
                data=img_bytes,
                file_name=f"epc_qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png",
            )

            # Display payment summary
            st.subheader("Payment Summary")
            info = st.session_state.payment_info

            with st.expander("Payment Details", expanded=True):
                st.write(f"**Beneficiary:** {info['beneficiary_name']}")
                st.write(f"**IBAN:** {info['beneficiary_iban']}")
                if info["bic"]:
                    st.write(f"**BIC:** {info['bic']}")
                if info["amount"] > 0:
                    st.write(f"**Amount:** EUR {info['amount']:.2f}")
                else:
                    st.write("**Amount:** Variable")
                if info["purpose"]:
                    st.write(f"**Purpose:** {info['purpose']}")
                if info["remittance_info"]:
                    st.write(f"**Reference:** {info['remittance_info']}")
                if info["debtor_reference"]:
                    st.write(f"**Structured Reference:** {info['debtor_reference']}")

            # Show raw EPC data
            with st.expander("Raw EPC Data"):
                st.code(st.session_state.epc_data)

        else:
            st.info(
                "Fill in the payment information and click 'Generate QR Code' to create your EPC QR code."
            )

            # Information about EPC QR codes
            with st.expander("About EPC QR Codes", expanded=True):
                st.markdown(
                    """
                **EPC QR codes** enable easy SEPA payments by scanning with banking apps.
                
                **Features:**
                - ✅ SEPA Credit Transfer compatible
                - ✅ Works with most European banking apps
                - ✅ Follows EPC069-12 standard
                - ✅ Supports fixed and variable amounts
                - ✅ Includes payment references
                - ✅ Optional logo customization with high error correction
                
                **Required fields:**
                - Beneficiary name
                - Beneficiary IBAN
                
                **Optional fields:**
                - BIC (recommended for non-SEPA countries)
                - Amount (leave 0 for variable amount)
                - Purpose code
                - Payment reference
                - Logo in center (Euro symbol or custom upload)
                
                **Logo Guidelines:**
                - Square images work best
                - PNG format recommended for transparency
                - Simple designs scan better than complex ones
                - Always test with your banking app
                """
                )


if __name__ == "__main__":
    main()
