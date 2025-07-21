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
- Combine both options:
  ```sh
  uv run -m autoscrobbler -c /path/to/credentials.json -d 45
  ```

## Notes
- The program will print information about your default input device and status messages for each scrobble attempt.
- If the credentials file is missing or invalid, you'll get a helpful error message.
- The actual interval between attempts is always as close as possible to your specified duty cycle, accounting for processing time.

## Dependencies
- `pylast`
- `sounddevice`
- `soundfile`
- `shazamio`
- (see `pyproject.toml` for full list)

## License
MIT 