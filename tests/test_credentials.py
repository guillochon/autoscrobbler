"""Tests for credential loading functionality."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from autoscrobbler.__main__ import find_credentials_path, load_credentials


class TestFindCredentialsPath:
    """Test credential path finding functionality."""

    @pytest.mark.unit
    def test_find_credentials_path_with_existing_file(self, credentials_file):
        """Test finding credentials with explicit path."""
        result = find_credentials_path(credentials_file)
        assert result == credentials_file

    @patch("autoscrobbler.__main__.os.path.isfile")
    def test_find_credentials_path_with_nonexistent_file(self, mock_isfile):
        """Test finding credentials with non-existent explicit path."""
        mock_isfile.return_value = False
        with pytest.raises(FileNotFoundError, match="Could not find credentials.json"):
            find_credentials_path("/nonexistent/path/credentials.json")

    @patch("autoscrobbler.__main__.os.getcwd")
    @patch("autoscrobbler.__main__.os.path.isfile")
    def test_find_credentials_path_in_cwd(
        self, mock_isfile, mock_getcwd, credentials_file
    ):
        """Test finding credentials in current working directory."""
        mock_getcwd.return_value = "/test/cwd"
        mock_isfile.side_effect = lambda path: path == os.path.join(
            "/test/cwd", "credentials.json"
        )

        result = find_credentials_path()
        expected_path = os.path.join("/test/cwd", "credentials.json")
        assert result == expected_path

    @patch("autoscrobbler.__main__.os.getcwd")
    @patch("autoscrobbler.__main__.os.path.isfile")
    @patch("autoscrobbler.__main__.os.path.dirname")
    def test_find_credentials_path_in_package(
        self, mock_dirname, mock_isfile, mock_getcwd
    ):
        """Test finding credentials in package directory."""
        mock_getcwd.return_value = "/test/cwd"
        mock_dirname.return_value = "/test/package"
        mock_isfile.side_effect = lambda path: path == os.path.join(
            "/test/package", "credentials.json"
        )

        result = find_credentials_path()
        expected_path = os.path.join("/test/package", "credentials.json")
        assert result == expected_path

    @patch("autoscrobbler.__main__.os.getcwd")
    @patch("autoscrobbler.__main__.os.path.isfile")
    @patch("autoscrobbler.__main__.__file__")
    def test_find_credentials_path_not_found(self, mock_file, mock_isfile, mock_getcwd):
        """Test finding credentials when not found anywhere."""
        mock_getcwd.return_value = "/test/cwd"
        mock_file.return_value = "/test/package/__main__.py"
        mock_isfile.return_value = False

        with pytest.raises(FileNotFoundError, match="Could not find credentials.json"):
            find_credentials_path()


class TestLoadCredentials:
    """Test credential loading functionality."""

    @pytest.mark.unit
    def test_load_credentials_success(self, sample_credentials, credentials_file):
        """Test successfully loading credentials from file."""
        result = load_credentials(credentials_file)
        assert result == sample_credentials

    @patch("autoscrobbler.__main__.os.path.isfile")
    def test_load_credentials_file_not_found(self, mock_isfile):
        """Test loading credentials from non-existent file."""
        mock_isfile.return_value = False
        with pytest.raises(FileNotFoundError, match="Could not find credentials.json"):
            load_credentials("/nonexistent/path/credentials.json")

    def test_load_credentials_invalid_json(self):
        """Test loading credentials from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json}')
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                load_credentials(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)
