"""Scavio Target tools for CrewAI.

1 credit flat (TARGET_CREDIT_COST = scrapedoCreditCost(5) -- reached via the
headless browser, 5 upstream, still 1 customer credit; the 2-credit rule
triggers above 10).

- PRICE SETTLED 2026-08-09: stays at 1 credit. redsky refuses scrape.do's proxy
  pools and is now reached through the headless browser (5 upstream). The
  2-credit rule triggers above 10 upstream, so no reprice.
- LATENCY IS THE DOC RISK, not price: product ~4s, search ~9s, category ~37s,
  reviews ~40s; a 502-then-retry was observed at 105s. Do not overpromise
  speed.
- reviews returns 8 BODIES MAXIMUM regardless of review_count. `limit` only
  TRIMS -- do not advertise a page or offset param.
- seller_* is NULL for first-party stock, which is most of Target. Only Target
  Plus marketplace listings name a vendor (22/24 rows for 'office chair', 0/24
  for 'patio furniture'). Docs should say null means 'sold by Target'.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_TargetSearchSort = Literal[
    "relevance", "featured", "price_low", "price_high", "rating_high",
    "best_seller", "newest"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _TargetSearchInput(BaseModel):
    """Input schema for ScavioTargetSearchTool."""

    keyword: str = Field(
        ...,
        description="Search keyword (1-500 characters).",
    )
    page: int | None = Field(
        default=None,
        description="Results page, 1-based.",
    )
    count: int | None = Field(
        default=None,
        description=(
            "Results per page, 1-28. Defaults to 24; Target rejects anything above 28 "
            "outright."
        ),
    )
    sort: _TargetSearchSort | None = Field(
        default=None,
        description="Result sort order. Defaults to 'relevance'.",
    )
    store_id: str | None = Field(
        default=None,
        description=(
            "Numeric Target store id whose prices and availability the response "
            "reflects. Defaults to '3991', the store target.com uses with no store "
            "context."
        ),
    )


class _TargetCategoryInput(BaseModel):
    """Input schema for ScavioTargetCategoryTool."""

    category_id: str = Field(
        ...,
        description=(
            "Target category id: the segment after 'N-' in a target.com /c/ URL "
            "(target.com/c/apple/-/N-5xtg6 -> '5xtg6')."
        ),
    )
    page: int | None = Field(
        default=None,
        description="Results page, 1-based.",
    )
    count: int | None = Field(
        default=None,
        description=(
            "Results per page, 1-28. Defaults to 24; Target rejects anything above 28 "
            "outright."
        ),
    )
    sort: _TargetSearchSort | None = Field(
        default=None,
        description="Result sort order. Defaults to 'relevance'.",
    )
    store_id: str | None = Field(
        default=None,
        description=(
            "Numeric Target store id whose prices and availability the response "
            "reflects. Defaults to '3991'."
        ),
    )


class _TargetProductInput(BaseModel):
    """Input schema for ScavioTargetProductTool."""

    tcin: str = Field(
        ...,
        description=(
            "Target catalog id (tcin, e.g. '1010453160'). A colour/size child tcin is "
            "answered by its variation parent, with the child present in 'variants'."
        ),
    )
    store_id: str | None = Field(
        default=None,
        description=(
            "Numeric Target store id whose prices and availability the response "
            "reflects. Defaults to '3991'."
        ),
    )


class _TargetReviewsInput(BaseModel):
    """Input schema for ScavioTargetReviewsTool."""

    tcin: str = Field(
        ...,
        description="Target catalog id (tcin, e.g. '1010453160').",
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Trim the returned reviews to at most this many (1 or greater). Target "
            "publishes 8 anonymously and offers no paging, so this only trims."
        ),
    )
    store_id: str | None = Field(
        default=None,
        description=(
            "Numeric Target store id whose prices and availability the response "
            "reflects. Defaults to '3991'."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioTargetSearchTool(ScavioBaseTool):
    """Search Target.com, the US retailer: prices, ratings, badges and promotions."""

    name: str = "Scavio Target Search"
    description: str = (
        "Search Target.com, the US retailer: prices, ratings, badges and promotions. "
        "Up to 28 results per page; rendered upstream, so expect around 9 seconds. "
        "Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _TargetSearchInput

    def _run(
        self,
        keyword: str,
        page: int | None = None,
        count: int | None = None,
        sort: _TargetSearchSort | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/target/search synchronously.

        Args:
            keyword: Search keyword (1-500 characters).
            page: Results page, 1-based.
            count: Results per page, 1-28. Defaults to 24; Target rejects anything above
                28 outright.
            sort: Result sort order. Defaults to 'relevance'.
            store_id: Numeric Target store id whose prices and availability the response
                reflects.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.target.search(
            keyword=keyword,
            page=page,
            count=count,
            sort=sort,
            store_id=store_id,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        keyword: str,
        page: int | None = None,
        count: int | None = None,
        sort: _TargetSearchSort | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/target/search asynchronously.

        Args:
            keyword: Search keyword (1-500 characters).
            page: Results page, 1-based.
            count: Results per page, 1-28. Defaults to 24; Target rejects anything above
                28 outright.
            sort: Result sort order. Defaults to 'relevance'.
            store_id: Numeric Target store id whose prices and availability the response
                reflects.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.target.search(
            keyword=keyword,
            page=page,
            count=count,
            sort=sort,
            store_id=store_id,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioTargetCategoryTool(ScavioBaseTool):
    """Products in a Target category, same shape as search plus the category breadcrumb.
    """

    name: str = "Scavio Target Category"
    description: str = (
        "Products in a Target category, same shape as search plus the category "
        "breadcrumb. Up to 28 per page; the slowest Target endpoint at around 37 "
        "seconds. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _TargetCategoryInput

    def _run(
        self,
        category_id: str,
        page: int | None = None,
        count: int | None = None,
        sort: _TargetSearchSort | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/target/category synchronously.

        Args:
            category_id: Target category id: the segment after 'N-' in a target.com /c/
                URL (target.com/c/apple/-/N-5xtg6 -> '5xtg6').
            page: Results page, 1-based.
            count: Results per page, 1-28. Defaults to 24; Target rejects anything above
                28 outright.
            sort: Result sort order. Defaults to 'relevance'.
            store_id: Numeric Target store id whose prices and availability the response
                reflects.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.target.category(
            category_id=category_id,
            page=page,
            count=count,
            sort=sort,
            store_id=store_id,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        category_id: str,
        page: int | None = None,
        count: int | None = None,
        sort: _TargetSearchSort | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/target/category asynchronously.

        Args:
            category_id: Target category id: the segment after 'N-' in a target.com /c/
                URL (target.com/c/apple/-/N-5xtg6 -> '5xtg6').
            page: Results page, 1-based.
            count: Results per page, 1-28. Defaults to 24; Target rejects anything above
                28 outright.
            sort: Result sort order. Defaults to 'relevance'.
            store_id: Numeric Target store id whose prices and availability the response
                reflects.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.target.category(
            category_id=category_id,
            page=page,
            count=count,
            sort=sort,
            store_id=store_id,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioTargetProductTool(ScavioBaseTool):
    """Target product details by TCIN: price, rating, images, specifications, variants,
    return policy, fulfillment. seller_id/seller_name are null for stock sold by Target.
    """

    name: str = "Scavio Target Product"
    description: str = (
        "Target product details by TCIN: price, rating, images, specifications, "
        "variants, return policy, fulfillment. seller_id/seller_name are null for "
        "stock sold by Target. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _TargetProductInput

    def _run(self, tcin: str, store_id: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/target/product synchronously.

        Args:
            tcin: Target catalog id (tcin, e.g. '1010453160').
            store_id: Numeric Target store id whose prices and availability the response
                reflects.

        Returns:
            JSON-serialised product details.
        """
        raw = self.client.target.product(tcin=tcin, store_id=store_id)
        return self._format_response(raw)

    async def _arun(self, tcin: str, store_id: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/target/product asynchronously.

        Args:
            tcin: Target catalog id (tcin, e.g. '1010453160').
            store_id: Numeric Target store id whose prices and availability the response
                reflects.

        Returns:
            JSON-serialised product details.
        """
        raw = await self.async_client.target.product(tcin=tcin, store_id=store_id)
        return self._format_response(raw)


class ScavioTargetReviewsTool(ScavioBaseTool):
    """Target reviews with the rating breakdown, per-attribute averages and guest
    photos.
    """

    name: str = "Scavio Target Reviews"
    description: str = (
        "Target reviews with the rating breakdown, per-attribute averages and guest "
        "photos. 8 review bodies maximum and no paging; expect around 40 seconds. "
        "Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _TargetReviewsInput

    def _run(
        self,
        tcin: str,
        limit: int | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/target/reviews synchronously.

        Args:
            tcin: Target catalog id (tcin, e.g. '1010453160').
            limit: Trim the returned reviews to at most this many (1 or greater).
            store_id: Numeric Target store id whose prices and availability the response
                reflects.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.target.reviews(tcin=tcin, limit=limit, store_id=store_id)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        tcin: str,
        limit: int | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/target/reviews asynchronously.

        Args:
            tcin: Target catalog id (tcin, e.g. '1010453160').
            limit: Trim the returned reviews to at most this many (1 or greater).
            store_id: Numeric Target store id whose prices and availability the response
                reflects.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.target.reviews(
            tcin=tcin,
            limit=limit,
            store_id=store_id,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
