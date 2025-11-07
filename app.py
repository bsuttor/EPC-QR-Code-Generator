import streamlit as st
import qrcode
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw
from urllib.parse import unquote, quote, urlencode
from i18n import (
    get_text,
    get_purpose_options,
    set_streamlit_language,
    render_language_footer,
)


def get_url_params():
    """
    Extract URL parameters for pre-filling form fields.
    Supports the following parameters:
    - name: Beneficiary name
    - iban: Beneficiary IBAN
    - bic: BIC/SWIFT code
    - amount: Payment amount
    - purpose: Purpose code
    - ref: Remittance information/reference
    - debtor_ref: Structured reference
    - lang: Language override
    - hide: Hide all fields except amount (any value activates this)
    - logo: Logo type (default, papas, none)
    """
    params = {}

    # Get URL query parameters from Streamlit
    query_params = st.query_params if hasattr(st, "query_params") else {}

    # Map URL parameter names to internal field names
    param_mapping = {
        "beneficiary_name": "beneficiary_name",
        "beneficiary_iban": "beneficiary_iban",
        "bic_swift": "bic",
        "amount": "amount",
        "purpose_code": "purpose",
        "remittance_info": "remittance_info",
        "structured_ref": "debtor_reference",
        "lang": "language",
        "hide": "hide",
        "logo": "logo",
        # Short aliases for convenience
        "name": "beneficiary_name",
        "iban": "beneficiary_iban",
        "bic": "bic",
        "purpose": "purpose",
        "ref": "remittance_info",
    }

    # Extract and decode parameters
    for url_param, field_name in param_mapping.items():
        if url_param in query_params:
            try:
                # URL decode the parameter value
                value = unquote(query_params[url_param])
                params[field_name] = value
            except Exception as e:
                st.sidebar.warning(f"Invalid URL parameter '{url_param}': {e}")

    return params


def generate_share_url(params: dict) -> str:
    """
    Generate a shareable URL with form parameters.

    Args:
        params: Dictionary of form parameters

    Returns:
        Complete URL with query parameters
    """

    # Map internal field names to URL parameter names
    reverse_mapping = {
        "beneficiary_name": "beneficiary_name",
        "beneficiary_iban": "beneficiary_iban",
        "bic": "bic_swift",
        "amount": "amount",
        "purpose": "purpose_code",
        "remittance_info": "remittance_info",
        "debtor_reference": "structured_ref",
        "language": "lang",
        "logo": "logo",
        "hide": "hide",
    }

    # Build query parameters, filtering out empty values
    query_params = {}
    for field_name, url_param in reverse_mapping.items():
        if field_name in params:
            # Special handling for 'hide' parameter - always include it even if empty
            if field_name == "hide":
                query_params[url_param] = ""
            elif params[field_name]:
                # Handle special cases
                if field_name == "amount" and params[field_name] == 0.0:
                    continue  # Skip zero amounts
                query_params[url_param] = str(params[field_name])

    # Get current URL base (without query parameters)
    if hasattr(st, "query_params"):
        base_url = st.query_params.get("__streamlit_url", "http://localhost:8501")
    else:
        base_url = "http://localhost:8501"  # fallback

    if query_params:
        query_string = urlencode(query_params, safe="", quote_via=quote)
        return f"{base_url}?{query_string}"

    return base_url


def update_url_params(params: dict) -> None:
    """
    Update the browser URL with current form parameters.

    Args:
        params: Dictionary of form parameters to include in URL
    """
    if not hasattr(st, "query_params"):
        return

    # Map internal field names to URL parameter names
    url_mapping = {
        "beneficiary_name": "beneficiary_name",
        "beneficiary_iban": "beneficiary_iban",
        "bic": "bic_swift",
        "amount": "amount",
        "purpose": "purpose_code",
        "remittance_info": "remittance_info",
        "debtor_reference": "structured_ref",
        "language": "lang",
        "logo": "logo",
        "hide": "hide",
    }

    # Clear existing parameters and set new ones
    st.query_params.clear()

    for field_name, value in params.items():
        if field_name in url_mapping:
            url_param = url_mapping[field_name]
            # Special handling for 'hide' parameter - always include it even if empty
            if field_name == "hide":
                st.query_params[url_param] = ""
            elif value and str(value).strip():
                # Only add non-empty values for other parameters
                st.query_params[url_param] = str(value)


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

    # Get URL parameters for pre-filling form
    url_params = get_url_params()

    # Check if fields should be hidden (only show amount)
    hide_fields = "hide" in url_params

    # Override language if specified in URL
    if "language" in url_params:
        url_lang = (
            url_params["language"]
            if url_params["language"] in ["en", "fr", "de", "es", "nl"]
            else lang
        )
        # Update session state if URL language is different
        if url_lang != lang:
            st.session_state.language_selector = url_lang
            lang = url_lang

    st.set_page_config(
        page_title=get_text("main_title", lang),
        page_icon="🏦",
        layout="wide",
    )

    # Create clickable title that links to home page
    st.markdown(
        f"""
        <style>
        .stApp > div:first-child {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        h1 a {{
            text-decoration: none !important;
            color: inherit !important;
        }}
        h1 a:hover {{
            text-decoration: none !important;
            color: inherit !important;
        }}
        </style>
        # [{get_text('main_title', lang)}](/)
        """,
        unsafe_allow_html=True,
    )
    st.markdown(get_text("subtitle", lang))

    # Quick QR from URL section
    with st.expander(get_text("quick_qr_from_url", lang), expanded=False):
        st.markdown(get_text("quick_qr_explanation", lang))

        # Get current URL base
        current_url = "http://localhost:8501"  # Default for local development
        if hasattr(st.context, "url"):
            try:
                current_url = getattr(st.context, "url", current_url)
            except Exception:
                pass

        # Sample URLs with different examples
        sample_urls = {
            "en": {
                "name": "John Doe",
                "iban": "GB82WEST12345698765432",
                "amount": "25.50",
                "ref": "Invoice 123",
            },
            "fr": {
                "name": "Jean Dupont",
                "iban": "FR1420041010050500013M02606",
                "amount": "50.00",
                "ref": "Facture 456",
            },
            "de": {
                "name": "Max Mustermann",
                "iban": "DE89370400440532013000",
                "amount": "75.25",
                "ref": "Rechnung 789",
            },
            "es": {
                "name": "Juan Pérez",
                "iban": "ES9121000418450200051332",
                "amount": "100.00",
                "ref": "Factura 321",
            },
            "nl": {
                "name": "Jan de Vries",
                "iban": "NL91ABNA0417164300",
                "amount": "42.75",
                "ref": "Factuur 2024-456",
            },
        }

        sample = sample_urls.get(lang, sample_urls["en"])
        sample_url = f"{current_url}/?beneficiary_name={sample['name'].replace(' ', '%20')}&beneficiary_iban={sample['iban']}&amount={sample['amount']}&structured_ref={sample['ref'].replace(' ', '%20')}&lang={lang}"

        # Hide mode example
        hide_sample_url = f"{current_url}/?hide&name={sample['name'].replace(' ', '%20')}&iban={sample['iban']}&amount={sample['amount']}&logo=papas&lang={lang}"

        st.markdown("**Regular mode (all fields visible):**")
        st.code(sample_url, language="text")

        st.markdown("**Hide mode (only amount field visible):**")
        st.code(hide_sample_url, language="text")

        col_example1, col_example2, col_example3 = st.columns([1, 1, 1])

        with col_example1:
            if st.button(get_text("quick_qr_try", lang), key="try_sample_url"):
                st.query_params.clear()
                st.query_params["beneficiary_name"] = sample["name"]
                st.query_params["beneficiary_iban"] = sample["iban"]
                st.query_params["amount"] = sample["amount"]
                st.query_params["structured_ref"] = sample["ref"]
                st.query_params["lang"] = lang
                st.rerun()

        with col_example2:
            if st.button("Try Hide Mode", key="try_hide_mode"):
                st.query_params.clear()
                st.query_params["hide"] = ""
                st.query_params["name"] = sample["name"]
                st.query_params["iban"] = sample["iban"]
                st.query_params["amount"] = sample["amount"]
                st.query_params["logo"] = "papas"
                st.query_params["lang"] = lang
                st.rerun()

        with col_example3:
            st.link_button(
                get_text("url_parameters_guide", lang),
                "https://github.com/bsuttor/EPC-QR-Code-Generator/tree/main?tab=readme-ov-file#supported-url-parameters",
            )

    # Show URL sharing info if parameters were detected
    # if url_params and any(k != "language" for k in url_params.keys()):
    #     st.info(f"🔗 {get_text('url_prefilled', lang)}")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header(get_text("payment_info", lang))

        # Show info message when hide mode is active
        # if hide_fields:
        #     st.info(
        #         "🔒 Simplified mode: Only amount field is visible. Other payment details are pre-filled from URL parameters."
        #     )

        # Show info about URL updating when form is generated
        # if url_params:
        #     st.info(get_text("url_prefilled", lang))
        # else:
        #     st.info(get_text("url_updates_info", lang))

        # Beneficiary Information
        if not hide_fields:
            st.subheader(get_text("beneficiary_details", lang))
            beneficiary_name = st.text_input(
                get_text("beneficiary_name", lang) + " *",
                value=url_params.get("beneficiary_name", ""),
                placeholder=get_text("beneficiary_name_placeholder", lang),
                max_chars=70,
                help=get_text("beneficiary_name_help", lang),
            )

            beneficiary_iban = (
                st.text_input(
                    get_text("beneficiary_iban", lang) + " *",
                    value=url_params.get("beneficiary_iban", ""),
                    placeholder=get_text("beneficiary_iban_placeholder", lang),
                    help=get_text("beneficiary_iban_help", lang),
                )
                .replace(" ", "")
                .upper()
            )

            bic = st.text_input(
                get_text("bic_swift", lang),
                value=url_params.get("bic", ""),
                placeholder=get_text("bic_swift_placeholder", lang),
                help=get_text("bic_swift_help", lang),
            ).upper()
        else:
            # Use default/hidden values when hide mode is active
            beneficiary_name = url_params.get("beneficiary_name", "")
            beneficiary_iban = (
                url_params.get("beneficiary_iban", "").replace(" ", "").upper()
            )
            bic = url_params.get("bic", "").upper()

        # Payment Details
        st.subheader(get_text("payment_details", lang))

        # Handle amount from URL parameter
        default_amount = 0.0
        if "amount" in url_params:
            try:
                default_amount = float(url_params["amount"])
            except ValueError:
                st.warning(f"Invalid amount in URL: {url_params['amount']}")

        amount = st.number_input(
            get_text("amount", lang),
            min_value=0.0,
            max_value=999999999.99,
            value=default_amount,
            step=0.01,
            help=get_text("amount_help", lang),
        )

        if not hide_fields:
            debtor_reference = st.text_input(
                get_text("structured_ref", lang),
                value=url_params.get("debtor_reference", ""),
                placeholder=get_text("structured_ref_placeholder", lang),
                max_chars=35,
                help=get_text("structured_ref_help", lang),
            )

            purpose_options = get_purpose_options(lang)
            with st.expander(get_text("purpose_code", lang), expanded=False):
                # Find default purpose index from URL parameter
                purpose_default_index = 0
                purpose_keys = list(purpose_options.keys())
                if "purpose" in url_params and url_params["purpose"] in purpose_keys:
                    purpose_default_index = purpose_keys.index(url_params["purpose"])

                purpose_key = st.selectbox(
                    get_text("purpose_code", lang),
                    options=purpose_keys,
                    index=purpose_default_index,
                    format_func=lambda x: (
                        f"{x} - {purpose_options[x]}" if x else purpose_options[x]
                    ),
                    help=get_text("purpose_help", lang),
                )
        else:
            # Use default/hidden values when hide mode is active
            debtor_reference = url_params.get("debtor_reference", "")
            purpose_options = get_purpose_options(lang)
            purpose_keys = list(purpose_options.keys())
            if "purpose" in url_params and url_params["purpose"] in purpose_keys:
                purpose_key = url_params["purpose"]
            else:
                purpose_key = purpose_keys[0] if purpose_keys else ""

        if not hide_fields:
            with st.expander(get_text("remittance_info", lang), expanded=False):
                remittance_info = st.text_area(
                    get_text("remittance_info", lang),
                    value=url_params.get("remittance_info", ""),
                    placeholder=get_text("remittance_info_placeholder", lang),
                    max_chars=140,
                    help=get_text("remittance_info_help", lang),
                )
        else:
            # Use default/hidden value when hide mode is active
            remittance_info = url_params.get("remittance_info", "")

        # Logo Options
        if not hide_fields:
            st.subheader(get_text("qr_customization", lang))

            # Determine default values from URL parameters
            logo_param = url_params.get("logo", "default").lower()
            default_add_logo = logo_param != "none"

            # Map logo parameter to radio option index
            logo_options = [
                get_text("default_logo", lang),
                get_text("papas_logo", lang),
                get_text("custom_upload", lang),
            ]
            default_logo_index = 0  # default logo
            if logo_param == "papas":
                default_logo_index = 1
            elif logo_param == "custom":
                default_logo_index = 2

            add_logo = st.checkbox(
                get_text("add_logo", lang),
                value=default_add_logo,
                help=get_text("add_logo_help", lang),
            )

            logo_option = st.radio(
                get_text("logo_type", lang),
                logo_options,
                index=default_logo_index,
                disabled=not add_logo,
                help=get_text("logo_type_help", lang),
            )

            custom_logo = None
            if add_logo and logo_option == get_text("papas_logo", lang):
                # Load papas logo
                try:
                    papas_logo = Image.open("logo_papas.jpg").convert("RGBA")
                    custom_logo = papas_logo
                    # Show preview
                    st.image(
                        custom_logo, caption=get_text("logo_preview", lang), width=100
                    )
                except Exception as e:
                    st.error(get_text("error_loading_logo", lang) + str(e))
                    custom_logo = None
            elif add_logo and logo_option == get_text("custom_upload", lang):
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
                            custom_logo,
                            caption=get_text("logo_preview", lang),
                            width=100,
                        )
                    except Exception as e:
                        st.error(get_text("error_loading_logo", lang) + str(e))
                        custom_logo = None
        else:
            # Use default settings when hide mode is active
            # Check URL parameter for logo preference
            logo_param = url_params.get("logo", "default").lower()
            if logo_param == "none":
                add_logo = False
                custom_logo = None
            elif logo_param == "papas":
                add_logo = True
                try:
                    papas_logo = Image.open("logo_papas.jpg").convert("RGBA")
                    custom_logo = papas_logo
                except Exception:
                    custom_logo = None
            else:  # default or any other value
                add_logo = True
                custom_logo = None

        # Validation
        if hide_fields:
            # When hiding fields, use URL parameters for validation
            # Only require amount (visible field), and use defaults for others if not provided
            is_valid = bool(
                beneficiary_name or url_params.get("beneficiary_name")
            ) and bool(beneficiary_iban or url_params.get("beneficiary_iban"))
            # If required fields are missing from URL params, show a message
            if not is_valid:
                st.warning(
                    "Required fields (beneficiary name and IBAN) must be provided in URL parameters when using hide mode."
                )
        else:
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

                    st.success(get_text("qr_code_generated", lang))

                    # Determine logo parameter value
                    logo_param_value = "default"
                    if not add_logo:
                        logo_param_value = "none"
                    elif custom_logo is not None:
                        # Check if it's the papas logo (custom_logo was set from papas logo file)
                        if not hide_fields and logo_option == get_text(
                            "papas_logo", lang
                        ):
                            logo_param_value = "papas"
                        elif (
                            hide_fields
                            and url_params.get("logo", "").lower() == "papas"
                        ):
                            logo_param_value = "papas"
                        else:
                            logo_param_value = "custom"

                    # Update URL parameters to reflect current form state
                    current_params = {
                        "beneficiary_name": beneficiary_name,
                        "beneficiary_iban": beneficiary_iban,
                        "bic": bic,
                        "amount": amount,
                        "purpose": purpose_key,
                        "remittance_info": remittance_info,
                        "debtor_reference": debtor_reference,
                        "language": lang,
                        "logo": logo_param_value,
                    }
                    # Keep hide parameter if it was in the URL
                    if hide_fields:
                        current_params["hide"] = ""
                    update_url_params(current_params)

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

            # URL Sharing functionality
            st.subheader(get_text("share_url", lang))

            # Determine logo parameter from session state or URL params
            logo_param_value = "default"
            if "payment_info" in st.session_state:
                # Try to get from URL params first
                logo_param_value = url_params.get("logo", "default")

            # Generate shareable URL with current form values
            current_params = {
                "beneficiary_name": beneficiary_name,
                "beneficiary_iban": beneficiary_iban,
                "bic": bic,
                "amount": amount,
                "purpose": purpose_key,
                "remittance_info": remittance_info,
                "debtor_reference": debtor_reference,
                "language": lang,
                "logo": logo_param_value,
            }
            # Keep hide parameter if it was in the URL
            if hide_fields:
                current_params["hide"] = ""

            share_url = generate_share_url(current_params)

            # Display shareable URL
            st.text_area(
                get_text("shareable_url", lang),
                value=share_url,
                height=100,
                help=get_text("shareable_url_help", lang),
            )

            # Copy to clipboard button (using st.code for easy copying)
            col_copy1, col_copy2 = st.columns([3, 1])
            with col_copy1:
                if st.button(get_text("copy_url", lang)):
                    st.success(get_text("url_copied", lang))
                    # JavaScript to copy to clipboard
                    st.components.v1.html(
                        f"""
                    <script>
                    navigator.clipboard.writeText('{share_url}').then(function() {{
                        console.log('URL copied to clipboard');
                    }});
                    </script>
                    """,
                        height=0,
                    )

            with col_copy2:
                st.markdown(f"📋 [Preview]({share_url})")

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
            with st.expander(get_text("about_epc_qr", lang), expanded=False):
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

    # Render language selection footer
    render_language_footer()


if __name__ == "__main__":
    main()
