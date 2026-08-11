"""Scavio Capterra Software Reviews tools for CrewAI.

2 credits flat on all three endpoints (CAPTERRA_CREDIT_COST =
scrapedoCreditCost(10), premium per-domain table).

- Product `vendor` is NULL -- Capterra does not publish it as structured data on
  the product page (verified). The reviews name the vendor per review.
- SEARCH DOES NOT PAGINATE: Capterra fixes the result set at 20 and ?page=2
  returns identical rows, so there is deliberately NO page param on /search.
- A term-less /search/ serves a fixed popular-products list that has nothing to
  do with the caller, hence query (or a URL carrying one) is required.
- `slug` is cosmetic on /product (/p/186596/Zzzjunk/ returns Notion's profile
  byte-for-byte) but LOAD-BEARING on /reviews: it is case-sensitive upstream
  and a wrong one silently serves PAGE ONE under a billed 200. Pass back the
  slug or reviews_url from /search or /product.
"""


from typing import Any, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _CapterraSearchInput(BaseModel):
    """Input schema for ScavioCapterraSearchTool."""

    query: str | None = Field(
        default=None,
        description=(
            "Search term (1-200 characters). Required in practice: a term-less "
            "Capterra search serves a fixed popular-products list unrelated to the "
            "caller."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full capterra.com search URL, as an alternative to query (1-1000 "
            "characters; the transport also accepts capterra.co.uk and capterra.com.br "
            "hosts)."
        ),
    )


class _CapterraProductInput(BaseModel):
    """Input schema for ScavioCapterraProductTool."""

    product_id: str | None = Field(
        default=None,
        description=(
            "The number in a Capterra product path such as /p/186596/Notion/ (1-50 "
            "characters). Must be a STRING -- a JSON number is rejected."
        ),
    )
    slug: str | None = Field(
        default=None,
        description=(
            "Product slug (1-200 characters). Cosmetic on this endpoint -- a wrong "
            "slug still returns the right profile -- but load-bearing on reviews()."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full Capterra product URL, as an alternative to product_id (1-1000 "
            "characters)."
        ),
    )


class _CapterraReviewsInput(BaseModel):
    """Input schema for ScavioCapterraReviewsTool."""

    product_id: str | None = Field(
        default=None,
        description="Capterra product id as a string (1-50 characters).",
    )
    slug: str | None = Field(
        default=None,
        description=(
            "Product slug (1-200 characters). LOAD-BEARING here: it is case-sensitive "
            "upstream and a wrong one silently serves page one under a billed 200. "
            "Pass back the slug from search() or product()."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full Capterra reviews URL, as an alternative to product_id (1-1000 "
            "characters). Passing back reviews_url from product() is the reliable way "
            "to page."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "1-based page number (1-100); 25 reviews per page. 100 is a hard cap "
            "whatever the review count says -- past it Capterra answers 200 with page "
            "one."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioCapterraSearchTool(ScavioBaseTool):
    """Search Capterra, the B2B software review site: 20 ranked products with name,
    vendor description, rating, review count, logo and paid-placement flag, each row
    carrying product_id and slug.
    """

    name: str = "Scavio Capterra Search"
    description: str = (
        "Search Capterra, the B2B software review site: 20 ranked products with name, "
        "vendor description, rating, review count, logo and paid-placement flag, each "
        "row carrying product_id and slug. The result set is fixed at 20 and does NOT "
        "paginate -- Capterra serves identical rows for page 2, so there is "
        "deliberately no page parameter. Provide query or url. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _CapterraSearchInput

    def _run(
        self,
        query: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/capterra/search synchronously.

        Args:
            query: Search term (1-200 characters).
            url: Full capterra.com search URL, as an alternative to query (1-1000
                characters; the transport also accepts capterra.co.uk and
                capterra.com.br hosts).

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.capterra.search(query=query, url=url)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/capterra/search asynchronously.

        Args:
            query: Search term (1-200 characters).
            url: Full capterra.com search URL, as an alternative to query (1-1000
                characters; the transport also accepts capterra.co.uk and
                capterra.com.br hosts).

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.capterra.search(query=query, url=url)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioCapterraProductTool(ScavioBaseTool):
    """Full Capterra profile: rating with per-star histogram and the four scored
    criteria, likelihood to recommend, review sentiment and topics, the complete pricing
    table with every plan and its features, every rated feature and integration,
    AI-derived pros and cons with the quoted review, FAQs, screenshots, badges and
    awards, competitor comparisons and alternatives, and the buyer profile by company
    size, industry and job function -- PLUS the 25 most recent reviews at no extra cost.
    vendor is always null here: Capterra does not publish it as structured data on the
    product page.
    """

    name: str = "Scavio Capterra Product"
    description: str = (
        "Full Capterra profile: rating with per-star histogram and the four scored "
        "criteria, likelihood to recommend, review sentiment and topics, the complete "
        "pricing table with every plan and its features, every rated feature and "
        "integration, AI-derived pros and cons with the quoted review, FAQs, "
        "screenshots, badges and awards, competitor comparisons and alternatives, and "
        "the buyer profile by company size, industry and job function -- PLUS the 25 "
        "most recent reviews at no extra cost. vendor is always null here: Capterra "
        "does not publish it as structured data on the product page. Provide "
        "product_id or url. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _CapterraProductInput

    def _run(
        self,
        product_id: str | None = None,
        slug: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/capterra/product synchronously.

        Args:
            product_id: The number in a Capterra product path such as /p/186596/Notion/
                (1-50 characters).
            slug: Product slug (1-200 characters).
            url: Full Capterra product URL, as an alternative to product_id (1-1000
                characters).

        Returns:
            JSON-serialised product details.
        """
        raw = self.client.capterra.product(product_id=product_id, slug=slug, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        product_id: str | None = None,
        slug: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/capterra/product asynchronously.

        Args:
            product_id: The number in a Capterra product path such as /p/186596/Notion/
                (1-50 characters).
            slug: Product slug (1-200 characters).
            url: Full Capterra product URL, as an alternative to product_id (1-1000
                characters).

        Returns:
            JSON-serialised product details.
        """
        raw = await self.async_client.capterra.product(
            product_id=product_id,
            slug=slug,
            url=url,
        )
        return self._format_response(raw)


class ScavioCapterraReviewsTool(ScavioBaseTool):
    """A page of Capterra reviews: overall score plus five per-criterion scores, title,
    pros, cons, advice, usage duration, incentivized flag, alternatives considered and
    what they switched from, reviewer job title, industry and company size, and the
    vendor response -- plus a competitor list richer than the profile's, each
    alternative with its own rating histogram and starting price.
    """

    name: str = "Scavio Capterra Reviews"
    description: str = (
        "A page of Capterra reviews: overall score plus five per-criterion scores, "
        "title, pros, cons, advice, usage duration, incentivized flag, alternatives "
        "considered and what they switched from, reviewer job title, industry and "
        "company size, and the vendor response -- plus a competitor list richer than "
        "the profile's, each alternative with its own rating histogram and starting "
        "price. 25 reviews per page, capped at page 100. Page 1 already rides along "
        "inside product(), so use this to page past it. Provide product_id or url. "
        "Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _CapterraReviewsInput

    def _run(
        self,
        product_id: str | None = None,
        slug: str | None = None,
        url: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/capterra/reviews synchronously.

        Args:
            product_id: Capterra product id as a string (1-50 characters).
            slug: Product slug (1-200 characters).
            url: Full Capterra reviews URL, as an alternative to product_id (1-1000
                characters).
            page: 1-based page number (1-100); 25 reviews per page.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.capterra.reviews(
            product_id=product_id,
            slug=slug,
            url=url,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        product_id: str | None = None,
        slug: str | None = None,
        url: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/capterra/reviews asynchronously.

        Args:
            product_id: Capterra product id as a string (1-50 characters).
            slug: Product slug (1-200 characters).
            url: Full Capterra reviews URL, as an alternative to product_id (1-1000
                characters).
            page: 1-based page number (1-100); 25 reviews per page.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.capterra.reviews(
            product_id=product_id,
            slug=slug,
            url=url,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
