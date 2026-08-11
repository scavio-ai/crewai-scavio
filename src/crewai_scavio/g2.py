"""Scavio G2 Software Reviews tools for CrewAI.

5 credits flat on all three endpoints (G2_CREDIT_COST = scrapedoCreditCost(25))
-- the ONLY 5-credit platform and the thinnest margin we serve. Every surface
must show the 5 prominently.

- THINNEST MARGIN WE SERVE. g2.com bills 25 scrape.do credits per call with
  neither render nor super asked for. A 3x retry would cost 75 upstream
  credits, so retry policy is deliberately conservative.
- A BOT WALL OR HOLLOW SHELL ON G2 IS A BILLED 502: it arrives as a real HTTP
  200 that scrape.do charged all 25 credits for, so the caller is charged for a
  page we could not use. This is the opposite of Yelp's behaviour.
- An unknown `order` is SILENTLY ACCEPTED upstream -- order=zzznotasort answers
  200 with a full result set in some unstated ordering, so the sort never ran
  and nothing says so. Hence closed enums.
- An unknown filters[...] value MATCHES NOTHING -- a bogus company_segment id
  returns 'Reviews (0)' which reads as 'this product has no enterprise
  reviews'.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_G2ReviewsSort = Literal[
    "relevance", "newest", "most_helpful", "rating_high", "rating_low"
]
_G2ReviewsCompanySize = Literal[
    "small_business", "mid_market", "enterprise"
]
_G2ReviewsRole = Literal[
    "user", "administrator", "executive_sponsor", "internal_consultant",
    "consultant", "agency", "industry_analyst"
]
_G2ReviewsRegion = Literal[
    "north_america", "europe", "asia", "latin_america", "anz",
    "middle_east", "africa"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _G2SearchInput(BaseModel):
    """Input schema for ScavioG2SearchTool."""

    query: str | None = Field(
        default=None,
        description="Search term (1-200 characters). Provide this or url.",
    )
    page: int | None = Field(
        default=None,
        description=(
            "1-based page number; page size follows limit (server default 20). G2 "
            "keeps paginating well past its own widget's page links."
        ),
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Results per page (1-100; server default 20). The 100 ceiling is ours, to "
            "keep a single request inside the 60s deadline; G2 itself paginates at any "
            "size."
        ),
    )
    sort: Literal["relevance", "popular", "alphabetical", "rating"] | None = Field(
        default=None,
        description=(
            "Result sort order (server default 'relevance'). Closed enum: G2 silently "
            "accepts an unknown sort and answers 200 with an unstated ordering."
        ),
    )
    rating: Literal[1, 2, 3, 4, 5] | None = Field(
        default=None,
        description=(
            "Only products at or above this star rating (1-5, sent as an integer). "
            "Omit for no rating floor."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full g2.com/search URL, as an alternative to query (1-1000 characters; "
            "the host is checked by the transport)."
        ),
    )


class _G2ProductInput(BaseModel):
    """Input schema for ScavioG2ProductTool."""

    product_id: str | None = Field(
        default=None,
        description=(
            "G2 product slug ('notion') or the numeric G2 id ('82623') as a string "
            "(1-200 characters); both resolve on the same upstream path."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full g2.com product URL, as an alternative to product_id (1-1000 "
            "characters)."
        ),
    )


class _G2ReviewsInput(BaseModel):
    """Input schema for ScavioG2ReviewsTool."""

    product_id: str | None = Field(
        default=None,
        description="G2 product slug or numeric G2 id as a string (1-200 characters).",
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full g2.com reviews URL, as an alternative to product_id (1-1000 "
            "characters)."
        ),
    )
    page: int | None = Field(
        default=None,
        description="1-based page number; fixed at 10 reviews per page.",
    )
    sort: _G2ReviewsSort | None = Field(
        default=None,
        description=(
            "Review sort order (server default 'relevance'). Closed enum: an unknown "
            "sort is silently accepted upstream and never runs."
        ),
    )
    rating: Literal[1, 2, 3, 4, 5] | None = Field(
        default=None,
        description=(
            "Only reviews in this star bucket (1-5, sent as an integer). Buckets are "
            "half- star-inclusive: 1 returns 0, 0.5 and 1-star reviews."
        ),
    )
    company_size: _G2ReviewsCompanySize | None = Field(
        default=None,
        description=(
            "Reviewer company size: small_business is 50 employees or fewer, "
            "mid_market 51-1000, enterprise over 1000. Closed enum -- an unknown value "
            "matches nothing and returns a billed 'Reviews (0)'."
        ),
    )
    role: _G2ReviewsRole | None = Field(
        default=None,
        description=(
            "Reviewer role. Closed enum -- an unknown value matches nothing rather "
            "than erroring."
        ),
    )
    region: _G2ReviewsRegion | None = Field(
        default=None,
        description=(
            "Reviewer region. Closed enum -- an unknown value matches nothing rather "
            "than erroring."
        ),
    )
    query: str | None = Field(
        default=None,
        description=(
            "Full-text search within this product's reviews (1-200 characters); "
            "narrows the review list AND every facet count."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioG2SearchTool(ScavioBaseTool):
    """Search G2, the B2B software review site, for products: star rating, review count,
    vendor, categories, seller description and logo, with product_id and slug on every
    row.
    """

    name: str = "Scavio G2 Search"
    description: str = (
        "Search G2, the B2B software review site, for products: star rating, review "
        "count, vendor, categories, seller description and logo, with product_id and "
        "slug on every row. Up to 100 results per page (server default 20) and "
        "page-paginated; total_results is G2's Products-tab headline and caps at "
        "10000, while total_by_type splits the query across products, sellers, "
        "categories and discussions. Provide query or url. Costs 5 credits."
    )
    args_schema: Type[BaseModel] = _G2SearchInput

    def _run(
        self,
        query: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        sort: Literal["relevance", "popular", "alphabetical", "rating"] | None = None,
        rating: Literal[1, 2, 3, 4, 5] | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/g2/search synchronously.

        Args:
            query: Search term (1-200 characters).
            page: 1-based page number; page size follows limit (server default 20).
            limit: Results per page (1-100; server default 20).
            sort: Result sort order (server default 'relevance').
            rating: Only products at or above this star rating (1-5, sent as an
                integer).
            url: Full g2.com/search URL, as an alternative to query (1-1000 characters;
                the host is checked by the transport).

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.g2.search(
            query=query,
            page=page,
            limit=limit,
            sort=sort,
            rating=rating,
            url=url,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        sort: Literal["relevance", "popular", "alphabetical", "rating"] | None = None,
        rating: Literal[1, 2, 3, 4, 5] | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/g2/search asynchronously.

        Args:
            query: Search term (1-200 characters).
            page: 1-based page number; page size follows limit (server default 20).
            limit: Results per page (1-100; server default 20).
            sort: Result sort order (server default 'relevance').
            rating: Only products at or above this star rating (1-5, sent as an
                integer).
            url: Full g2.com/search URL, as an alternative to query (1-1000 characters;
                the host is checked by the transport).

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.g2.search(
            query=query,
            page=page,
            limit=limit,
            sort=sort,
            rating=rating,
            url=url,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioG2ProductTool(ScavioBaseTool):
    """Full G2 product profile: rating with per-star histogram, review count, vendor,
    description and seller website, pricing editions with parsed amounts, feature
    groups, categories and breadcrumbs, supported languages, integrations, alternatives,
    head-to-head comparisons, media, community discussions and G2's AI-derived pros and
    cons.
    """

    name: str = "Scavio G2 Product"
    description: str = (
        "Full G2 product profile: rating with per-star histogram, review count, "
        "vendor, description and seller website, pricing editions with parsed amounts, "
        "feature groups, categories and breadcrumbs, supported languages, "
        "integrations, alternatives, head-to-head comparisons, media, community "
        "discussions and G2's AI-derived pros and cons. Carries NO review text at all "
        "-- G2 loads review bodies in a separate frame, so call reviews() for those. "
        "Provide product_id or url. Costs 5 credits."
    )
    args_schema: Type[BaseModel] = _G2ProductInput

    def _run(
        self,
        product_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/g2/product synchronously.

        Args:
            product_id: G2 product slug ('notion') or the numeric G2 id ('82623') as a
                string (1-200 characters); both resolve on the same upstream path.
            url: Full g2.com product URL, as an alternative to product_id (1-1000
                characters).

        Returns:
            JSON-serialised product details.
        """
        raw = self.client.g2.product(product_id=product_id, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        product_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/g2/product asynchronously.

        Args:
            product_id: G2 product slug ('notion') or the numeric G2 id ('82623') as a
                string (1-200 characters); both resolve on the same upstream path.
            url: Full g2.com product URL, as an alternative to product_id (1-1000
                characters).

        Returns:
            JSON-serialised product details.
        """
        raw = await self.async_client.g2.product(product_id=product_id, url=url)
        return self._format_response(raw)


class ScavioG2ReviewsTool(ScavioBaseTool):
    """A page of G2 reviews: rating, title, likes and dislikes, problems solved,
    reviewer job title, industry and company size, validated and incentivized flags --
    plus what the profile page has no form of: exact per-star counts, pros and cons with
    per-theme counts, and company-size, role, industry, region and category facets with
    counts.
    """

    name: str = "Scavio G2 Reviews"
    description: str = (
        "A page of G2 reviews: rating, title, likes and dislikes, problems solved, "
        "reviewer job title, industry and company size, validated and incentivized "
        "flags -- plus what the profile page has no form of: exact per-star counts, "
        "pros and cons with per-theme counts, and company-size, role, industry, region "
        "and category facets with counts. Fixed at 10 reviews per page and paginates "
        "well past the 10 pages G2's own widget links to. Provide product_id or url. "
        "Costs 5 credits."
    )
    args_schema: Type[BaseModel] = _G2ReviewsInput

    def _run(
        self,
        product_id: str | None = None,
        url: str | None = None,
        page: int | None = None,
        sort: _G2ReviewsSort | None = None,
        rating: Literal[1, 2, 3, 4, 5] | None = None,
        company_size: _G2ReviewsCompanySize | None = None,
        role: _G2ReviewsRole | None = None,
        region: _G2ReviewsRegion | None = None,
        query: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/g2/reviews synchronously.

        Args:
            product_id: G2 product slug or numeric G2 id as a string (1-200 characters).
            url: Full g2.com reviews URL, as an alternative to product_id (1-1000
                characters).
            page: 1-based page number; fixed at 10 reviews per page.
            sort: Review sort order (server default 'relevance').
            rating: Only reviews in this star bucket (1-5, sent as an integer).
            company_size: Reviewer company size: small_business is 50 employees or
                fewer, mid_market 51-1000, enterprise over 1000.
            role: Reviewer role. Closed enum -- an unknown value matches nothing rather
                than erroring.
            region: Reviewer region. Closed enum -- an unknown value matches nothing
                rather than erroring.
            query: Full-text search within this product's reviews (1-200 characters);
                narrows the review list AND every facet count.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.g2.reviews(
            product_id=product_id,
            url=url,
            page=page,
            sort=sort,
            rating=rating,
            company_size=company_size,
            role=role,
            region=region,
            query=query,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        product_id: str | None = None,
        url: str | None = None,
        page: int | None = None,
        sort: _G2ReviewsSort | None = None,
        rating: Literal[1, 2, 3, 4, 5] | None = None,
        company_size: _G2ReviewsCompanySize | None = None,
        role: _G2ReviewsRole | None = None,
        region: _G2ReviewsRegion | None = None,
        query: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/g2/reviews asynchronously.

        Args:
            product_id: G2 product slug or numeric G2 id as a string (1-200 characters).
            url: Full g2.com reviews URL, as an alternative to product_id (1-1000
                characters).
            page: 1-based page number; fixed at 10 reviews per page.
            sort: Review sort order (server default 'relevance').
            rating: Only reviews in this star bucket (1-5, sent as an integer).
            company_size: Reviewer company size: small_business is 50 employees or
                fewer, mid_market 51-1000, enterprise over 1000.
            role: Reviewer role. Closed enum -- an unknown value matches nothing rather
                than erroring.
            region: Reviewer region. Closed enum -- an unknown value matches nothing
                rather than erroring.
            query: Full-text search within this product's reviews (1-200 characters);
                narrows the review list AND every facet count.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.g2.reviews(
            product_id=product_id,
            url=url,
            page=page,
            sort=sort,
            rating=rating,
            company_size=company_size,
            role=role,
            region=region,
            query=query,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
