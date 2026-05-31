"""Tests for Scavio Google Search tool."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from crewai_scavio.google import ScavioSearchTool
from tests.conftest import mock_search_response

MOCK_API_KEY = "sk_live_test_key_12345"


class TestScavioSearchTool:
    """Tests for ScavioSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioSearchTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio Search"
        assert tool.max_results == 5
        assert tool.search_type == "classic"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_results(self, mock_async, mock_client_cls):
        """Test that results are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.google.search.return_value = mock_search_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioSearchTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="test query")
        parsed = json.loads(result)
        assert len(parsed["results"]) == 3

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_strips_disabled_sections(self, mock_async, mock_client_cls):
        """Test that disabled sections are removed."""
        mock_client = MagicMock()
        mock_client.google.search.return_value = mock_search_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioSearchTool(
            api_key=MOCK_API_KEY,
            include_knowledge_graph=False,
            include_questions=False,
        )
        result = tool._run(query="test query")
        parsed = json.loads(result)
        assert "knowledge_graph" not in parsed
        assert "questions" not in parsed

    @pytest.mark.asyncio
    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    async def test_arun(self, mock_async_cls, mock_client):
        """Test async execution path."""
        mock_async_client = MagicMock()
        mock_async_client.google.search = AsyncMock(
            return_value=mock_search_response()
        )
        mock_async_cls.return_value = mock_async_client

        tool = ScavioSearchTool(api_key=MOCK_API_KEY, max_results=2)
        result = await tool._arun(query="test")
        parsed = json.loads(result)
        assert len(parsed["results"]) == 2

    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", False)
    def test_raises_import_error(self):
        """Test ImportError when scavio is missing."""
        with pytest.raises(ImportError, match="scavio"):
            ScavioSearchTool(api_key=MOCK_API_KEY)

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_raises_value_error_no_key(self, mock_async, mock_client):
        """Test ValueError when API key is missing."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key"):
                ScavioSearchTool(api_key=None)
