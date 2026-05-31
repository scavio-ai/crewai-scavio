"""Tests for Scavio Reddit tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.reddit import ScavioRedditPostTool, ScavioRedditSearchTool
from tests.conftest import mock_reddit_post_response, mock_reddit_search_response

MOCK_API_KEY = "sk_live_test_key_12345"


class TestScavioRedditSearchTool:
    """Tests for ScavioRedditSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioRedditSearchTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio Reddit Search"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_posts(self, mock_async, mock_client_cls):
        """Test that posts are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.reddit.search.return_value = mock_reddit_search_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditSearchTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="python")
        parsed = json.loads(result)
        assert len(parsed["data"]["posts"]) == 3


class TestScavioRedditPostTool:
    """Tests for ScavioRedditPostTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_post(self, mock_async, mock_client_cls):
        """Test that post data is returned."""
        mock_client = MagicMock()
        mock_client.reddit.post.return_value = mock_reddit_post_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditPostTool(api_key=MOCK_API_KEY)
        result = tool._run(url="https://reddit.com/r/test/comments/abc/test")
        parsed = json.loads(result)
        assert parsed["data"]["post"]["id"] == "post_1"
