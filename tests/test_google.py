"""Tests for Scavio Google Search tool."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from crewai_scavio.google import (
    ScavioGoogleAiModeTool,
    ScavioGoogleFlightsTool,
    ScavioGoogleHotelsDetailTool,
    ScavioGoogleHotelsTool,
    ScavioGoogleMapsPlaceTool,
    ScavioGoogleMapsReviewsTool,
    ScavioGoogleMapsSearchTool,
    ScavioGoogleNewsTool,
    ScavioGoogleShoppingProductTool,
    ScavioGoogleShoppingStoresTool,
    ScavioGoogleShoppingTool,
    ScavioGoogleTrendingTool,
    ScavioGoogleTrendsTool,
    ScavioSearchTool,
)
from tests.conftest import (
    mock_google_ai_mode_response,
    mock_google_flights_response,
    mock_google_hotels_detail_response,
    mock_google_hotels_response,
    mock_google_maps_place_response,
    mock_google_maps_reviews_response,
    mock_google_maps_search_response,
    mock_google_news_response,
    mock_google_shopping_product_response,
    mock_google_shopping_response,
    mock_google_shopping_stores_response,
    mock_google_trending_response,
    mock_google_trends_response,
    mock_search_response,
)

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
        assert tool.device == "desktop"

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
        assert len(parsed["organic_results"]) == 3
        assert parsed["organic_results"][0]["link"].startswith("https://")
        assert "snippet" in parsed["organic_results"][0]

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_maps_v2_params(self, mock_async, mock_client_cls):
        """Test that country_code/language/page map to gl/hl/start."""
        mock_client = MagicMock()
        mock_client.google.search.return_value = mock_search_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioSearchTool(
            api_key=MOCK_API_KEY,
            country_code="fr",
            language="de",
            page=3,
        )
        tool._run(query="test query")

        _, kwargs = mock_client.google.search.call_args
        assert kwargs["gl"] == "fr"
        assert kwargs["hl"] == "de"
        assert kwargs["start"] == 20
        # v1-only params must never reach the SDK.
        assert "country_code" not in kwargs
        assert "language" not in kwargs
        assert "page" not in kwargs
        assert "search_type" not in kwargs
        assert "light_request" not in kwargs

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_page_one_omits_start(self, mock_async, mock_client_cls):
        """Test that page 1 (or unset) does not send a start offset."""
        mock_client = MagicMock()
        mock_client.google.search.return_value = mock_search_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioSearchTool(api_key=MOCK_API_KEY)
        tool._run(query="test query")

        _, kwargs = mock_client.google.search.call_args
        assert "start" not in kwargs
        assert "gl" not in kwargs
        assert "hl" not in kwargs
        assert kwargs["device"] == "desktop"

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
        assert len(parsed["organic_results"]) == 2

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


class TestScavioGoogleAiModeTool:
    """Tests for ScavioGoogleAiModeTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_flat_response_and_truncation(self, mock_async, mock_client_cls):
        """Test that the response is flat and references are truncated."""
        mock_client = MagicMock()
        mock_client.google.ai_mode.return_value = mock_google_ai_mode_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleAiModeTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="what is a search api")
        parsed = json.loads(result)
        assert "data" not in parsed
        assert len(parsed["references"]) == 3
        mock_client.google.ai_mode.assert_called_once_with(
            query="what is a search api"
        )


class TestScavioGoogleMapsSearchTool:
    """Tests for ScavioGoogleMapsSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_local_results(self, mock_async, mock_client_cls):
        """Test that local_results are truncated and params forwarded."""
        mock_client = MagicMock()
        mock_client.google.maps_search.return_value = (
            mock_google_maps_search_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleMapsSearchTool(api_key=MOCK_API_KEY, max_results=4)
        result = tool._run(query="coffee in brooklyn", start=20, gl="us")
        parsed = json.loads(result)
        assert len(parsed["local_results"]) == 4
        mock_client.google.maps_search.assert_called_once_with(
            query="coffee in brooklyn", start=20, gl="us"
        )

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_schema_has_no_v1_params(self, mock_async, mock_client_cls):
        """Test that retired v1 param names are absent from the schema."""
        tool = ScavioGoogleMapsSearchTool(api_key=MOCK_API_KEY)
        fields = tool.args_schema.model_fields
        for retired in ("light_request", "country_code", "language", "page"):
            assert retired not in fields


class TestScavioGoogleMapsPlaceTool:
    """Tests for ScavioGoogleMapsPlaceTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_accepts_place_id(self, mock_async, mock_client_cls):
        """Test that place details are returned for a place_id."""
        mock_client = MagicMock()
        mock_client.google.maps_place.return_value = (
            mock_google_maps_place_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleMapsPlaceTool(api_key=MOCK_API_KEY)
        result = tool._run(place_id="ChIJ_1")
        parsed = json.loads(result)
        assert parsed["place_results"]["place_id"] == "ChIJ_1"
        mock_client.google.maps_place.assert_called_once_with(
            place_id="ChIJ_1", data_cid=None
        )


class TestScavioGoogleMapsReviewsTool:
    """Tests for ScavioGoogleMapsReviewsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_reviews(self, mock_async, mock_client_cls):
        """Test that reviews are truncated and sort_by is forwarded."""
        mock_client = MagicMock()
        mock_client.google.maps_reviews.return_value = (
            mock_google_maps_reviews_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleMapsReviewsTool(api_key=MOCK_API_KEY, max_results=2)
        result = tool._run(place_id="ChIJ_1", sort_by="newest")
        parsed = json.loads(result)
        assert len(parsed["reviews"]) == 2
        mock_client.google.maps_reviews.assert_called_once_with(
            place_id="ChIJ_1", sort_by="newest"
        )


class TestScavioGoogleShoppingTool:
    """Tests for ScavioGoogleShoppingTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_shopping_results(self, mock_async, mock_client_cls):
        """Test that shopping_results are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.google.shopping.return_value = mock_google_shopping_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleShoppingTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="running shoes", min_price=50)
        parsed = json.loads(result)
        assert len(parsed["shopping_results"]) == 3
        mock_client.google.shopping.assert_called_once_with(
            query="running shoes", min_price=50
        )


class TestScavioGoogleShoppingProductTool:
    """Tests for ScavioGoogleShoppingProductTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_forwards_catalog_id_and_query(self, mock_async, mock_client_cls):
        """Test that catalog_id is paired with query as the API requires."""
        mock_client = MagicMock()
        mock_client.google.shopping_product.return_value = (
            mock_google_shopping_product_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleShoppingProductTool(api_key=MOCK_API_KEY)
        result = tool._run(catalog_id="catalog_1", query="running shoes")
        parsed = json.loads(result)
        assert parsed["product_results"]["title"] == "Product 1"
        mock_client.google.shopping_product.assert_called_once_with(
            catalog_id="catalog_1", query="running shoes"
        )


class TestScavioGoogleShoppingStoresTool:
    """Tests for ScavioGoogleShoppingStoresTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_requires_both_fields(self, mock_async, mock_client_cls):
        """Test that catalog_id and next_page_token are both required."""
        mock_client = MagicMock()
        mock_client.google.shopping_stores.return_value = (
            mock_google_shopping_stores_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleShoppingStoresTool(api_key=MOCK_API_KEY)
        result = tool._run(catalog_id="catalog_1", next_page_token="token_2")
        parsed = json.loads(result)
        assert len(parsed["product_results"]["stores"]) == 3
        fields = tool.args_schema.model_fields
        assert fields["catalog_id"].is_required()
        assert fields["next_page_token"].is_required()
        mock_client.google.shopping_stores.assert_called_once_with(
            catalog_id="catalog_1", next_page_token="token_2"
        )


class TestScavioGoogleFlightsTool:
    """Tests for ScavioGoogleFlightsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_both_flight_lists(self, mock_async, mock_client_cls):
        """Test that best_flights and other_flights are both truncated."""
        mock_client = MagicMock()
        mock_client.google.flights.return_value = mock_google_flights_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleFlightsTool(api_key=MOCK_API_KEY, max_results=2)
        result = tool._run(
            departure_id="JFK",
            arrival_id="LAX",
            outbound_date="2026-09-01",
            type=2,
        )
        parsed = json.loads(result)
        assert len(parsed["best_flights"]) == 2
        assert len(parsed["other_flights"]) == 2
        mock_client.google.flights.assert_called_once_with(
            departure_id="JFK",
            arrival_id="LAX",
            outbound_date="2026-09-01",
            type=2,
        )


class TestScavioGoogleHotelsTool:
    """Tests for ScavioGoogleHotelsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_properties(self, mock_async, mock_client_cls):
        """Test that properties are truncated and carry a detail_token."""
        mock_client = MagicMock()
        mock_client.google.hotels.return_value = mock_google_hotels_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleHotelsTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(
            query="Lisbon hotels",
            check_in_date="2026-09-01",
            check_out_date="2026-09-04",
        )
        parsed = json.loads(result)
        assert len(parsed["properties"]) == 3
        assert parsed["properties"][0]["detail_token"] == "detail_token_1"
        mock_client.google.hotels.assert_called_once_with(
            query="Lisbon hotels",
            check_in_date="2026-09-01",
            check_out_date="2026-09-04",
        )


class TestScavioGoogleHotelsDetailTool:
    """Tests for ScavioGoogleHotelsDetailTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_booking_sources(self, mock_async, mock_client_cls):
        """Test that a property's booking sources are returned."""
        mock_client = MagicMock()
        mock_client.google.hotels_detail.return_value = (
            mock_google_hotels_detail_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleHotelsDetailTool(api_key=MOCK_API_KEY)
        result = tool._run(
            detail_token="detail_token_1",
            check_in_date="2026-09-01",
            check_out_date="2026-09-04",
        )
        parsed = json.loads(result)
        assert parsed["property"]["booking_sources"][0]["name"] == "Booking.com"
        mock_client.google.hotels_detail.assert_called_once_with(
            detail_token="detail_token_1",
            check_in_date="2026-09-01",
            check_out_date="2026-09-04",
        )


class TestScavioGoogleNewsTool:
    """Tests for ScavioGoogleNewsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_news_results(self, mock_async, mock_client_cls):
        """Test that news_results are truncated for a single driver."""
        mock_client = MagicMock()
        mock_client.google.news.return_value = mock_google_news_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleNewsTool(api_key=MOCK_API_KEY, max_results=4)
        result = tool._run(query="ai agents", so=1)
        parsed = json.loads(result)
        assert len(parsed["news_results"]) == 4
        mock_client.google.news.assert_called_once_with(query="ai agents", so=1)


class TestScavioGoogleTrendsTool:
    """Tests for ScavioGoogleTrendsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_interest_by_region(self, mock_async, mock_client_cls):
        """Test that interest_by_region is truncated and timeseries kept."""
        mock_client = MagicMock()
        mock_client.google.trends.return_value = mock_google_trends_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleTrendsTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="search api", geo="US", data_type="GEO_MAP")
        parsed = json.loads(result)
        assert len(parsed["interest_by_region"]) == 3
        assert "timeline_data" in parsed["interest_over_time"]
        mock_client.google.trends.assert_called_once_with(
            query="search api", geo="US", data_type="GEO_MAP"
        )


class TestScavioGoogleTrendingTool:
    """Tests for ScavioGoogleTrendingTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_requires_geo(self, mock_async, mock_client_cls):
        """Test that geo is required and trends are truncated."""
        mock_client = MagicMock()
        mock_client.google.trending.return_value = mock_google_trending_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioGoogleTrendingTool(api_key=MOCK_API_KEY, max_results=5)
        result = tool._run(geo="US", hours=24)
        parsed = json.loads(result)
        assert len(parsed["trends"]) == 5
        assert tool.args_schema.model_fields["geo"].is_required()
        mock_client.google.trending.assert_called_once_with(geo="US", hours=24)
