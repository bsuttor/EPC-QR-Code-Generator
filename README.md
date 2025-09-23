# EPC QR Code Generator / Générateur de QR Code EPC

A multilingual Streamlit web application that generates QR codes for SEPA Credit Transfer according to the EPC069-12 standard. This allows users to create payment QR codes that can be scanned by European banking applications.

*Une application web Streamlit multilingue qui génère des QR codes pour les virements SEPA selon la norme EPC069-12. Cela permet aux utilisateurs de créer des QR codes de paiement qui peuvent être scannés par les applications bancaires européennes.*

## Features / Fonctionnalités

- ✅ **EPC069-12 Compliant**: Generates QR codes following the official European Payment Council standard
- ✅ **SEPA Compatible**: Works with all SEPA Credit Transfer enabled banks
- ✅ **Multilingual Interface**: Full support for English and French (🇬🇧 🇫🇷)
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

## Usage / Utilisation

1. **Select Language / Choisir la langue**
   - Use the sidebar to choose between English (🇬🇧) and French (🇫🇷)
   - *Utilisez la barre latérale pour choisir entre l'anglais et le français*

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

See `TESTING.md` for detailed testing documentation.

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