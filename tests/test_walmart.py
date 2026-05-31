"""Tests for Scavio Walmart tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.walmart import ScavioWalmartProductTool, ScavioWalmartSearchTool
from tests.conftest import mock_walmart_product_response, mock_walmart_search_response

MOCK_API_KEY = "sk_live_test_key_12345"


class TestScavioWalmartSearchTool:
    """Tests for ScavioWalmartSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioWalmartSearchTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio Walmart Search"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_products(self, mock_async, mock_client_cls):
        """Test that products are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.walmart.search.return_value = mock_walmart_search_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioWalmartSearchTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="air fryer")
        parsed = json.loads(result)
        assert len(parsed["data"]["products"]) == 3


class TestScavioWalmartProductTool:
    """Tests for ScavioWalmartProductTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_product(self, mock_async, mock_client_cls):
        """Test that product data is returned."""
        mock_client = MagicMock()
        mock_client.walmart.product.return_value = mock_walmart_product_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioWalmartProductTool(api_key=MOCK_API_KEY)
        result = tool._run(product_id="WM1")
        parsed = json.loads(result)
        assert parsed["data"]["product_id"] == "WM1"
