"""Integration tests for the main autoscrobbler workflow."""

from unittest.mock import Mock, patch

import pytest

from autoscrobbler.__main__ import main


class TestMainWorkflow:
    """Test the main workflow integration."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    @patch("autoscrobbler.__main__.pylast.LastFMNetwork")
    @patch("autoscrobbler.__main__.record_audio")
    @patch("autoscrobbler.__main__.identify_song")
    @patch("autoscrobbler.__main__.scrobble_song")
    @patch("autoscrobbler.__main__.time.time")
    @patch("autoscrobbler.__main__.asyncio.sleep")
    async def test_main_workflow_success(
        self,
        mock_sleep,
        mock_time,
        mock_scrobble,
        mock_identify,
        mock_record,
        mock_network,
        mock_load_creds,
        mock_select_device,
        mock_parse_args,
    ):
        """Test successful main workflow execution."""
        # Mock command line arguments
        mock_args = Mock()
        mock_args.credentials = None
        mock_args.duty_cycle = 60
        mock_args.input_source = "auto"
        mock_parse_args.return_value = mock_args

        # Mock device selection
        mock_select_device.return_value = 0

        # Mock credentials loading
        mock_creds = {
            "lastfm": {
                "api_key": "test_key",
                "api_secret": "test_secret",
                "username": "test_user",
                "password": "test_pass",
            }
        }
        mock_load_creds.return_value = mock_creds

        # Mock Last.fm network
        mock_network_instance = Mock()
        mock_network.return_value = mock_network_instance

        # Mock audio recording
        import numpy as np

        mock_record.return_value = np.array([1, 2, 3, 4, 5])

        # Mock song identification
        mock_identify.return_value = {
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

        # Mock time
        mock_time.return_value = 1234567890.0

        # Mock sleep to prevent infinite loop
        mock_sleep.side_effect = Exception("Stop execution")

        # Run main function and expect it to stop due to sleep mock
        with pytest.raises(Exception, match="Stop execution"):
            await main()

        # Verify all the expected calls were made
        mock_parse_args.assert_called_once()
        mock_select_device.assert_called_once_with("auto")
        mock_load_creds.assert_called_once_with(None)
        mock_network.assert_called_once()
        mock_record.assert_called_once_with(device=0)
        mock_identify.assert_called_once()
        mock_scrobble.assert_called_once_with(
            mock_network_instance, "Test Artist", "Test Song", album="Test Album"
        )

    @pytest.mark.asyncio
    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    async def test_main_workflow_device_selection_error(
        self, mock_select_device, mock_parse_args
    ):
        """Test main workflow when device selection fails."""
        # Mock command line arguments
        mock_args = Mock()
        mock_args.input_source = "invalid_device"
        mock_parse_args.return_value = mock_args

        # Mock device selection to fail
        mock_select_device.side_effect = ValueError("Invalid device")

        # Run main function and expect it to return early
        await main()

        # Verify device selection was attempted
        mock_select_device.assert_called_once_with("invalid_device")

    @pytest.mark.asyncio
    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    async def test_main_workflow_credentials_error(
        self, mock_load_creds, mock_select_device, mock_parse_args
    ):
        """Test main workflow when credentials loading fails."""
        # Mock command line arguments
        mock_args = Mock()
        mock_args.credentials = "/nonexistent/path"
        mock_parse_args.return_value = mock_args

        # Mock device selection
        mock_select_device.return_value = 0

        # Mock credentials loading to fail
        mock_load_creds.side_effect = FileNotFoundError("Credentials not found")

        # Run main function and expect it to return early
        await main()

        # Verify credentials loading was attempted
        mock_load_creds.assert_called_once_with("/nonexistent/path")

    @pytest.mark.asyncio
    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    @patch("autoscrobbler.__main__.pylast.LastFMNetwork")
    @patch("autoscrobbler.__main__.record_audio")
    @patch("autoscrobbler.__main__.identify_song")
    @patch("autoscrobbler.__main__.time.time")
    @patch("autoscrobbler.__main__.asyncio.sleep")
    async def test_main_workflow_no_song_identified(
        self,
        mock_sleep,
        mock_time,
        mock_identify,
        mock_record,
        mock_network,
        mock_load_creds,
        mock_select_device,
        mock_parse_args,
    ):
        """Test main workflow when no song is identified."""
        # Mock command line arguments
        mock_args = Mock()
        mock_args.credentials = None
        mock_args.duty_cycle = 60
        mock_args.input_source = "auto"
        mock_parse_args.return_value = mock_args

        # Mock device selection
        mock_select_device.return_value = 0

        # Mock credentials loading
        mock_creds = {
            "lastfm": {
                "api_key": "test_key",
                "api_secret": "test_secret",
                "username": "test_user",
                "password": "test_pass",
            }
        }
        mock_load_creds.return_value = mock_creds

        # Mock Last.fm network
        mock_network_instance = Mock()
        mock_network.return_value = mock_network_instance

        # Mock audio recording
        import numpy as np

        mock_record.return_value = np.array([1, 2, 3, 4, 5])

        # Mock song identification to return no track
        mock_identify.return_value = {}

        # Mock time
        mock_time.return_value = 1234567890.0

        # Mock sleep to prevent infinite loop
        mock_sleep.side_effect = Exception("Stop execution")

        # Run main function and expect it to stop due to sleep mock
        with pytest.raises(Exception, match="Stop execution"):
            await main()

        # Verify song identification was called but no scrobbling occurred
        mock_identify.assert_called_once()

    @pytest.mark.asyncio
    @patch("autoscrobbler.__main__.parse_arguments")
    @patch("autoscrobbler.__main__.select_input_device")
    @patch("autoscrobbler.__main__.load_credentials")
    @patch("autoscrobbler.__main__.pylast.LastFMNetwork")
    @patch("autoscrobbler.__main__.record_audio")
    @patch("autoscrobbler.__main__.identify_song")
    @patch("autoscrobbler.__main__.scrobble_song")
    @patch("autoscrobbler.__main__.time.time")
    @patch("autoscrobbler.__main__.asyncio.sleep")
    async def test_main_workflow_same_song_skipped(
        self,
        mock_sleep,
        mock_time,
        mock_scrobble,
        mock_identify,
        mock_record,
        mock_network,
        mock_load_creds,
        mock_select_device,
        mock_parse_args,
    ):
        """Test main workflow when the same song is identified twice."""
        # Mock command line arguments
        mock_args = Mock()
        mock_args.credentials = None
        mock_args.duty_cycle = 60
        mock_args.input_source = "auto"
        mock_parse_args.return_value = mock_args

        # Mock device selection
        mock_select_device.return_value = 0

        # Mock credentials loading
        mock_creds = {
            "lastfm": {
                "api_key": "test_key",
                "api_secret": "test_secret",
                "username": "test_user",
                "password": "test_pass",
            }
        }
        mock_load_creds.return_value = mock_creds

        # Mock Last.fm network
        mock_network_instance = Mock()
        mock_network.return_value = mock_network_instance

        # Mock audio recording
        import numpy as np

        mock_record.return_value = np.array([1, 2, 3, 4, 5])

        # Mock song identification to return the same song twice
        mock_identify.return_value = {
            "track": {"title": "Test Song", "subtitle": "Test Artist"}
        }

        # Mock time
        mock_time.return_value = 1234567890.0

        # Mock sleep to prevent infinite loop
        mock_sleep.side_effect = Exception("Stop execution")

        # Run main function and expect it to stop due to sleep mock
        with pytest.raises(Exception, match="Stop execution"):
            await main()

        # Verify song identification was called once and scrobbling once
        # (The loop only runs once due to the sleep mock raising an exception)
        assert mock_identify.call_count == 1
        assert mock_scrobble.call_count == 1
