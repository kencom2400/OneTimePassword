# One-Time Password Generator Application

A one-time password (OTP) generation application with functionality similar to Google Authenticator. It can read QR codes using a PC camera and simultaneously manage and display OTPs for multiple accounts.

**[日本語版はこちら (Japanese version is available here)](README.md)**

## 📑 Table of Contents

### 👤 For Users (Using the App)
- [🚀 Quick Start](#-quick-start)
- [📖 Basic Usage](#-basic-usage)
- [📋 Command Reference](#-command-reference)
- [🔒 Security Settings](#-security-settings)
- [🐛 Troubleshooting](#-troubleshooting)

### 👨‍💻 For Developers (Developing the App)
- [🛠️ Development Environment Setup](#️-development-environment-setup)
- [📂 Project Structure](#-project-structure)
- [🔧 Development Tools and Commands](#-development-tools-and-commands)
- [🧪 Testing and Coverage](#-testing-and-coverage)
- [📚 Developer Documentation](#-developer-documentation)

### 📚 Other
- [🚀 Key Features](#-key-features)
- [📋 System Requirements](#-system-requirements)

---

## 👤 For Users (Using the App)

This section is for those who want to **use** the OneTimePassword application.

### 🚀 Quick Start

**The simplest way to get started:** Using the wrapper shell

```bash
# 1. Clone the repository
git clone https://github.com/your-username/OneTimePassword.git
cd OneTimePassword

# 2. Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# 3. Run immediately! (Dependencies are installed automatically on first run)
./otp --help

# 4. Set up master password (first time only)
echo "your_strong_password" > ~/.otp_password
chmod 600 ~/.otp_password

# Done! That's all 🎉
```

**Next Steps:**
- [Basic Usage](#-basic-usage) - Add accounts and display OTPs
- [Security Settings](#-security-settings) - Detailed password configuration

### 📖 Basic Usage

#### 1. Add an Account

```bash
# Read QR code from camera
./otp add --camera

# Or add from an image file
./otp add --image qr_code.png
```

#### 2. Display OTPs

```bash
# Display all accounts' OTPs (real-time updates)
./otp show --all

# Display specific account only
./otp show <account_id>
```

#### 3. Manage Accounts

```bash
# List all accounts
./otp list

# Search accounts
./otp search "GitHub"

# Update account information
./otp update <account_id> --name "New Name"

# Delete an account
./otp delete <account_id>
```

#### 4. Check System Status

```bash
# Check application status
./otp status

# Set up Docker environment (first time only)
./otp setup

# Clean up Docker images
./otp cleanup
```

### 📋 Command Reference

#### Choosing Execution Method

There are three ways to run this application:

| Method | Command Example | Rating | Use Case |
|--------|----------------|--------|----------|
| **Wrapper Shell** | `./otp show --all` | ⭐⭐⭐ | Daily use (easiest) |
| **Poetry Direct** | `poetry run python src/main.py show --all` | ⭐⭐ | Development/Debugging |
| **Docker** | `docker-compose -f docker/docker-compose.yml run --rm app ...` | ⭐ | Test execution |

Following command examples use the **wrapper shell format**. For other methods, refer to the table above.

#### Command List

**Account Management**

```bash
./otp add --camera              # Read QR code from camera
./otp add --image <path>        # Read from image file
./otp list                      # List accounts
./otp show --all                # Display all OTPs (real-time)
./otp show <account_id>         # Display specific account's OTP
./otp search <keyword>          # Search accounts
./otp update <id> --name <name> # Update account
./otp delete <account_id>       # Delete account
```

**System Management**

```bash
./otp status                    # Display status
./otp setup                     # Set up Docker environment
./otp cleanup                   # Delete Docker images
./otp --help                    # Display help
```

### 🔒 Security Settings

#### About Master Password

This application uses a master password to encrypt and store security codes.

**Encryption Mechanism:**
- PBKDF2 key derivation (100,000 iterations)
- Fernet encryption (AES-128-CBC + HMAC-SHA256)
- Unique 16-byte random salt for each encryption
- Local storage only (not committed to GitHub)

#### How to Set Master Password

**Method 1: Password File (Recommended - Easiest)**

```bash
# Save to default file (no environment variable needed)
echo "your_strong_password" > ~/.otp_password
chmod 600 ~/.otp_password

# That's it!
./otp show --all
```

**Method 2: Custom Password File**

```bash
# Save to custom location
echo "your_strong_password" > /path/to/password
chmod 600 /path/to/password

# Specify location via environment variable (add to ~/.zshrc)
echo 'export OTP_PASSWORD_FILE="/path/to/password"' >> ~/.zshrc
source ~/.zshrc
```

**Method 3: Environment Variable**

```bash
# Add to ~/.zshrc
echo 'export OTP_MASTER_PASSWORD="your_strong_password"' >> ~/.zshrc
source ~/.zshrc
```

**Method 4: Interactive Input**

If none of the above are configured, you'll be prompted for a password when running the application.

**⚠️ Security Warning:**
- Use a strong, hard-to-guess password
- Always set file permissions to 600 for password files
- Never commit passwords to version control systems
- Changing the password will make existing data unrecoverable

### 🐛 Troubleshooting

#### Camera Not Recognized

```bash
# Check camera connection
poetry run python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# On macOS: Check camera permissions in System Preferences
# System Preferences > Security & Privacy > Privacy > Camera
```

#### Docker Errors

```bash
# Check Docker status
docker --version
docker ps

# Check otpauth image
docker images | grep otpauth

# If image doesn't exist, it will be built automatically
./otp add --camera

# Or manually set up
./otp setup
```

#### QR Code Cannot Be Read

- Ensure QR code is clear and sufficiently large
- Adjust camera focus
- Improve lighting conditions
- Verify QR code format (`otpauth-migration://offline?data=...`)

#### Poetry Environment Issues

```bash
# Recreate virtual environment
poetry env remove python
poetry install

# Update dependencies
poetry update
```

---

## 👨‍💻 For Developers (Developing the App)

This section is for those who want to **contribute to development** of the OneTimePassword application.

### 🛠️ Development Environment Setup

#### Required Tools

- **Python 3.13 or higher** (recommended: 3.13.9)
- **Poetry** (dependency management)
- **Docker** (QR code parsing, test execution)
- **Git** (version control)
- **zbar** (QR code reading library)

#### Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/OneTimePassword.git
cd OneTimePassword

# 2. Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# 3. Install dependencies
poetry install

# 4. Install system libraries (macOS)
brew install zbar

# 5. Set up Docker environment
poetry run python src/main.py setup

# 6. Verify installation
poetry run python src/main.py --help
```

#### Verify Development Environment

```bash
# Check Python version
python --version  # 3.13 or higher

# Check Poetry
poetry --version

# Check virtual environment
poetry env info

# Check Docker
docker --version
docker ps
```

### 📂 Project Structure

```
OneTimePassword/
├── 🚀 Executables
│   ├── otp                       # Wrapper shell (for users)
│   └── run_tests.sh              # Test execution script
│
├── 📁 Source Code
│   └── src/
│       ├── main.py               # Main application (CLI)
│       ├── camera_qr_reader.py   # Camera QR code reading
│       ├── otp_generator.py      # OTP generation and display
│       ├── security_manager.py   # Account management and encryption
│       ├── crypto_utils.py       # Encryption utilities
│       └── docker_manager.py     # Docker container management
│
├── 🧪 Test Code
│   └── tests/
│       ├── unit/                 # Unit tests (163 tests)
│       ├── integration/          # Integration tests (10 tests)
│       └── conftest.py           # pytest configuration
│
├── 📚 Documentation
│   ├── README.md                 # Japanese user guide
│   ├── README.en.md              # This file
│   └── docs/
│       ├── README.md             # Developer documentation overview
│       ├── REQUIREMENTS_OVERVIEW.md
│       ├── REQUIREMENTS_SPECIFICATION.md
│       └── TEST_DESIGN.md        # Test design document
│
├── 🐳 Docker Related
│   └── docker/
│       ├── docker-compose.yml    # Docker Compose configuration
│       ├── Dockerfile            # For application
│       ├── Dockerfile.test       # For testing
│       └── Dockerfile.lint       # For linting
│
└── ⚙️ Configuration Files
    ├── pyproject.toml            # Poetry configuration
    ├── poetry.lock               # Dependency lock file
    └── .gitignore                # Git exclusion settings
```

### 🔧 Development Tools and Commands

#### Code Quality Checks

```bash
# Code formatting (Black)
poetry run black src/ tests/

# Format check (no changes)
poetry run black --check --diff src/ tests/

# Lint check (Flake8)
poetry run flake8 src/ tests/ --count --statistics

# Type check (MyPy)
poetry run mypy src/ --ignore-missing-imports --show-error-codes
```

#### Batch Execution (Using Docker)

```bash
# Run all lint checks
docker-compose -f docker/docker-compose.yml run --rm black
docker-compose -f docker/docker-compose.yml run --rm flake8
docker-compose -f docker/docker-compose.yml run --rm mypy

# Apply formatting
docker-compose -f docker/docker-compose.yml run --rm format
```

#### Debug Execution

```bash
# Run with Python debugger
poetry run python -m pdb src/main.py [command]

# Verbose logging
poetry run python src/main.py --verbose [command]

# Display environment information
poetry run python src/main.py status
```

#### Dependency Management

```bash
# Add dependency
poetry add <package>

# Add dev dependency
poetry add --group dev <package>

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree
```

### 🧪 Testing and Coverage

#### How to Run Tests

**Quick Execution (Recommended)**

```bash
# Run all tests (easiest)
./run_tests.sh

# Run with coverage
./run_tests.sh coverage --html

# Unit tests only
./run_tests.sh unit

# Integration tests only
./run_tests.sh integration

# Quick run (no coverage)
./run_tests.sh quick

# Clean test cache
./run_tests.sh clean

# Display help
./run_tests.sh --help
```

**Detailed Execution Options**

```bash
# Run all tests
poetry run pytest tests/ -v

# Run with coverage
poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term

# Test specific module
poetry run pytest tests/unit/test_crypto_utils.py -v

# Test specific class
poetry run pytest tests/unit/test_main.py::TestOneTimePasswordApp -v

# Test specific function
poetry run pytest tests/unit/test_main.py::test_add_account_success -v

# Parallel execution (faster)
poetry run pytest tests/ -n auto

# Re-run only failed tests
poetry run pytest tests/ --lf

# Verbose output
poetry run pytest tests/ -vv

# Show test execution time
poetry run pytest tests/ --durations=10
```

**Test Execution in Docker Environment**

```bash
# All tests
docker-compose -f docker/docker-compose.yml run --rm test

# Unit tests only
docker-compose -f docker/docker-compose.yml run --rm test-unit

# Integration tests only
docker-compose -f docker/docker-compose.yml run --rm test-integration
```

#### Test Statistics and Coverage

**Current Test Statistics**

- **Total Tests**: 173
  - Unit tests: 163
  - Integration tests: 10
- **Success Rate**: 100% ✅
- **Execution Time**: ~2.8 seconds
- **Current Coverage**: 67%
- **Target Coverage**: 90%

**Coverage by Module**

| Module | Coverage | Tests |
|--------|----------|-------|
| `main.py` | 84% | 34 |
| `crypto_utils.py` | 80% | 25 |
| `docker_manager.py` | 73% | 32 |
| `security_manager.py` | 67% | 23 |
| `camera_qr_reader.py` | 52% | 30 |
| `otp_generator.py` | 37% | 19 |

**Checking Coverage Reports**

```bash
# Generate and view HTML report
poetry run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Display detailed report in terminal
poetry run pytest tests/ --cov=src --cov-report=term-missing
```

#### How to Write Tests

Follow these guidelines when adding new tests:

**1. Naming Conventions**
- File name: `test_<module_name>.py`
- Class name: `Test<ClassName>`
- Method name: `test_<functionality>_<scenario>`

**2. AAA Pattern**
```python
def test_add_account_success(self, security_manager):
    """TC-SEC-001: Add account (success)"""
    # Arrange
    account_data = {
        "account_id": "test_001",
        "account_name": "TestAccount",
        "issuer": "TestIssuer",
        "secret": "JBSWY3DPEHPK3PXP"
    }
    
    # Act
    result = security_manager.add_account(**account_data)
    
    # Assert
    assert result is not None
    assert len(result) > 0
```

**3. Mocking Best Practices**

```python
from unittest.mock import Mock, patch

# Mock external dependencies
@patch('cv2.VideoCapture')
def test_camera_access(mock_camera):
    mock_camera.return_value.isOpened.return_value = True
    # Test code
```

**4. Test Independence**
- Each test should run independently
- Don't share state between tests
- Initialize with fixtures

**5. Documentation**
- Include test case ID and purpose in docstring
- Add comments for complex tests

**Test Structure**

```
tests/
├── conftest.py              # Common fixtures
├── unit/                    # Unit tests
│   ├── test_crypto_utils.py      # Encryption (25 tests)
│   ├── test_otp_generator.py     # OTP generation (19 tests)
│   ├── test_security_manager.py  # Security (23 tests)
│   ├── test_camera_qr_reader.py  # Camera QR (30 tests)
│   ├── test_docker_manager.py    # Docker (32 tests)
│   └── test_main.py              # Main (34 tests)
└── integration/             # Integration tests
    └── test_integration.py       # Integration (10 tests)
```

**Test Troubleshooting**

**Tests Hang**
```bash
# Set timeout
timeout 120 poetry run pytest tests/ -v

# Skip specific tests
poetry run pytest tests/ -k "not test_problematic"
```

**Camera Access Errors**
- All camera tests are fully mocked
- Actual camera is not required
- See [TEST_DESIGN.md](docs/TEST_DESIGN.md) for details

**Detailed Test Design**

For complete test design, refer to **[docs/TEST_DESIGN.md](docs/TEST_DESIGN.md)**. It includes:
- Test strategy and test pyramid
- Details of all 173 test cases
- Mocking best practices
- Troubleshooting guide

### 📚 Developer Documentation

Detailed documentation for development is available in the `docs/` directory:

- **[docs/README.md](docs/README.md)** - Documentation overview and navigation
- **[docs/REQUIREMENTS_OVERVIEW.md](docs/REQUIREMENTS_OVERVIEW.md)** - Initial project requirements
- **[docs/REQUIREMENTS_SPECIFICATION.md](docs/REQUIREMENTS_SPECIFICATION.md)** - Detailed functional specifications
- **[docs/TEST_DESIGN.md](docs/TEST_DESIGN.md)** - Test strategy and 173 test cases

**Recommended Reading Order:**

1. **REQUIREMENTS_OVERVIEW.md** - Understand the project overview
2. **REQUIREMENTS_SPECIFICATION.md** - Learn detailed specifications
3. **TEST_DESIGN.md** - Study test strategy

---

## 📚 Other

### 🚀 Key Features

- **QR Code Reading**: Read QR codes from PC camera or image files
- **Multiple Account Management**: Manage and display OTPs for multiple accounts simultaneously
- **Real-time Display**: Auto-update OTPs every second with progress bar
- **Secure Storage**: Security codes are encrypted with PBKDF2 and stored locally
- **Command-line Operation**: Intuitive command-line interface
- **Docker Integration**: QR code parsing using otpauth container
- **Account Management**: List, search, update, and delete functionality

### 📋 System Requirements

- **Python**: 3.13 or higher (recommended: 3.13.9)
- **Poetry**: Dependency management
- **Docker**: For QR code parsing
- **macOS**: Camera access permissions
- **System Library**: zbar (for QR code reading)

#### Main Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.13"
pyotp = "^2.9.0"              # OTP generation
opencv-python = "^4.8.1"      # QR code reading
cryptography = "^41.0.7"      # Encryption
Pillow = "^10.0.1"            # Image processing
docker = "^6.1.3"             # Docker client
numpy = "^1.24.0"             # Numerical computation

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"             # Test framework
pytest-cov = "^4.0.0"         # Coverage
black = "^23.0.0"             # Formatter
flake8 = "^6.0.0"             # Linter
mypy = "^1.0.0"               # Type checker
```

---

**Development Environment**: macOS Sequoia 24.6.0 | Python 3.13.9 | Poetry 2.2.1
