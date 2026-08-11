"""Scavio Google Play tools for CrewAI.

2 credits flat on all three endpoints (GOOGLEPLAY_CREDIT_COST =
scrapedoCreditCost(10), premium per-domain table, bills 10 upstream). NOT the
1-credit Google-exempt price -- this is a SEPARATE namespace from `google`
partly because of that.

- NO PAGINATION ON SEARCH -- one shelf of ~30 apps. Data is in
  AF_initDataCallback arrays parsed POSITIONALLY: brittle, pinned by fixtures.
- `hl` changes the storefront, not only the strings: at hl=pt-BR the title,
  description, install formatting and content rating all move with it. Play
  silently falls back to English/US on values it does not serve.
- The reviews `cursor` is opaque and SINGLE-USE and encodes the sort as well as
  the position -- send it back with the SAME `sort` it came from. A cursor past
  the last review is a 404, not an empty page.
- count is capped at 200 on our side (MAX_REVIEW_COUNT); Play honours more but
  a single page that large is megabytes for one credit.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _GooglePlaySearchInput(BaseModel):
    """Input schema for ScavioGooglePlaySearchTool."""

    query: str = Field(
        ...,
        description=(
            "What to search the store for (1-200 characters): an app name, a "
            "publisher, or a category phrase. Apps only - games are folded into the "
            "apps vertical, but books and films use a different card shape and are not "
            "covered."
        ),
    )
    hl: str | None = Field(
        default=None,
        description=(
            "UI language, 2-20 characters (default 'en'). Changes the STOREFRONT, not "
            "only the strings: at hl=pt-BR the title, description, install formatting "
            "and content rating all move with it. Play silently falls back to English "
            "on a value it does not serve."
        ),
    )
    gl: str | None = Field(
        default=None,
        description=(
            "Country code, 2-10 characters (default 'us'), deciding which storefront's "
            "price and availability are returned. Play silently falls back to the US "
            "storefront on a country it does not serve."
        ),
    )


class _GooglePlayAppInput(BaseModel):
    """Input schema for ScavioGooglePlayAppTool."""

    app_id: str = Field(
        ...,
        description=(
            "Android package name ('com.spotify.music') or any play.google.com URL "
            "carrying one in its id param (1-500 characters)."
        ),
    )
    hl: str | None = Field(
        default=None,
        description=(
            "UI language, 2-20 characters (default 'en'). Changes the STOREFRONT, not "
            "only the strings: title, description, install formatting and content "
            "rating all move with it. Play silently falls back to English on a value "
            "it does not serve."
        ),
    )
    gl: str | None = Field(
        default=None,
        description=(
            "Country code, 2-10 characters (default 'us'), deciding which storefront's "
            "price and availability are returned. Play silently falls back to the US "
            "storefront on a country it does not serve."
        ),
    )


class _GooglePlayReviewsInput(BaseModel):
    """Input schema for ScavioGooglePlayReviewsTool."""

    app_id: str = Field(
        ...,
        description=(
            "Android package name ('com.spotify.music') or any play.google.com URL "
            "carrying one in its id param (1-500 characters)."
        ),
    )
    sort: Literal["relevance", "newest", "rating"] | None = Field(
        default=None,
        description=(
            "Review ordering (default 'newest'). Closed enum. The cursor encodes the "
            "sort, so keep this identical when paging."
        ),
    )
    count: int | None = Field(
        default=None,
        description=(
            "Reviews to return, 1-200 (default 50); 200 is our cap, not Play's. Play "
            "honours more, but a single page that large is megabytes for one credit - "
            "page with cursor instead."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Continuation token from a prior response's next_cursor (1-4000 "
            "characters). Opaque and SINGLE-USE, and it encodes the sort as well as "
            "the position - send it back with the SAME sort it came from. A cursor "
            "past the last review is a 404, not an empty page."
        ),
    )
    hl: str | None = Field(
        default=None,
        description=(
            "UI language, 2-20 characters (default 'en'). Changes the STOREFRONT, not "
            "only the strings. Play silently falls back to English on a value it does "
            "not serve."
        ),
    )
    gl: str | None = Field(
        default=None,
        description=(
            "Country code, 2-10 characters (default 'us'), deciding which storefront's "
            "price and availability are returned. Play silently falls back to the US "
            "storefront on a country it does not serve."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioGooglePlaySearchTool(ScavioBaseTool):
    """Ranked Google Play apps: package name, title, developer, rating, install count,
    price and IAP range, content rating, icon and screenshots.
    """

    name: str = "Scavio Google Play Search"
    description: str = (
        "Ranked Google Play apps: package name, title, developer, rating, install "
        "count, price and IAP range, content rating, icon and screenshots. A branded "
        "query returns the hero card as result 1 in the same row shape, plus Play's "
        "related-query rail. NO PAGINATION - one shelf of about 30 apps. Costs 2 "
        "credits."
    )
    args_schema: Type[BaseModel] = _GooglePlaySearchInput

    def _run(
        self,
        query: str,
        hl: str | None = None,
        gl: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleplay/search synchronously.

        Args:
            query: What to search the store for (1-200 characters): an app name, a
                publisher, or a category phrase.
            hl: UI language, 2-20 characters (default 'en').
            gl: Country code, 2-10 characters (default 'us'), deciding which
                storefront's price and availability are returned.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.google_play.search(query=query, hl=hl, gl=gl)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        hl: str | None = None,
        gl: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleplay/search asynchronously.

        Args:
            query: What to search the store for (1-200 characters): an app name, a
                publisher, or a category phrase.
            hl: UI language, 2-20 characters (default 'en').
            gl: Country code, 2-10 characters (default 'us'), deciding which
                storefront's price and availability are returned.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.google_play.search(query=query, hl=hl, gl=gl)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


class ScavioGooglePlayAppTool(ScavioBaseTool):
    """Full Google Play store listing: installs including the REAL count Play publishes
    but never renders, rating and star histogram, description, developer identity and
    legal contact, price and IAPs, categories and gameplay tags, screenshots and
    trailer, version and Android requirement, release and update dates, changelog, the
    full permission tree, the Data safety table, the 20 server-rendered reviews and the
    similar-apps and more-by-developer rails.
    """

    name: str = "Scavio Google Play App"
    description: str = (
        "Full Google Play store listing: installs including the REAL count Play "
        "publishes but never renders, rating and star histogram, description, "
        "developer identity and legal contact, price and IAPs, categories and gameplay "
        "tags, screenshots and trailer, version and Android requirement, release and "
        "update dates, changelog, the full permission tree, the Data safety table, the "
        "20 server-rendered reviews and the similar-apps and more-by-developer rails. "
        "Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _GooglePlayAppInput

    def _run(
        self,
        app_id: str,
        hl: str | None = None,
        gl: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleplay/app synchronously.

        Args:
            app_id: Android package name ('com.spotify.music') or any play.google.com
                URL carrying one in its id param (1-500 characters).
            hl: UI language, 2-20 characters (default 'en').
            gl: Country code, 2-10 characters (default 'us'), deciding which
                storefront's price and availability are returned.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.google_play.app(app_id=app_id, hl=hl, gl=gl)
        return self._format_response(raw)

    async def _arun(
        self,
        app_id: str,
        hl: str | None = None,
        gl: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleplay/app asynchronously.

        Args:
            app_id: Android package name ('com.spotify.music') or any play.google.com
                URL carrying one in its id param (1-500 characters).
            hl: UI language, 2-20 characters (default 'en').
            gl: Country code, 2-10 characters (default 'us'), deciding which
                storefront's price and availability are returned.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.google_play.app(app_id=app_id, hl=hl, gl=gl)
        return self._format_response(raw)


class ScavioGooglePlayReviewsTool(ScavioBaseTool):
    """A page of Google Play reviews: star score, full text, author, thumbs-up count,
    developer reply and the APP VERSION the reviewer was running.
    """

    name: str = "Scavio Google Play Reviews"
    description: str = (
        "A page of Google Play reviews: star score, full text, author, thumbs-up "
        "count, developer reply and the APP VERSION the reviewer was running. Paged by "
        "cursor, up to 200 per call. app() already returns the 20 reviews Play "
        "server-renders; use this to page past them or sort differently. Costs 2 "
        "credits."
    )
    args_schema: Type[BaseModel] = _GooglePlayReviewsInput

    def _run(
        self,
        app_id: str,
        sort: Literal["relevance", "newest", "rating"] | None = None,
        count: int | None = None,
        cursor: str | None = None,
        hl: str | None = None,
        gl: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleplay/reviews synchronously.

        Args:
            app_id: Android package name ('com.spotify.music') or any play.google.com
                URL carrying one in its id param (1-500 characters).
            sort: Review ordering (default 'newest').
            count: Reviews to return, 1-200 (default 50); 200 is our cap, not Play's.
            cursor: Continuation token from a prior response's next_cursor (1-4000
                characters).
            hl: UI language, 2-20 characters (default 'en').
            gl: Country code, 2-10 characters (default 'us'), deciding which
                storefront's price and availability are returned.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.google_play.reviews(
            app_id=app_id,
            sort=sort,
            count=count,
            cursor=cursor,
            hl=hl,
            gl=gl,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        app_id: str,
        sort: Literal["relevance", "newest", "rating"] | None = None,
        count: int | None = None,
        cursor: str | None = None,
        hl: str | None = None,
        gl: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleplay/reviews asynchronously.

        Args:
            app_id: Android package name ('com.spotify.music') or any play.google.com
                URL carrying one in its id param (1-500 characters).
            sort: Review ordering (default 'newest').
            count: Reviews to return, 1-200 (default 50); 200 is our cap, not Play's.
            cursor: Continuation token from a prior response's next_cursor (1-4000
                characters).
            hl: UI language, 2-20 characters (default 'en').
            gl: Country code, 2-10 characters (default 'us'), deciding which
                storefront's price and availability are returned.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.google_play.reviews(
            app_id=app_id,
            sort=sort,
            count=count,
            cursor=cursor,
            hl=hl,
            gl=gl,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
