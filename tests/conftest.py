"""Common test fixtures and configuration for autoscrobbler tests."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def sample_credentials():
    """Sample credentials for testing."""
    return {
        "lastfm": {
            "api_key": "test_api_key",
            "api_secret": "test_api_secret",
            "username": "test_username",
            "password": "test_password",
        }
    }


@pytest.fixture
def credentials_file(sample_credentials):
    """Create a temporary credentials file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_credentials, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def mock_sounddevice():
    """Mock sounddevice module."""
    with pytest.MonkeyPatch().context() as m:
        mock_sd = Mock()
        mock_sd.default.device = [0, 1]  # Default input, output

        # Define the devices list
        devices = [
            {
                "name": "Test Microphone",
                "index": 0,
                "max_input_channels": 2,
                "default_samplerate": 44100,
            },
            {
                "name": "Test Speaker",
                "index": 1,
                "max_input_channels": 0,
                "default_samplerate": 44100,
            },
        ]

        def query_devices_side_effect(kind=None, **kwargs):
            if kind == "input":
                return {
                    "index": 0,
                    "name": "Test Microphone",
                    "max_input_channels": 2,
                    "default_samplerate": 44100,
                }
            else:
                return devices

        mock_sd.query_devices.side_effect = query_devices_side_effect
        mock_sd.rec.return_value = Mock()
        mock_sd.wait.return_value = None

        m.setattr("autoscrobbler.__main__.sd", mock_sd)
        yield mock_sd


@pytest.fixture
def mock_shazam():
    """Mock Shazam module."""
    with pytest.MonkeyPatch().context() as m:
        mock_shazam = Mock()

        # Create an async mock function
        async def mock_recognize(file_path):
            return {
                "track": {
                    "title": "Test Song",
                    "subtitle": "Test Artist",
                    "sections": [
                        {
                            "type": "SONG",
                            "metadata": [{"title": "Album", "text": "Test Album"}],
                        }
                    ],
                }
            }

        # Create a mock that can be called and has assert methods
        mock_recognize_func = Mock(side_effect=mock_recognize)
        mock_shazam.recognize = mock_recognize_func

        m.setattr("autoscrobbler.__main__.Shazam", Mock(return_value=mock_shazam))
        yield mock_shazam


@pytest.fixture
def mock_pylast():
    """Mock pylast module."""
    with pytest.MonkeyPatch().context() as m:
        mock_network = Mock()
        mock_network.scrobble.return_value = None

        mock_pylast_module = Mock()
        mock_pylast_module.LastFMNetwork.return_value = mock_network
        mock_pylast_module.md5.return_value = "hashed_password"

        m.setattr("autoscrobbler.__main__.pylast", mock_pylast_module)
        yield mock_network
