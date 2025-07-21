# autoscrobbler

Automatically scrobble songs to Last.fm by listening to your environment and identifying music with Shazam.

## Features
- **Passive audio scrobbling**: Listens to your microphone, identifies music, and scrobbles to Last.fm automatically.
- **Shazam integration**: Uses Shazam for robust song identification.
- **Customizable duty cycle**: Control how often the program listens and scrobbles.
- **Flexible credentials**: Easily specify your credentials file location.

## Requirements
- Python 3.8+
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
