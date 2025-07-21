# autoscrobbler

[![CI Status](https://github.com/guillochon/autoscrobbler/actions/workflows/ci.yml/badge.svg)](https://github.com/guillochon/autoscrobbler/actions/workflows/ci.yml)
![License](https://img.shields.io/github/license/guillochon/autoscrobbler)
![Coverage](https://img.shields.io/badge/coverage-85.35%25-brightgreen)

Automatically scrobble songs to Last.fm by listening to your environment and identifying music with Shazam. Useful for when you are playing music from a source without a digital integration (vinyl, tape deck, vintage CD player, etc.).

## Features
- **Passive audio scrobbling**: Listens to your microphone, identifies music, and scrobbles to Last.fm automatically.
- **Shazam integration**: Uses Shazam for robust song identification.
- **Customizable duty cycle**: Control how often the program listens and scrobbles.
- **Flexible credentials**: Easily specify your credentials file location.

## Requirements
- Python 3.8 - 3.12 (pydub dependency is restricted to <=3.12 because of impending audioop removal in 3.13)
- [uv](https://github.com/astral-sh/uv) (for running and installing dependencies)
- Microphone/input device

## Installation
1. **Clone the repository**
   ```sh
   git clone <your-repo-url>
   cd autoscrobbler
   ```
2. **Install dependencies**
   ```sh
   uv sync
   ```

## Configuration
Create a `credentials.json` file in the project root or specify its path with `--credentials`. Instructions on how to get your last.fm credentials available [here](https://www.last.fm/api/authentication).

Example `credentials.json`:
```json
{
  "lastfm": {
    "api_key": "YOUR_LASTFM_API_KEY",
    "api_secret": "YOUR_LASTFM_API_SECRET",
    "username": "YOUR_LASTFM_USERNAME",
    "password": "YOUR_LASTFM_PASSWORD"
  }
}
```

## Usage
Run the program using `uv run`:

```sh
uv run -m autoscrobbler
```

### Options
- `-c`, `--credentials <path>`: Path to your `credentials.json` file (optional if in project root or package directory)
- `-d`, `--duty-cycle <seconds>`: Time in seconds between each listening/scrobbling attempt (default: 60)
- `-i`, `--input-source <source>`: Input source for recording. Can be:
  - `auto`: Use the first available input device
  - Device index (number): Use the ith device in the list
  - Device name (string): Use the device whose name contains the string (case-insensitive)
  - If not set, you will be prompted to select a device at startup

### Examples
- Run with default settings:
  ```sh
  uv run -m autoscrobbler
  ```
- Specify a custom credentials file:
  ```sh
  uv run -m autoscrobbler --credentials /path/to/credentials.json
  ```
- Change the duty cycle to 30 seconds:
  ```sh
  uv run -m autoscrobbler --duty-cycle 30
  ```
- Use the first available input device automatically:
  ```sh
  uv run -m autoscrobbler --input-source auto
  ```
- Use the 2nd device in the list (index 1):
  ```sh
  uv run -m autoscrobbler -i 1
  ```
- Use a device by (partial) name:
  ```sh
  uv run -m autoscrobbler -i "USB Microphone"
  ```
- Combine all options:
  ```sh
  uv run -m autoscrobbler -c /path/to/credentials.json -d 45 -i auto
  ```

## Notes
- At startup, all available input devices will be listed with their index and name.
- If `--input-source` is not set, you will be prompted to select a device interactively.
- The program will print information about your selected input device and status messages for each scrobble attempt.
- If the credentials file is missing or invalid, you'll get a helpful error message.
- The actual interval between attempts is always as close as possible to your specified duty cycle, accounting for processing time.

## Dependencies
- `pylast`
- `sounddevice`
- `soundfile`
- `shazamio`
- (see `pyproject.toml` for full list)

## Development

### Setup
1. **Install development dependencies**
   ```sh
   uv sync --extras dev
   ```

2. **Install pre-commit hooks**
   ```sh
   pre-commit install
   ```

### Testing

The project uses pytest for testing with comprehensive unit and integration tests.

#### Running Tests

**Run all tests:**
```sh
uv run pytest
```

**Run tests with verbose output:**
```sh
uv run pytest -v
```

**Run specific test file:**
```sh
uv run pytest tests/test_credentials.py
```

**Run specific test function:**
```sh
uv run pytest tests/test_credentials.py::TestLoadCredentials::test_load_credentials_success
```

**Run tests by marker:**
```sh
uv run pytest -m unit          # Run only unit tests
uv run pytest -m integration   # Run only integration tests
uv run pytest -m "not slow"    # Run all tests except slow ones
```

**Run tests with coverage:**
```sh
uv run pytest --cov=autoscrobbler --cov-report=html
```

**Using the test runner script:**
```sh
python run_tests.py all          # Run all tests
python run_tests.py unit         # Run only unit tests
python run_tests.py integration  # Run only integration tests
python run_tests.py coverage     # Run tests with coverage report
python run_tests.py fast         # Run fast tests (exclude slow ones)
python run_tests.py lint         # Run linting
python run_tests.py format       # Run code formatting
```

#### Test Structure

- **`tests/conftest.py`**: Common fixtures and test configuration
- **`tests/test_credentials.py`**: Tests for credential loading functionality
- **`tests/test_audio.py`**: Tests for audio recording and device selection
- **`tests/test_shazam.py`**: Tests for Shazam song identification
- **`tests/test_lastfm.py`**: Tests for Last.fm scrobbling
- **`tests/test_integration.py`**: Integration tests for the main workflow

#### Writing Tests

Tests use pytest fixtures and mocking to isolate units of functionality:

- **Fixtures**: Common test data and mocked dependencies
- **Mocking**: External dependencies like sounddevice, Shazam, and pylast
- **Async testing**: Uses pytest-asyncio for testing async functions
- **Markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, etc. to categorize tests

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality. These hooks will run automatically on each commit:
- **Ruff**: Lints and formats Python code
- **Ruff format**: Ensures consistent code formatting
- **Basic checks**: Trailing whitespace, end-of-file fixer, YAML validation, and large file detection

### Manual Checks
You can run the pre-commit hooks manually:
```sh
pre-commit run --all-files
```

## License
MIT
