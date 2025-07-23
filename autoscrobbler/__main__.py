import argparse
import asyncio
import json
import logging
import os
import tempfile
import time

import pylast
import sounddevice as sd
import soundfile as sf
from shazamio import Shazam


# Try to find credentials.json in the current working directory, then in the package directory
def find_credentials_path(credentials_path=None):
    if credentials_path and os.path.isfile(credentials_path):
        return credentials_path

    cwd_path = os.path.join(os.getcwd(), "credentials.json")
    pkg_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    if os.path.isfile(cwd_path):
        return cwd_path
    elif os.path.isfile(pkg_path):
        return pkg_path
    else:
        raise FileNotFoundError(
            f"Could not find credentials.json in {cwd_path} or {pkg_path}. Please provide your credentials.json."
        )


# Load credentials from credentials.json
def load_credentials(credentials_path=None):
    path = find_credentials_path(credentials_path)
    with open(path, "r") as f:
        return json.load(f)


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# Print information about the default input device
def print_default_input_device_info():
    try:
        default_input = sd.default.device[0]
        device_info = sd.query_devices(default_input)
        logger.info("Recording from device:")
        logger.info(f"  Name: {device_info['name']}")
        logger.info(f"  Index: {default_input}")
        logger.info(f"  Samplerate: {device_info['default_samplerate']}")
        logger.info(f"  Channels: {device_info['max_input_channels']}")
    except Exception as e:
        logger.error(f"Could not get default input device info: {e}")


def select_input_device(input_source=None):
    devices = sd.query_devices()
    input_devices = [d for d in devices if d["max_input_channels"] > 0]
    if not input_devices:
        raise RuntimeError("No input devices found.")

    default_input_device_index = sd.query_devices(kind="input").get("index")

    if input_source is None:
        # Prompt user
        print("Select input device:")
        for dev in input_devices:
            print(
                f"  [{dev['index']}] {dev['name']} (channels={dev['max_input_channels']})"
            )
        while True:
            choice = input(f"Enter device number [{default_input_device_index}]: ")
            if choice == "":
                return default_input_device_index
            try:
                idx = int(choice)
                for dev in input_devices:
                    if dev["index"] == idx:
                        return dev["index"]
            except Exception:
                pass
            print("Invalid selection. Try again.")
    elif isinstance(input_source, str):
        if input_source.lower() == "auto":
            return default_input_device_index
        # Try to match by name (case-insensitive)
        for dev in input_devices:
            if input_source.lower() in dev["name"].lower():
                return dev["index"]
        raise ValueError(
            f"No input device found with name containing '{input_source}'."
        )
    elif isinstance(input_source, int):
        if 0 <= input_source < len(input_devices):
            return input_devices[input_source]["index"]
        raise ValueError(f"Input device index {input_source} out of range.")
    else:
        raise ValueError(f"Invalid input_source: {input_source}")


def record_audio(duration=10, sample_rate=44100, device=None):
    logger.info("Recording audio...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        device=device,
    )
    sd.wait()
    return audio.flatten()


# Identify song using ShazamIO
async def identify_song(audio_data, sample_rate=44100):
    shazam = Shazam()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        sf.write(tmpfile.name, audio_data, sample_rate)
        out = await shazam.recognize(tmpfile.name)
    os.unlink(tmpfile.name)
    return out


# Scrobble song to Last.fm
def scrobble_song(network, artist, title, album=None):
    logger.info(
        f"Scrobbling: {artist} - {title} [{album if album else 'Unknown album'}]"
    )
    network.scrobble(
        artist=artist, title=title, timestamp=int(time.time())
        # Shazam returns an inconsistent album name, so we don't use it
        # artist=artist, title=title, album=album, timestamp=int(time.time())
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Automatically scrobble songs to Last.fm using audio recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m autoscrobbler
  python -m autoscrobbler --credentials /path/to/credentials.json
  python -m autoscrobbler --duty-cycle 30
  python -m autoscrobbler -c /path/to/credentials.json -d 45
        """,
    )

    parser.add_argument(
        "-c",
        "--credentials",
        help="Path to credentials.json file (default: auto-detect)",
        type=str,
        default=None,
    )

    parser.add_argument(
        "-d",
        "--duty-cycle",
        help="Duty cycle in seconds between recording attempts (default: 60)",
        type=int,
        default=60,
    )
    parser.add_argument(
        "-i",
        "--input-source",
        help="Input source for recording: 'auto', device index, device name, or prompt if not set (default: prompt)",
        type=str,
        default=None,
    )
    return parser.parse_args()


async def main():
    # Parse command line arguments
    args = parse_arguments()

    # Determine input device
    input_source = args.input_source
    # Try to convert to int if possible
    if input_source is not None and input_source.lower() != "auto":
        try:
            input_source_val = int(input_source)
        except Exception:
            input_source_val = input_source
    else:
        input_source_val = input_source
    try:
        selected_device = select_input_device(input_source_val)
    except Exception as e:
        logger.error(f"Error selecting input device: {e}")
        return
    logger.info(f"Using input device index: {selected_device}")
    try:
        device_info = sd.query_devices(selected_device)
        logger.info(f"  Name: {device_info['name']}")
        logger.info(f"  Index: {selected_device}")
        logger.info(f"  Samplerate: {device_info['default_samplerate']}")
        logger.info(f"  Channels: {device_info['max_input_channels']}")
    except Exception as e:
        logger.error(f"Could not get selected input device info: {e}")

    # Load credentials
    try:
        creds = load_credentials(args.credentials)
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        logger.error(
            "Use --credentials flag to specify a custom path to credentials.json"
        )
        return
    lastfm_creds = creds["lastfm"]
    # shazamio_creds = creds.get("shazamio", {})
    # locale = shazamio_creds.get("locale", "en-US")

    # Set up Last.fm network
    network = pylast.LastFMNetwork(
        api_key=lastfm_creds["api_key"],
        api_secret=lastfm_creds["api_secret"],
        username=lastfm_creds["username"],
        password_hash=pylast.md5(lastfm_creds["password"]),
    )

    last_song = None
    logger.info(
        f"Starting passive audio scrobbler with {args.duty_cycle}s duty cycle. Press Ctrl+C to stop."
    )
    while True:
        start_time = time.time()
        try:
            audio_data = record_audio(device=selected_device)
            result = await identify_song(audio_data)
            # Write last result to file
            with open("last_result.json", "w") as f:
                json.dump(result, f)
            track_info = result.get("track")
            if track_info:
                artist = track_info.get("subtitle").strip()
                title = track_info.get("title").split("(")[0].strip()
                if len(title) < 3:
                    title = track_info.get("title").strip()
                if artist and title:
                    if (artist.lower(), title.lower()) != last_song:
                        track_kwargs = {}
                        sections = track_info.get("sections", [])
                        for section in sections:
                            if section.get("type") == "SONG":
                                for item in section.get("metadata", []):
                                    if item.get("title") == "Album":
                                        track_kwargs["album"] = item.get("text")
                                break
                        scrobble_song(network, artist, title, **track_kwargs)
                        last_song = (artist.lower(), title.lower())
                    else:
                        logger.info("Same song as last time, skipping scrobble.")
                else:
                    logger.warning("Incomplete track info, skipping.")
            else:
                logger.warning("No song identified.")
        except Exception as e:
            logger.error(f"Error: {e}")

        # Calculate processing time and adjust sleep duration
        processing_time = time.time() - start_time
        sleep_time = max(0, args.duty_cycle - processing_time)
        logger.info(
            f"Processing took {processing_time:.1f}s, waiting {sleep_time:.1f}s before next attempt..."
        )
        await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(main())
