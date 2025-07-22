#!/usr/bin/env python3
"""
Test script to verify Docker audio setup for autoscrobbler.
Run this inside the Docker container to check if audio devices are accessible.

Usage:
  uv run python test_docker_audio.py
  # or
  python test_docker_audio.py (if dependencies are installed globally)
"""

import sys
import warnings

# Suppress pydub warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pydub")


def test_audio_devices():
    """Test if audio devices are accessible."""
    print("=== Docker Audio Setup Test ===\n")

    # Test 1: Check if sounddevice can be imported
    try:
        import sounddevice as sd

        print("✓ sounddevice imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import sounddevice: {e}")
        print("\nThis usually means:")
        print("  - Dependencies not installed in current environment")
        print("  - Need to run with 'uv run python test_docker_audio.py'")
        print("  - Or install dependencies globally")
        return False

    # Test 2: Check if devices can be queried
    try:
        devices = sd.query_devices()
        print(f"✓ Found {len(devices)} total audio devices")
    except Exception as e:
        print(f"✗ Failed to query devices: {e}")
        return False

    # Test 3: Check for input devices
    try:
        input_devices = [d for d in devices if d["max_input_channels"] > 0]
        print(f"✓ Found {len(input_devices)} input devices")

        if not input_devices:
            print("✗ No input devices found!")
            print("\nAvailable devices:")
            for i, dev in enumerate(devices):
                print(
                    f"  [{i}] {dev['name']} (input channels: {dev['max_input_channels']})"
                )
            return False

        # List input devices
        print("\nInput devices:")
        for i, dev in enumerate(input_devices):
            print(f"  [{i}] {dev['name']} (channels: {dev['max_input_channels']})")

    except Exception as e:
        print(f"✗ Failed to check input devices: {e}")
        return False

    # Test 4: Check default input device
    try:
        default_input = sd.query_devices(kind="input")
        print(f"\n✓ Default input device: {default_input['name']}")
    except Exception as e:
        print(f"✗ Failed to get default input device: {e}")
        return False

    # Test 5: Test basic recording (1 second)
    try:
        print("\nTesting recording (1 second)...")

        audio = sd.rec(int(1 * 44100), samplerate=44100, channels=1, dtype="int16")
        sd.wait()
        print(f"✓ Recording successful (samples: {len(audio)})")
    except Exception as e:
        print(f"✗ Recording failed: {e}")
        return False

    # Test 6: Check if soundfile works
    try:
        import soundfile as sf  # noqa: F401

        print("✓ soundfile imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import soundfile: {e}")
        return False

    # Test 7: Check if Shazam can be imported
    try:
        from shazamio import Shazam  # noqa: F401

        print("✓ shazamio imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import shazamio: {e}")
        return False

    print("\n=== All tests passed! ===")
    print("Your Docker audio setup is working correctly.")
    print("You can now run autoscrobbler with:")
    print("  docker run --rm -it --device /dev/snd \\")
    print("    -v /path/to/credentials.json:/app/credentials.json:ro \\")
    print("    autoscrobbler")

    return True


if __name__ == "__main__":
    success = test_audio_devices()
    sys.exit(0 if success else 1)
