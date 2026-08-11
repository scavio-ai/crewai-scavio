"""Scavio Redfin tools for CrewAI.

1 credit flat on all three endpoints (REDFIN_CREDIT_COST =
scrapedoCreditCost(1)) -- internal stingray JSON API.

- Responses are prefixed with a 4-char anti-hijack guard that must be stripped.
- days_on_market IS ALWAYS NULL: mainHouseInfo has no `dom` key. OWNER DECISION
  OPEN -- drop the field or find its real source. Do not document it as
  populated.
- CITY NAMES ARE NOT ACCEPTED on `location`: Redfin's own name lookup is the
  single path its edge blocks our proxy pool from. Pass a redfin.com region URL
  (/city/, /neighborhood/, /county/, /zipcode/) or region_id + region_type.
- region_id is NOT a ZIP code -- different number spaces, and a ZIP there
  resolves to another city rather than failing.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_RedfinSearchSort = Literal[
    "recommended", "price_low", "price_high", "newest", "oldest",
    "sqft_low", "sqft_high", "price_per_sqft_low", "price_per_sqft_high"
]
_RedfinSearchPropertyType = Literal[
    "house", "condo", "townhouse", "multi_family", "land", "other", "co_op"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _RedfinSearchInput(BaseModel):
    """Input schema for ScavioRedfinSearchTool."""

    location: str | None = Field(
        default=None,
        description=(
            "A redfin.com region URL (/city/, /neighborhood/, /county/, /zipcode/) or "
            "a bare 5-digit ZIP (1-500 characters). CITY NAMES ARE NOT ACCEPTED - "
            "Redfin's own name lookup is blocked to us; use region_id + region_type "
            "instead."
        ),
    )
    region_id: int | None = Field(
        default=None,
        description=(
            "Redfin internal region id (>= 1), used together with region_type. NOT a "
            "ZIP code - the two are different number spaces and a ZIP here resolves to "
            "another city rather than failing."
        ),
    )
    region_type: Literal[1, 2, 5, 6] | None = Field(
        default=None,
        description=(
            "Region kind that region_id belongs to: 1 neighborhood, 2 ZIP, 5 county, 6 "
            "city. Must be sent together with region_id or both are ignored in favour "
            "of location."
        ),
    )
    listing_status: Literal["for_sale", "sold", "for_rent"] | None = Field(
        default=None,
        description="Market to search. Defaults to 'for_sale'.",
    )
    sold_within_days: int | None = Field(
        default=None,
        description=(
            "Sold within the last N days (>= 1). REJECTED unless "
            "listing_status='sold', where it defaults to 90."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based; page size is whatever limit is set to. No upper "
            "bound."
        ),
    )
    limit: int | None = Field(
        default=None,
        description="Listings per page, 1-350. Defaults to 100.",
    )
    sort: _RedfinSearchSort | None = Field(
        default=None,
        description=(
            "Result sort order. Defaults to 'recommended', Redfin's own ranking."
        ),
    )
    min_price: float | None = Field(
        default=None,
        description=(
            "Minimum price, inclusive (>= 0). Monthly rent when "
            "listing_status='for_rent'."
        ),
    )
    max_price: float | None = Field(
        default=None,
        description=(
            "Maximum price, inclusive (>= 0). Monthly rent when "
            "listing_status='for_rent'."
        ),
    )
    beds_min: int | None = Field(
        default=None,
        description=(
            "Minimum bedrooms (whole number >= 0); fractional values are rejected."
        ),
    )
    beds_max: int | None = Field(
        default=None,
        description=(
            "Maximum bedrooms (whole number >= 0); fractional values are rejected."
        ),
    )
    baths_min: int | None = Field(
        default=None,
        description=(
            "Minimum bathrooms (whole number >= 0). WHOLE BATHS ONLY - 1.5 is rejected "
            "rather than silently truncated to 1. There is no baths_max."
        ),
    )
    sqft_min: int | None = Field(
        default=None,
        description="Minimum living area in square feet (whole number >= 0).",
    )
    sqft_max: int | None = Field(
        default=None,
        description="Maximum living area in square feet (whole number >= 0).",
    )
    lot_size_min: int | None = Field(
        default=None,
        description=(
            "Minimum lot size in square feet (whole number >= 0). There is no "
            "lot_size_max."
        ),
    )
    year_built_min: int | None = Field(
        default=None,
        description="Earliest year built (whole number >= 0).",
    )
    year_built_max: int | None = Field(
        default=None,
        description="Latest year built (whole number >= 0).",
    )
    max_hoa: float | None = Field(
        default=None,
        description="Maximum monthly HOA fee in dollars (>= 0).",
    )
    property_type: _RedfinSearchPropertyType | None = Field(
        default=None,
        description="Restrict to one property type.",
    )
    has_pool: bool | None = Field(
        default=None,
        description="Only listings with a pool.",
    )
    max_days_on_market: int | None = Field(
        default=None,
        description=(
            "Listed at most N days ago (whole number >= 0). Cannot be combined with "
            "min_days_on_market - Redfin expresses both bounds through one param."
        ),
    )
    min_days_on_market: int | None = Field(
        default=None,
        description=(
            "Listed at least N days ago (whole number >= 0). Cannot be combined with "
            "max_days_on_market."
        ),
    )


class _RedfinPropertyInput(BaseModel):
    """Input schema for ScavioRedfinPropertyTool."""

    property_id: str = Field(
        ...,
        description=(
            "Redfin property id, or any redfin.com listing URL carrying one (1-500 "
            "characters)."
        ),
    )


class _RedfinMarketInput(BaseModel):
    """Input schema for ScavioRedfinMarketTool."""

    location: str | None = Field(
        default=None,
        description=(
            "A redfin.com region URL (/city/, /neighborhood/, /county/, /zipcode/) or "
            "a bare 5-digit ZIP (1-500 characters). City names are not accepted."
        ),
    )
    region_id: int | None = Field(
        default=None,
        description=(
            "Redfin internal region id (>= 1), used together with region_type. Not a "
            "ZIP code."
        ),
    )
    region_type: Literal[1, 2, 5, 6] | None = Field(
        default=None,
        description=(
            "Region kind that region_id belongs to: 1 neighborhood, 2 ZIP, 5 county, 6 "
            "city. Must be sent together with region_id or both are ignored in favour "
            "of location."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioRedfinSearchTool(ScavioBaseTool):
    """Redfin listings: price, price per sqft, beds, baths, living area, lot size, year
    built, coordinates, listing remarks and full photo galleries, for sale, sold or for
    rent.
    """

    name: str = "Scavio Redfin Search"
    description: str = (
        "Redfin listings: price, price per sqft, beds, baths, living area, lot size, "
        "year built, coordinates, listing remarks and full photo galleries, for sale, "
        "sold or for rent. Up to 350 per page. Provide location, or region_id together "
        "with region_type. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _RedfinSearchInput

    def _run(
        self,
        location: str | None = None,
        region_id: int | None = None,
        region_type: Literal[1, 2, 5, 6] | None = None,
        listing_status: Literal["for_sale", "sold", "for_rent"] | None = None,
        sold_within_days: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        sort: _RedfinSearchSort | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        beds_min: int | None = None,
        beds_max: int | None = None,
        baths_min: int | None = None,
        sqft_min: int | None = None,
        sqft_max: int | None = None,
        lot_size_min: int | None = None,
        year_built_min: int | None = None,
        year_built_max: int | None = None,
        max_hoa: float | None = None,
        property_type: _RedfinSearchPropertyType | None = None,
        has_pool: bool | None = None,
        max_days_on_market: int | None = None,
        min_days_on_market: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/redfin/search synchronously.

        Args:
            location: A redfin.com region URL (/city/, /neighborhood/, /county/,
                /zipcode/) or a bare 5-digit ZIP (1-500 characters).
            region_id: Redfin internal region id (>= 1), used together with region_type.
            region_type: Region kind that region_id belongs to: 1 neighborhood, 2 ZIP, 5
                county, 6 city.
            listing_status: Market to search. Defaults to 'for_sale'.
            sold_within_days: Sold within the last N days (>= 1).
            page: Results page, 1-based; page size is whatever limit is set to.
            limit: Listings per page, 1-350. Defaults to 100.
            sort: Result sort order. Defaults to 'recommended', Redfin's own ranking.
            min_price: Minimum price, inclusive (>= 0).
            max_price: Maximum price, inclusive (>= 0).
            beds_min: Minimum bedrooms (whole number >= 0); fractional values are
                rejected.
            beds_max: Maximum bedrooms (whole number >= 0); fractional values are
                rejected.
            baths_min: Minimum bathrooms (whole number >= 0).
            sqft_min: Minimum living area in square feet (whole number >= 0).
            sqft_max: Maximum living area in square feet (whole number >= 0).
            lot_size_min: Minimum lot size in square feet (whole number >= 0).
            year_built_min: Earliest year built (whole number >= 0).
            year_built_max: Latest year built (whole number >= 0).
            max_hoa: Maximum monthly HOA fee in dollars (>= 0).
            property_type: Restrict to one property type.
            has_pool: Only listings with a pool.
            max_days_on_market: Listed at most N days ago (whole number >= 0).
            min_days_on_market: Listed at least N days ago (whole number >= 0).

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.redfin.search(
            location=location,
            region_id=region_id,
            region_type=region_type,
            listing_status=listing_status,
            sold_within_days=sold_within_days,
            page=page,
            limit=limit,
            sort=sort,
            min_price=min_price,
            max_price=max_price,
            beds_min=beds_min,
            beds_max=beds_max,
            baths_min=baths_min,
            sqft_min=sqft_min,
            sqft_max=sqft_max,
            lot_size_min=lot_size_min,
            year_built_min=year_built_min,
            year_built_max=year_built_max,
            max_hoa=max_hoa,
            property_type=property_type,
            has_pool=has_pool,
            max_days_on_market=max_days_on_market,
            min_days_on_market=min_days_on_market,
        )
        raw = self._truncate_nested(raw, "data", "listings")
        return self._format_response(raw)

    async def _arun(
        self,
        location: str | None = None,
        region_id: int | None = None,
        region_type: Literal[1, 2, 5, 6] | None = None,
        listing_status: Literal["for_sale", "sold", "for_rent"] | None = None,
        sold_within_days: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        sort: _RedfinSearchSort | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        beds_min: int | None = None,
        beds_max: int | None = None,
        baths_min: int | None = None,
        sqft_min: int | None = None,
        sqft_max: int | None = None,
        lot_size_min: int | None = None,
        year_built_min: int | None = None,
        year_built_max: int | None = None,
        max_hoa: float | None = None,
        property_type: _RedfinSearchPropertyType | None = None,
        has_pool: bool | None = None,
        max_days_on_market: int | None = None,
        min_days_on_market: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/redfin/search asynchronously.

        Args:
            location: A redfin.com region URL (/city/, /neighborhood/, /county/,
                /zipcode/) or a bare 5-digit ZIP (1-500 characters).
            region_id: Redfin internal region id (>= 1), used together with region_type.
            region_type: Region kind that region_id belongs to: 1 neighborhood, 2 ZIP, 5
                county, 6 city.
            listing_status: Market to search. Defaults to 'for_sale'.
            sold_within_days: Sold within the last N days (>= 1).
            page: Results page, 1-based; page size is whatever limit is set to.
            limit: Listings per page, 1-350. Defaults to 100.
            sort: Result sort order. Defaults to 'recommended', Redfin's own ranking.
            min_price: Minimum price, inclusive (>= 0).
            max_price: Maximum price, inclusive (>= 0).
            beds_min: Minimum bedrooms (whole number >= 0); fractional values are
                rejected.
            beds_max: Maximum bedrooms (whole number >= 0); fractional values are
                rejected.
            baths_min: Minimum bathrooms (whole number >= 0).
            sqft_min: Minimum living area in square feet (whole number >= 0).
            sqft_max: Maximum living area in square feet (whole number >= 0).
            lot_size_min: Minimum lot size in square feet (whole number >= 0).
            year_built_min: Earliest year built (whole number >= 0).
            year_built_max: Latest year built (whole number >= 0).
            max_hoa: Maximum monthly HOA fee in dollars (>= 0).
            property_type: Restrict to one property type.
            has_pool: Only listings with a pool.
            max_days_on_market: Listed at most N days ago (whole number >= 0).
            min_days_on_market: Listed at least N days ago (whole number >= 0).

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.redfin.search(
            location=location,
            region_id=region_id,
            region_type=region_type,
            listing_status=listing_status,
            sold_within_days=sold_within_days,
            page=page,
            limit=limit,
            sort=sort,
            min_price=min_price,
            max_price=max_price,
            beds_min=beds_min,
            beds_max=beds_max,
            baths_min=baths_min,
            sqft_min=sqft_min,
            sqft_max=sqft_max,
            lot_size_min=lot_size_min,
            year_built_min=year_built_min,
            year_built_max=year_built_max,
            max_hoa=max_hoa,
            property_type=property_type,
            has_pool=has_pool,
            max_days_on_market=max_days_on_market,
            min_days_on_market=min_days_on_market,
        )
        raw = self._truncate_nested(raw, "data", "listings")
        return self._format_response(raw)


class ScavioRedfinPropertyTool(ScavioBaseTool):
    """One Redfin listing in full: price, Redfin Estimate and rental estimate, complete
    MLS fact sheet, price and tax history, listing agents, open houses, schools, climate
    risk, walkability, sun exposure, monthly weather, permits, zoning, comparable sales
    and photos.
    """

    name: str = "Scavio Redfin Property"
    description: str = (
        "One Redfin listing in full: price, Redfin Estimate and rental estimate, "
        "complete MLS fact sheet, price and tax history, listing agents, open houses, "
        "schools, climate risk, walkability, sun exposure, monthly weather, permits, "
        "zoning, comparable sales and photos. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _RedfinPropertyInput

    def _run(self, property_id: str, **kwargs: Any) -> str:
        """Call /api/v1/redfin/property synchronously.

        Args:
            property_id: Redfin property id, or any redfin.com listing URL carrying one
                (1-500 characters).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.redfin.property(property_id=property_id)
        return self._format_response(raw)

    async def _arun(self, property_id: str, **kwargs: Any) -> str:
        """Call /api/v1/redfin/property asynchronously.

        Args:
            property_id: Redfin property id, or any redfin.com listing URL carrying one
                (1-500 characters).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.redfin.property(property_id=property_id)
        return self._format_response(raw)


class ScavioRedfinMarketTool(ScavioBaseTool):
    """Redfin housing-market stats for a region: median list and sale price, price per
    sqft, sale-to-list ratio, average offers and days on market, YoY movement, 0-100
    compete score, live inventory by property type and by bedroom count, and Redfin
    agent presence.
    """

    name: str = "Scavio Redfin Market"
    description: str = (
        "Redfin housing-market stats for a region: median list and sale price, price "
        "per sqft, sale-to-list ratio, average offers and days on market, YoY "
        "movement, 0-100 compete score, live inventory by property type and by bedroom "
        "count, and Redfin agent presence. Provide location, or region_id together "
        "with region_type. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _RedfinMarketInput

    def _run(
        self,
        location: str | None = None,
        region_id: int | None = None,
        region_type: Literal[1, 2, 5, 6] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/redfin/market synchronously.

        Args:
            location: A redfin.com region URL (/city/, /neighborhood/, /county/,
                /zipcode/) or a bare 5-digit ZIP (1-500 characters).
            region_id: Redfin internal region id (>= 1), used together with region_type.
            region_type: Region kind that region_id belongs to: 1 neighborhood, 2 ZIP, 5
                county, 6 city.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.redfin.market(
            location=location,
            region_id=region_id,
            region_type=region_type,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        location: str | None = None,
        region_id: int | None = None,
        region_type: Literal[1, 2, 5, 6] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/redfin/market asynchronously.

        Args:
            location: A redfin.com region URL (/city/, /neighborhood/, /county/,
                /zipcode/) or a bare 5-digit ZIP (1-500 characters).
            region_id: Redfin internal region id (>= 1), used together with region_type.
            region_type: Region kind that region_id belongs to: 1 neighborhood, 2 ZIP, 5
                county, 6 city.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.redfin.market(
            location=location,
            region_id=region_id,
            region_type=region_type,
        )
        return self._format_response(raw)
