"""Tests for CLI and argument parsing functionality."""

from unittest.mock import Mock, patch

import pytest

from autoscrobbler.__main__ import list_input_devices, main, parse_arguments


class TestParseArguments:
    """Test argument parsing functionality."""

    def test_parse_arguments_default(self):
        """Test parsing arguments with default values."""
        with patch("sys.argv", ["autoscrobbler"]):
            args = parse_arguments()
            assert args.credentials is None
            assert args.duty_cycle == 60
            assert args.input_source is None

    def test_parse_arguments_with_credentials(self):
        """Test parsing arguments with credentials path."""
        with patch("sys.argv", ["autoscrobbler", "-c", "/path/to/creds.json"]):
            args = parse_arguments()
            assert args.credentials == "/path/to/creds.json"
            assert args.duty_cycle == 60
            assert args.input_source is None

    def test_parse_arguments_with_credentials_short(self):
        """Test parsing arguments with credentials path using short flag."""
        with patch("sys.argv", ["autoscrobbler", "--credentials", "/path/to/creds.json"]):
            args = parse_arguments()
            assert args.credentials == "/path/to/creds.json"

    def test_parse_arguments_with_duty_cycle(self):
        """Test parsing arguments with duty cycle."""
        with patch("sys.argv", ["autoscrobbler", "-d", "30"]):
            args = parse_arguments()
            assert args.credentials is None
            assert args.duty_cycle == 30
            assert args.input_source is None

    def test_parse_arguments_with_duty_cycle_long(self):
        """Test parsing arguments with duty cycle using long flag."""
        with patch("sys.argv", ["autoscrobbler", "--duty-cycle", "45"]):
            args = parse_arguments()
            assert args.duty_cycle == 45

    def test_parse_arguments_with_input_source(self):
        """Test parsing arguments with input source."""
        with patch("sys.argv", ["autoscrobbler", "-i", "auto"]):
            args = parse_arguments()
            assert args.credentials is None
            assert args.duty_cycle == 60
            assert args.input_source == "auto"

    def test_parse_arguments_with_input_source_long(self):
        """Test parsing arguments with input source using long flag."""
        with patch("sys.argv", ["autoscrobbler", "--input-source", "Microphone"]):
            args = parse_arguments()
            assert args.input_source == "Microphone"

    def test_parse_arguments_with_all_options(self):
        """Test parsing arguments with all options specified."""
        with patch("sys.argv", ["autoscrobbler", "-c", "/creds.json", "-d", "30", "-i", "list"]):
            args = parse_arguments()
            assert args.credentials == "/creds.json"
            assert args.duty_cycle == 30
            assert args.input_source == "list"


class TestMainFunction:
    """Test main function edge cases."""

    @patch("autoscrobbler.__main__.parse_arguments")
    def test_main_list_devices(self, mock_parse_args):
        """Test main function when listing devices."""
        mock_args = Mock()
        mock_args.input_source = "list"
        mock_parse_args.return_value = mock_args

        with patch("autoscrobbler.__main__.list_input_devices") as mock_list:
            main()
            mock_list.assert_called_once()

    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    def test_main_device_selection_exception(self, mock_select_device, mock_parse_args):
        """Test main function when device selection raises an exception."""
        mock_args = Mock()
        mock_args.input_source = "auto"
        mock_parse_args.return_value = mock_args

        mock_select_device.side_effect = Exception("Device error")

        main()
        # Should handle the error gracefully and return

    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    def test_main_credentials_file_not_found(self, mock_load_creds, mock_select_device, mock_parse_args):
        """Test main function when credentials file is not found."""
        mock_args = Mock()
        mock_args.input_source = "auto"
        mock_args.credentials = None
        mock_parse_args.return_value = mock_args

        mock_select_device.return_value = 0
        mock_load_creds.side_effect = FileNotFoundError("Credentials not found")

        main()
        # Should handle the error gracefully and return

    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    @patch("autoscrobbler.__main__.pylast.LastFMNetwork")
    def test_main_incomplete_track_info(self, mock_network, mock_load_creds, mock_select_device, mock_parse_args):
        """Test main function when track info is incomplete."""
        mock_args = Mock()
        mock_args.input_source = "auto"
        mock_args.credentials = None
        mock_args.duty_cycle = 60
        mock_parse_args.return_value = mock_args

        mock_select_device.return_value = 0
        mock_load_creds.return_value = {
            "lastfm": {
                "api_key": "test_key",
                "api_secret": "test_secret",
                "username": "test_user",
                "password": "test_pass",
            }
        }

        with patch("autoscrobbler.__main__.sd.query_devices") as mock_query_devices, \
             patch("autoscrobbler.__main__.record_audio") as mock_record, \
             patch("autoscrobbler.__main__.identify_song") as mock_identify, \
             patch("autoscrobbler.__main__.json.dump") as mock_json_dump, \
             patch("autoscrobbler.__main__.time.time") as mock_time, \
             patch("autoscrobbler.__main__.time.sleep") as mock_sleep:
            import numpy as np
            
            mock_query_devices.return_value = {"name": "Test Device", "index": 0, "default_samplerate": 44100, "max_input_channels": 1}
            mock_record.return_value = np.array([1, 2, 3])
            mock_identify.return_value = {
                "track": {
                    "title": "",  # Empty title
                    "subtitle": "Test Artist",
                }
            }
            mock_time.return_value = 1234567890.0
            mock_sleep.side_effect = Exception("Stop execution")

            with pytest.raises(Exception, match="Stop execution"):
                main()

    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    @patch("autoscrobbler.__main__.pylast.LastFMNetwork")
    def test_main_title_with_parentheses(self, mock_network, mock_load_creds, mock_select_device, mock_parse_args):
        """Test main function when title contains parentheses."""
        mock_args = Mock()
        mock_args.input_source = "auto"
        mock_args.credentials = None
        mock_args.duty_cycle = 60
        mock_parse_args.return_value = mock_args

        mock_select_device.return_value = 0
        mock_load_creds.return_value = {
            "lastfm": {
                "api_key": "test_key",
                "api_secret": "test_secret",
                "username": "test_user",
                "password": "test_pass",
            }
        }

        with patch("autoscrobbler.__main__.sd.query_devices") as mock_query_devices, \
             patch("autoscrobbler.__main__.record_audio") as mock_record, \
             patch("autoscrobbler.__main__.identify_song") as mock_identify, \
             patch("autoscrobbler.__main__.scrobble_song") as mock_scrobble, \
             patch("autoscrobbler.__main__.json.dump") as mock_json_dump, \
             patch("autoscrobbler.__main__.time.time") as mock_time, \
             patch("autoscrobbler.__main__.time.sleep") as mock_sleep:
            import numpy as np
            
            mock_query_devices.return_value = {"name": "Test Device", "index": 0, "default_samplerate": 44100, "max_input_channels": 1}
            mock_record.return_value = np.array([1, 2, 3])
            mock_identify.return_value = {
                "track": {
                    "title": "Test Song (Remix)",
                    "subtitle": "Test Artist",
                }
            }
            mock_time.return_value = 1234567890.0
            mock_sleep.side_effect = Exception("Stop execution")

            with pytest.raises(Exception, match="Stop execution"):
                main()

            # Verify scrobble was called with cleaned title
            mock_scrobble.assert_called_once()
            call_args = mock_scrobble.call_args[0]
            assert call_args[2] == "Test Song"  # Should strip (Remix)

    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    @patch("autoscrobbler.__main__.pylast.LastFMNetwork")
    def test_main_record_exception(self, mock_network, mock_load_creds, mock_select_device, mock_parse_args):
        """Test main function when recording raises an exception."""
        mock_args = Mock()
        mock_args.input_source = "auto"
        mock_args.credentials = None
        mock_args.duty_cycle = 60
        mock_parse_args.return_value = mock_args

        mock_select_device.return_value = 0
        mock_load_creds.return_value = {
            "lastfm": {
                "api_key": "test_key",
                "api_secret": "test_secret",
                "username": "test_user",
                "password": "test_pass",
            }
        }

        with patch("autoscrobbler.__main__.sd.query_devices") as mock_query_devices, \
             patch("autoscrobbler.__main__.record_audio") as mock_record, \
             patch("autoscrobbler.__main__.time.time") as mock_time, \
             patch("autoscrobbler.__main__.time.sleep") as mock_sleep:
            
            mock_query_devices.return_value = {"name": "Test Device", "index": 0, "default_samplerate": 44100, "max_input_channels": 1}
            mock_record.side_effect = Exception("Recording error")
            mock_time.return_value = 1234567890.0
            mock_sleep.side_effect = Exception("Stop execution")

            with pytest.raises(Exception, match="Stop execution"):
                main()

            # Should handle the recording error gracefully
            mock_record.assert_called_once()

    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    @patch("autoscrobbler.__main__.pylast.LastFMNetwork")
    def test_main_short_title_with_parentheses(self, mock_network, mock_load_creds, mock_select_device, mock_parse_args):
        """Test main function when title has parentheses but is short."""
        mock_args = Mock()
        mock_args.input_source = "auto"
        mock_args.credentials = None
        mock_args.duty_cycle = 60
        mock_parse_args.return_value = mock_args

        mock_select_device.return_value = 0
        mock_load_creds.return_value = {
            "lastfm": {
                "api_key": "test_key",
                "api_secret": "test_secret",
                "username": "test_user",
                "password": "test_pass",
            }
        }

        with patch("autoscrobbler.__main__.sd.query_devices") as mock_query_devices, \
             patch("autoscrobbler.__main__.record_audio") as mock_record, \
             patch("autoscrobbler.__main__.identify_song") as mock_identify, \
             patch("autoscrobbler.__main__.scrobble_song") as mock_scrobble, \
             patch("autoscrobbler.__main__.json.dump") as mock_json_dump, \
             patch("autoscrobbler.__main__.time.time") as mock_time, \
             patch("autoscrobbler.__main__.time.sleep") as mock_sleep:
            import numpy as np
            
            mock_query_devices.return_value = {"name": "Test Device", "index": 0, "default_samplerate": 44100, "max_input_channels": 1}
            mock_record.return_value = np.array([1, 2, 3])
            mock_identify.return_value = {
                "track": {
                    "title": "Hi (Remix)",  # Title after splitting is "Hi" which is < 3 chars
                    "subtitle": "Test Artist",
                }
            }
            mock_time.return_value = 1234567890.0
            mock_sleep.side_effect = Exception("Stop execution")

            with pytest.raises(Exception, match="Stop execution"):
                main()

            # Verify scrobble was called with original title since it's short
            mock_scrobble.assert_called_once()

    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    @patch("autoscrobbler.__main__.pylast.LastFMNetwork")
    def test_main_with_album_info(self, mock_network, mock_load_creds, mock_select_device, mock_parse_args):
        """Test main function when track has album info."""
        mock_args = Mock()
        mock_args.input_source = "auto"
        mock_args.credentials = None
        mock_args.duty_cycle = 60
        mock_parse_args.return_value = mock_args

        mock_select_device.return_value = 0
        mock_load_creds.return_value = {
            "lastfm": {
                "api_key": "test_key",
                "api_secret": "test_secret",
                "username": "test_user",
                "password": "test_pass",
            }
        }

        with patch("autoscrobbler.__main__.sd.query_devices") as mock_query_devices, \
             patch("autoscrobbler.__main__.record_audio") as mock_record, \
             patch("autoscrobbler.__main__.identify_song") as mock_identify, \
             patch("autoscrobbler.__main__.scrobble_song") as mock_scrobble, \
             patch("autoscrobbler.__main__.json.dump") as mock_json_dump, \
             patch("autoscrobbler.__main__.time.time") as mock_time, \
             patch("autoscrobbler.__main__.time.sleep") as mock_sleep:
            import numpy as np
            
            mock_query_devices.return_value = {"name": "Test Device", "index": 0, "default_samplerate": 44100, "max_input_channels": 1}
            mock_record.return_value = np.array([1, 2, 3])
            mock_identify.return_value = {
                "track": {
                    "title": "Test Song",
                    "subtitle": "Test Artist",
                    "sections": [
                        {
                            "type": "SONG",
                            "metadata": [
                                {"title": "Album", "text": "Test Album (Deluxe Edition)"}
                            ],
                        }
                    ],
                }
            }
            mock_time.return_value = 1234567890.0
            mock_sleep.side_effect = Exception("Stop execution")

            with pytest.raises(Exception, match="Stop execution"):
                main()

            # Verify scrobble was called with album info
            mock_scrobble.assert_called_once()
            call_kwargs = mock_scrobble.call_args[1]
            assert call_kwargs["album"] == "Test Album"  # Should strip (Deluxe Edition)

    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    @patch("autoscrobbler.__main__.pylast.LastFMNetwork")
    def test_main_device_info_error(self, mock_network, mock_load_creds, mock_select_device, mock_parse_args):
        """Test main function when getting device info raises an exception."""
        mock_args = Mock()
        mock_args.input_source = "auto"
        mock_args.credentials = None
        mock_args.duty_cycle = 60
        mock_parse_args.return_value = mock_args

        mock_select_device.return_value = 0
        mock_load_creds.return_value = {
            "lastfm": {
                "api_key": "test_key",
                "api_secret": "test_secret",
                "username": "test_user",
                "password": "test_pass",
            }
        }

        with patch("autoscrobbler.__main__.sd.query_devices") as mock_query_devices:
            mock_query_devices.side_effect = Exception("Device info error")
            
            # Should handle the error gracefully and continue
            main()

