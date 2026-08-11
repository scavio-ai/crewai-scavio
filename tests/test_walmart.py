"""Tests for Scavio Walmart tools.

Walmart was rebuilt on scrape.do: ``device``, ``delivery_zip`` and ``store_id``
are retired (the API answers 200 with a ``warnings[]`` array if you send them),
five endpoints are new, and ``domain`` is the price-bearing parameter. These
tests pin the shape the tools must have after that rebuild, not the one they
had before it.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

from crewai_scavio.walmart import (
    ScavioWalmartCategoryTool,
    ScavioWalmartOffersTool,
    ScavioWalmartProductTool,
    ScavioWalmartReviewsTool,
    ScavioWalmartSearchTool,
    ScavioWalmartSellerProductsTool,
    ScavioWalmartSellerTool,
    _WalmartProductInput,
    _WalmartSearchInput,
)
from tests.conftest import mock_walmart_product_response, mock_walmart_search_response

MOCK_API_KEY = "sk_live_test_key_12345"

RETIRED_PARAMS = {"device", "delivery_zip", "store_id"}

ALL_TOOLS = [
    ScavioWalmartSearchTool,
    ScavioWalmartProductTool,
    ScavioWalmartReviewsTool,
    ScavioWalmartCategoryTool,
    ScavioWalmartOffersTool,
    ScavioWalmartSellerTool,
    ScavioWalmartSellerProductsTool,
]


class TestWalmartSurface:
    """The endpoint set and the parameters it accepts."""

    def test_all_seven_endpoints_are_wrapped(self):
        """search, product, reviews, category, offers, seller, seller-products."""
        assert len({tool.__name__ for tool in ALL_TOOLS}) == 7

    def test_retired_params_are_gone_everywhere(self):
        """device / delivery_zip / store_id were retired with the rebuild."""
        for tool in ALL_TOOLS:
            fields = set(tool.model_fields["args_schema"].default.model_fields)
            assert fields & RETIRED_PARAMS == set(), tool.__name__

    def test_search_schema_matches_the_live_route(self):
        assert set(_WalmartSearchInput.model_fields) == {
            "query",
            "domain",
            "page",
            "start_page",
            "sort_by",
            "min_price",
            "max_price",
            "fulfillment_speed",
            "fulfillment_type",
        }

    def test_product_takes_no_domain(self):
        """walmart.ca product pages cannot be fetched, so there is no domain."""
        assert set(_WalmartProductInput.model_fields) == {"product_id"}


class TestWalmartPricing:
    """`domain` is the price-bearing parameter, so descriptions must say so."""

    def test_domain_priced_tools_name_both_prices(self):
        for tool in (ScavioWalmartSearchTool, ScavioWalmartCategoryTool):
            description = tool.model_fields["description"].default
            assert "2 credits on 'com.mx'" in description, tool.__name__

    def test_domainless_tools_explain_why_they_are_flat(self):
        for tool in (ScavioWalmartProductTool, ScavioWalmartSellerProductsTool):
            description = tool.model_fields["description"].default
            assert "body-priced" in description.lower(), tool.__name__


class TestScavioWalmartSearchTool:
    """Tests for ScavioWalmartSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        tool = ScavioWalmartSearchTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio Walmart Search"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_products(self, mock_async, mock_client_cls):
        mock_client = MagicMock()
        mock_client.walmart.search.return_value = mock_walmart_search_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioWalmartSearchTool(api_key=MOCK_API_KEY, max_results=3)
        parsed = json.loads(tool._run(query="air fryer"))
        assert len(parsed["data"]["products"]) == 3

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_search_params_reach_the_api(self, mock_async, mock_client_cls):
        mock_client = MagicMock()
        mock_client.walmart.search.return_value = mock_walmart_search_response(2)
        mock_client_cls.return_value = mock_client

        tool = ScavioWalmartSearchTool(api_key=MOCK_API_KEY)
        tool._run(
            query="air fryer",
            page=2,
            sort_by="price_low",
            domain="com.mx",
            min_price=20,
            max_price=200,
            fulfillment_speed="tomorrow",
            fulfillment_type="in_store",
        )

        _, kwargs = mock_client.walmart.search.call_args
        assert kwargs["page"] == 2
        assert kwargs["sort_by"] == "price_low"
        assert kwargs["domain"] == "com.mx"
        assert kwargs["min_price"] == 20
        assert kwargs["max_price"] == 200
        assert kwargs["fulfillment_speed"] == "tomorrow"
        assert kwargs["fulfillment_type"] == "in_store"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    async def test_arun(self, mock_async_cls, mock_client):
        mock_async_client = MagicMock()
        mock_async_client.walmart.search = AsyncMock(
            return_value=mock_walmart_search_response(10)
        )
        mock_async_cls.return_value = mock_async_client

        tool = ScavioWalmartSearchTool(api_key=MOCK_API_KEY, max_results=2)
        parsed = json.loads(await tool._arun(query="air fryer"))
        assert len(parsed["data"]["products"]) == 2


class TestScavioWalmartProductTool:
    """Tests for ScavioWalmartProductTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_product(self, mock_async, mock_client_cls):
        mock_client = MagicMock()
        mock_client.walmart.product.return_value = mock_walmart_product_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioWalmartProductTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(product_id="WM1"))
        assert parsed["data"]["product_id"] == "WM1"


class TestScavioWalmartSellerProductsTool:
    """Tests for ScavioWalmartSellerProductsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_the_catalog_page(self, mock_async, mock_client_cls):
        mock_client = MagicMock()
        mock_client.walmart.seller_products.return_value = mock_walmart_search_response(
            10
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioWalmartSellerProductsTool(api_key=MOCK_API_KEY, max_results=4)
        parsed = json.loads(tool._run(seller_id="101480084"))
        assert len(parsed["data"]["products"]) == 4

    def test_seller_id_is_documented_as_the_numeric_catalog_id(self):
        """The GUID seller_id 404s; the numeric catalog id is the one that works."""
        field = ScavioWalmartSellerProductsTool.model_fields[
            "args_schema"
        ].default.model_fields["seller_id"]
        assert "seller_catalog_id" in field.description
