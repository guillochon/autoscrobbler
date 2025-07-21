"""Tests for Last.fm scrobbling functionality."""

from unittest.mock import patch

import pytest

from autoscrobbler.__main__ import scrobble_song


class TestScrobbleSong:
    """Test Last.fm scrobbling functionality."""

    @pytest.mark.unit
    def test_scrobble_song_success(self, mock_pylast):
        """Test successful song scrobbling."""
        scrobble_song(mock_pylast, "Test Artist", "Test Song")

        # Verify network.scrobble was called with correct parameters
        mock_pylast.scrobble.assert_called_once()
        call_args = mock_pylast.scrobble.call_args

        assert call_args[1]["artist"] == "Test Artist"
        assert call_args[1]["title"] == "Test Song"
        assert "timestamp" in call_args[1]

    def test_scrobble_song_with_album(self, mock_pylast):
        """Test song scrobbling with album information."""
        scrobble_song(mock_pylast, "Test Artist", "Test Song", album="Test Album")

        # Verify network.scrobble was called with album
        mock_pylast.scrobble.assert_called_once()
        call_args = mock_pylast.scrobble.call_args

        assert call_args[1]["artist"] == "Test Artist"
        assert call_args[1]["title"] == "Test Song"
        assert call_args[1]["album"] == "Test Album"
        assert "timestamp" in call_args[1]

    def test_scrobble_song_without_album(self, mock_pylast):
        """Test song scrobbling without album information."""
        scrobble_song(mock_pylast, "Test Artist", "Test Song")

        # Verify network.scrobble was called without album
        mock_pylast.scrobble.assert_called_once()
        call_args = mock_pylast.scrobble.call_args

        assert call_args[1]["artist"] == "Test Artist"
        assert call_args[1]["title"] == "Test Song"
        # Note: album=None is still passed to the function, which is correct behavior
        assert call_args[1]["album"] is None
        assert "timestamp" in call_args[1]

    def test_scrobble_song_network_error(self, mock_pylast):
        """Test song scrobbling when network raises an error."""
        # Mock network to raise an exception
        mock_pylast.scrobble.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            scrobble_song(mock_pylast, "Test Artist", "Test Song")

    @patch("autoscrobbler.__main__.time.time")
    def test_scrobble_song_timestamp(self, mock_time, mock_pylast):
        """Test that scrobble uses current timestamp."""
        mock_time.return_value = 1234567890.0

        scrobble_song(mock_pylast, "Test Artist", "Test Song")

        # Verify timestamp was used
        mock_pylast.scrobble.assert_called_once()
        call_args = mock_pylast.scrobble.call_args

        assert call_args[1]["timestamp"] == 1234567890

    def test_scrobble_song_empty_artist(self, mock_pylast):
        """Test song scrobbling with empty artist."""
        scrobble_song(mock_pylast, "", "Test Song")

        mock_pylast.scrobble.assert_called_once()
        call_args = mock_pylast.scrobble.call_args

        assert call_args[1]["artist"] == ""

    def test_scrobble_song_empty_title(self, mock_pylast):
        """Test song scrobbling with empty title."""
        scrobble_song(mock_pylast, "Test Artist", "")

        mock_pylast.scrobble.assert_called_once()
        call_args = mock_pylast.scrobble.call_args

        assert call_args[1]["title"] == ""
