"""Scavio Google Ads Transparency tools for CrewAI.

1 credit flat on all three endpoints (V2_GOOGLE_CREDIT_COST) -- GOOGLE-EXEMPT:
bills 10 upstream but Google is absorbed rather than passed on.

- Plain JSON-RPC at /anji/_/rpc/; customHeaders=true is MANDATORY or Google
  400s the binary body.
- IMPRESSIONS AND REACH ARE EEA-ONLY (DSA-compelled). US creatives return null
  for impressions_min/max/first_shown -- not a bug, Google only publishes reach
  where law requires. The playground should default to an EEA example.
- SEARCH NOW PAGINATES (shipped 2026-08-10, backend abb227e / dashboard
  09c7722): `cursor` request param + `next_cursor` response field, 100/page.
  Re-send the SAME filters with the cursor. Docs/SDK/MCP propagation MUST
  document cursor/next_cursor.
- /advertisers (autocomplete, ~20/arm) and /creative do NOT paginate.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_GoogleAdsSearchPlatform = Literal[
    "play", "maps", "search", "shopping", "youtube"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _GoogleAdsAdvertisersInput(BaseModel):
    """Input schema for ScavioGoogleAdsAdvertisersTool."""

    query: str = Field(
        ...,
        description="Brand name or domain to resolve (1-200 characters).",
    )
    region: str | None = Field(
        default=None,
        description=(
            "ISO 3166-1 alpha-2 country ('US', 'GB', 'DE') or a Google geo criteria id "
            "as a string (2-12 characters). Default: no region filter."
        ),
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Rows per arm (1-20; server default 10). Advertisers and domains are "
            "capped separately, so a name query can return up to twice this many rows."
        ),
    )


class _GoogleAdsSearchInput(BaseModel):
    """Input schema for ScavioGoogleAdsSearchTool."""

    domain: str | None = Field(
        default=None,
        description=(
            "Advertiser website (1-253 characters): bare host, www host or full URL, "
            "reduced to the registrable host. The only way to get `domain` back on "
            "each row."
        ),
    )
    advertiser_id: str | None = Field(
        default=None,
        description=(
            "Google advertiser id, e.g. 'AR16735076323512287233' (3-40 characters). "
            "The shape is checked before any request, so a typo costs no credits. "
            "Querying by id drops `domain` from every row."
        ),
    )
    region: str | None = Field(
        default=None,
        description=(
            "ISO 3166-1 alpha-2 country ('US', 'GB', 'DE') or a Google geo criteria id "
            "as a string (2-12 characters). Scopes the deep links on every row, and "
            "the same advertiser can share zero creatives between two countries. "
            "Default: worldwide."
        ),
    )
    format: Literal["text", "image", "video"] | None = Field(
        default=None,
        description=(
            "Creative format. The three sets are disjoint -- an advertiser's text, "
            "image and video ads share no creatives. Default: all formats."
        ),
    )
    platform: _GoogleAdsSearchPlatform | None = Field(
        default=None,
        description="Google surface the ad ran on. Default: all surfaces.",
    )
    topic: Literal["all", "political"] | None = Field(
        default=None,
        description="Ad topic (server default 'all').",
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Ads per page (1-100; server default 40). 100 is a hard upstream ceiling, "
            "not our policy: Google answers a larger request with zero rows rather "
            "than an error."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "next_cursor from the previous response (1-4000 characters), 100 ads per "
            "page. Re-send the same filters alongside it; next_cursor is null once "
            "exhausted."
        ),
    )


class _GoogleAdsCreativeInput(BaseModel):
    """Input schema for ScavioGoogleAdsCreativeTool."""

    advertiser_id: str = Field(
        ...,
        description=(
            "Google advertiser id, e.g. 'AR16735076323512287233' (3-40 characters)."
        ),
    )
    creative_id: str = Field(
        ...,
        description=(
            "Creative id (3-40 characters). It must belong to the advertiser_id sent "
            "with it -- the lookup is keyed by the pair and a mismatched pair is a "
            "404."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioGoogleAdsAdvertisersTool(ScavioBaseTool):
    """Resolve a brand name or domain to the advertiser_id that search() and creative()
    are keyed by.
    """

    name: str = "Scavio Google Ads Advertisers"
    description: str = (
        "Resolve a brand name or domain to the advertiser_id that search() and "
        "creative() are keyed by. Returns two row kinds in one list: 'advertiser' rows "
        "carrying the id, verified name, verification country and total ad count as a "
        "range, and 'domain' rows carrying a website. A name query returns both kinds; "
        "a domain-shaped query returns domains only. Autocomplete-backed, roughly 20 "
        "rows per arm, and it does not paginate. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _GoogleAdsAdvertisersInput

    def _run(
        self,
        query: str,
        region: str | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleads/advertisers synchronously.

        Args:
            query: Brand name or domain to resolve (1-200 characters).
            region: ISO 3166-1 alpha-2 country ('US', 'GB', 'DE') or a Google geo
                criteria id as a string (2-12 characters).
            limit: Rows per arm (1-20; server default 10).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.google_ads.advertisers(
            query=query,
            region=region,
            limit=limit,
        )
        raw = self._truncate_nested(raw, "data", "suggestions")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        region: str | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleads/advertisers asynchronously.

        Args:
            query: Brand name or domain to resolve (1-200 characters).
            region: ISO 3166-1 alpha-2 country ('US', 'GB', 'DE') or a Google geo
                criteria id as a string (2-12 characters).
            limit: Rows per arm (1-20; server default 10).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.google_ads.advertisers(
            query=query,
            region=region,
            limit=limit,
        )
        raw = self._truncate_nested(raw, "data", "suggestions")
        return self._format_response(raw)


class ScavioGoogleAdsSearchTool(ScavioBaseTool):
    """Every ad Google Ads Transparency holds for one advertiser: the creative (archived
    image, rich-media bundle, Google's renderer link, dimensions), advertiser id and
    name, format, first and last seen dates and days actually run, plus total_ads_min
    and total_ads_max -- Google publishes the advertiser's ad total as a range, never an
    exact figure.
    """

    name: str = "Scavio Google Ads Search"
    description: str = (
        "Every ad Google Ads Transparency holds for one advertiser: the creative "
        "(archived image, rich-media bundle, Google's renderer link, dimensions), "
        "advertiser id and name, format, first and last seen dates and days actually "
        "run, plus total_ads_min and total_ads_max -- Google publishes the "
        "advertiser's ad total as a range, never an exact figure. Up to 100 ads per "
        "page (server default 40); paginate by sending next_cursor back as cursor "
        "alongside the SAME filters. Provide domain or advertiser_id. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _GoogleAdsSearchInput

    def _run(
        self,
        domain: str | None = None,
        advertiser_id: str | None = None,
        region: str | None = None,
        format: Literal["text", "image", "video"] | None = None,
        platform: _GoogleAdsSearchPlatform | None = None,
        topic: Literal["all", "political"] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleads/search synchronously.

        Args:
            domain: Advertiser website (1-253 characters): bare host, www host or full
                URL, reduced to the registrable host.
            advertiser_id: Google advertiser id, e.g. 'AR16735076323512287233' (3-40
                characters).
            region: ISO 3166-1 alpha-2 country ('US', 'GB', 'DE') or a Google geo
                criteria id as a string (2-12 characters).
            format: Creative format. The three sets are disjoint -- an advertiser's
                text, image and video ads share no creatives.
            platform: Google surface the ad ran on. Default: all surfaces.
            topic: Ad topic (server default 'all').
            limit: Ads per page (1-100; server default 40).
            cursor: next_cursor from the previous response (1-4000 characters), 100 ads
                per page.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.google_ads.search(
            domain=domain,
            advertiser_id=advertiser_id,
            region=region,
            format=format,
            platform=platform,
            topic=topic,
            limit=limit,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "creatives")
        return self._format_response(raw)

    async def _arun(
        self,
        domain: str | None = None,
        advertiser_id: str | None = None,
        region: str | None = None,
        format: Literal["text", "image", "video"] | None = None,
        platform: _GoogleAdsSearchPlatform | None = None,
        topic: Literal["all", "political"] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/googleads/search asynchronously.

        Args:
            domain: Advertiser website (1-253 characters): bare host, www host or full
                URL, reduced to the registrable host.
            advertiser_id: Google advertiser id, e.g. 'AR16735076323512287233' (3-40
                characters).
            region: ISO 3166-1 alpha-2 country ('US', 'GB', 'DE') or a Google geo
                criteria id as a string (2-12 characters).
            format: Creative format. The three sets are disjoint -- an advertiser's
                text, image and video ads share no creatives.
            platform: Google surface the ad ran on. Default: all surfaces.
            topic: Ad topic (server default 'all').
            limit: Ads per page (1-100; server default 40).
            cursor: next_cursor from the previous response (1-4000 characters), 100 ads
                per page.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.google_ads.search(
            domain=domain,
            advertiser_id=advertiser_id,
            region=region,
            format=format,
            platform=platform,
            topic=topic,
            limit=limit,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "creatives")
        return self._format_response(raw)


class ScavioGoogleAdsCreativeTool(ScavioBaseTool):
    """One creative in full, and the only endpoint carrying its history: every size
    variation of the asset, the impression bucket, the per-region breakdown with first
    and last shown dates and a per-surface impression split inside each region, the
    format, Google's category label and the funder disclosure on political ads.
    """

    name: str = "Scavio Google Ads Creative"
    description: str = (
        "One creative in full, and the only endpoint carrying its history: every size "
        "variation of the asset, the impression bucket, the per-region breakdown with "
        "first and last shown dates and a per-surface impression split inside each "
        "region, the format, Google's category label and the funder disclosure on "
        "political ads. Impressions and first_shown are EEA-only (DSA-compelled) and "
        "come back null for US creatives, and an impression bucket may carry only a "
        "lower or only an upper bound. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _GoogleAdsCreativeInput

    def _run(self, advertiser_id: str, creative_id: str, **kwargs: Any) -> str:
        """Call /api/v1/googleads/creative synchronously.

        Args:
            advertiser_id: Google advertiser id, e.g. 'AR16735076323512287233' (3-40
                characters).
            creative_id: Creative id (3-40 characters).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.google_ads.creative(
            advertiser_id=advertiser_id,
            creative_id=creative_id,
        )
        return self._format_response(raw)

    async def _arun(self, advertiser_id: str, creative_id: str, **kwargs: Any) -> str:
        """Call /api/v1/googleads/creative asynchronously.

        Args:
            advertiser_id: Google advertiser id, e.g. 'AR16735076323512287233' (3-40
                characters).
            creative_id: Creative id (3-40 characters).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.google_ads.creative(
            advertiser_id=advertiser_id,
            creative_id=creative_id,
        )
        return self._format_response(raw)
