import streamlit as st
import qrcode
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw
import base64
from i18n import get_text, get_purpose_options, set_streamlit_language


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
    # Language selection using i18n system
    lang = set_streamlit_language()
    st.set_page_config(
        page_title=get_text("main_title", lang),
        page_icon="🏦",
        layout="wide",
    )

    st.title(get_text("main_title", lang))
    st.markdown(get_text("subtitle", lang))

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header(get_text("payment_info", lang))

        # Beneficiary Information
        st.subheader(get_text("beneficiary_details", lang))
        beneficiary_name = st.text_input(
            get_text("beneficiary_name", lang) + " *",
            placeholder=get_text("beneficiary_name_placeholder", lang),
            max_chars=70,
            help=get_text("beneficiary_name_help", lang),
        )

        beneficiary_iban = (
            st.text_input(
                get_text("beneficiary_iban", lang) + " *",
                placeholder=get_text("beneficiary_iban_placeholder", lang),
                help=get_text("beneficiary_iban_help", lang),
            )
            .replace(" ", "")
            .upper()
        )

        bic = st.text_input(
            get_text("bic_swift", lang),
            placeholder=get_text("bic_swift_placeholder", lang),
            help=get_text("bic_swift_help", lang),
        ).upper()

        # Payment Details
        st.subheader(get_text("payment_details", lang))
        amount = st.number_input(
            get_text("amount", lang),
            min_value=0.0,
            max_value=999999999.99,
            value=0.0,
            step=0.01,
            help=get_text("amount_help", lang),
        )

        debtor_reference = st.text_input(
            get_text("structured_ref", lang),
            placeholder=get_text("structured_ref_placeholder", lang),
            max_chars=35,
            help=get_text("structured_ref_help", lang),
        )

        purpose_options = get_purpose_options(lang)
        with st.expander(get_text("purpose_code", lang), expanded=False):
            purpose_key = st.selectbox(
                get_text("purpose_code", lang),
                options=list(purpose_options.keys()),
                format_func=lambda x: (
                    f"{x} - {purpose_options[x]}" if x else purpose_options[x]
                ),
                help=get_text("purpose_help", lang),
            )

        with st.expander(get_text("remittance_info", lang), expanded=False):
            remittance_info = st.text_area(
                get_text("remittance_info", lang),
                placeholder=get_text("remittance_info_placeholder", lang),
                max_chars=140,
                help=get_text("remittance_info_help", lang),
            )

        # Logo Options
        st.subheader(get_text("qr_customization", lang))
        add_logo = st.checkbox(
            get_text("add_logo", lang),
            value=True,
            help=get_text("add_logo_help", lang),
        )

        logo_option = st.radio(
            get_text("logo_type", lang),
            [get_text("default_logo", lang), get_text("custom_upload", lang)],
            disabled=not add_logo,
            help=get_text("logo_type_help", lang),
        )

        custom_logo = None
        if add_logo and logo_option == get_text("custom_upload", lang):
            uploaded_file = st.file_uploader(
                get_text("upload_logo", lang),
                type=["png", "jpg", "jpeg"],
                help=get_text("upload_logo_help", lang),
            )
            if uploaded_file is not None:
                try:
                    custom_logo = Image.open(uploaded_file).convert("RGBA")
                    # Show preview
                    st.image(
                        custom_logo, caption=get_text("logo_preview", lang), width=100
                    )
                except Exception as e:
                    st.error(get_text("error_loading_logo", lang) + str(e))
                    custom_logo = None

        # Validation
        is_valid = bool(beneficiary_name and beneficiary_iban)

        if st.button(
            get_text("generate_qr", lang), disabled=not is_valid, type="primary"
        ):
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

                    st.success(get_text("qr_generated_success", lang))

                except Exception as e:
                    st.error(get_text("error_generating_qr", lang) + str(e))
            else:
                st.error(get_text("fill_required_fields", lang))

    with col2:
        st.header(get_text("generated_qr_code", lang))

        if hasattr(st.session_state, "qr_image") and st.session_state.qr_image:
            # Convert PIL image to bytes for display
            img_buffer = BytesIO()
            st.session_state.qr_image.save(img_buffer, format="PNG")
            img_bytes = img_buffer.getvalue()

            # Display QR code
            st.image(img_bytes, caption=get_text("epc_qr_code", lang), width=300)

            # Download button
            st.download_button(
                label=get_text("download_qr", lang),
                data=img_bytes,
                file_name=f"epc_qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png",
            )

            # Display payment summary
            st.subheader(get_text("payment_summary", lang))
            info = st.session_state.payment_info

            with st.expander(get_text("payment_details_summary", lang), expanded=True):
                st.write(
                    f"**{get_text('beneficiary', lang)}** {info['beneficiary_name']}"
                )
                st.write(f"**{get_text('iban', lang)}** {info['beneficiary_iban']}")
                if info["bic"]:
                    st.write(f"**{get_text('bic', lang)}** {info['bic']}")
                if info["amount"] > 0:
                    st.write(
                        f"**{get_text('amount_label', lang)}** EUR {info['amount']:.2f}"
                    )
                else:
                    st.write(
                        f"**{get_text('amount_label', lang)}** {get_text('amount_variable', lang)}"
                    )
                if info["purpose"]:
                    st.write(f"**{get_text('purpose', lang)}** {info['purpose']}")
                if info["remittance_info"]:
                    st.write(
                        f"**{get_text('reference', lang)}** {info['remittance_info']}"
                    )
                if info["debtor_reference"]:
                    st.write(
                        f"**{get_text('structured_reference', lang)}** {info['debtor_reference']}"
                    )

            # Show raw EPC data
            with st.expander(get_text("raw_epc_data", lang)):
                st.code(st.session_state.epc_data)

        else:
            st.info(get_text("fill_payment_info", lang))

            # Information about EPC QR codes
            with st.expander(get_text("about_epc_qr", lang), expanded=True):
                info_text = f"""
{get_text("epc_description", lang)}

{get_text("features", lang)}
- {get_text("sepa_compatible", lang)}
- {get_text("banking_apps", lang)}
- {get_text("epc069_standard", lang)}
- {get_text("flexible_amounts", lang)}
- {get_text("payment_references", lang)}
- {get_text("logo_customization", lang)}

{get_text("required_fields", lang)}
{get_text("required_name_iban", lang)}

{get_text("optional_fields", lang)}
{get_text("optional_list", lang)}

{get_text("logo_guidelines", lang)}
{get_text("logo_tips", lang)}
                """
                st.markdown(info_text)


if __name__ == "__main__":
    main()
