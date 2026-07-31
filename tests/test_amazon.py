"""Tests for Scavio Amazon tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.amazon import (
    ScavioAmazonOffersTool,
    ScavioAmazonProductTool,
    ScavioAmazonSearchTool,
)
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
        assert tool.country is None

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_forwards_country_and_page(self, mock_async, mock_client_cls):
        """country and page reach the SDK; nothing retired is sent."""
        mock_client = MagicMock()
        mock_client.amazon.search.return_value = mock_amazon_search_response(2)
        mock_client_cls.return_value = mock_client

        tool = ScavioAmazonSearchTool(api_key=MOCK_API_KEY)
        tool._run(query="headphones", country="gb", page=2)
        assert mock_client.amazon.search.call_args.kwargs == {
            "query": "headphones",
            "country": "gb",
            "page": 2,
        }

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_tool_country_is_the_fallback(self, mock_async, mock_client_cls):
        """The tool-level country applies when the agent passes none."""
        mock_client = MagicMock()
        mock_client.amazon.search.return_value = mock_amazon_search_response(2)
        mock_client_cls.return_value = mock_client

        tool = ScavioAmazonSearchTool(api_key=MOCK_API_KEY, country="de")
        tool._run(query="headphones")
        assert mock_client.amazon.search.call_args.kwargs["country"] == "de"

    def test_retired_params_are_not_schema_fields(self):
        """A tool schema must not advertise a filter the API drops."""
        retired = {
            "sort_by",
            "pages",
            "category_id",
            "merchant_id",
            "language",
            "currency",
            "device",
            "zip_code",
            "autoselect_variant",
        }
        from crewai_scavio.amazon import ScavioAmazonSearchInput

        assert not set(ScavioAmazonSearchInput.model_fields) & retired

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


class TestScavioAmazonOffersTool:
    """Tests for ScavioAmazonOffersTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioAmazonOffersTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio Amazon Offers"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_offers(self, mock_async, mock_client_cls):
        """Offers are returned and the ASIN reaches the SDK."""
        mock_client = MagicMock()
        mock_client.amazon.offers.return_value = {
            "data": {
                "asin": "B001",
                "count": 2,
                "offers": [
                    {"seller_name": "A", "price": 10.0, "is_buy_box_winner": True},
                    {"seller_name": "B", "price": 11.0, "is_buy_box_winner": False},
                ],
            }
        }
        mock_client_cls.return_value = mock_client

        tool = ScavioAmazonOffersTool(api_key=MOCK_API_KEY)
        result = tool._run(asin="B001", country="gb")
        parsed = json.loads(result)
        assert parsed["data"]["offers"][0]["is_buy_box_winner"] is True
        assert mock_client.amazon.offers.call_args.kwargs == {
            "asin": "B001",
            "country": "gb",
        }
