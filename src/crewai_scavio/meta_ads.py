"""Scavio Meta Ad Library tools for CrewAI.

1 credit flat on all three endpoints (METAADS_CREDIT_COST =
scrapedoCreditCost(1)). Each cursor page is another credit, so 'scrape the
whole library' is real but the cost scales with depth (~10 ads per credit past
the first 30) -- docs must say this.

- THE HOST IS LOAD-BEARING: business.facebook.com works;
  www.facebook.com/ads/library 502s on every proxy option. Any doc/SDK example
  MUST use the endpoints, never a www URL.
- total_results caps at 50000 with total_is_capped:true -- Meta only reports
  '>50,000'. Do not present it as an exact count.
- Political/issue ads carry spend, reach, impressions and the paid-for-by
  disclosure; commercial ads leave those NULL (expected, not a bug). Set
  ad_type=political_and_issue_ads to expose them.
- FULL CURSOR PAGINATION on search + advertiser: page 1 = 30 ads via SSR, then
  10/page via a GraphQL POST off next_cursor. Walk has_next_page to scrape a
  whole query or advertiser. THE BIG DIFFERENTIATOR over the $79-399/mo tools --
  lead with it.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_MetaAdsSearchMediaType = Literal[
    "all", "image", "video", "meme", "image_and_meme", "none"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _MetaAdsSearchInput(BaseModel):
    """Input schema for ScavioMetaAdsSearchTool."""

    query: str = Field(
        ...,
        description="Keyword to search the ad library for (1-200 characters).",
    )
    country: str | None = Field(
        default=None,
        description=(
            "Ad library country as an exactly 2-character ISO 3166-1 alpha-2 code "
            "(server default 'US')."
        ),
    )
    active_status: Literal["all", "active", "inactive"] | None = Field(
        default=None,
        description="Whether the ad is still running (server default 'all').",
    )
    ad_type: Literal["all", "political_and_issue_ads"] | None = Field(
        default=None,
        description=(
            "Set 'political_and_issue_ads' to expose spend, reach, impressions and the "
            "paid-for-by disclosure; commercial ads leave all four null (server "
            "default 'all')."
        ),
    )
    media_type: _MetaAdsSearchMediaType | None = Field(
        default=None,
        description="Creative media filter. Default: no media filter.",
    )
    search_type: Literal["keyword_unordered", "keyword_exact_phrase"] | None = Field(
        default=None,
        description="How the query is matched (server default 'keyword_unordered').",
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "next_cursor from the previous response: page 1 is 30 ads, every cursor "
            "page is 10. The cursor is a self-contained blob, so ALL other filters are "
            "ignored when it is present."
        ),
    )


class _MetaAdsAdvertiserInput(BaseModel):
    """Input schema for ScavioMetaAdsAdvertiserTool."""

    page_id: str = Field(
        ...,
        description=(
            "The advertiser's numeric Facebook Page id (3-25 digits, as a string)."
        ),
    )
    country: str | None = Field(
        default=None,
        description=(
            "Ad library country as an exactly 2-character ISO 3166-1 alpha-2 code "
            "(server default 'US')."
        ),
    )
    active_status: Literal["all", "active", "inactive"] | None = Field(
        default=None,
        description="Whether the ad is still running (server default 'all').",
    )
    ad_type: Literal["all", "political_and_issue_ads"] | None = Field(
        default=None,
        description=(
            "Set 'political_and_issue_ads' to expose spend, reach, impressions and the "
            "paid-for-by disclosure; commercial ads leave all four null (server "
            "default 'all')."
        ),
    )
    media_type: _MetaAdsSearchMediaType | None = Field(
        default=None,
        description="Creative media filter. Default: no media filter.",
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "next_cursor from the previous response: page 1 is 30 ads, every cursor "
            "page is 10. ALL other filters are ignored when it is present."
        ),
    )


class _MetaAdsAdInput(BaseModel):
    """Input schema for ScavioMetaAdsAdTool."""

    ad_archive_id: str = Field(
        ...,
        description="Meta ad archive id (3-25 digits, as a string).",
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioMetaAdsSearchTool(ScavioBaseTool):
    """Search the Meta Ad Library by keyword: 30 ads on page 1 with the full creative --
    page name, ad copy, headline, CTA, images and videos, the platforms each ran on and
    its run dates -- then 10 ads per cursor page, walking has_next_page to the end of
    the query. total_results caps at 50000 with total_is_capped true, because Meta only
    reports '>50,000'; never present it as an exact count.
    """

    name: str = "Scavio Meta Ads Search"
    description: str = (
        "Search the Meta Ad Library by keyword: 30 ads on page 1 with the full "
        "creative -- page name, ad copy, headline, CTA, images and videos, the "
        "platforms each ran on and its run dates -- then 10 ads per cursor page, "
        "walking has_next_page to the end of the query. total_results caps at 50000 "
        "with total_is_capped true, because Meta only reports '>50,000'; never present "
        "it as an exact count. Every page costs 1 credit."
    )
    args_schema: Type[BaseModel] = _MetaAdsSearchInput

    def _run(
        self,
        query: str,
        country: str | None = None,
        active_status: Literal["all", "active", "inactive"] | None = None,
        ad_type: Literal["all", "political_and_issue_ads"] | None = None,
        media_type: _MetaAdsSearchMediaType | None = None,
        search_type: Literal["keyword_unordered", "keyword_exact_phrase"] | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/meta-ads/search synchronously.

        Args:
            query: Keyword to search the ad library for (1-200 characters).
            country: Ad library country as an exactly 2-character ISO 3166-1 alpha-2
                code (server default 'US').
            active_status: Whether the ad is still running (server default 'all').
            ad_type: Set 'political_and_issue_ads' to expose spend, reach, impressions
                and the paid-for-by disclosure; commercial ads leave all four null
                (server default 'all').
            media_type: Creative media filter. Default: no media filter.
            search_type: How the query is matched (server default 'keyword_unordered').
            cursor: next_cursor from the previous response: page 1 is 30 ads, every
                cursor page is 10.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.meta_ads.search(
            query=query,
            country=country,
            active_status=active_status,
            ad_type=ad_type,
            media_type=media_type,
            search_type=search_type,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "ads")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        country: str | None = None,
        active_status: Literal["all", "active", "inactive"] | None = None,
        ad_type: Literal["all", "political_and_issue_ads"] | None = None,
        media_type: _MetaAdsSearchMediaType | None = None,
        search_type: Literal["keyword_unordered", "keyword_exact_phrase"] | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/meta-ads/search asynchronously.

        Args:
            query: Keyword to search the ad library for (1-200 characters).
            country: Ad library country as an exactly 2-character ISO 3166-1 alpha-2
                code (server default 'US').
            active_status: Whether the ad is still running (server default 'all').
            ad_type: Set 'political_and_issue_ads' to expose spend, reach, impressions
                and the paid-for-by disclosure; commercial ads leave all four null
                (server default 'all').
            media_type: Creative media filter. Default: no media filter.
            search_type: How the query is matched (server default 'keyword_unordered').
            cursor: next_cursor from the previous response: page 1 is 30 ads, every
                cursor page is 10.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.meta_ads.search(
            query=query,
            country=country,
            active_status=active_status,
            ad_type=ad_type,
            media_type=media_type,
            search_type=search_type,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "ads")
        return self._format_response(raw)


class ScavioMetaAdsAdvertiserTool(ScavioBaseTool):
    """Every ad a Facebook Page is running, by numeric page id: 30 ads on page 1 with
    the same creative detail as search(), then 10 ads per cursor page, walking
    has_next_page to the end of the advertiser.
    """

    name: str = "Scavio Meta Ads Advertiser"
    description: str = (
        "Every ad a Facebook Page is running, by numeric page id: 30 ads on page 1 "
        "with the same creative detail as search(), then 10 ads per cursor page, "
        "walking has_next_page to the end of the advertiser. Every page costs 1 "
        "credit."
    )
    args_schema: Type[BaseModel] = _MetaAdsAdvertiserInput

    def _run(
        self,
        page_id: str,
        country: str | None = None,
        active_status: Literal["all", "active", "inactive"] | None = None,
        ad_type: Literal["all", "political_and_issue_ads"] | None = None,
        media_type: _MetaAdsSearchMediaType | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/meta-ads/advertiser synchronously.

        Args:
            page_id: The advertiser's numeric Facebook Page id (3-25 digits, as a
                string).
            country: Ad library country as an exactly 2-character ISO 3166-1 alpha-2
                code (server default 'US').
            active_status: Whether the ad is still running (server default 'all').
            ad_type: Set 'political_and_issue_ads' to expose spend, reach, impressions
                and the paid-for-by disclosure; commercial ads leave all four null
                (server default 'all').
            media_type: Creative media filter. Default: no media filter.
            cursor: next_cursor from the previous response: page 1 is 30 ads, every
                cursor page is 10.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.meta_ads.advertiser(
            page_id=page_id,
            country=country,
            active_status=active_status,
            ad_type=ad_type,
            media_type=media_type,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "ads")
        return self._format_response(raw)

    async def _arun(
        self,
        page_id: str,
        country: str | None = None,
        active_status: Literal["all", "active", "inactive"] | None = None,
        ad_type: Literal["all", "political_and_issue_ads"] | None = None,
        media_type: _MetaAdsSearchMediaType | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/meta-ads/advertiser asynchronously.

        Args:
            page_id: The advertiser's numeric Facebook Page id (3-25 digits, as a
                string).
            country: Ad library country as an exactly 2-character ISO 3166-1 alpha-2
                code (server default 'US').
            active_status: Whether the ad is still running (server default 'all').
            ad_type: Set 'political_and_issue_ads' to expose spend, reach, impressions
                and the paid-for-by disclosure; commercial ads leave all four null
                (server default 'all').
            media_type: Creative media filter. Default: no media filter.
            cursor: next_cursor from the previous response: page 1 is 30 ads, every
                cursor page is 10.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.meta_ads.advertiser(
            page_id=page_id,
            country=country,
            active_status=active_status,
            ad_type=ad_type,
            media_type=media_type,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "ads")
        return self._format_response(raw)


class ScavioMetaAdsAdTool(ScavioBaseTool):
    """One Meta ad in full by archive id: creative, advertiser, run dates, the platforms
    it ran on, and the political disclosure when the ad carries one.
    """

    name: str = "Scavio Meta Ads Ad"
    description: str = (
        "One Meta ad in full by archive id: creative, advertiser, run dates, the "
        "platforms it ran on, and the political disclosure when the ad carries one. "
        "Commercial ads leave spend, reach and impressions null. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _MetaAdsAdInput

    def _run(self, ad_archive_id: str, **kwargs: Any) -> str:
        """Call /api/v1/meta-ads/ad synchronously.

        Args:
            ad_archive_id: Meta ad archive id (3-25 digits, as a string).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.meta_ads.ad(ad_archive_id=ad_archive_id)
        return self._format_response(raw)

    async def _arun(self, ad_archive_id: str, **kwargs: Any) -> str:
        """Call /api/v1/meta-ads/ad asynchronously.

        Args:
            ad_archive_id: Meta ad archive id (3-25 digits, as a string).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.meta_ads.ad(ad_archive_id=ad_archive_id)
        return self._format_response(raw)
