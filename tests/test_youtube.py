"""Tests for Scavio YouTube tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.youtube import ScavioYouTubeMetadataTool, ScavioYouTubeSearchTool
from tests.conftest import mock_youtube_metadata_response, mock_youtube_search_response

MOCK_API_KEY = "sk_live_test_key_12345"


class TestScavioYouTubeSearchTool:
    """Tests for ScavioYouTubeSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioYouTubeSearchTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio YouTube Search"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_results(self, mock_async, mock_client_cls):
        """Test that results are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.youtube.search.return_value = mock_youtube_search_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeSearchTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="python tutorial")
        parsed = json.loads(result)
        assert len(parsed["data"]["results"]) == 3


class TestScavioYouTubeMetadataTool:
    """Tests for ScavioYouTubeMetadataTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioYouTubeMetadataTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio YouTube Metadata"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_metadata(self, mock_async, mock_client_cls):
        """Test that metadata is returned."""
        mock_client = MagicMock()
        mock_client.youtube.metadata.return_value = mock_youtube_metadata_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeMetadataTool(api_key=MOCK_API_KEY)
        result = tool._run(video_id="vid_1")
        parsed = json.loads(result)
        assert parsed["data"]["video_id"] == "vid_1"
