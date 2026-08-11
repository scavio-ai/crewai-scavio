"""Scavio Indeed tools for CrewAI.

2 credits flat on all four endpoints (INDEED_CREDIT_COST =
scrapedoCreditCost(10), premium per-domain table).

- radius is a closed set (0,5,10,15,25,35,50,100) -- Indeed IGNORES anything
  else and returns the unfiltered set, so a caller asking for 7 miles would be
  billed for a search covering fifty. Upstream default is 50.
- max_age_days is a closed set (1,3,7,14) for the same reason.
- min_salary filters on INDEED'S OWN ESTIMATE for the role, not a posted
  figure, so postings publishing no salary still match. Docs must say this.
- A location-only search (no query) is valid -- every posting in a metro.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_IndeedSearchJobType = Literal[
    "full_time", "part_time", "contract", "temporary", "internship"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _IndeedSearchInput(BaseModel):
    """Input schema for ScavioIndeedSearchTool."""

    query: str | None = Field(
        default=None,
        description=(
            "Job title, keywords or employer (1-500 characters). Required unless "
            "location is given."
        ),
    )
    location: str | None = Field(
        default=None,
        description=(
            "City and state, postal code, state, country, or 'Remote' (1-200 "
            "characters). Valid on its own with no query."
        ),
    )
    page: int | None = Field(
        default=None,
        description="Results page, 1-based. 10 postings per page, 1 call each.",
    )
    radius: Literal[0, 5, 10, 15, 25, 35, 50, 100] | None = Field(
        default=None,
        description=(
            "Search radius in miles around location. Closed set: Indeed IGNORES any "
            "other value and returns the unfiltered set. Upstream default 50."
        ),
    )
    max_age_days: Literal[1, 3, 7, 14] | None = Field(
        default=None,
        description=(
            "Maximum posting age in days. Closed set: Indeed IGNORES any other value "
            "and returns postings of every age."
        ),
    )
    job_type: _IndeedSearchJobType | None = Field(
        default=None,
        description="Employment type filter.",
    )
    min_salary: float | None = Field(
        default=None,
        description=(
            "Minimum annual salary, >= 0. Filters on INDEED'S OWN ESTIMATE for the "
            "role, not a posted figure, so postings publishing no salary still match."
        ),
    )
    remote: bool | None = Field(
        default=None,
        description="Remote postings only.",
    )


class _IndeedJobInput(BaseModel):
    """Input schema for ScavioIndeedJobTool."""

    job_id: str = Field(
        ...,
        description=(
            "16-hex Indeed job key, or any indeed.com URL carrying jk= (/viewjob, "
            "/rc/clk, /pagead/clk)."
        ),
    )


class _IndeedCompanyInput(BaseModel):
    """Input schema for ScavioIndeedCompanyTool."""

    company: str = Field(
        ...,
        description=(
            "indeed.com/cmp/<slug> slug or a full profile URL (1-200 characters); "
            "slugs are untidy, e.g. 'Tata-Consultancy-Services-(tcs)'."
        ),
    )


class _IndeedCompanyReviewsInput(BaseModel):
    """Input schema for ScavioIndeedCompanyReviewsTool."""

    company: str = Field(
        ...,
        description=(
            "indeed.com/cmp/<slug> slug or a full profile URL (1-200 characters)."
        ),
    )
    page: int | None = Field(
        default=None,
        description="Reviews page, 1-based. 20 reviews per page.",
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioIndeedSearchTool(ScavioBaseTool):
    """Indeed job postings: title, employer, rating, location, salary range, job type,
    benefits, posting age, apply route.
    """

    name: str = "Scavio Indeed Search"
    description: str = (
        "Indeed job postings: title, employer, rating, location, salary range, job "
        "type, benefits, posting age, apply route. 10 postings per page. Provide query "
        "or location - a location-only search (every posting in a metro) is valid. "
        "Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _IndeedSearchInput

    def _run(
        self,
        query: str | None = None,
        location: str | None = None,
        page: int | None = None,
        radius: Literal[0, 5, 10, 15, 25, 35, 50, 100] | None = None,
        max_age_days: Literal[1, 3, 7, 14] | None = None,
        job_type: _IndeedSearchJobType | None = None,
        min_salary: float | None = None,
        remote: bool | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/indeed/search synchronously.

        Args:
            query: Job title, keywords or employer (1-500 characters).
            location: City and state, postal code, state, country, or 'Remote' (1-200
                characters).
            page: Results page, 1-based. 10 postings per page, 1 call each.
            radius: Search radius in miles around location.
            max_age_days: Maximum posting age in days. Closed set: Indeed IGNORES any
                other value and returns postings of every age.
            job_type: Employment type filter.
            min_salary: Minimum annual salary, >= 0. Filters on INDEED'S OWN ESTIMATE
                for the role, not a posted figure, so postings publishing no salary
                still match.
            remote: Remote postings only.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.indeed.search(
            query=query,
            location=location,
            page=page,
            radius=radius,
            max_age_days=max_age_days,
            job_type=job_type,
            min_salary=min_salary,
            remote=remote,
        )
        raw = self._truncate_nested(raw, "data", "jobs")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str | None = None,
        location: str | None = None,
        page: int | None = None,
        radius: Literal[0, 5, 10, 15, 25, 35, 50, 100] | None = None,
        max_age_days: Literal[1, 3, 7, 14] | None = None,
        job_type: _IndeedSearchJobType | None = None,
        min_salary: float | None = None,
        remote: bool | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/indeed/search asynchronously.

        Args:
            query: Job title, keywords or employer (1-500 characters).
            location: City and state, postal code, state, country, or 'Remote' (1-200
                characters).
            page: Results page, 1-based. 10 postings per page, 1 call each.
            radius: Search radius in miles around location.
            max_age_days: Maximum posting age in days. Closed set: Indeed IGNORES any
                other value and returns postings of every age.
            job_type: Employment type filter.
            min_salary: Minimum annual salary, >= 0. Filters on INDEED'S OWN ESTIMATE
                for the role, not a posted figure, so postings publishing no salary
                still match.
            remote: Remote postings only.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.indeed.search(
            query=query,
            location=location,
            page=page,
            radius=radius,
            max_age_days=max_age_days,
            job_type=job_type,
            min_salary=min_salary,
            remote=remote,
        )
        raw = self._truncate_nested(raw, "data", "jobs")
        return self._format_response(raw)


class ScavioIndeedJobTool(ScavioBaseTool):
    """One Indeed posting in full: description text and HTML, structured salary,
    employment types, benefits, geocoded address, employer rating, applicant count,
    original ATS link.
    """

    name: str = "Scavio Indeed Job"
    description: str = (
        "One Indeed posting in full: description text and HTML, structured salary, "
        "employment types, benefits, geocoded address, employer rating, applicant "
        "count, original ATS link. An unknown job key is a real 404 that is still "
        "billed. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _IndeedJobInput

    def _run(self, job_id: str, **kwargs: Any) -> str:
        """Call /api/v1/indeed/job synchronously.

        Args:
            job_id: 16-hex Indeed job key, or any indeed.com URL carrying jk= (/viewjob,
                /rc/clk, /pagead/clk).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.indeed.job(job_id=job_id)
        return self._format_response(raw)

    async def _arun(self, job_id: str, **kwargs: Any) -> str:
        """Call /api/v1/indeed/job asynchronously.

        Args:
            job_id: 16-hex Indeed job key, or any indeed.com URL carrying jk= (/viewjob,
                /rc/clk, /pagead/clk).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.indeed.job(job_id=job_id)
        return self._format_response(raw)


class ScavioIndeedCompanyTool(ScavioBaseTool):
    """Indeed employer profile: description, industry, HQ, size, revenue, CEO approval,
    overall and per-category ratings, reported salaries, open roles, locations.
    """

    name: str = "Scavio Indeed Company"
    description: str = (
        "Indeed employer profile: description, industry, HQ, size, revenue, CEO "
        "approval, overall and per-category ratings, reported salaries, open roles, "
        "locations. An unknown slug is a real 404 that is still billed. Costs 2 "
        "credits."
    )
    args_schema: Type[BaseModel] = _IndeedCompanyInput

    def _run(self, company: str, **kwargs: Any) -> str:
        """Call /api/v1/indeed/company synchronously.

        Args:
            company: indeed.com/cmp/<slug> slug or a full profile URL (1-200
                characters); slugs are untidy, e.g. 'Tata-Consultancy-Services-(tcs)'.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.indeed.company(company=company)
        return self._format_response(raw)

    async def _arun(self, company: str, **kwargs: Any) -> str:
        """Call /api/v1/indeed/company asynchronously.

        Args:
            company: indeed.com/cmp/<slug> slug or a full profile URL (1-200
                characters); slugs are untidy, e.g. 'Tata-Consultancy-Services-(tcs)'.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.indeed.company(company=company)
        return self._format_response(raw)


class ScavioIndeedCompanyReviewsTool(ScavioBaseTool):
    """Indeed employee reviews, 20 per page, with per-category ratings, pros/cons,
    reviewer job title and location, plus aggregated sentiment and
    topic/location/job-title breakdowns.
    """

    name: str = "Scavio Indeed Company Reviews"
    description: str = (
        "Indeed employee reviews, 20 per page, with per-category ratings, pros/cons, "
        "reviewer job title and location, plus aggregated sentiment and "
        "topic/location/job-title breakdowns. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _IndeedCompanyReviewsInput

    def _run(self, company: str, page: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/indeed/company/reviews synchronously.

        Args:
            company: indeed.com/cmp/<slug> slug or a full profile URL (1-200
                characters).
            page: Reviews page, 1-based. 20 reviews per page.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.indeed.company_reviews(company=company, page=page)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(self, company: str, page: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/indeed/company/reviews asynchronously.

        Args:
            company: indeed.com/cmp/<slug> slug or a full profile URL (1-200
                characters).
            page: Reviews page, 1-based. 20 reviews per page.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.indeed.company_reviews(company=company, page=page)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
