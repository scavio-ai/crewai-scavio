"""Scavio Apple App Store tools for CrewAI.

1 credit flat on all three endpoints (APPSTORE_CREDIT_COST =
scrapedoCreditCost(1)) -- official iTunes JSON API.

- SEARCH HAS NO PAGINATION. `limit` (1..200) is the only lever; every offset
  spelling is silently ignored. Docs must say 'raise limit', never 'page'.
- /app accepts BOTH a numeric App Store id and a bundle id (auto-detected,
  identical payload). /reviews is NUMERIC ONLY -- the RSS feed has no bundle-id
  form.
- Reviews RSS types `entry` BY CARDINALITY: an array at 2+, a bare object at 1,
  absent at 0. Any consumer parsing this must handle all three.
- Reviews CANNOT 404 -- an unknown id and a real app with zero reviews return
  the same empty feed.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _AppStoreSearchInput(BaseModel):
    """Input schema for ScavioAppStoreSearchTool."""

    term: str = Field(
        ...,
        description=(
            "What to search for (1-500 characters). Apple matches an app name, a "
            "keyword OR a publisher name, so searching a developer returns their "
            "catalogue."
        ),
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Apps to return, 1-200 (default 25). The ONLY lever on result volume: the "
            "search API has no pagination and every offset spelling is silently "
            "ignored."
        ),
    )
    country: str | None = Field(
        default=None,
        description=(
            "Two-letter ISO storefront code (default 'us'); decides price, currency, "
            "localised title and whether the app is sold there at all. Anything that "
            "is not exactly two letters is rejected with a free 400."
        ),
    )
    entity: Literal["software", "ipad_software", "mac_software"] | None = Field(
        default=None,
        description=(
            "Which catalogue to search: iPhone/iPad apps ('software', the default), "
            "iPad apps, or Mac App Store apps. These are separate stores, not a filter "
            "- Mac rows carry no iPad/Apple TV screenshots, advisories, features, "
            "supported devices or Game Center flag, returning them empty rather than "
            "absent."
        ),
    )
    lang: str | None = Field(
        default=None,
        description=(
            "Listing text language as a five-letter code ('en_us', 'ja_jp'); any other "
            "shape is rejected. Independent of country: the storefront sets the price, "
            "this sets the words."
        ),
    )


class _AppStoreAppInput(BaseModel):
    """Input schema for ScavioAppStoreAppTool."""

    app_id: str = Field(
        ...,
        description=(
            "App Store id - the digits after 'id' in an apps.apple.com URL - or the "
            "app's bundle id ('notion.id', 'com.burbn.instagram'); both resolve to the "
            "identical payload. 1-255 characters matching "
            "^[A-Za-z0-9][A-Za-z0-9._-]*$, so a pasted apps.apple.com URL is rejected "
            "with a free 400. An id Apple cannot resolve is a billed 404."
        ),
    )
    country: str | None = Field(
        default=None,
        description=(
            "Two-letter ISO storefront code (default 'us'); decides price, currency, "
            "localised title and whether the app is sold there at all. Anything that "
            "is not exactly two letters is rejected with a free 400."
        ),
    )


class _AppStoreReviewsInput(BaseModel):
    """Input schema for ScavioAppStoreReviewsTool."""

    app_id: str = Field(
        ...,
        description=(
            "App Store id, NUMERIC ONLY - unlike app(), the reviews feed has no "
            "bundle-id form."
        ),
    )
    country: str | None = Field(
        default=None,
        description=(
            "Two-letter ISO storefront code (default 'us'). Anything that is not "
            "exactly two letters is rejected with a free 400. Ask a different country "
            "to reach past the 500-review ceiling."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Reviews page, 1-10, 50 reviews each (default 1). Apple hard-stops at page "
            "10."
        ),
    )
    sort: Literal["most_recent", "most_helpful"] | None = Field(
        default=None,
        description=(
            "Review ordering (default 'most_recent'). The choice decides whether the "
            "vote fields mean anything: under most_recent almost every review is too "
            "new to have been voted on and returns zeroes, while most_helpful returns "
            "them densely populated."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioAppStoreSearchTool(ScavioBaseTool):
    """Search the App Store and get up to 200 fully-shaped app rows - the same 43-field
    row as app() - so a search doubles as a bulk metadata fetch and as a publisher
    lookup.
    """

    name: str = "Scavio App Store Search"
    description: str = (
        "Search the App Store and get up to 200 fully-shaped app rows - the same "
        "43-field row as app() - so a search doubles as a bulk metadata fetch and as a "
        "publisher lookup. NO PAGINATION: raise limit, there is no second page. Costs "
        "1 credit."
    )
    args_schema: Type[BaseModel] = _AppStoreSearchInput

    def _run(
        self,
        term: str,
        limit: int | None = None,
        country: str | None = None,
        entity: Literal["software", "ipad_software", "mac_software"] | None = None,
        lang: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/appstore/search synchronously.

        Args:
            term: What to search for (1-500 characters).
            limit: Apps to return, 1-200 (default 25).
            country: Two-letter ISO storefront code (default 'us'); decides price,
                currency, localised title and whether the app is sold there at all.
            entity: Which catalogue to search: iPhone/iPad apps ('software', the
                default), iPad apps, or Mac App Store apps.
            lang: Listing text language as a five-letter code ('en_us', 'ja_jp'); any
                other shape is rejected.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.app_store.search(
            term=term,
            limit=limit,
            country=country,
            entity=entity,
            lang=lang,
        )
        raw = self._truncate_nested(raw, "data", "apps")
        return self._format_response(raw)

    async def _arun(
        self,
        term: str,
        limit: int | None = None,
        country: str | None = None,
        entity: Literal["software", "ipad_software", "mac_software"] | None = None,
        lang: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/appstore/search asynchronously.

        Args:
            term: What to search for (1-500 characters).
            limit: Apps to return, 1-200 (default 25).
            country: Two-letter ISO storefront code (default 'us'); decides price,
                currency, localised title and whether the app is sold there at all.
            entity: Which catalogue to search: iPhone/iPad apps ('software', the
                default), iPad apps, or Mac App Store apps.
            lang: Listing text language as a five-letter code ('en_us', 'ja_jp'); any
                other shape is rejected.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.app_store.search(
            term=term,
            limit=limit,
            country=country,
            entity=entity,
            lang=lang,
        )
        raw = self._truncate_nested(raw, "data", "apps")
        return self._format_response(raw)


class ScavioAppStoreAppTool(ScavioBaseTool):
    """Full App Store listing: title, description, developer and seller identity, price
    and currency, all-time and current-version ratings, version and release notes,
    genres, content rating and advisories, icons at three sizes, screenshots, download
    size, minimum OS, languages, supported devices and the Game Center and VPP flags.
    """

    name: str = "Scavio App Store App"
    description: str = (
        "Full App Store listing: title, description, developer and seller identity, "
        "price and currency, all-time and current-version ratings, version and release "
        "notes, genres, content rating and advisories, icons at three sizes, "
        "screenshots, download size, minimum OS, languages, supported devices and the "
        "Game Center and VPP flags. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _AppStoreAppInput

    def _run(self, app_id: str, country: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/appstore/app synchronously.

        Args:
            app_id: App Store id - the digits after 'id' in an apps.apple.com URL - or
                the app's bundle id ('notion.id', 'com.burbn.instagram'); both resolve
                to the identical payload.
            country: Two-letter ISO storefront code (default 'us'); decides price,
                currency, localised title and whether the app is sold there at all.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.app_store.app(app_id=app_id, country=country)
        return self._format_response(raw)

    async def _arun(
        self,
        app_id: str,
        country: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/appstore/app asynchronously.

        Args:
            app_id: App Store id - the digits after 'id' in an apps.apple.com URL - or
                the app's bundle id ('notion.id', 'com.burbn.instagram'); both resolve
                to the identical payload.
            country: Two-letter ISO storefront code (default 'us'); decides price,
                currency, localised title and whether the app is sold there at all.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.app_store.app(app_id=app_id, country=country)
        return self._format_response(raw)


class ScavioAppStoreReviewsTool(ScavioBaseTool):
    """A page of App Store reviews: star rating, title, full text, author and the APP
    VERSION the review was written against.
    """

    name: str = "Scavio App Store Reviews"
    description: str = (
        "A page of App Store reviews: star rating, title, full text, author and the "
        "APP VERSION the review was written against. 50 per page, hard-stopped at page "
        "10 - 500 reviews per storefront is Apple's anonymous ceiling. This endpoint "
        "cannot 404: an unknown id and a real app with no reviews return the same "
        "empty feed. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _AppStoreReviewsInput

    def _run(
        self,
        app_id: str,
        country: str | None = None,
        page: int | None = None,
        sort: Literal["most_recent", "most_helpful"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/appstore/reviews synchronously.

        Args:
            app_id: App Store id, NUMERIC ONLY - unlike app(), the reviews feed has no
                bundle-id form.
            country: Two-letter ISO storefront code (default 'us').
            page: Reviews page, 1-10, 50 reviews each (default 1).
            sort: Review ordering (default 'most_recent').

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.app_store.reviews(
            app_id=app_id,
            country=country,
            page=page,
            sort=sort,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        app_id: str,
        country: str | None = None,
        page: int | None = None,
        sort: Literal["most_recent", "most_helpful"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/appstore/reviews asynchronously.

        Args:
            app_id: App Store id, NUMERIC ONLY - unlike app(), the reviews feed has no
                bundle-id form.
            country: Two-letter ISO storefront code (default 'us').
            page: Reviews page, 1-10, 50 reviews each (default 1).
            sort: Review ordering (default 'most_recent').

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.app_store.reviews(
            app_id=app_id,
            country=country,
            page=page,
            sort=sort,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
