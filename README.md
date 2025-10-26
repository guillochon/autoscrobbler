# autoscrobbler

[![CI Status](https://github.com/guillochon/autoscrobbler/actions/workflows/ci.yml/badge.svg)](https://github.com/guillochon/autoscrobbler/actions/workflows/ci.yml)
![License](https://img.shields.io/github/license/guillochon/autoscrobbler)
![Coverage](https://img.shields.io/badge/coverage-97.60%25-brightgreen)

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
   git clone git@github.com:guillochon/autoscrobbler.git
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

**Note:** You may see some harmless warnings from the `pydub` library (used by Shazam). These are SyntaxWarnings about regex patterns and don't affect functionality. They are automatically suppressed in the latest version.

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

## Docker Usage

**⚠️ Windows Docker Users:** Running autoscrobbler via Docker on Windows is **unsupported** due to the complexity of audio device access through WSL2. Setting up PulseAudio and audio forwarding in WSL2 is cumbersome and often unreliable. We recommend running autoscrobbler natively on Windows instead.

Run autoscrobbler in a Docker container (Linux/macOS only):

### Quick Start
```sh
# Build the image
docker build -t autoscrobbler .

# Run with your credentials file
docker run --rm -it --device /dev/snd \
  -v /path/to/credentials.json:/app/credentials.json:ro \
  autoscrobbler
```

### Custom Options
```sh
# Run with custom duty cycle and input device
docker run --rm -it --device /dev/snd \
  -v /path/to/credentials.json:/app/credentials.json:ro \
  autoscrobbler --duty-cycle 30 --input-source "USB Microphone"
```

### Requirements
- Docker installed on your system
- Audio device access (the `--device /dev/snd` flag)
- Your `credentials.json` file mounted into the container

### Notes
- The container uses Python 3.12 and includes all necessary audio dependencies
- Your credentials file must be mounted at runtime for security
- Audio input requires access to the host's sound devices

### Docker Troubleshooting

**If you see "No input devices found" error:**

1. **Check audio device access:**
   ```sh
   # Run the audio check script inside the container
   docker run --rm -it --device /dev/snd autoscrobbler /app/check_audio.sh
   ```

2. **Verify host audio setup:**
   ```sh
   # On the host system, check if ALSA is working
   aplay -l
   arecord -l
   ```

3. **Common solutions:**
   - **Linux host:** Ensure ALSA is installed and working
   - **Windows host:** Use WSL2 with audio forwarding enabled
   - **macOS host:** Use Docker Desktop with audio device sharing
   - **Raspberry Pi:** Add user to audio group: `sudo usermod -a -G audio $USER`

4. **Alternative Docker run commands:**
   ```sh
   # For Linux with PulseAudio
   docker run --rm -it --device /dev/snd --group-add audio \
     -v /path/to/credentials.json:/app/credentials.json:ro \
     autoscrobbler

   # For systems with specific audio device
   docker run --rm -it --device /dev/snd \
     -v /path/to/credentials.json:/app/credentials.json:ro \
     -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
     autoscrobbler
   ```

5. **Test audio manually:**
   ```sh
   # Test recording inside container
   docker run --rm -it --device /dev/snd autoscrobbler \
     uv run python -c "import sounddevice as sd; print(sd.query_devices())"
   
   # Run comprehensive audio test
   docker run --rm -it --device /dev/snd autoscrobbler \
     uv run python test_docker_audio.py
   ```

## Raspberry Pi Service Installation

For continuous operation, you can install autoscrobbler as a systemd service on a Raspberry Pi. This allows it to run automatically on boot and restart if it crashes.

### Prerequisites
- Raspberry Pi with Raspberry Pi OS (or similar Linux distribution)
- Python 3.8 - 3.12 installed
- USB microphone or audio input device connected
- Internet connection for Shazam and Last.fm API access

### Installation Steps

1. **Install required system dependencies**
   ```sh
   sudo apt-get update && sudo apt-get install -y portaudio19-dev
   ```

2. **Clone and install the project**
   ```sh
   git clone git@github.com:guillochon/autoscrobbler.git
   cd autoscrobbler
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc
   uv sync
   ```
   
   **Note:** The uv installer places the binary in `~/.local/bin/uv`. Make sure this directory is in your PATH.

3. **Create credentials file**
   ```sh
   sudo mkdir -p /opt/autoscrobbler
   sudo chown -R pi:pi /opt/autoscrobbler
   sudo cp credentials.example.json /opt/autoscrobbler/credentials.json
   ```

   Edit the newly created file to add your last.fm API credentials.

4. **Run the setup script**
   ```sh
   chmod +x setup_audio_service.sh
   ./setup_audio_service.sh
   ```

   This script will:
   - Add your user to the audio group (if not already added)
   - Create the necessary service directory
   - Copy the service file to the user space
   - Enable the service
   - Test audio device access

   **Note:** If the script adds you to the audio group, you'll need to log out and log back in for the changes to take effect.

### Troubleshooting

**If the service fails to start:**
1. Check the logs: `journalctl --user -u autoscrobbler.service -n 50`
2. Verify audio device permissions: `groups` (should include audio)
3. Test audio manually: `uv run -m autoscrobbler --input-source auto`
4. Check credentials file permissions and content
5. Verify uv is installed in the correct location: `which uv` (should show `/home/pi/.local/bin/uv`)
6. Ensure the project is cloned to `/home/pi/autoscrobbler` as expected by the service

**Audio device issues:**
- Ensure your microphone is properly connected and recognized
- Test with: `arecord -l` to list audio devices
- Check volume levels: `alsamixer`

**Network connectivity:**
- Ensure the Pi has internet access
- Test Shazam API connectivity manually
- Check firewall settings if applicable

### Configuration Options

You can modify the service file at `~/.config/systemd/user/autoscrobbler.service` to customize:
- **Duty cycle**: Change `--duty-cycle 60` to your preferred interval
- **Input device**: Replace `--input-source auto` with a specific device
- **Credentials path**: Update the path if you store credentials elsewhere
- **Working directory**: Change the `WorkingDirectory` path if your project is located elsewhere

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
