"""Tests for Scavio TikTok Shop tools.

The mock bodies in tests/conftest.py are the normalized shapes the backend
emits, produced by running the backend normalizers over the recorded fixtures,
so a tool reading the wrong key fails here rather than at runtime.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.tiktok_shop import (
    ScavioTikTokShopCategoriesTool,
    ScavioTikTokShopCategoryProductsTool,
    ScavioTikTokShopProductReviewsTool,
    ScavioTikTokShopProductTool,
    ScavioTikTokShopResolveTool,
    ScavioTikTokShopSearchSuggestionsTool,
    ScavioTikTokShopSearchTool,
    ScavioTikTokShopShopProductsTool,
)
from tests.conftest import (
    MockNotFoundError,
    mock_tiktok_shop_categories_response,
    mock_tiktok_shop_category_products_response,
    mock_tiktok_shop_product_response,
    mock_tiktok_shop_resolve_response,
    mock_tiktok_shop_reviews_response,
    mock_tiktok_shop_search_response,
    mock_tiktok_shop_shop_products_response,
    mock_tiktok_shop_suggestions_response,
)

MOCK_API_KEY = "sk_live_test_key_12345"


class TestScavioTikTokShopSearchTool:
    """Tests for ScavioTikTokShopSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_products_with_exact_prices(self, mock_async, mock_client_cls):
        """Test that search returns product cards carrying real prices."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.search.return_value = (
            mock_tiktok_shop_search_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopSearchTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(search="phone case"))
        assert parsed["data"]["products"][0]["price"]["current"] == 4.88
        assert parsed["data"]["has_more"] is True
        assert parsed["data"]["degraded"] is False

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_products(self, mock_async, mock_client_cls):
        """Test that products are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.search.return_value = (
            mock_tiktok_shop_search_response(30)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopSearchTool(api_key=MOCK_API_KEY, max_results=3)
        parsed = json.loads(tool._run(search="phone case"))
        assert len(parsed["data"]["products"]) == 3

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_forwards_search_and_cursor(self, mock_async, mock_client_cls):
        """Test that the keyword is sent positionally and the cursor by name."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.search.return_value = (
            mock_tiktok_shop_search_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopSearchTool(api_key=MOCK_API_KEY)
        tool._run(search="phone case", cursor="eyJ")
        mock_client.tiktok_shop.search.assert_called_once_with(
            "phone case", cursor="eyJ"
        )

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_description_states_coverage_limit(self, mock_async, mock_client_cls):
        """Test that search never advertises a reliable detail pipeline."""
        tool = ScavioTikTokShopSearchTool(api_key=MOCK_API_KEY)
        assert "44%" in tool.description
        assert "exact prices" in tool.description


class TestScavioTikTokShopSearchSuggestionsTool:
    """Tests for ScavioTikTokShopSearchSuggestionsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_plain_strings(self, mock_async, mock_client_cls):
        """Test that suggestions come back as a flat list of strings."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.search_suggestions.return_value = (
            mock_tiktok_shop_suggestions_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopSearchSuggestionsTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(search="wireless", region="GB"))
        assert parsed["data"]["suggestions"][0] == "wireless charger"
        mock_client.tiktok_shop.search_suggestions.assert_called_once_with(
            "wireless", region="GB"
        )


class TestScavioTikTokShopProductTool:
    """Tests for ScavioTikTokShopProductTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_detail(self, mock_async, mock_client_cls):
        """Test that product detail is returned with variants and shop profile."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.product.return_value = (
            mock_tiktok_shop_product_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopProductTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(product_id="1732293553906094315"))
        assert parsed["data"]["shop"]["followers_count"] == 588860
        assert parsed["data"]["variants"][0]["in_stock"] is True
        assert parsed["data"]["rating"]["distribution"]["5"] == 10163

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_price_is_null_on_detail(self, mock_async, mock_client_cls):
        """Upstream masks the digits, so detail never carries a price."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.product.return_value = (
            mock_tiktok_shop_product_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopProductTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(product_id="1732293553906094315"))
        assert parsed["data"]["price"]["current"] is None
        assert parsed["data"]["price"]["original"] is None

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_404_is_a_normal_not_found(self, mock_async, mock_client_cls):
        """A 404 is a normal answer here, not a raised error."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.product.side_effect = MockNotFoundError(
            "Product not found in this region."
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopProductTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(product_id="1732293553906094315"))
        assert parsed["not_found"] is True
        assert parsed["data"] is None
        assert "44%" in parsed["guidance"]

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_other_errors_still_raise(self, mock_async, mock_client_cls):
        """A non-404 failure is a real failure and must not be swallowed."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.product.side_effect = RuntimeError("boom")
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopProductTool(api_key=MOCK_API_KEY)
        try:
            tool._run(product_id="1732293553906094315")
        except RuntimeError as err:
            assert str(err) == "boom"
        else:
            raise AssertionError("expected RuntimeError")

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_description_carries_both_honesty_notes(self, mock_async, mock_client_cls):
        """Both the price gap and the 44% coverage must be stated."""
        tool = ScavioTikTokShopProductTool(api_key=MOCK_API_KEY)
        assert "does NOT return a price" in tool.description
        assert "44%" in tool.description


class TestScavioTikTokShopProductReviewsTool:
    """Tests for ScavioTikTokShopProductReviewsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_and_truncates_reviews(self, mock_async, mock_client_cls):
        """Test that reviews are returned and truncated to max_results."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.product_reviews.return_value = (
            mock_tiktok_shop_reviews_response(20)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopProductReviewsTool(api_key=MOCK_API_KEY, max_results=5)
        parsed = json.loads(tool._run(product_id="1732293553906094315"))
        assert len(parsed["data"]["reviews"]) == 5
        assert parsed["data"]["reviews"][0]["reviewer_name"] == "C**"
        assert parsed["data"]["filters_applied"]["sort"] == "relevant"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_all_filters_forwarded(self, mock_async, mock_client_cls):
        """Test that every review filter reaches the client unchanged."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.product_reviews.return_value = (
            mock_tiktok_shop_reviews_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopProductReviewsTool(api_key=MOCK_API_KEY)
        tool._run(
            product_id="1732293553906094315",
            page=2,
            page_size=100,
            sort="recent",
            rating=5,
            has_media=True,
            verified_only=False,
            region="US",
        )
        mock_client.tiktok_shop.product_reviews.assert_called_once_with(
            "1732293553906094315",
            page=2,
            page_size=100,
            sort="recent",
            rating=5,
            has_media=True,
            verified_only=False,
            region="US",
        )

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_description_warns_about_total_reviews(self, mock_async, mock_client_cls):
        """total_reviews drifts and must not drive page math."""
        tool = ScavioTikTokShopProductReviewsTool(api_key=MOCK_API_KEY)
        assert "drifts" in tool.description


class TestScavioTikTokShopCategoriesTool:
    """Tests for ScavioTikTokShopCategoriesTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_tree(self, mock_async, mock_client_cls):
        """Test that the two-level category tree comes back intact."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.categories.return_value = (
            mock_tiktok_shop_categories_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopCategoriesTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run())
        assert parsed["data"]["total_categories"] == 240
        top = parsed["data"]["categories"][0]
        assert top["parent_id"] is None
        assert top["children"][0]["parent_id"] == "601450"
        mock_client.tiktok_shop.categories.assert_called_once_with()


class TestScavioTikTokShopCategoryProductsTool:
    """Tests for ScavioTikTokShopCategoryProductsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_listing(self, mock_async, mock_client_cls):
        """Test that a category listing returns cards with exact prices."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.category_products.return_value = (
            mock_tiktok_shop_category_products_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopCategoryProductsTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(category_id="601450", region="GB"))
        assert parsed["data"]["category_id"] == "601450"
        assert parsed["data"]["products"][0]["price"]["currency"] == "USD"
        mock_client.tiktok_shop.category_products.assert_called_once_with(
            "601450", cursor=None, region="GB"
        )

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_unknown_category_is_not_found(self, mock_async, mock_client_cls):
        """An unknown category id is a not-found result, not a raise."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.category_products.side_effect = MockNotFoundError(
            "No products found for this category id."
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopCategoryProductsTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(category_id="999999"))
        assert parsed["not_found"] is True


class TestScavioTikTokShopShopProductsTool:
    """Tests for ScavioTikTokShopShopProductsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_catalog(self, mock_async, mock_client_cls):
        """Test that a shop catalog returns the brief shop block and cards."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.shop_products.return_value = (
            mock_tiktok_shop_shop_products_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopShopProductsTool(api_key=MOCK_API_KEY, max_results=4)
        parsed = json.loads(tool._run(shop_id="7495514739648989419"))
        assert parsed["data"]["shop"]["shop_name"] == "medicube US Store"
        assert "followers_count" not in parsed["data"]["shop"]
        assert len(parsed["data"]["products"]) == 4

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_unknown_shop_is_not_found(self, mock_async, mock_client_cls):
        """An unknown shop id is a not-found result, not a raise."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.shop_products.side_effect = MockNotFoundError(
            "Shop not found or has no products."
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopShopProductsTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(shop_id="123456"))
        assert parsed["not_found"] is True


class TestScavioTikTokShopResolveTool:
    """Tests for ScavioTikTokShopResolveTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_resolves_share_link(self, mock_async, mock_client_cls):
        """Test that a share link resolves to an id and a canonical URL."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.resolve.return_value = (
            mock_tiktok_shop_resolve_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopResolveTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(url="https://vt.tiktok.com/ZT2AHoGsE/"))
        assert parsed["data"]["type"] == "product"
        assert parsed["data"]["product_id"] == "8651224669119091502"
        assert parsed["data"]["url"].startswith("https://shop.tiktok.com/")
        assert parsed["data"]["resolved_by"] == "share_link"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_dead_link_is_not_found(self, mock_async, mock_client_cls):
        """A dead share link is a not-found result, not a raise."""
        mock_client = MagicMock()
        mock_client.tiktok_shop.resolve.side_effect = MockNotFoundError(
            "Could not resolve this link."
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokShopResolveTool(api_key=MOCK_API_KEY)
        parsed = json.loads(tool._run(url="https://vt.tiktok.com/DEAD/"))
        assert parsed["not_found"] is True


class TestPackageExports:
    """The eight tools must be importable from the package root."""

    def test_all_tools_exported(self):
        """Test that every TikTok Shop tool is in __all__."""
        import crewai_scavio

        for name in (
            "ScavioTikTokShopSearchTool",
            "ScavioTikTokShopSearchSuggestionsTool",
            "ScavioTikTokShopProductTool",
            "ScavioTikTokShopProductReviewsTool",
            "ScavioTikTokShopCategoriesTool",
            "ScavioTikTokShopCategoryProductsTool",
            "ScavioTikTokShopShopProductsTool",
            "ScavioTikTokShopResolveTool",
        ):
            assert name in crewai_scavio.__all__
            assert hasattr(crewai_scavio, name)
