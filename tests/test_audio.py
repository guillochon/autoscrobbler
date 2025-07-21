"""Tests for audio recording and device selection functionality."""

from unittest.mock import Mock, patch

import numpy as np
import pytest

from autoscrobbler.__main__ import record_audio, select_input_device


class TestSelectInputDevice:
    """Test input device selection functionality."""

    @pytest.mark.unit
    def test_select_input_device_auto(self, mock_sounddevice):
        """Test selecting input device with 'auto' option."""
        result = select_input_device("auto")
        assert result == 0  # Default input device index

    def test_select_input_device_by_index(self, mock_sounddevice):
        """Test selecting input device by index."""
        result = select_input_device(0)
        assert result == 0

    def test_select_input_device_by_name(self, mock_sounddevice):
        """Test selecting input device by name."""
        result = select_input_device("Test Microphone")
        assert result == 0

    def test_select_input_device_by_partial_name(self, mock_sounddevice):
        """Test selecting input device by partial name."""
        result = select_input_device("Microphone")
        assert result == 0

    def test_select_input_device_invalid_index(self, mock_sounddevice):
        """Test selecting input device with invalid index."""
        with pytest.raises(ValueError, match="Input device index 999 out of range"):
            select_input_device(999)

    def test_select_input_device_invalid_name(self, mock_sounddevice):
        """Test selecting input device with invalid name."""
        with pytest.raises(
            ValueError,
            match="No input device found with name containing 'InvalidDevice'",
        ):
            select_input_device("InvalidDevice")

    def test_select_input_device_invalid_type(self, mock_sounddevice):
        """Test selecting input device with invalid type."""
        with pytest.raises(ValueError, match="Invalid input_source"):
            select_input_device([])  # Pass a list instead of None

    @patch("autoscrobbler.__main__.sd.query_devices")
    def test_select_input_device_no_input_devices(self, mock_query_devices):
        """Test selecting input device when no input devices are available."""
        mock_query_devices.return_value = [
            {
                "name": "Test Speaker",
                "index": 0,
                "max_input_channels": 0,  # No input channels
                "default_samplerate": 44100,
            }
        ]

        with pytest.raises(RuntimeError, match="No input devices found"):
            select_input_device("auto")

    @patch("builtins.input")
    def test_select_input_device_prompt_user(self, mock_input, mock_sounddevice):
        """Test selecting input device with user prompt."""
        mock_input.return_value = "0"

        result = select_input_device()
        assert result == 0
        mock_input.assert_called_once()

    @patch("builtins.input")
    def test_select_input_device_prompt_user_default(
        self, mock_input, mock_sounddevice
    ):
        """Test selecting input device with user prompt using default."""
        mock_input.return_value = ""

        result = select_input_device()
        assert result == 0  # Default input device index
        mock_input.assert_called_once()

    @patch("builtins.input")
    def test_select_input_device_prompt_user_invalid_then_valid(
        self, mock_input, mock_sounddevice
    ):
        """Test selecting input device with invalid then valid user input."""
        mock_input.side_effect = ["invalid", "999", "0"]

        result = select_input_device()
        assert result == 0
        assert mock_input.call_count == 3


class TestRecordAudio:
    """Test audio recording functionality."""

    @pytest.mark.unit
    def test_record_audio_success(self, mock_sounddevice):
        """Test successful audio recording."""
        # Mock the audio data
        mock_audio = Mock()
        mock_audio.flatten.return_value = np.array([1, 2, 3, 4, 5])
        mock_sounddevice.rec.return_value = mock_audio

        result = record_audio(duration=1, sample_rate=44100, device=0)

        # Verify sounddevice.rec was called with correct parameters
        mock_sounddevice.rec.assert_called_once_with(
            int(1 * 44100),  # samples
            samplerate=44100,
            channels=1,
            dtype="int16",
            device=0,
        )

        # Verify sounddevice.wait was called
        mock_sounddevice.wait.assert_called_once()

        # Verify audio.flatten was called
        mock_audio.flatten.assert_called_once()

        # Verify result
        assert isinstance(result, np.ndarray)
        assert len(result) == 5

    def test_record_audio_default_parameters(self, mock_sounddevice):
        """Test audio recording with default parameters."""
        mock_audio = Mock()
        mock_audio.flatten.return_value = np.array([1, 2, 3])
        mock_sounddevice.rec.return_value = mock_audio

        result = record_audio()

        # Verify default parameters were used
        mock_sounddevice.rec.assert_called_once_with(
            int(10 * 44100),  # 10 seconds * 44100 Hz
            samplerate=44100,
            channels=1,
            dtype="int16",
            device=None,
        )

        assert isinstance(result, np.ndarray)
