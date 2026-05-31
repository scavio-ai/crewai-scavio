"""Tests for Scavio Amazon tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.amazon import ScavioAmazonProductTool, ScavioAmazonSearchTool
from tests.conftest import mock_amazon_product_response, mock_amazon_search_response

MOCK_API_KEY = "sk_live_test_key_12345"


class TestScavioAmazonSearchTool:
    """Tests for ScavioAmazonSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioAmazonSearchTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio Amazon Search"
        assert tool.domain == "com"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_products(self, mock_async, mock_client_cls):
        """Test that products are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.amazon.search.return_value = mock_amazon_search_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioAmazonSearchTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="headphones")
        parsed = json.loads(result)
        assert len(parsed["data"]["products"]) == 3


class TestScavioAmazonProductTool:
    """Tests for ScavioAmazonProductTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioAmazonProductTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio Amazon Product"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_product(self, mock_async, mock_client_cls):
        """Test that product data is returned."""
        mock_client = MagicMock()
        mock_client.amazon.product.return_value = mock_amazon_product_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioAmazonProductTool(api_key=MOCK_API_KEY)
        result = tool._run(asin="B001")
        parsed = json.loads(result)
        assert parsed["data"]["asin"] == "B001"
