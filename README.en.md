# One-Time Password Generator Application

A one-time password (OTP) generation application with functionality similar to Google Authenticator. It can read QR codes using a PC camera and simultaneously manage and display OTPs for multiple accounts.

**[日本語版はこちら (Japanese version is available here)](README.md)**

## 📑 Table of Contents

- [🚀 Key Features](#-key-features)
- [📖 Usage](#-usage)
- [🛠️ Setup](#️-setup)
- [📋 Requirements](#-requirements)
- [🔒 Security](#-security)
- [🐛 Troubleshooting](#-troubleshooting)
- [📝 License](#-license)
- [📞 Support](#-support)
- [🔧 Developer Information](#-developer-information)
- [🧪 Testing](#-testing) ⭐ **Test Design Document Included**
- [🤝 Contributing](#-contributing)

## 🚀 Key Features

- **QR Code Reading**: Read QR codes from PC camera or image files
- **Multiple Account Management**: Manage and display OTPs for multiple accounts simultaneously
- **Real-time Display**: Auto-update OTPs every second with progress bar
- **Secure Storage**: Security codes are encrypted with PBKDF2 and stored locally
- **Command-line Operation**: Intuitive command-line interface
- **Docker Integration**: QR code parsing using otpauth container
- **Account Management**: List, search, update, and delete functionality

## 📖 Usage

### 🐳 Running with Docker (Recommended)

Using Docker eliminates the need for environment setup and provides immediate usability.

```bash
# Run tests
docker-compose run --rm test

# Run unit tests only
docker-compose run --rm test-unit

# Run integration tests only
docker-compose run --rm test-integration

# Lint checks (Black, Flake8, MyPy)
docker-compose run --rm black
docker-compose run --rm flake8
docker-compose run --rm mypy

# Run the application
docker-compose run --rm app poetry run python src/main.py [command]
```

### Running with Poetry Environment

```bash
# Run within Poetry virtual environment
poetry run python src/main.py [command]

# Or activate the virtual environment first
poetry shell
python src/main.py [command]
```

### Command List

#### Adding Accounts

```bash
# Read QR code with camera
poetry run python src/main.py add --camera

# Read QR code from image file
poetry run python src/main.py add --image qr_code.png
```

#### Displaying OTP

```bash
# Display OTP for all accounts (real-time updates)
poetry run python src/main.py show --all

# Display OTP for specific account
poetry run python src/main.py show <account_id>
```

#### Account Management

```bash
# Display account list
poetry run python src/main.py list

# Delete account
poetry run python src/main.py delete <account_id>

# Update account information
poetry run python src/main.py update <account_id> --name "New Name"

# Search accounts
poetry run python src/main.py search "keyword"
```

#### System Management

```bash
# Display application status
poetry run python src/main.py status

# Setup Docker environment
poetry run python src/main.py setup

# Remove Docker image
poetry run python src/main.py cleanup
```

## 🛠️ Setup

### 1. Poetry Environment Setup

```bash
# If Poetry is not installed
curl -sSL https://install.python-poetry.org | python3 -

# PATH configuration (add to ~/.zshrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Navigate to project directory
cd /path/to/OneTimePassword

# Install dependencies
poetry install
```

### 2. System Dependencies Installation (macOS)

```bash
# zbar library (for QR code reading)
brew install zbar
```

### 3. Docker Environment Setup

```bash
# Setup Docker environment (clone otpauth repository and build image)
poetry run python src/main.py setup

# Verify setup completion
docker images | grep otpauth
# Example output: otpauth      latest    eeb083890349   9 minutes ago   21.1MB
```

**Note**: The QR code reading functionality will automatically attempt to build the image if it doesn't exist. Initial use may take some time.

### 4. Environment Testing

```bash
# Check application functionality
poetry run python src/main.py --help

# Check status
poetry run python src/main.py status
```

## 📋 Requirements

- **Python**: 3.8.1 or higher (Recommended: 3.13.9)
- **Poetry**: Dependency management
- **Docker**: For QR code parsing
- **macOS**: Camera access permissions
- **System Libraries**: zbar (for QR code reading)

## 🔒 Security

- **Encryption**: Security codes are encrypted with PBKDF2 before storage
- **Random Salts**: Generate a unique 16-byte random salt for each encryption (protects against rainbow table attacks)
- **Local Storage**: Confidential data is not committed to GitHub
- **Memory Clearing**: Sensitive data is cleared immediately after use
- **Permission Management**: Appropriate file permission settings
- **Camera Access**: Access camera with minimal permissions
- **Environment Variables**: Master password is securely managed through environment variables

### 🔐 Encryption Mechanism

This application follows industry-standard security practices:

1. **Unique Salt Per Encryption**: Even encrypting the same data produces different results each time
2. **PBKDF2 Key Derivation**: Derives encryption keys from master password with 100,000 iterations
3. **Fernet Encryption**: Authenticated encryption using AES-128-CBC and HMAC-SHA256
4. **Salt Storage**: 16-byte random salt is stored alongside encrypted data

### 🔐 Master Password Configuration (Important)

The application uses a master password to encrypt security codes.
Configure the master password using one of the following methods:

#### Method 1: Environment Variable (Recommended)

```bash
# Add to ~/.zshrc or ~/.bashrc
export OTP_MASTER_PASSWORD="your_strong_password_here"

# Apply settings
source ~/.zshrc
```

#### Method 2: Password File (More Secure - Recommended)

**Using default file `~/.otp_password` (no environment variable needed):**

```bash
# Create password file with restricted permissions
echo "your_strong_password_here" > ~/.otp_password
chmod 600 ~/.otp_password

# That's it! No environment variable needed
poetry run python src/main.py show --all
```

**Using custom password file location:**

```bash
# Create password file at custom location
echo "your_strong_password_here" > /path/to/custom_password
chmod 600 /path/to/custom_password

# Add to ~/.zshrc or ~/.bashrc
export OTP_PASSWORD_FILE="/path/to/custom_password"

# Apply settings
source ~/.zshrc
```

#### Method 3: Interactive Input

If neither environment variables nor password file are configured, you will be prompted to enter the password when the application starts.

#### Optional: Custom Salt Configuration

To customize the default salt:

```bash
# Add to ~/.zshrc or ~/.bashrc
export OTP_SALT="your_custom_salt_value"
```

**⚠️ Security Warning**:
- Use a strong, difficult-to-guess master password
- When using a password file, ensure proper file permissions (600) are set
- Never commit environment variables or password files to version control systems
- Changing the password may make existing data unrecoverable

## 🐛 Troubleshooting

### When Camera is Not Recognized

```bash
# Check camera connection
poetry run python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Check camera permissions (macOS)
# System Preferences > Security & Privacy > Privacy > Camera
```

### Docker Errors

```bash
# Check Docker status
docker --version
docker info

# Check Docker daemon is running
docker ps

# Check network connection
ping github.com

# If otpauth image doesn't exist (will be auto-built)
poetry run python src/main.py add --camera

# Manual setup
poetry run python src/main.py setup

# Verify image
docker images | grep otpauth

# Remove image
poetry run python src/main.py cleanup
```

### When QR Code Cannot Be Read

- Verify QR code is clear and sufficiently large
- Adjust camera focus
- Improve lighting conditions
- Check QR code format (`otpauth-migration://offline?data=...`)

### QR Code Parsing Errors

```bash
# Debug parsing errors
poetry run python -c "
from src.docker_manager import DockerManager
dm = DockerManager()
# Test parsing with sample output
test_output = 'otpauth://totp/account?algorithm=SHA1&digits=6&issuer=GitHub&period=30&secret=SECRET'
result = dm.parse_otpauth_output(test_output)
print('Parse result:', result)
"
```

### Poetry Environment Issues

```bash
# Recreate virtual environment
poetry env remove python
poetry install

# Update dependencies
poetry update

# Regenerate lock file
poetry lock
```

## 📝 License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter issues, please follow these steps:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing Issues
3. Create a new Issue (include detailed information)

---

## 🔧 Developer Information

### Project Structure

```
OneTimePassword/
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main application (CLI)
│   ├── camera_qr_reader.py      # Camera QR code reading
│   ├── otp_generator.py         # OTP generation/display
│   ├── security_manager.py      # Security code management
│   ├── crypto_utils.py          # Encryption utilities
│   └── docker_manager.py        # Docker container management
├── tests/                        # Test code
│   ├── TEST_DESIGN.md           # Test design document
│   ├── conftest.py              # pytest common fixtures
│   ├── unit/                    # Unit tests (163 tests)
│   │   ├── test_crypto_utils.py
│   │   ├── test_otp_generator.py
│   │   ├── test_security_manager.py
│   │   ├── test_camera_qr_reader.py
│   │   ├── test_docker_manager.py
│   │   └── test_main.py
│   ├── integration/             # Integration tests (10 tests)
│   │   └── test_integration.py
│   ├── run_tests.py             # Python test execution script
│   └── run_tests.sh             # Bash wrapper script
├── data/                         # Data directory
│   └── accounts.json            # Account data (encrypted)
├── htmlcov/                      # Coverage HTML reports (auto-generated)
├── pyproject.toml               # Poetry configuration file
├── poetry.lock                  # Poetry dependency lock file
├── requirements.txt             # Traditional dependencies (reference)
├── .gitignore                   # Git exclusion settings
├── LICENSE                      # License file
├── README.md                    # This file (Japanese)
├── README.en.md                 # This file (English)
├── REQUIREMENTS_OVERVIEW.md     # High-level project requirements
└── requirements_specification.md # Requirements specification
```

### Technical Specifications

#### Technologies Used

- **Language**: Python 3.8.1+
- **Dependency Management**: Poetry
- **Virtual Environment**: pyenv + Poetry
- **Encryption**: cryptography (PBKDF2)
- **QR Code**: OpenCV (cv2.QRCodeDetector)
- **OTP Generation**: pyotp
- **Container**: Docker
- **Image Processing**: Pillow

#### Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.8.1"
pyotp = "^2.9.0"
opencv-python = "^4.8.1"
cryptography = "^41.0.7"
Pillow = "^10.0.1"
docker = "^6.1.3"
numpy = "^1.24.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-cov = "^4.0.0"
pytest-mock = "^3.0.0"
pytest-asyncio = "^0.21.0"
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"
```

### Development Environment Information

- **Python**: 3.13.9 (managed by pyenv)
- **Poetry**: 2.2.1
- **Virtual Environment**: `/Users/kencom/Library/Caches/pypoetry/virtualenvs/onetimepassword-78G70__u-py3.13`
- **OS**: macOS Sequoia 24.6.0

## 🧪 Testing

### 📚 Test Design Document

For detailed test design, please refer to the [Test Design Document (TEST_DESIGN.md)](tests/TEST_DESIGN.md).

The test design document includes:
- Test strategy and test pyramid
- Module-specific test design (173 test cases)
- Integration and E2E test design
- Mocking best practices
- Troubleshooting guide
- Detailed test execution methods

### 📊 Test Statistics

- **Total Tests**: 173
  - Unit tests: 163
  - Integration tests: 10
- **Test Success Rate**: 100% ✅
- **Execution Time**: Approximately 2.8 seconds
- **Current Coverage**: 67%
- **Target Coverage**: 90%+

### 🚀 Test Execution Methods

#### 1. Wrapper Shell Script (Recommended)

```bash
# Run all tests (recommended)
./run_tests.sh

# Run unit tests only
./run_tests.sh unit

# Run integration tests only
./run_tests.sh integration

# Run tests with coverage (generate HTML/XML reports)
./run_tests.sh coverage --html

# Quick test execution (no coverage)
./run_tests.sh quick

# Watch mode (auto-run on file changes)
./run_tests.sh watch

# Clear test cache
./run_tests.sh clean

# Display help
./run_tests.sh --help
```

#### 2. Direct Execution

```bash
# Run all tests
poetry run pytest tests/ -v

# Run tests with coverage
poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run specific module tests
poetry run pytest tests/unit/test_crypto_utils.py -v

# Run specific test class
poetry run pytest tests/unit/test_main.py::TestOneTimePasswordApp -v

# Run specific test function
poetry run pytest tests/unit/test_main.py::TestOneTimePasswordApp::test_add_account_from_camera_success -v

# Parallel execution (faster)
poetry run pytest tests/ -n auto

# Execute with timeout (for hanging tests)
timeout 120 poetry run pytest tests/ -v
```

### 🗂️ Test Structure

```
tests/
├── TEST_DESIGN.md           # Test design document (detailed documentation)
├── conftest.py              # pytest common fixtures
├── unit/                    # Unit tests (163 tests)
│   ├── test_crypto_utils.py      # Encryption utilities (25 tests)
│   ├── test_otp_generator.py     # OTP generation (19 tests)
│   ├── test_security_manager.py  # Security management (23 tests)
│   ├── test_camera_qr_reader.py  # Camera QR reading (30 tests)
│   ├── test_docker_manager.py    # Docker management (32 tests)
│   └── test_main.py              # Main app (34 tests)
├── integration/             # Integration tests (10 tests)
│   └── test_integration.py
├── run_tests.py             # Python test execution script
└── run_tests.sh             # Bash wrapper script
```

### 📋 Test Execution Options

#### Wrapper Shell Options

- `-v, --verbose`: Detailed output (display test case names and results)
- `-q, --quiet`: Brief output (summary only)
- `-f, --fail-fast`: Stop at first failure
- `-p, --parallel`: Parallel execution (faster)
- `--no-cov`: Disable coverage measurement (faster execution)
- `--html`: Generate HTML coverage report (`htmlcov/index.html`)
- `--xml`: Generate XML coverage report (`coverage.xml`)
- `-m MARKER`: Run only tests with specific marker

#### pytest Option Examples

```bash
# Rerun only failed tests
poetry run pytest tests/ --lf

# Run failed tests first
poetry run pytest tests/ --ff

# Short traceback display
poetry run pytest tests/ --tb=short

# No traceback display
poetry run pytest tests/ --tb=no

# Detailed output (each test detail)
poetry run pytest tests/ -vv

# Display test execution time
poetry run pytest tests/ --durations=10
```

### 🔍 Coverage Reports

After test execution, the following coverage reports are generated:

```bash
# View HTML report
open htmlcov/index.html

# Display coverage in terminal
poetry run pytest tests/ --cov=src --cov-report=term-missing
```

**Current Coverage Details**:
- `src/main.py`: 84%
- `src/crypto_utils.py`: 80%
- `src/docker_manager.py`: 73%
- `src/security_manager.py`: 67%
- `src/camera_qr_reader.py`: 52%
- `src/otp_generator.py`: 37%

### 🐛 Test Troubleshooting

#### When Tests Hang

```bash
# Execute with timeout
timeout 120 poetry run pytest tests/ -v

# Skip specific tests
poetry run pytest tests/ -k "not test_hanging_test"
```

#### Camera Access Errors

All camera tests are fully mocked, so no actual camera is required.
If errors occur, refer to the [Test Design Document Troubleshooting](tests/TEST_DESIGN.md#13-troubleshooting).

#### Docker-related Errors

Docker environment is not required, so tests will pass even if Docker is not running.
All Docker commands are mocked with `subprocess.run`.

### 📝 Writing Tests

When adding new tests, please follow these guidelines:

1. **Proper Mocking**: Always mock external dependencies
2. **Clear Test Names**: Use `test_<method>_<scenario>` format
3. **AAA Pattern**: Arrange, Act, Assert
4. **Independence**: Each test should be independently executable
5. **Documentation**: Include test case ID and purpose in docstring

Example:
```python
def test_add_account_success(self, security_manager):
    """TC-SEC-001: Add account (success)"""
    # Arrange
    account_data = {...}
    
    # Act
    result = security_manager.add_account(**account_data)
    
    # Assert
    assert result is not None
    assert len(result) > 0
```

For details, refer to the [Test Design Document](tests/TEST_DESIGN.md).

### Development Commands

```bash
# Code formatting
poetry run black src/

# Linting
poetry run flake8 src/

# Type checking
poetry run mypy src/

# Run tests
poetry run pytest
```

### Prerequisites Check (For Developers)

```bash
# Check Python 3.13.9
python --version

# Check pyenv
pyenv versions

# Check Docker
docker --version

# Check virtual environment
poetry env info
```

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

---

**Note**: This application is created for educational and research purposes. Please conduct thorough testing before production use.

