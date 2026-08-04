"""Tests for Scavio Walmart tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.walmart import (
    ScavioWalmartProductTool,
    ScavioWalmartProductToolSchema,
    ScavioWalmartSearchTool,
    ScavioWalmartSearchToolSchema,
)
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

    def test_schema_exposes_every_search_param(self):
        """Every /walmart/search param is agent-visible, not constructor-only."""
        assert set(ScavioWalmartSearchToolSchema.model_fields) == {
            "query",
            "domain",
            "device",
            "sort_by",
            "start_page",
            "min_price",
            "max_price",
            "fulfillment_speed",
            "fulfillment_type",
            "delivery_zip",
            "store_id",
        }

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_search_params_reach_the_api(self, mock_async, mock_client_cls):
        """Test that per-call paging, sort and filters are forwarded."""
        mock_client = MagicMock()
        mock_client.walmart.search.return_value = mock_walmart_search_response(2)
        mock_client_cls.return_value = mock_client

        tool = ScavioWalmartSearchTool(api_key=MOCK_API_KEY)
        tool._run(
            query="air fryer",
            start_page=2,
            sort_by="price_low",
            domain="walmart.com",
            device="mobile",
            min_price=20,
            max_price=200,
            fulfillment_speed="tomorrow",
            fulfillment_type="in_store",
            delivery_zip="10001",
            store_id="3520",
        )

        _, kwargs = mock_client.walmart.search.call_args
        assert kwargs["start_page"] == 2
        assert kwargs["sort_by"] == "price_low"
        assert kwargs["domain"] == "walmart.com"
        assert kwargs["device"] == "mobile"
        assert kwargs["min_price"] == 20
        assert kwargs["max_price"] == 200
        assert kwargs["fulfillment_speed"] == "tomorrow"
        assert kwargs["fulfillment_type"] == "in_store"
        assert kwargs["delivery_zip"] == "10001"
        assert kwargs["store_id"] == "3520"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_call_args_beat_constructor_defaults(
        self, mock_async, mock_client_cls
    ):
        """Test that domain/sort_by stay defaults an agent can override."""
        mock_client = MagicMock()
        mock_client.walmart.search.return_value = mock_walmart_search_response(2)
        mock_client_cls.return_value = mock_client

        tool = ScavioWalmartSearchTool(
            api_key=MOCK_API_KEY, domain="walmart.com", sort_by="best_match"
        )

        tool._run(query="air fryer")
        _, kwargs = mock_client.walmart.search.call_args
        assert kwargs["domain"] == "walmart.com"
        assert kwargs["sort_by"] == "best_match"

        tool._run(query="air fryer", sort_by="best_seller")
        _, kwargs = mock_client.walmart.search.call_args
        assert kwargs["sort_by"] == "best_seller"
        assert kwargs["domain"] == "walmart.com"


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

    def test_schema_exposes_every_product_param(self):
        """Every /walmart/product param is agent-visible."""
        assert set(ScavioWalmartProductToolSchema.model_fields) == {
            "product_id",
            "domain",
            "device",
            "delivery_zip",
            "store_id",
        }

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_localization_params_reach_the_api(
        self, mock_async, mock_client_cls
    ):
        """Test that device, delivery_zip and store_id are forwarded."""
        mock_client = MagicMock()
        mock_client.walmart.product.return_value = mock_walmart_product_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioWalmartProductTool(api_key=MOCK_API_KEY)
        tool._run(
            product_id="WM1",
            domain="walmart.com",
            device="tablet",
            delivery_zip="10001",
            store_id="3520",
        )

        _, kwargs = mock_client.walmart.product.call_args
        assert kwargs["domain"] == "walmart.com"
        assert kwargs["device"] == "tablet"
        assert kwargs["delivery_zip"] == "10001"
        assert kwargs["store_id"] == "3520"
