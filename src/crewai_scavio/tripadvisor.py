"""Scavio Tripadvisor tools for CrewAI.

2 credits flat on all four endpoints (TRIPADVISOR_CREDIT_COST =
scrapedoCreditCost(10), premium per-domain table).

- LOOKUP FIRST. /tripadvisor/locations was added after the first build shipped
  without one. Every other endpoint is keyed by ids that exist only inside
  TripAdvisor's own URLs, so a caller holding a place NAME has no other entry
  point. Docs must LEAD with it -- this was the first thing the owner hit in
  testing.
- A GEO row from /locations answers geo_id for /search; a business row answers
  the geo_id + location_id pair /location and /reviews take.
- Review page size differs by family -- 15 for restaurants, 10 for hotels and
  attractions -- so `category` should match the location's own type on any page
  past the first.
- Consecutive review pages can repeat one review at the boundary; de-duplicate
  on review_id when concatenating.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _TripadvisorLocationsInput(BaseModel):
    """Input schema for ScavioTripadvisorLocationsTool."""

    query: str = Field(
        ...,
        description="Place or business name to resolve (1-120 characters).",
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Rows to return, 1-20 (default 12). Sizes the response only; there is no "
            "paging here."
        ),
    )


class _TripadvisorSearchInput(BaseModel):
    """Input schema for ScavioTripadvisorSearchTool."""

    geo_id: str | None = Field(
        default=None,
        description=(
            "TripAdvisor geo id (1-500 characters): 30196, g30196, or a URL carrying "
            "one. Required unless url is given."
        ),
    )
    category: Literal["restaurants", "hotels", "attractions"] | None = Field(
        default=None,
        description="Listing family to search (default 'restaurants').",
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based. 30 locations per page; a page beyond the last is a "
            "404, not an empty result."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full tripadvisor.com listing URL (1-500 characters), as an alternative to "
            "geo_id; country sites are accepted."
        ),
    )


class _TripadvisorLocationInput(BaseModel):
    """Input schema for ScavioTripadvisorLocationTool."""

    location_id: str | None = Field(
        default=None,
        description=(
            "TripAdvisor location id (1-500 characters): 1899234, d1899234, or a full "
            "_Review URL. Required unless url is given."
        ),
    )
    geo_id: str | None = Field(
        default=None,
        description=(
            "Geo the location sits in; required when location_id is a bare d-id."
        ),
    )
    category: Literal["restaurants", "hotels", "attractions"] | None = Field(
        default=None,
        description=(
            "Location family (default 'restaurants'); match the location's own type."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full tripadvisor.com _Review URL (1-500 characters), as an alternative to "
            "location_id."
        ),
    )


class _TripadvisorReviewsInput(BaseModel):
    """Input schema for ScavioTripadvisorReviewsTool."""

    location_id: str | None = Field(
        default=None,
        description=(
            "TripAdvisor location id (1-500 characters): 1899234, d1899234, or a full "
            "_Review URL. Required unless url is given."
        ),
    )
    geo_id: str | None = Field(
        default=None,
        description=(
            "Geo the location sits in; required when location_id is a bare d-id."
        ),
    )
    category: Literal["restaurants", "hotels", "attractions"] | None = Field(
        default=None,
        description=(
            "Location family (default 'restaurants'). It sets the page size, so it "
            "must match the location's own type on any page past the first."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full tripadvisor.com _Review URL (1-500 characters), as an alternative to "
            "location_id."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Reviews page, 1-based. 15 per page for restaurants, 10 for hotels and "
            "attractions; past the last page is a 404."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioTripadvisorLocationsTool(ScavioBaseTool):
    """START HERE: resolve a place or business NAME to the TripAdvisor geo_id /
    location_id pair every other TripAdvisor endpoint is keyed by.
    """

    name: str = "Scavio Tripadvisor Locations"
    description: str = (
        "START HERE: resolve a place or business NAME to the TripAdvisor geo_id / "
        "location_id pair every other TripAdvisor endpoint is keyed by. Up to 20 rows. "
        "Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _TripadvisorLocationsInput

    def _run(self, query: str, limit: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/tripadvisor/locations synchronously.

        Args:
            query: Place or business name to resolve (1-120 characters).
            limit: Rows to return, 1-20 (default 12).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.tripadvisor.locations(query=query, limit=limit)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(self, query: str, limit: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/tripadvisor/locations asynchronously.

        Args:
            query: Place or business name to resolve (1-120 characters).
            limit: Rows to return, 1-20 (default 12).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.tripadvisor.locations(query=query, limit=limit)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


class ScavioTripadvisorSearchTool(ScavioBaseTool):
    """Restaurants, hotels or attractions in a TripAdvisor geo, TripAdvisor-ranked:
    rating, review count, price band, address, coordinates, phone, hours, Travelers'
    Choice badge; each row carries the location_id + geo_id pair.
    """

    name: str = "Scavio Tripadvisor Search"
    description: str = (
        "Restaurants, hotels or attractions in a TripAdvisor geo, TripAdvisor-ranked: "
        "rating, review count, price band, address, coordinates, phone, hours, "
        "Travelers' Choice badge; each row carries the location_id + geo_id pair. 30 "
        "locations per page. Provide geo_id or url. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _TripadvisorSearchInput

    def _run(
        self,
        geo_id: str | None = None,
        category: Literal["restaurants", "hotels", "attractions"] | None = None,
        page: int | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/tripadvisor/search synchronously.

        Args:
            geo_id: TripAdvisor geo id (1-500 characters): 30196, g30196, or a URL
                carrying one.
            category: Listing family to search (default 'restaurants').
            page: Results page, 1-based. 30 locations per page; a page beyond the last
                is a 404, not an empty result.
            url: Full tripadvisor.com listing URL (1-500 characters), as an alternative
                to geo_id; country sites are accepted.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.tripadvisor.search(
            geo_id=geo_id,
            category=category,
            page=page,
            url=url,
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(
        self,
        geo_id: str | None = None,
        category: Literal["restaurants", "hotels", "attractions"] | None = None,
        page: int | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/tripadvisor/search asynchronously.

        Args:
            geo_id: TripAdvisor geo id (1-500 characters): 30196, g30196, or a URL
                carrying one.
            category: Listing family to search (default 'restaurants').
            page: Results page, 1-based. 30 locations per page; a page beyond the last
                is a 404, not an empty result.
            url: Full tripadvisor.com listing URL (1-500 characters), as an alternative
                to geo_id; country sites are accepted.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.tripadvisor.search(
            geo_id=geo_id,
            category=category,
            page=page,
            url=url,
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


class ScavioTripadvisorLocationTool(ScavioBaseTool):
    """One TripAdvisor location in full: rating, review histogram and per-aspect
    sub-ratings, city ranking, price band, cuisines, amenities, address, coordinates,
    contact, photos, and the FIRST PAGE OF REVIEWS.
    """

    name: str = "Scavio Tripadvisor Location"
    description: str = (
        "One TripAdvisor location in full: rating, review histogram and per-aspect "
        "sub-ratings, city ranking, price band, cuisines, amenities, address, "
        "coordinates, contact, photos, and the FIRST PAGE OF REVIEWS. Provide "
        "location_id or url. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _TripadvisorLocationInput

    def _run(
        self,
        location_id: str | None = None,
        geo_id: str | None = None,
        category: Literal["restaurants", "hotels", "attractions"] | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/tripadvisor/location synchronously.

        Args:
            location_id: TripAdvisor location id (1-500 characters): 1899234, d1899234,
                or a full _Review URL.
            geo_id: Geo the location sits in; required when location_id is a bare d-id.
            category: Location family (default 'restaurants'); match the location's own
                type.
            url: Full tripadvisor.com _Review URL (1-500 characters), as an alternative
                to location_id.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.tripadvisor.location(
            location_id=location_id,
            geo_id=geo_id,
            category=category,
            url=url,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        location_id: str | None = None,
        geo_id: str | None = None,
        category: Literal["restaurants", "hotels", "attractions"] | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/tripadvisor/location asynchronously.

        Args:
            location_id: TripAdvisor location id (1-500 characters): 1899234, d1899234,
                or a full _Review URL.
            geo_id: Geo the location sits in; required when location_id is a bare d-id.
            category: Location family (default 'restaurants'); match the location's own
                type.
            url: Full tripadvisor.com _Review URL (1-500 characters), as an alternative
                to location_id.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.tripadvisor.location(
            location_id=location_id,
            geo_id=geo_id,
            category=category,
            url=url,
        )
        return self._format_response(raw)


class ScavioTripadvisorReviewsTool(ScavioBaseTool):
    """A page of TripAdvisor reviews: rating, trip date and type, reviewer home town and
    contribution count, management response.
    """

    name: str = "Scavio Tripadvisor Reviews"
    description: str = (
        "A page of TripAdvisor reviews: rating, trip date and type, reviewer home town "
        "and contribution count, management response. Page 1 already rides along in "
        "location(), so use this to page PAST it; consecutive pages can repeat one "
        "review at the boundary, so de-duplicate on review_id. Provide location_id or "
        "url. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _TripadvisorReviewsInput

    def _run(
        self,
        location_id: str | None = None,
        geo_id: str | None = None,
        category: Literal["restaurants", "hotels", "attractions"] | None = None,
        url: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/tripadvisor/reviews synchronously.

        Args:
            location_id: TripAdvisor location id (1-500 characters): 1899234, d1899234,
                or a full _Review URL.
            geo_id: Geo the location sits in; required when location_id is a bare d-id.
            category: Location family (default 'restaurants').
            url: Full tripadvisor.com _Review URL (1-500 characters), as an alternative
                to location_id.
            page: Reviews page, 1-based. 15 per page for restaurants, 10 for hotels and
                attractions; past the last page is a 404.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.tripadvisor.reviews(
            location_id=location_id,
            geo_id=geo_id,
            category=category,
            url=url,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        location_id: str | None = None,
        geo_id: str | None = None,
        category: Literal["restaurants", "hotels", "attractions"] | None = None,
        url: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/tripadvisor/reviews asynchronously.

        Args:
            location_id: TripAdvisor location id (1-500 characters): 1899234, d1899234,
                or a full _Review URL.
            geo_id: Geo the location sits in; required when location_id is a bare d-id.
            category: Location family (default 'restaurants').
            url: Full tripadvisor.com _Review URL (1-500 characters), as an alternative
                to location_id.
            page: Reviews page, 1-based. 15 per page for restaurants, 10 for hotels and
                attractions; past the last page is a 404.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.tripadvisor.reviews(
            location_id=location_id,
            geo_id=geo_id,
            category=category,
            url=url,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
