"""Scavio Glassdoor tools for CrewAI.

1 credit flat on all four endpoints (GLASSDOOR_CREDIT_COST =
scrapedoCreditCost(5), render-only domain). NOTE: addressing /reviews or
/salaries by employer_id costs TWO upstream fetches (10 scrape.do credits for 1
customer credit) -- the customer price does not change, but the single-fetch
path (pass back reviews_url / salaries_url as `url`) should still lead the
docs.

- LOOKUP FIRST. /glassdoor/companies was added after the first build shipped
  without one. /company, /reviews and /salaries all take an employer_id that
  exists only inside Glassdoor's /Overview/ URLs. Docs must LEAD with the
  lookup.
- REVIEWS ARE CAPPED AT THREE per response by Glassdoor's login wall. There is
  deliberately NO `page` param on /reviews -- use category and employment_status
  to move the window, and filtered_review_count to see how many match.
- Requires `render` -- the plain pool times out 3/3. 5 upstream credits for 1
  customer credit.
- SLOW AND FLAKY: per-attempt success 48% across 25 attempts, per-call 87%.
  Latency company ~3-47s, reviews ~75s, salaries ~41s; a fully failing call can
  take ~172s before its 502.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_GlassdoorReviewsCategory = Literal[
    "career_development", "compensation", "culture",
    "diversity_and_inclusion", "management", "work_life_balance"
]
_GlassdoorReviewsEmploymentStatus = Literal[
    "full_time", "part_time", "contract", "intern"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _GlassdoorCompaniesInput(BaseModel):
    """Input schema for ScavioGlassdoorCompaniesTool."""

    query: str = Field(
        ...,
        description="Company name to resolve (1-120 characters).",
    )


class _GlassdoorCompanyInput(BaseModel):
    """Input schema for ScavioGlassdoorCompanyTool."""

    employer_id: str | None = Field(
        default=None,
        description=(
            "Glassdoor employer id (1-50 characters) in any form Glassdoor writes it: "
            "'1699', 'E1699' or 'IE1699'. Must be a STRING - a JSON number is "
            "rejected."
        ),
    )
    company: str | None = Field(
        default=None,
        description=(
            "Employer name as it appears in a Glassdoor slug (1-200 characters). "
            "COSMETIC: the profile resolves on employer_id alone, it is ignored "
            "entirely when url is set, and it does not satisfy the employer_id-or-url "
            "requirement."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Any glassdoor.com employer URL (1-500 characters): /Overview/, /Reviews/ "
            "or /Salary/. A non-glassdoor.com host is rejected."
        ),
    )


class _GlassdoorReviewsInput(BaseModel):
    """Input schema for ScavioGlassdoorReviewsTool."""

    employer_id: str | None = Field(
        default=None,
        description=(
            "Glassdoor employer id (1-50 characters): '1699', 'E1699' or 'IE1699'. "
            "Must be a STRING - a JSON number is rejected. Addressing by id costs two "
            "upstream fetches; the customer price is unchanged."
        ),
    )
    company: str | None = Field(
        default=None,
        description=(
            "Employer name as it appears in a Glassdoor slug (1-200 characters). "
            "COSMETIC: ignored when url is set, and it does not satisfy the "
            "employer_id-or-url requirement."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Any glassdoor.com employer URL (1-500 characters). Pass back reviews_url "
            "from company() to skip the resolve fetch. A non-glassdoor.com host is "
            "rejected."
        ),
    )
    category: _GlassdoorReviewsCategory | None = Field(
        default=None,
        description=(
            "Restrict to reviews Glassdoor files under one topic. Closed enum: "
            "Glassdoor IGNORES an unknown value and serves the unfiltered set under a "
            "200. Read filtered_review_count on the response to see how many match."
        ),
    )
    employment_status: _GlassdoorReviewsEmploymentStatus | None = Field(
        default=None,
        description=(
            "Restrict to one kind of employment. Closed enum for the same reason as "
            "category; FREELANCE is deliberately absent because it was never confirmed "
            "to change the result set."
        ),
    )


class _GlassdoorSalariesInput(BaseModel):
    """Input schema for ScavioGlassdoorSalariesTool."""

    employer_id: str | None = Field(
        default=None,
        description=(
            "Glassdoor employer id (1-50 characters): '1699', 'E1699' or 'IE1699'. "
            "Must be a STRING - a JSON number is rejected. Addressing by id costs two "
            "upstream fetches; the customer price is unchanged."
        ),
    )
    company: str | None = Field(
        default=None,
        description=(
            "Employer name as it appears in a Glassdoor slug (1-200 characters). "
            "COSMETIC: ignored when url is set, and it does not satisfy the "
            "employer_id-or-url requirement."
        ),
    )
    url: str | None = Field(
        default=None,
        description=(
            "Any glassdoor.com employer URL (1-500 characters). Pass back salaries_url "
            "from company() to skip the resolve fetch. A non-glassdoor.com host is "
            "rejected."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based. Ten job titles per page; page_count on the "
            "response is how many pages exist."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioGlassdoorCompaniesTool(ScavioBaseTool):
    """START HERE. Resolve a company NAME to the employer_id every other Glassdoor
    method is keyed by, ranked by Glassdoor and de-duplicated.
    """

    name: str = "Scavio Glassdoor Companies"
    description: str = (
        "START HERE. Resolve a company NAME to the employer_id every other Glassdoor "
        "method is keyed by, ranked by Glassdoor and de-duplicated. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _GlassdoorCompaniesInput

    def _run(self, query: str, **kwargs: Any) -> str:
        """Call /api/v1/glassdoor/companies synchronously.

        Args:
            query: Company name to resolve (1-120 characters).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.glassdoor.companies(query=query)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Call /api/v1/glassdoor/companies asynchronously.

        Args:
            query: Company name to resolve (1-120 characters).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.glassdoor.companies(query=query)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


class ScavioGlassdoorCompanyTool(ScavioBaseTool):
    """Glassdoor employer profile: description, mission, industry, sector, HQ, size and
    revenue bands, stock symbol, year founded, overall and per-category ratings, star
    distribution, CEO approval, awards, FAQ and the five server-rendered reviews.
    """

    name: str = "Scavio Glassdoor Company"
    description: str = (
        "Glassdoor employer profile: description, mission, industry, sector, HQ, size "
        "and revenue bands, stock symbol, year founded, overall and per-category "
        "ratings, star distribution, CEO approval, awards, FAQ and the five "
        "server-rendered reviews. Also returns reviews_url and salaries_url, which "
        "reviews() and salaries() accept as url to save a fetch. Provide employer_id "
        "or url. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _GlassdoorCompanyInput

    def _run(
        self,
        employer_id: str | None = None,
        company: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/glassdoor/company synchronously.

        Args:
            employer_id: Glassdoor employer id (1-50 characters) in any form Glassdoor
                writes it: '1699', 'E1699' or 'IE1699'.
            company: Employer name as it appears in a Glassdoor slug (1-200 characters).
            url: Any glassdoor.com employer URL (1-500 characters): /Overview/,
                /Reviews/ or /Salary/.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.glassdoor.company(
            employer_id=employer_id,
            company=company,
            url=url,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        employer_id: str | None = None,
        company: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/glassdoor/company asynchronously.

        Args:
            employer_id: Glassdoor employer id (1-50 characters) in any form Glassdoor
                writes it: '1699', 'E1699' or 'IE1699'.
            company: Employer name as it appears in a Glassdoor slug (1-200 characters).
            url: Any glassdoor.com employer URL (1-500 characters): /Overview/,
                /Reviews/ or /Salary/.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.glassdoor.company(
            employer_id=employer_id,
            company=company,
            url=url,
        )
        return self._format_response(raw)


class ScavioGlassdoorReviewsTool(ScavioBaseTool):
    """Up to THREE full Glassdoor reviews - the cap is Glassdoor's login wall - with
    per-axis scores, pros, cons, advice, job title, location, employment status and
    employer response, plus complete rating statistics, star distribution, aggregate
    pro/con highlight terms and per-job-title review counts.
    """

    name: str = "Scavio Glassdoor Reviews"
    description: str = (
        "Up to THREE full Glassdoor reviews - the cap is Glassdoor's login wall - with "
        "per-axis scores, pros, cons, advice, job title, location, employment status "
        "and employer response, plus complete rating statistics, star distribution, "
        "aggregate pro/con highlight terms and per-job-title review counts. There is "
        "no page param: move the window with category and employment_status. Provide "
        "employer_id or url. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _GlassdoorReviewsInput

    def _run(
        self,
        employer_id: str | None = None,
        company: str | None = None,
        url: str | None = None,
        category: _GlassdoorReviewsCategory | None = None,
        employment_status: _GlassdoorReviewsEmploymentStatus | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/glassdoor/reviews synchronously.

        Args:
            employer_id: Glassdoor employer id (1-50 characters): '1699', 'E1699' or
                'IE1699'.
            company: Employer name as it appears in a Glassdoor slug (1-200 characters).
            url: Any glassdoor.com employer URL (1-500 characters).
            category: Restrict to reviews Glassdoor files under one topic.
            employment_status: Restrict to one kind of employment.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.glassdoor.reviews(
            employer_id=employer_id,
            company=company,
            url=url,
            category=category,
            employment_status=employment_status,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        employer_id: str | None = None,
        company: str | None = None,
        url: str | None = None,
        category: _GlassdoorReviewsCategory | None = None,
        employment_status: _GlassdoorReviewsEmploymentStatus | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/glassdoor/reviews asynchronously.

        Args:
            employer_id: Glassdoor employer id (1-50 characters): '1699', 'E1699' or
                'IE1699'.
            company: Employer name as it appears in a Glassdoor slug (1-200 characters).
            url: Any glassdoor.com employer URL (1-500 characters).
            category: Restrict to reviews Glassdoor files under one topic.
            employment_status: Restrict to one kind of employment.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.glassdoor.reviews(
            employer_id=employer_id,
            company=company,
            url=url,
            category=category,
            employment_status=employment_status,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)


class ScavioGlassdoorSalariesTool(ScavioBaseTool):
    """Glassdoor salaries by job title, 10 titles per page: base-pay and total-pay
    percentiles P10-P90 with medians called out, sample counts, currency, pay period and
    last-reported date.
    """

    name: str = "Scavio Glassdoor Salaries"
    description: str = (
        "Glassdoor salaries by job title, 10 titles per page: base-pay and total-pay "
        "percentiles P10-P90 with medians called out, sample counts, currency, pay "
        "period and last-reported date. The figures are Glassdoor's ESTIMATES for the "
        "title, not individual reported salaries. Provide employer_id or url. Costs 1 "
        "credit."
    )
    args_schema: Type[BaseModel] = _GlassdoorSalariesInput

    def _run(
        self,
        employer_id: str | None = None,
        company: str | None = None,
        url: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/glassdoor/salaries synchronously.

        Args:
            employer_id: Glassdoor employer id (1-50 characters): '1699', 'E1699' or
                'IE1699'.
            company: Employer name as it appears in a Glassdoor slug (1-200 characters).
            url: Any glassdoor.com employer URL (1-500 characters).
            page: Results page, 1-based. Ten job titles per page; page_count on the
                response is how many pages exist.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.glassdoor.salaries(
            employer_id=employer_id,
            company=company,
            url=url,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "salaries")
        return self._format_response(raw)

    async def _arun(
        self,
        employer_id: str | None = None,
        company: str | None = None,
        url: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/glassdoor/salaries asynchronously.

        Args:
            employer_id: Glassdoor employer id (1-50 characters): '1699', 'E1699' or
                'IE1699'.
            company: Employer name as it appears in a Glassdoor slug (1-200 characters).
            url: Any glassdoor.com employer URL (1-500 characters).
            page: Results page, 1-based. Ten job titles per page; page_count on the
                response is how many pages exist.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.glassdoor.salaries(
            employer_id=employer_id,
            company=company,
            url=url,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "salaries")
        return self._format_response(raw)
