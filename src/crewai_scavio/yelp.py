"""Scavio Yelp tools for CrewAI.

2 credits flat on all three endpoints (YELP_CREDIT_COST =
scrapedoCreditCost(10), premium per-domain table).

- REVIEWS PAGE 1 IS REDUNDANT: it re-fetches the same document /business
  already returned, and costs another 2 credits. The playground defaults
  reviews to page 2 for this reason; docs MUST say it.
- popular_items has a stub-shell state (2 of 6 fetches returned 8 rows with
  every field null but `identifier`). Stub rows are dropped and
  popular_items_omitted flags it.
- location is effectively required -- Yelp geolocates a location-less search off
  the proxy exit, so the same request answers about a different metro run to
  run.
- Yelp fixes the page size at 10 for both search and reviews. A page past the
  last review is a 404, not an empty result.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_YelpReviewsSort = Literal[
    "relevance", "newest", "oldest", "rating_high", "rating_low", "elites"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _YelpSearchInput(BaseModel):
    """Input schema for ScavioYelpSearchTool."""

    term: str | None = Field(
        default=None,
        description=(
            "What to look for (1-200 characters): a category ('plumbers'), a dish, or "
            "a business name. Required together with location unless url is given."
        ),
    )
    location: str | None = Field(
        default=None,
        description=(
            "Where to look (1-200 characters): city and region, a full address, or a "
            "postcode. Effectively required - Yelp geolocates a location-less search "
            "off the proxy exit, so the same request answers about a different metro "
            "run to run."
        ),
    )
    page: int | None = Field(
        default=None,
        description="Results page, 1-based. Yelp fixes the page size at 10.",
    )
    sort: Literal["recommended", "rating", "review_count"] | None = Field(
        default=None,
        description=(
            "Result ordering (upstream default 'recommended'). Closed enum: Yelp "
            "IGNORES an unrecognised sortby and serves default ranking under a 200, "
            "billing a premium scrape for a sort that never ran."
        ),
    )
    price: list[Literal[1, 2, 3, 4]] | None = Field(
        default=None,
        description=(
            "Price bands to include, 1 ($) to 4 ($$$$); 1-4 values, combined freely - "
            "[1, 2] means $ or $$."
        ),
    )
    open_now: bool | None = Field(
        default=None,
        description="Only businesses open at the moment of the request.",
    )
    attributes: list[str] | None = Field(
        default=None,
        description=(
            "Raw Yelp filter aliases, max 20, each 1-100 characters "
            "('RestaurantsDelivery', 'GoodForKids', 'WheelchairAccessible'). A "
            "deliberate PASSTHROUGH, not an enum - Yelp's vocabulary runs to ~117 "
            "values per vertical and an alias it does not know is ignored upstream, "
            "returning unfiltered results."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "A full yelp.com/search URL (1-1000 characters) as an alternative to term "
            "+ location; the query, offset and sort are read out of it and the URL is "
            "rebuilt."
        ),
    )


class _YelpBusinessInput(BaseModel):
    """Input schema for ScavioYelpBusinessTool."""

    business_id: str | None = Field(
        default=None,
        description=(
            "A Yelp business alias ('desnudo-coffee-austin-2'), its opaque encid, or "
            "any yelp.com/biz URL carrying one (1-500 characters). Search rows return "
            "both id forms."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "A full yelp.com/biz URL (1-1000 characters) as an alternative to "
            "business_id."
        ),
    )


class _YelpReviewsInput(BaseModel):
    """Input schema for ScavioYelpReviewsTool."""

    business_id: str | None = Field(
        default=None,
        description=(
            "A Yelp business alias ('desnudo-coffee-austin-2'), its opaque encid, or "
            "any yelp.com/biz URL carrying one (1-500 characters)."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "A full yelp.com/biz URL (1-1000 characters) as an alternative to "
            "business_id."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Reviews page, 1-based, 10 per page. Page 1 duplicates the reviews "
            "business() already returned and costs another 2 credits - start at 2. A "
            "page past the last review is a 404, not an empty result."
        ),
    )
    sort: _YelpReviewsSort | None = Field(
        default=None,
        description=(
            "Review ordering (upstream default 'relevance'). Closed enum: Yelp IGNORES "
            "an unrecognised value and serves default ranking under a billed 200."
        ),
    )
    rating: Literal[1, 2, 3, 4, 5] | None = Field(
        default=None,
        description=(
            "Only reviews at this star rating, 1-5. Changes filtered_review_count on "
            "the response, not review_count."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioYelpSearchTool(ScavioBaseTool):
    """Businesses in Yelp's ranked order: rating, review count, price band, categories,
    address, contact rails, hours, photos and a review snippet; every row carries both
    business_id and alias.
    """

    name: str = "Scavio Yelp Search"
    description: str = (
        "Businesses in Yelp's ranked order: rating, review count, price band, "
        "categories, address, contact rails, hours, photos and a review snippet; every "
        "row carries both business_id and alias. Yelp fixes the page size at 10. "
        "Provide term and location, or url. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _YelpSearchInput

    def _run(
        self,
        term: str | None = None,
        location: str | None = None,
        page: int | None = None,
        sort: Literal["recommended", "rating", "review_count"] | None = None,
        price: list[Literal[1, 2, 3, 4]] | None = None,
        open_now: bool | None = None,
        attributes: list[str] | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/yelp/search synchronously.

        Args:
            term: What to look for (1-200 characters): a category ('plumbers'), a dish,
                or a business name.
            location: Where to look (1-200 characters): city and region, a full address,
                or a postcode.
            page: Results page, 1-based. Yelp fixes the page size at 10.
            sort: Result ordering (upstream default 'recommended').
            price: Price bands to include, 1 ($) to 4 ($$$$); 1-4 values, combined
                freely - [1, 2] means $ or $$.
            open_now: Only businesses open at the moment of the request.
            attributes: Raw Yelp filter aliases, max 20, each 1-100 characters
                ('RestaurantsDelivery', 'GoodForKids', 'WheelchairAccessible').
            url: A full yelp.com/search URL (1-1000 characters) as an alternative to
                term + location; the query, offset and sort are read out of it and the
                URL is rebuilt.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.yelp.search(
            term=term,
            location=location,
            page=page,
            sort=sort,
            price=price,
            open_now=open_now,
            attributes=attributes,
            url=url,
        )
        raw = self._truncate_nested(raw, "data", "businesses")
        return self._format_response(raw)

    async def _arun(
        self,
        term: str | None = None,
        location: str | None = None,
        page: int | None = None,
        sort: Literal["recommended", "rating", "review_count"] | None = None,
        price: list[Literal[1, 2, 3, 4]] | None = None,
        open_now: bool | None = None,
        attributes: list[str] | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/yelp/search asynchronously.

        Args:
            term: What to look for (1-200 characters): a category ('plumbers'), a dish,
                or a business name.
            location: Where to look (1-200 characters): city and region, a full address,
                or a postcode.
            page: Results page, 1-based. Yelp fixes the page size at 10.
            sort: Result ordering (upstream default 'recommended').
            price: Price bands to include, 1 ($) to 4 ($$$$); 1-4 values, combined
                freely - [1, 2] means $ or $$.
            open_now: Only businesses open at the moment of the request.
            attributes: Raw Yelp filter aliases, max 20, each 1-100 characters
                ('RestaurantsDelivery', 'GoodForKids', 'WheelchairAccessible').
            url: A full yelp.com/search URL (1-1000 characters) as an alternative to
                term + location; the query, offset and sort are read out of it and the
                URL is rebuilt.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.yelp.search(
            term=term,
            location=location,
            page=page,
            sort=sort,
            price=price,
            open_now=open_now,
            attributes=attributes,
            url=url,
        )
        raw = self._truncate_nested(raw, "data", "businesses")
        return self._format_response(raw)


class ScavioYelpBusinessTool(ScavioBaseTool):
    """One business in full: rating and per-star histogram, review count, price band,
    categories, address and coordinates, phone, website and menu links, hours and
    holidays, amenities, photos and videos, popular items, health inspections, Q&A,
    licences and claim status - plus the first page of reviews at no extra cost.
    """

    name: str = "Scavio Yelp Business"
    description: str = (
        "One business in full: rating and per-star histogram, review count, price "
        "band, categories, address and coordinates, phone, website and menu links, "
        "hours and holidays, amenities, photos and videos, popular items, health "
        "inspections, Q&A, licences and claim status - plus the first page of reviews "
        "at no extra cost. Provide business_id or url. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _YelpBusinessInput

    def _run(
        self,
        business_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/yelp/business synchronously.

        Args:
            business_id: A Yelp business alias ('desnudo-coffee-austin-2'), its opaque
                encid, or any yelp.com/biz URL carrying one (1-500 characters).
            url: A full yelp.com/biz URL (1-1000 characters) as an alternative to
                business_id.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.yelp.business(business_id=business_id, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        business_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/yelp/business asynchronously.

        Args:
            business_id: A Yelp business alias ('desnudo-coffee-austin-2'), its opaque
                encid, or any yelp.com/biz URL carrying one (1-500 characters).
            url: A full yelp.com/biz URL (1-1000 characters) as an alternative to
                business_id.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.yelp.business(business_id=business_id, url=url)
        return self._format_response(raw)


class ScavioYelpReviewsTool(ScavioBaseTool):
    """A page of reviews: rating, full text, language, author profile and expertise
    counts, attached photos, reaction counts and owner response.
    """

    name: str = "Scavio Yelp Reviews"
    description: str = (
        "A page of reviews: rating, full text, language, author profile and expertise "
        "counts, attached photos, reaction counts and owner response. 10 per page. "
        "PAGE 1 IS REDUNDANT - it re-fetches the document business() already returned "
        "- so start at page 2. Provide business_id or url. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _YelpReviewsInput

    def _run(
        self,
        business_id: str | None = None,
        url: str | None = None,
        page: int | None = None,
        sort: _YelpReviewsSort | None = None,
        rating: Literal[1, 2, 3, 4, 5] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/yelp/reviews synchronously.

        Args:
            business_id: A Yelp business alias ('desnudo-coffee-austin-2'), its opaque
                encid, or any yelp.com/biz URL carrying one (1-500 characters).
            url: A full yelp.com/biz URL (1-1000 characters) as an alternative to
                business_id.
            page: Reviews page, 1-based, 10 per page.
            sort: Review ordering (upstream default 'relevance').
            rating: Only reviews at this star rating, 1-5.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.yelp.reviews(
            business_id=business_id,
            url=url,
            page=page,
            sort=sort,
            rating=rating,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        business_id: str | None = None,
        url: str | None = None,
        page: int | None = None,
        sort: _YelpReviewsSort | None = None,
        rating: Literal[1, 2, 3, 4, 5] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/yelp/reviews asynchronously.

        Args:
            business_id: A Yelp business alias ('desnudo-coffee-austin-2'), its opaque
                encid, or any yelp.com/biz URL carrying one (1-500 characters).
            url: A full yelp.com/biz URL (1-1000 characters) as an alternative to
                business_id.
            page: Reviews page, 1-based, 10 per page.
            sort: Review ordering (upstream default 'relevance').
            rating: Only reviews at this star rating, 1-5.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.yelp.reviews(
            business_id=business_id,
            url=url,
            page=page,
            sort=sort,
            rating=rating,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
