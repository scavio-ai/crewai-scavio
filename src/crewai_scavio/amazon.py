"""Scavio Amazon tools for CrewAI.

The Amazon API moved to a new upstream provider in 2026-07 and the request
surface shrank. ``sort_by``, ``pages``, ``category_id``, ``merchant_id``,
``language``, ``currency``, ``device``, ``zip_code`` and
``autoselect_variant`` are gone. They are removed here rather than kept as
silent no-ops: ``sort_by`` was verified against the marketplace and every sort
value returns the identical unordered result set, so a tool attribute promising
a sort is a promise the API cannot keep.

``country`` (ISO 3166-1 alpha-2: us, gb, de, ...) replaces the old ``domain``
suffix. The API still accepts ``domain`` as a deprecated alias, but these tools
only speak ``country`` so an agent never sees two spellings of one param.
"""


from typing import Any, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


_COUNTRY_DESCRIPTION = (
    "Marketplace country code (ISO 3166-1 alpha-2), not a domain: 'us' "
    "(default), 'gb' (the UK is gb, not uk), 'ca', 'de', 'fr', 'es', 'it', "
    "'jp', 'in', 'au', 'br', 'mx', 'nl', 'pl', 'se', 'sg', 'ae', 'sa', 'eg', "
    "'cn', 'be', 'tr'. An unrecognised code falls back to 'us'."
)


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class ScavioAmazonSearchInput(BaseModel):
    """Input schema for ScavioAmazonSearchTool."""

    query: str = Field(..., description="The product search query.")
    country: str | None = Field(default=None, description=_COUNTRY_DESCRIPTION)
    page: int | None = Field(
        default=None,
        description="Result page, 1-based. One page per call, 1 credit each.",
    )


class ScavioAmazonProductInput(BaseModel):
    """Input schema for ScavioAmazonProductTool."""

    asin: str = Field(..., description="The Amazon Standard Identification Number.")
    country: str | None = Field(default=None, description=_COUNTRY_DESCRIPTION)


class ScavioAmazonOffersInput(BaseModel):
    """Input schema for ScavioAmazonOffersTool."""

    asin: str = Field(..., description="The Amazon Standard Identification Number.")
    country: str | None = Field(default=None, description=_COUNTRY_DESCRIPTION)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class ScavioAmazonSearchTool(ScavioBaseTool):
    """Amazon product search tool powered by the Scavio Amazon API.

    Attributes:
        country: Default marketplace country code when the agent passes none.
    """

    name: str = "Scavio Amazon Search"
    description: str = (
        "Search for products on Amazon using the Scavio Amazon API. "
        "Returns products with asin, title, url, image, price, currency, "
        "rating, reviews_count, is_sponsored, position, badge, sales_volume "
        "and delivery. Results are not sorted and cannot be sorted or filtered "
        "by category, merchant or price - rank them yourself."
    )
    args_schema: Type[BaseModel] = ScavioAmazonSearchInput

    country: str | None = None

    def _run(
        self,
        query: str,
        country: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous Amazon product search.

        Args:
            query: The product search query.
            country: Marketplace country code. Falls back to the tool default.
            page: Result page, 1-based.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.amazon.search(
            query=query,
            country=country or self.country,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        country: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous Amazon product search.

        Args:
            query: The product search query.
            country: Marketplace country code. Falls back to the tool default.
            page: Result page, 1-based.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.amazon.search(
            query=query,
            country=country or self.country,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioAmazonProductTool(ScavioBaseTool):
    """Amazon product detail tool powered by the Scavio Amazon API.

    Retrieves detailed information for a single product by its ASIN.
    """

    name: str = "Scavio Amazon Product"
    description: str = (
        "Get detailed product information from Amazon by ASIN using the Scavio "
        "Amazon API. Returns title, brand, description, features, price, "
        "list_price, rating, reviews_count, availability, images, "
        "best_sellers_rank and specifications. `price` is the buy-box price "
        "only - use Scavio Amazon Offers for competing sellers."
    )
    args_schema: Type[BaseModel] = ScavioAmazonProductInput

    country: str | None = None

    def _run(self, asin: str, country: str | None = None, **kwargs: Any) -> str:
        """Fetch product details by ASIN synchronously.

        Args:
            asin: The Amazon Standard Identification Number.
            country: Marketplace country code. Falls back to the tool default.

        Returns:
            JSON-serialised product details.
        """
        raw = self.client.amazon.product(
            asin=asin,
            country=country or self.country,
        )
        return self._format_response(raw)

    async def _arun(
        self, asin: str, country: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch product details by ASIN asynchronously.

        Args:
            asin: The Amazon Standard Identification Number.
            country: Marketplace country code. Falls back to the tool default.

        Returns:
            JSON-serialised product details.
        """
        raw = await self.async_client.amazon.product(
            asin=asin,
            country=country or self.country,
        )
        return self._format_response(raw)


class ScavioAmazonOffersTool(ScavioBaseTool):
    """Amazon seller-offer tool powered by the Scavio Amazon API.

    Lists every seller offer for one ASIN, including which one holds the buy
    box. Use for price comparison, reseller research and buy-box monitoring.
    """

    name: str = "Scavio Amazon Offers"
    description: str = (
        "List every seller offer for an Amazon ASIN using the Scavio Amazon "
        "API. Returns condition, seller_name, ships_from, is_buy_box_winner, "
        "is_prime, price, list_price, shipping_price and discount_percentage "
        "per offer. `price` excludes shipping_price and the buy-box winner is "
        "not always the cheapest. Page 1 only. An ASIN sold only by Amazon "
        "returns an empty offers list plus a `note` - that is a normal answer."
    )
    args_schema: Type[BaseModel] = ScavioAmazonOffersInput

    country: str | None = None

    def _run(self, asin: str, country: str | None = None, **kwargs: Any) -> str:
        """Fetch the offer listing for an ASIN synchronously.

        Args:
            asin: The Amazon Standard Identification Number.
            country: Marketplace country code. Falls back to the tool default.

        Returns:
            JSON-serialised offer listing.
        """
        raw = self.client.amazon.offers(
            asin=asin,
            country=country or self.country,
        )
        raw = self._truncate_nested(raw, "data", "offers")
        return self._format_response(raw)

    async def _arun(
        self, asin: str, country: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch the offer listing for an ASIN asynchronously.

        Args:
            asin: The Amazon Standard Identification Number.
            country: Marketplace country code. Falls back to the tool default.

        Returns:
            JSON-serialised offer listing.
        """
        raw = await self.async_client.amazon.offers(
            asin=asin,
            country=country or self.country,
        )
        raw = self._truncate_nested(raw, "data", "offers")
        return self._format_response(raw)
