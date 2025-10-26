"""Tests for Last.fm scrobbling functionality."""

from unittest.mock import Mock, patch

import pytest

from autoscrobbler.__main__ import get_last_scrobbled_track, scrobble_song


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


class TestGetLastScrobbledTrack:
    """Test getting last scrobbled track functionality."""

    @pytest.mark.unit
    def test_get_last_scrobbled_track_success(self):
        """Test successfully getting the last scrobbled track."""
        # Create a mock network with user and tracks
        mock_network = Mock()
        mock_user = Mock()
        mock_track = Mock()
        mock_artist = Mock()
        
        mock_artist.get_name.return_value = "Test Artist"
        mock_track.get_artist.return_value = mock_artist
        mock_track.get_title.return_value = "Test Song"
        
        mock_last_track = Mock()
        mock_last_track.track = mock_track
        
        mock_user.get_recent_tracks.return_value = [mock_last_track]
        mock_network.get_user.return_value = mock_user
        
        result = get_last_scrobbled_track(mock_network, "test_username")
        
        assert result == ("test artist", "test song")
        mock_network.get_user.assert_called_once_with("test_username")
        mock_user.get_recent_tracks.assert_called_once_with(limit=1)

    @pytest.mark.unit
    def test_get_last_scrobbled_track_no_tracks(self):
        """Test when user has no scrobbled tracks."""
        mock_network = Mock()
        mock_user = Mock()
        
        mock_user.get_recent_tracks.return_value = []
        mock_network.get_user.return_value = mock_user
        
        result = get_last_scrobbled_track(mock_network, "test_username")
        
        assert result is None

    @pytest.mark.unit
    def test_get_last_scrobbled_track_error(self):
        """Test when an error occurs fetching tracks."""
        mock_network = Mock()
        mock_network.get_user.side_effect = Exception("API Error")
        
        result = get_last_scrobbled_track(mock_network, "test_username")
        
        assert result is None

    @pytest.mark.unit
    def test_get_last_scrobbled_track_case_insensitive(self):
        """Test that track names are normalized to lowercase."""
        mock_network = Mock()
        mock_user = Mock()
        mock_track = Mock()
        mock_artist = Mock()
        
        mock_artist.get_name.return_value = "The Beatles"
        mock_track.get_artist.return_value = mock_artist
        mock_track.get_title.return_value = "Hey Jude"
        
        mock_last_track = Mock()
        mock_last_track.track = mock_track
        
        mock_user.get_recent_tracks.return_value = [mock_last_track]
        mock_network.get_user.return_value = mock_user
        
        result = get_last_scrobbled_track(mock_network, "test_username")
        
        assert result == ("the beatles", "hey jude")
