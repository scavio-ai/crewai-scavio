"""Scavio Home Depot tools for CrewAI.

2 credits flat on all three endpoints (HOMEDEPOT_CREDIT_COST =
scrapedoCreditCost(10), premium per-domain table).

- Search page size is FIXED at 12 (HOMEDEPOT_PAGE_SIZE) with no way to change
  it -- paging is the only way to read further.
- Reviews are 30 per page; total_pages is the last that exists and asking past
  it is a 404.
- sort_by is CLOSED because Home Depot does NOT fall back on an unknown sort --
  it answers 200 with an empty page that scrape.do still bills. 'Newest'
  (arrivaldate) is deliberately absent: it works on category pages and is
  rejected on keyword search.
- The product endpoint carries only a 10-review preview; /reviews is the
  paginated surface.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_HomeDepotSearchSortBy = Literal[
    "best_match", "top_sellers", "top_rated", "price_low", "price_high"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _HomeDepotSearchInput(BaseModel):
    """Input schema for ScavioHomeDepotSearchTool."""

    query: str = Field(
        ...,
        description="Search keyword (1-500 characters).",
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based. Home Depot serves 12 products per page and offers "
            "no way to change that, so paging is the only way to read further."
        ),
    )
    sort_by: _HomeDepotSearchSortBy | None = Field(
        default=None,
        description=(
            "Result sort order. Defaults to 'best_match'. Closed enum: Home Depot "
            "answers an unknown sort with an empty page that is still billed. 'Newest' "
            "is absent - it is rejected on keyword search."
        ),
    )
    min_price: float | None = Field(
        default=None,
        description="Minimum price, inclusive. Must be 0 or greater.",
    )
    max_price: float | None = Field(
        default=None,
        description="Maximum price, inclusive. Must be 0 or greater.",
    )


class _HomeDepotProductInput(BaseModel):
    """Input schema for ScavioHomeDepotProductTool."""

    item_id: str = Field(
        ...,
        description=(
            "Home Depot item id (e.g. '325479354'), or a full homedepot.com/p/... "
            "product URL; tracking parameters on a pasted URL are discarded."
        ),
    )


class _HomeDepotReviewsInput(BaseModel):
    """Input schema for ScavioHomeDepotReviewsTool."""

    item_id: str = Field(
        ...,
        description=(
            "Home Depot item id (e.g. '325479354'), or a full homedepot.com/p/... "
            "product URL; tracking parameters on a pasted URL are discarded."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Reviews page, 1-based. 30 reviews per page; 'total_pages' in the response "
            "is the last one that exists, and asking past it is a 404."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioHomeDepotSearchTool(ScavioBaseTool):
    """Search Home Depot: price and promotions, brand and model, ratings, badges,
    per-store pickup/delivery.
    """

    name: str = "Scavio Home Depot Search"
    description: str = (
        "Search Home Depot: price and promotions, brand and model, ratings, badges, "
        "per-store pickup/delivery. Page size is fixed at 12 and cannot be changed. "
        "Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _HomeDepotSearchInput

    def _run(
        self,
        query: str,
        page: int | None = None,
        sort_by: _HomeDepotSearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/homedepot/search synchronously.

        Args:
            query: Search keyword (1-500 characters).
            page: Results page, 1-based. Home Depot serves 12 products per page and
                offers no way to change that, so paging is the only way to read further.
            sort_by: Result sort order. Defaults to 'best_match'.
            min_price: Minimum price, inclusive. Must be 0 or greater.
            max_price: Maximum price, inclusive. Must be 0 or greater.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.home_depot.search(
            query=query,
            page=page,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        page: int | None = None,
        sort_by: _HomeDepotSearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/homedepot/search asynchronously.

        Args:
            query: Search keyword (1-500 characters).
            page: Results page, 1-based. Home Depot serves 12 products per page and
                offers no way to change that, so paging is the only way to read further.
            sort_by: Result sort order. Defaults to 'best_match'.
            min_price: Minimum price, inclusive. Must be 0 or greater.
            max_price: Maximum price, inclusive. Must be 0 or greater.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.home_depot.search(
            query=query,
            page=page,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioHomeDepotProductTool(ScavioBaseTool):
    """Full Home Depot item detail: pricing, images and videos, spec table, dimensions,
    bullets, documents, return policy.
    """

    name: str = "Scavio Home Depot Product"
    description: str = (
        "Full Home Depot item detail: pricing, images and videos, spec table, "
        "dimensions, bullets, documents, return policy. Carries a 10-review preview "
        "only. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _HomeDepotProductInput

    def _run(self, item_id: str, **kwargs: Any) -> str:
        """Call /api/v1/homedepot/product synchronously.

        Args:
            item_id: Home Depot item id (e.g. '325479354'), or a full
                homedepot.com/p/... product URL; tracking parameters on a pasted URL are
                discarded.

        Returns:
            JSON-serialised product details.
        """
        raw = self.client.home_depot.product(item_id=item_id)
        return self._format_response(raw)

    async def _arun(self, item_id: str, **kwargs: Any) -> str:
        """Call /api/v1/homedepot/product asynchronously.

        Args:
            item_id: Home Depot item id (e.g. '325479354'), or a full
                homedepot.com/p/... product URL; tracking parameters on a pasted URL are
                discarded.

        Returns:
            JSON-serialised product details.
        """
        raw = await self.async_client.home_depot.product(item_id=item_id)
        return self._format_response(raw)


class ScavioHomeDepotReviewsTool(ScavioBaseTool):
    """One page of full Home Depot review bodies, the rating distribution, per-attribute
    ratings, photos and seller responses.
    """

    name: str = "Scavio Home Depot Reviews"
    description: str = (
        "One page of full Home Depot review bodies, the rating distribution, "
        "per-attribute ratings, photos and seller responses. 30 reviews per page. "
        "Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _HomeDepotReviewsInput

    def _run(self, item_id: str, page: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/homedepot/reviews synchronously.

        Args:
            item_id: Home Depot item id (e.g. '325479354'), or a full
                homedepot.com/p/... product URL; tracking parameters on a pasted URL are
                discarded.
            page: Reviews page, 1-based. 30 reviews per page; 'total_pages' in the
                response is the last one that exists, and asking past it is a 404.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.home_depot.reviews(item_id=item_id, page=page)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(self, item_id: str, page: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/homedepot/reviews asynchronously.

        Args:
            item_id: Home Depot item id (e.g. '325479354'), or a full
                homedepot.com/p/... product URL; tracking parameters on a pasted URL are
                discarded.
            page: Reviews page, 1-based. 30 reviews per page; 'total_pages' in the
                response is the last one that exists, and asking past it is a 404.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.home_depot.reviews(item_id=item_id, page=page)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
