# EPC QR Code Generator Makefile
# Uses uvx for Python package management and execution

.PHONY: help install run dev clean lint format test deps-check

# Default target
help:
	@echo "EPC QR Code Generator - Makefile Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  install     - Install dependencies using uvx"
	@echo "  deps-check  - Check if uvx is installed"
	@echo ""
	@echo "Development:"
	@echo "  run         - Run the Streamlit app"
	@echo "  dev         - Run in development mode with auto-reload"
	@echo "  lint        - Run code linting with ruff"
	@echo "  format      - Format code with ruff"
	@echo "  test        - Run tests (placeholder)"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean       - Clean up temporary files"
	@echo "  upgrade     - Upgrade dependencies"
	@echo ""

# Check if uvx is installed
deps-check:
	@echo "Checking if uvx is installed..."
	@command -v uvx >/dev/null 2>&1 || { \
		echo "Error: uvx is not installed."; \
		echo "Please install uvx first:"; \
		echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "  # or"; \
		echo "  pip install uv"; \
		exit 1; \
	}
	@echo "✓ uvx is installed"
	@uvx --version

# Install dependencies
install: deps-check
	@echo "Installing dependencies with uvx..."
	@uvx --from streamlit --with 'qrcode[pil]' --with Pillow streamlit --version
	@echo "✓ Dependencies are ready"

# Run the Streamlit app
run: deps-check
	@echo "Starting EPC QR Code Generator..."
	@uvx --from streamlit --with 'qrcode[pil]' --with Pillow streamlit run app.py

# Run in development mode
dev: deps-check
	@echo "Starting in development mode with auto-reload..."
	@uvx --from streamlit --with 'qrcode[pil]' --with Pillow streamlit run app.py --server.runOnSave true

# Run with custom port and host
run-custom: deps-check
	@echo "Starting on custom host/port..."
	@uvx --from streamlit --with 'qrcode[pil]' --with Pillow streamlit run app.py --server.port 8502 --server.address 0.0.0.0

# Lint code
lint: deps-check
	@echo "Running code linting..."
	@uvx ruff check app.py || echo "Install ruff for better linting: uvx install ruff"

# Format code
format: deps-check
	@echo "Formatting code..."
	@uvx ruff format app.py || echo "Install ruff for code formatting: uvx install ruff"

# Run tests (placeholder)
test:
	@echo "Running tests..."
	@echo "No tests configured yet. Consider adding pytest tests."

# Clean temporary files
clean:
	@echo "Cleaning up temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -f .streamlit/secrets.toml.bak
	@echo "✓ Cleanup completed"

# Upgrade dependencies
upgrade: deps-check
	@echo "Checking for dependency updates..."
	@echo "Note: uvx always uses the latest versions unless pinned"
	@uvx --from streamlit --version
	@echo "✓ Using latest versions with uvx"

# Create a simple test
create-test:
	@echo "Creating a basic test file..."
	@mkdir -p tests
	@echo 'def test_basic():\n    assert True' > tests/test_basic.py
	@echo "✓ Created tests/test_basic.py"

# Show app info
info:
	@echo "EPC QR Code Generator Information"
	@echo "================================"
	@echo "App file: app.py"
	@echo "Dependencies: streamlit, qrcode[pil], Pillow"
	@echo "Default URL: http://localhost:8501"
	@echo ""
	@echo "Quick start:"
	@echo "  make install  # Setup dependencies"
	@echo "  make run      # Start the app"

# Docker-related commands (bonus)
docker-build:
	@echo "Building Docker image..."
	@docker build -t epc-qr-generator .

docker-run:
	@echo "Running Docker container..."
	@docker run -p 8501:8501 epc-qr-generator

# Create Dockerfile
create-dockerfile:
	@echo "Creating Dockerfile..."
	@echo 'FROM python:3.11-slim\nWORKDIR /app\nRUN pip install uv\nCOPY app.py requirements.txt ./\nRUN uv pip install --system -r requirements.txt\nEXPOSE 8501\nCMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]' > Dockerfile
	@echo "✓ Created Dockerfile"

# Show dependency tree
deps-tree: deps-check
	@echo "Dependency information:"
	@echo "======================"
	@uvx --from streamlit --version
	@echo ""
	@echo "Required packages:"
	@cat requirements.txt