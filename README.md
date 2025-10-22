# EPC QR Code Generator / Générateur de QR Code EPC

https://lespapas.streamlit.app/

A multilingual Streamlit web application that generates QR codes for SEPA Credit Transfer according to the EPC069-12 standard. This allows users to create payment QR codes that can be scanned by European banking applications.

*Une application web Streamlit multilingue qui génère des QR codes pour les virements SEPA selon la norme EPC069-12. Cela permet aux utilisateurs de créer des QR codes de paiement qui peuvent être scannés par les applications bancaires européennes.*

## Features / Fonctionnalités

- ✅ **EPC069-12 Compliant**: Generates QR codes following the official European Payment Council standard
- ✅ **SEPA Compatible**: Works with all SEPA Credit Transfer enabled banks
- ✅ **Multilingual Interface**: Full support for 4 languages (🇬🇧 🇫🇷 🇩🇪 🇪🇸)
- ✅ **Auto Language Detection**: Automatically detects user's browser/system language
- ✅ **User Friendly**: Clean, intuitive web interface built with Streamlit  
- ✅ **Flexible Amounts**: Support for both fixed and variable payment amounts
- ✅ **Complete Payment Info**: Includes beneficiary details, references, and purpose codes
- ✅ **Custom Logos**: Add logos to the center of QR codes (default Euro symbol or custom upload)
- ✅ **Smart Error Correction**: Uses high error correction when logos are added
- ✅ **Instant Download**: Download generated QR codes as PNG images
- ✅ **Real-time Validation**: Input validation with helpful error messages

## Screenshot

The application provides a clean interface where users can:
- Enter beneficiary information (name, IBAN, BIC)
- Specify payment amount and purpose
- Add payment references and descriptions  
- Generate and download QR codes instantly

## Quick Start

### Prerequisites

- [uvx](https://github.com/astral-sh/uv) installed on your system

### Installation & Running

```bash
# Clone or download the project
cd qr-epc

# Install dependencies and run (one command!)
make run
```

The app will start at `http://localhost:8501`

## Available Commands

```bash
make help        # Show all available commands
make install     # Install dependencies  
make run         # Start the application
make dev         # Start with auto-reload
make run-custom  # Start on custom host/port
make test        # Run all tests with pytest
make test-unit   # Run unit tests only
make test-i18n   # Run internationalization tests
make test-qr     # Run QR code generation tests
make lint        # Code linting
make format      # Code formatting
make clean       # Clean temporary files
```

## 🔗 URL Parameters for Pre-filled Forms

The application supports URL parameters to pre-fill the payment form, making it easy to share specific payment configurations. This is perfect for invoices, recurring payments, or collaborative workflows.

### Quick Examples

**Simple Payment Request:**
```
http://localhost:8501/?beneficiary_name=John%20Doe&beneficiary_iban=GB82WEST12345698765432&amount=25.50
```

**Invoice Payment (French):**
```
http://localhost:8501/?beneficiary_name=Acme%20Corp&beneficiary_iban=FR1420041010050500013M02606&amount=150.00&remittance_info=Invoice%20INV-2024-001&lang=fr
```

**Donation Link (German):**
```
http://localhost:8501/?beneficiary_name=Charity%20Foundation&beneficiary_iban=DE89370400440532013000&purpose_code=CHAR&remittance_info=Monthly%20Donation&lang=de
```

### Supported URL Parameters

| Parameter | Description | Example Value | Note |
|-----------|-------------|---------------|------|
| `beneficiary_name` | Recipient's name | `John%20Doe` | **Required** - URL encoded |
| `beneficiary_iban` | Recipient's IBAN | `GB82WEST12345698765432` | **Required** |
| `bic_swift` | Bank BIC/SWIFT code | `ABNANL2A` | Optional |
| `amount` | Payment amount in EUR | `25.50` | Use `0` for variable amount |
| `purpose_code` | ISO 20022 purpose code | `SALA` (salary) | Optional |
| `remittance_info` | Payment reference/description | `Invoice%20INV-001` | URL encoded |
| `structured_ref` | Structured creditor reference | `RF18539007547034` | Optional |
| `lang` | Interface language | `en`, `fr`, `de`, `es` | Auto-detected if not provided |

### URL Encoding

Special characters must be URL encoded:
- Spaces: `%20` or `+`
- Ampersand: `%26` 
- Hash: `%23`
- Plus: `%2B`

**Examples:**
- `John Doe` → `John%20Doe`
- `Invoice #123` → `Invoice%20%23123`
- `A&B Company` → `A%26B%20Company`

### Purpose Codes (ISO 20022)

Common purpose codes you can use:

| Code | Description | Use Case |
|------|-------------|----------|
| `SALA` | Salary | Employee payments |
| `SUPP` | Supplier payment | Invoice payments |
| `TAXS` | Tax payment | Government payments |
| `CHAR` | Charity payment | Donations |
| `RENT` | Rent | Property payments |
| `COMC` | Commercial payment | Business transactions |
| `OTHR` | Other | General payments |

### Advanced Examples

**Employee Salary Payment:**
```
http://localhost:8501/?beneficiary_name=Jane%20Smith&beneficiary_iban=NL91ABNA0417164300&bic_swift=ABNANL2A&amount=3500.00&purpose_code=SALA&remittance_info=Salary%20December%202024&lang=en
```

**Supplier Invoice (with BIC):**
```
http://localhost:8501/?beneficiary_name=Tech%20Solutions%20Ltd&beneficiary_iban=BE68539007547034&bic_swift=GKCCBEBB&amount=1250.75&purpose_code=SUPP&remittance_info=Invoice%20TS-2024-0156&lang=en
```

**Variable Amount Donation:**
```
http://localhost:8501/?beneficiary_name=Red%20Cross&beneficiary_iban=CH9300762011623852957&amount=0&purpose_code=CHAR&remittance_info=Emergency%20Relief%20Fund&lang=en
```

### Automatic URL Updates

When you generate a QR code, the application automatically updates the browser URL with your current form values. This means:

- ✅ **Instant Sharing**: Copy the URL after generating to share your exact configuration
- ✅ **Bookmarking**: Save payment forms as bookmarks
- ✅ **No Manual Work**: URL updates happen automatically
- ✅ **Always Current**: URL always reflects the current form state

### Use Cases

**1. Invoice Payments**
Create payment links for invoices:
```bash
# Template
https://yourapp.com/?beneficiary_name=YOUR_COMPANY&beneficiary_iban=YOUR_IBAN&amount=INVOICE_AMOUNT&remittance_info=Invoice%20NUMBER

# Example
https://yourapp.com/?beneficiary_name=Acme%20Corp&beneficiary_iban=FR1420041010050500013M02606&amount=299.99&remittance_info=Invoice%20INV-2024-0123
```

**2. Salary Payments**
HR departments can create standardized salary payment forms:
```bash
https://yourapp.com/?beneficiary_name=EMPLOYEE_NAME&beneficiary_iban=EMPLOYEE_IBAN&purpose_code=SALA&remittance_info=Salary%20MONTH%20YEAR
```

**3. Subscription Payments**
Generate recurring payment QR codes:
```bash
https://yourapp.com/?beneficiary_name=Service%20Provider&beneficiary_iban=SERVICE_IBAN&amount=29.99&remittance_info=Monthly%20Subscription
```

**4. Charity Donations**
Create donation links with suggested amounts:
```bash
https://yourapp.com/?beneficiary_name=Charity%20Name&beneficiary_iban=CHARITY_IBAN&purpose_code=CHAR&amount=0&remittance_info=Monthly%20Donation
```

**5. International Payments**
Include BIC for non-SEPA countries:
```bash
https://yourapp.com/?beneficiary_name=Int%27l%20Supplier&beneficiary_iban=IBAN&bic_swift=SWIFTCODE&amount=500.00&purpose_code=SUPP
```

### Testing URL Parameters

You can test URL parameters locally:

```bash
# Start the application
make run

# Test with sample data
open "http://localhost:8501/?beneficiary_name=Test%20User&beneficiary_iban=BE68539007547034&amount=50.00&lang=en"
```

### Security Notes

- ✅ **No Sensitive Data**: URLs only contain payment details you choose to include
- ✅ **No Authentication**: No passwords or sensitive information in URLs
- ✅ **Public Safe**: URLs can be safely shared via email, chat, or links
- ⚠️ **Amount Visibility**: Payment amounts are visible in URLs - consider privacy needs
- ⚠️ **URL Length**: Very long references may hit browser URL length limits

## Usage / Utilisation

1. **Language Selection / Sélection de la langue**
   - 🌍 **Auto-Detection**: The app automatically detects your browser/system language
   - 🔄 **Manual Override**: Use the sidebar to switch between 4 languages:
     - 🇬🇧 English / �� Français / 🇩🇪 Deutsch / �� Español
   - 🔍 **Detection Display**: See which language was auto-detected in the sidebar

2. **Fill in Beneficiary Details / Remplir les détails du bénéficiaire**
   - Beneficiary Name (required) / *Nom du bénéficiaire (obligatoire)*
   - IBAN (required) / *IBAN (obligatoire)*
   - BIC/SWIFT Code (optional, recommended for non-SEPA) / *Code BIC/SWIFT (optionnel)*

3. **Payment Information / Informations de paiement**
   - Amount in EUR (leave 0.00 for variable amount) / *Montant en EUR (laisser 0,00 pour un montant variable)*
   - Purpose Code (optional, from ISO 20022 standard) / *Code d'objet (optionnel)*
   - Payment Reference/Description / *Référence/Description du paiement*

3. **QR Code Customization**
   - Enable/disable logo in QR code center
   - Choose default Euro symbol or upload custom logo
   - Supports PNG, JPG, JPEG formats (square images recommended)

4. **Generate & Download**
   - Click "Generate QR Code"
   - Preview the QR code with logo
   - Download as PNG image

## EPC QR Code Standard

This application generates QR codes according to **EPC069-12** specification with the following structure:

```
BCD                    # Service Tag
002                    # Version  
1                      # Character Set (UTF-8)
SCT                    # Identification (SEPA Credit Transfer)
{BIC}                  # Bank Identifier Code
{Beneficiary Name}     # Beneficiary Name (max 70 chars)
{IBAN}                # Beneficiary Account
EUR{Amount}           # Amount (or empty for variable)
{Purpose Code}        # Purpose Code (ISO 20022)
{Reference}           # Remittance Information
{Structured Ref}      # Structured Reference
```

## Supported Purpose Codes

The application includes common ISO 20022 purpose codes:

- **CBFF**: Capital building
- **CHAR**: Charity payment  
- **COMC**: Commercial payment
- **SALA**: Salary
- **TAXS**: Tax payment
- **SUPP**: Supplier payment
- And many more...

## Dependencies

- **Streamlit**: Web application framework
- **qrcode[pil]**: QR code generation with PIL support  
- **Pillow**: Image processing

All dependencies are managed through `uvx` for easy, isolated execution.

## Testing

The project includes a comprehensive pytest-based testing framework:

### Running Tests
```bash
# Run all tests
make test

# Run specific test suites  
make test-unit      # Core EPC functionality
make test-i18n      # Internationalization system
make test-qr        # QR code generation

# Verbose output
make test-verbose

# Manual test runner
python3 run_tests.py
```

### Test Coverage
- ✅ **24 comprehensive tests** covering all functionality
- ✅ **EPC069-12 compliance** testing
- ✅ **Multilingual support** testing (4 languages)
- ✅ **QR code generation** with and without logos
- ✅ **Edge cases** and error handling

## Development

### Project Structure

```
qr-epc/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── Makefile           # Build and run commands
├── README.md          # This file
└── .streamlit/        # Streamlit configuration (optional)
```

### Code Quality

```bash
make lint      # Check code with ruff
make format    # Format code with ruff
make test      # Run tests (placeholder)
```

### Docker Support

```bash
make create-dockerfile  # Create Dockerfile
make docker-build      # Build Docker image
make docker-run        # Run in container
```

## 🌍 Language Detection System

The application automatically detects and sets the most appropriate language for users:

### Detection Methods
1. **Browser Language**: Reads `Accept-Language` headers when available
2. **System Locale**: Falls back to system locale settings (e.g., `en_US` → English)
3. **Timezone Cultural Mapping**: Infers language from timezone (e.g., `Europe/Berlin` → German)
4. **Intelligent Language Mapping**: Maps similar languages to supported ones
   - Italian/Portuguese → French/Spanish (Romance languages)
   - Dutch/Danish/Swedish → German (Germanic languages)

### Language Fallback Chain
```
User's Browser Language → System Locale → Cultural Inference → French (Default)
```

### Supported Language Mappings
- **🇬🇧 English**: `en`, `en-US`, `en-GB`, `en-CA`, `en-AU`
- **🇫🇷 Français**: `fr`, `fr-FR`, `fr-BE`, `it` (Italian)
- **🇩🇪 Deutsch**: `de`, `de-DE`, `de-AT`, `nl`, `da`, `sv`, `no`
- **🇪🇸 Español**: `es`, `es-ES`, `es-MX`, `pt` (Portuguese)

## Banking App Compatibility

This QR code format is supported by most European banking applications, including:

- Mobile banking apps from major European banks
- Payment processing applications
- Point-of-sale systems supporting SEPA payments

## Security & Privacy

- No payment data is stored or transmitted
- All processing happens locally in your browser
- QR codes contain only the payment information you provide
- No external API calls or data collection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make lint` and `make format`
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## Support

For issues or questions:
- Check the [EPC069-12 specification](https://www.europeanpaymentscouncil.eu/document-library/guidance-documents/quick-response-code-guidelines-enable-data-capture-initiation)
- Review the application code in `app.py`
- Test with your banking application

---

**Note**: Always test generated QR codes with your target banking applications before production use. While this application follows the EPC069-12 standard, individual banking apps may have specific requirements or limitations.
