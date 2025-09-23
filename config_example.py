# Example EPC QR Code Configuration
# You can use this as reference for testing the application

# Beneficiary Information
BENEFICIARY_NAME = "John Doe"
BENEFICIARY_IBAN = "BE68539007547034"
BIC = "GKCCBEBB"

# Payment Details
AMOUNT = 123.45  # or 0.0 for variable amount
PURPOSE_CODE = "COMC"  # Commercial payment
REMITTANCE_INFO = "Invoice 2024-001"
DEBTOR_REFERENCE = ""

# Sample IBANs for testing (all valid format examples)
SAMPLE_IBANS = {
    "Belgium": "BE68539007547034",
    "Germany": "DE89370400440532013000",
    "France": "FR1420041010050500013M02606",
    "Netherlands": "NL91ABNA0417164300",
    "Italy": "IT60X0542811101000000123456",
    "Spain": "ES9121000418450200051332",
    "Austria": "AT611904300234573201",
    "Luxembourg": "LU280019400644750000",
}

# Purpose Codes Reference
PURPOSE_CODES = {
    "CBFF": "Capital building",
    "CHAR": "Charity payment",
    "COMC": "Commercial payment",
    "CPKC": "Car park charges",
    "DIVI": "Dividend",
    "GOVI": "Government insurance",
    "INST": "Insurance premium",
    "INTC": "Interest",
    "OTHR": "Other",
    "SALA": "Salary",
    "SUPP": "Supplier payment",
    "TAXS": "Tax payment",
    "TRAD": "Trade",
}
