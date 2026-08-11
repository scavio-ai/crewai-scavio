"""Scavio Zillow tools for CrewAI.

1 credit flat on all three endpoints (ZILLOW_CREDIT_COST =
scrapedoCreditCost(1), plain datacenter pool).

- A bare ZIP works alone but CANNOT be combined with a filter or a sort --
  Zillow resolves it by geolocation on that request shape and answers about
  another city. Use the city name there.
- On listing_status=for_rent, min_price/max_price mean MONTHLY RENT -- Zillow
  files rent under its payment filter, not price.
- days_on_zillow is a closed enum; an unrecognised `doz` returns the UNFILTERED
  set under a 200.
- Sorts that rank against a signed-in profile (saved/featured/personalised) are
  deliberately absent -- we are never signed in.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_ZillowSearchSort = Literal[
    "relevance", "recommended", "newest", "price_low", "price_high",
    "payment_low", "payment_high", "beds", "baths", "sqft", "lot_size",
    "zestimate_low", "zestimate_high", "recent_change"
]
_ZillowSearchHomeType = Literal[
    "houses", "townhomes", "multi_family", "condos", "apartments",
    "manufactured", "lots_land"
]
_ZillowSearchDaysOnZillow = Literal[
    "1", "7", "14", "30", "90", "6m", "12m", "24m", "36m"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _ZillowSearchInput(BaseModel):
    """Input schema for ScavioZillowSearchTool."""

    location: str = Field(
        ...,
        description=(
            "Region to search (1-200 characters): a Zillow slug ('austin-tx'), a human "
            "form ('Austin, TX'), a ZIP, or a pasted zillow.com search URL. A ZIP "
            "works alone but cannot be combined with a filter or sort; an unresolvable "
            "region is a 404."
        ),
    )
    listing_status: Literal["for_sale", "for_rent", "sold"] | None = Field(
        default=None,
        description="Which listings to return. Defaults to 'for_sale'.",
    )
    page: int | None = Field(
        default=None,
        description="Results page, 1-based.",
    )
    sort: _ZillowSearchSort | None = Field(
        default=None,
        description=(
            "Result sort order. Sorts that rank against a signed-in profile "
            "(saved/featured/personalised) are unsupported - we are never signed in."
        ),
    )
    min_price: float | None = Field(
        default=None,
        description=(
            "Minimum price, inclusive (0 or greater). On listing_status='for_rent' "
            "this is MONTHLY RENT - Zillow files rent under its payment filter."
        ),
    )
    max_price: float | None = Field(
        default=None,
        description=(
            "Maximum price, inclusive (0 or greater). On listing_status='for_rent' "
            "this is MONTHLY RENT."
        ),
    )
    beds_min: int | None = Field(
        default=None,
        description="Minimum bedrooms; whole number, 0 or greater.",
    )
    beds_max: int | None = Field(
        default=None,
        description="Maximum bedrooms; whole number, 0 or greater.",
    )
    baths_min: float | None = Field(
        default=None,
        description="Minimum bathrooms, 0 or greater. Half-baths are allowed (1.5).",
    )
    baths_max: float | None = Field(
        default=None,
        description="Maximum bathrooms, 0 or greater. Half-baths are allowed (1.5).",
    )
    sqft_min: int | None = Field(
        default=None,
        description="Minimum living area in square feet; whole number, 0 or greater.",
    )
    sqft_max: int | None = Field(
        default=None,
        description="Maximum living area in square feet; whole number, 0 or greater.",
    )
    lot_size_min: int | None = Field(
        default=None,
        description="Minimum lot size in square feet; whole number, 0 or greater.",
    )
    lot_size_max: int | None = Field(
        default=None,
        description="Maximum lot size in square feet; whole number, 0 or greater.",
    )
    year_built_min: int | None = Field(
        default=None,
        description="Earliest year built; whole number, 0 or greater.",
    )
    year_built_max: int | None = Field(
        default=None,
        description="Latest year built; whole number, 0 or greater.",
    )
    max_hoa: float | None = Field(
        default=None,
        description="Maximum monthly HOA fee in dollars, 0 or greater.",
    )
    home_type: _ZillowSearchHomeType | None = Field(
        default=None,
        description="Property type filter.",
    )
    days_on_zillow: _ZillowSearchDaysOnZillow | None = Field(
        default=None,
        description=(
            "Listed - or, with listing_status='sold', sold - within the last N days. "
            "Closed enum: an unrecognised value returns the UNFILTERED set under a "
            "200."
        ),
    )
    keywords: str | None = Field(
        default=None,
        description=(
            "Free-text match against the listing description (1-200 characters)."
        ),
    )
    has_pool: bool | None = Field(
        default=None,
        description="Only listings with a pool.",
    )
    has_garage: bool | None = Field(
        default=None,
        description="Only listings with a garage.",
    )
    has_air_conditioning: bool | None = Field(
        default=None,
        description="Only listings with air conditioning.",
    )
    is_waterfront: bool | None = Field(
        default=None,
        description="Only waterfront listings.",
    )
    has_basement: bool | None = Field(
        default=None,
        description="Only listings with a basement.",
    )
    is_new_construction: bool | None = Field(
        default=None,
        description="Only new-construction listings.",
    )
    has_open_house: bool | None = Field(
        default=None,
        description="Only listings with an upcoming open house.",
    )
    price_reduced: bool | None = Field(
        default=None,
        description="Only listings whose price was reduced.",
    )
    is_3d_tour: bool | None = Field(
        default=None,
        description="Only listings with a 3D tour.",
    )


class _ZillowPropertyInput(BaseModel):
    """Input schema for ScavioZillowPropertyTool."""

    zpid: str = Field(
        ...,
        description=(
            "Zillow property id (e.g. '29414894'), a full /homedetails/ URL, or a "
            "rental building URL (zillow.com/apartments/...). The building form is "
            "required for buildings: they have no zpid a caller can see."
        ),
    )


class _ZillowAgentReviewsInput(BaseModel):
    """Input schema for ScavioZillowAgentReviewsTool."""

    screen_name: str = Field(
        ...,
        description=(
            "Zillow agent profile screen name as it appears in "
            "zillow.com/profile/<name>/ (1-200 characters, may contain spaces), or a "
            "full profile URL."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioZillowSearchTool(ScavioBaseTool):
    """Zillow listings in a region: price, beds, baths, living area, Zestimate,
    coordinates, images, days on market.
    """

    name: str = "Scavio Zillow Search"
    description: str = (
        "Zillow listings in a region: price, beds, baths, living area, Zestimate, "
        "coordinates, images, days on market. A bare ZIP works alone but cannot be "
        "combined with a filter or a sort. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _ZillowSearchInput

    def _run(
        self,
        location: str,
        listing_status: Literal["for_sale", "for_rent", "sold"] | None = None,
        page: int | None = None,
        sort: _ZillowSearchSort | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        beds_min: int | None = None,
        beds_max: int | None = None,
        baths_min: float | None = None,
        baths_max: float | None = None,
        sqft_min: int | None = None,
        sqft_max: int | None = None,
        lot_size_min: int | None = None,
        lot_size_max: int | None = None,
        year_built_min: int | None = None,
        year_built_max: int | None = None,
        max_hoa: float | None = None,
        home_type: _ZillowSearchHomeType | None = None,
        days_on_zillow: _ZillowSearchDaysOnZillow | None = None,
        keywords: str | None = None,
        has_pool: bool | None = None,
        has_garage: bool | None = None,
        has_air_conditioning: bool | None = None,
        is_waterfront: bool | None = None,
        has_basement: bool | None = None,
        is_new_construction: bool | None = None,
        has_open_house: bool | None = None,
        price_reduced: bool | None = None,
        is_3d_tour: bool | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/zillow/search synchronously.

        Args:
            location: Region to search (1-200 characters): a Zillow slug ('austin-tx'),
                a human form ('Austin, TX'), a ZIP, or a pasted zillow.com search URL.
            listing_status: Which listings to return. Defaults to 'for_sale'.
            page: Results page, 1-based.
            sort: Result sort order. Sorts that rank against a signed-in profile
                (saved/featured/personalised) are unsupported - we are never signed in.
            min_price: Minimum price, inclusive (0 or greater).
            max_price: Maximum price, inclusive (0 or greater).
            beds_min: Minimum bedrooms; whole number, 0 or greater.
            beds_max: Maximum bedrooms; whole number, 0 or greater.
            baths_min: Minimum bathrooms, 0 or greater.
            baths_max: Maximum bathrooms, 0 or greater.
            sqft_min: Minimum living area in square feet; whole number, 0 or greater.
            sqft_max: Maximum living area in square feet; whole number, 0 or greater.
            lot_size_min: Minimum lot size in square feet; whole number, 0 or greater.
            lot_size_max: Maximum lot size in square feet; whole number, 0 or greater.
            year_built_min: Earliest year built; whole number, 0 or greater.
            year_built_max: Latest year built; whole number, 0 or greater.
            max_hoa: Maximum monthly HOA fee in dollars, 0 or greater.
            home_type: Property type filter.
            days_on_zillow: Listed - or, with listing_status='sold', sold - within the
                last N days.
            keywords: Free-text match against the listing description (1-200
                characters).
            has_pool: Only listings with a pool.
            has_garage: Only listings with a garage.
            has_air_conditioning: Only listings with air conditioning.
            is_waterfront: Only waterfront listings.
            has_basement: Only listings with a basement.
            is_new_construction: Only new-construction listings.
            has_open_house: Only listings with an upcoming open house.
            price_reduced: Only listings whose price was reduced.
            is_3d_tour: Only listings with a 3D tour.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.zillow.search(
            location=location,
            listing_status=listing_status,
            page=page,
            sort=sort,
            min_price=min_price,
            max_price=max_price,
            beds_min=beds_min,
            beds_max=beds_max,
            baths_min=baths_min,
            baths_max=baths_max,
            sqft_min=sqft_min,
            sqft_max=sqft_max,
            lot_size_min=lot_size_min,
            lot_size_max=lot_size_max,
            year_built_min=year_built_min,
            year_built_max=year_built_max,
            max_hoa=max_hoa,
            home_type=home_type,
            days_on_zillow=days_on_zillow,
            keywords=keywords,
            has_pool=has_pool,
            has_garage=has_garage,
            has_air_conditioning=has_air_conditioning,
            is_waterfront=is_waterfront,
            has_basement=has_basement,
            is_new_construction=is_new_construction,
            has_open_house=has_open_house,
            price_reduced=price_reduced,
            is_3d_tour=is_3d_tour,
        )
        raw = self._truncate_nested(raw, "data", "properties")
        return self._format_response(raw)

    async def _arun(
        self,
        location: str,
        listing_status: Literal["for_sale", "for_rent", "sold"] | None = None,
        page: int | None = None,
        sort: _ZillowSearchSort | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        beds_min: int | None = None,
        beds_max: int | None = None,
        baths_min: float | None = None,
        baths_max: float | None = None,
        sqft_min: int | None = None,
        sqft_max: int | None = None,
        lot_size_min: int | None = None,
        lot_size_max: int | None = None,
        year_built_min: int | None = None,
        year_built_max: int | None = None,
        max_hoa: float | None = None,
        home_type: _ZillowSearchHomeType | None = None,
        days_on_zillow: _ZillowSearchDaysOnZillow | None = None,
        keywords: str | None = None,
        has_pool: bool | None = None,
        has_garage: bool | None = None,
        has_air_conditioning: bool | None = None,
        is_waterfront: bool | None = None,
        has_basement: bool | None = None,
        is_new_construction: bool | None = None,
        has_open_house: bool | None = None,
        price_reduced: bool | None = None,
        is_3d_tour: bool | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/zillow/search asynchronously.

        Args:
            location: Region to search (1-200 characters): a Zillow slug ('austin-tx'),
                a human form ('Austin, TX'), a ZIP, or a pasted zillow.com search URL.
            listing_status: Which listings to return. Defaults to 'for_sale'.
            page: Results page, 1-based.
            sort: Result sort order. Sorts that rank against a signed-in profile
                (saved/featured/personalised) are unsupported - we are never signed in.
            min_price: Minimum price, inclusive (0 or greater).
            max_price: Maximum price, inclusive (0 or greater).
            beds_min: Minimum bedrooms; whole number, 0 or greater.
            beds_max: Maximum bedrooms; whole number, 0 or greater.
            baths_min: Minimum bathrooms, 0 or greater.
            baths_max: Maximum bathrooms, 0 or greater.
            sqft_min: Minimum living area in square feet; whole number, 0 or greater.
            sqft_max: Maximum living area in square feet; whole number, 0 or greater.
            lot_size_min: Minimum lot size in square feet; whole number, 0 or greater.
            lot_size_max: Maximum lot size in square feet; whole number, 0 or greater.
            year_built_min: Earliest year built; whole number, 0 or greater.
            year_built_max: Latest year built; whole number, 0 or greater.
            max_hoa: Maximum monthly HOA fee in dollars, 0 or greater.
            home_type: Property type filter.
            days_on_zillow: Listed - or, with listing_status='sold', sold - within the
                last N days.
            keywords: Free-text match against the listing description (1-200
                characters).
            has_pool: Only listings with a pool.
            has_garage: Only listings with a garage.
            has_air_conditioning: Only listings with air conditioning.
            is_waterfront: Only waterfront listings.
            has_basement: Only listings with a basement.
            is_new_construction: Only new-construction listings.
            has_open_house: Only listings with an upcoming open house.
            price_reduced: Only listings whose price was reduced.
            is_3d_tour: Only listings with a 3D tour.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.zillow.search(
            location=location,
            listing_status=listing_status,
            page=page,
            sort=sort,
            min_price=min_price,
            max_price=max_price,
            beds_min=beds_min,
            beds_max=beds_max,
            baths_min=baths_min,
            baths_max=baths_max,
            sqft_min=sqft_min,
            sqft_max=sqft_max,
            lot_size_min=lot_size_min,
            lot_size_max=lot_size_max,
            year_built_min=year_built_min,
            year_built_max=year_built_max,
            max_hoa=max_hoa,
            home_type=home_type,
            days_on_zillow=days_on_zillow,
            keywords=keywords,
            has_pool=has_pool,
            has_garage=has_garage,
            has_air_conditioning=has_air_conditioning,
            is_waterfront=is_waterfront,
            has_basement=has_basement,
            is_new_construction=is_new_construction,
            has_open_house=has_open_house,
            price_reduced=price_reduced,
            is_3d_tour=is_3d_tour,
        )
        raw = self._truncate_nested(raw, "data", "properties")
        return self._format_response(raw)


class ScavioZillowPropertyTool(ScavioBaseTool):
    """Full Zillow listing: price and price history, Zestimate, tax history, RESO facts,
    rooms, schools, open houses, photos.
    """

    name: str = "Scavio Zillow Property"
    description: str = (
        "Full Zillow listing: price and price history, Zestimate, tax history, RESO "
        "facts, rooms, schools, open houses, photos. Rental buildings return floor "
        "plans instead. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _ZillowPropertyInput

    def _run(self, zpid: str, **kwargs: Any) -> str:
        """Call /api/v1/zillow/property synchronously.

        Args:
            zpid: Zillow property id (e.g. '29414894'), a full /homedetails/ URL, or a
                rental building URL (zillow.com/apartments/...).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.zillow.property(zpid=zpid)
        return self._format_response(raw)

    async def _arun(self, zpid: str, **kwargs: Any) -> str:
        """Call /api/v1/zillow/property asynchronously.

        Args:
            zpid: Zillow property id (e.g. '29414894'), a full /homedetails/ URL, or a
                rental building URL (zillow.com/apartments/...).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.zillow.property(zpid=zpid)
        return self._format_response(raw)


class ScavioZillowAgentReviewsTool(ScavioBaseTool):
    """A Zillow AGENT's profile and reviews: rating, bodies with sub-ratings,
    specialties, licenses, service areas, sales counts.
    """

    name: str = "Scavio Zillow Agent Reviews"
    description: str = (
        "A Zillow AGENT's profile and reviews: rating, bodies with sub-ratings, "
        "specialties, licenses, service areas, sales counts. Zillow server-renders the "
        "first five. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _ZillowAgentReviewsInput

    def _run(self, screen_name: str, **kwargs: Any) -> str:
        """Call /api/v1/zillow/reviews synchronously.

        Args:
            screen_name: Zillow agent profile screen name as it appears in
                zillow.com/profile/<name>/ (1-200 characters, may contain spaces), or a
                full profile URL.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.zillow.agent_reviews(screen_name=screen_name)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(self, screen_name: str, **kwargs: Any) -> str:
        """Call /api/v1/zillow/reviews asynchronously.

        Args:
            screen_name: Zillow agent profile screen name as it appears in
                zillow.com/profile/<name>/ (1-200 characters, may contain spaces), or a
                full profile URL.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.zillow.agent_reviews(screen_name=screen_name)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
