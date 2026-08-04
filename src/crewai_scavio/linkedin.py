"""Scavio LinkedIn tools for CrewAI.

Nine live endpoints across three credit tiers: profile, company and single-post
reads cost 1 credit, the paginated list endpoints cost 10 per page, and job
detail costs 30 -- the most expensive call in the whole Scavio API. Every tool
below states its own cost.

Five LinkedIn paths (person/contact, company/people, company/jobs,
search/people, search/posts) were retired by the upstream provider and now
answer HTTP 410 unbilled. They are deliberately NOT exposed as tools: an agent
should never be able to plan a step that cannot succeed. Where a substitute
exists it is named in the replacement tool's description --
``ScavioLinkedInCompanyTool`` returns ``featured_employees``, and
``ScavioLinkedInSearchJobsTool`` takes a company name as its search term.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


_CURSOR_DESCRIPTION = (
    "Opaque cursor -- pass next_cursor from a previous response. Omit for the "
    "first page."
)
_USERNAME_DESCRIPTION = (
    "Public identifier / vanity handle from the profile URL "
    "(e.g. 'williamhgates')."
)
_COMPANY_DESCRIPTION = "Company universal name / slug (e.g. 'microsoft')."


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _PersonInput(BaseModel):
    """Input schema shared by the person and person-about tools."""

    username: str | None = Field(
        default=None, description=_USERNAME_DESCRIPTION
    )
    url: str | None = Field(
        default=None,
        description="Full LinkedIn profile URL, as an alternative to username.",
    )


class _PersonPostsInput(BaseModel):
    """Input schema for ScavioLinkedInPersonPostsTool."""

    username: str | None = Field(
        default=None, description=_USERNAME_DESCRIPTION
    )
    url: str | None = Field(
        default=None,
        description="Full LinkedIn profile URL, as an alternative to username.",
    )
    type: Literal["posts", "comments", "reactions"] | None = Field(
        default=None,
        description=(
            "Which feed to return: the member's own posts (default), posts "
            "they commented on, or posts they reacted to."
        ),
    )
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class _CompanyInput(BaseModel):
    """Input schema for ScavioLinkedInCompanyTool."""

    company: str | None = Field(default=None, description=_COMPANY_DESCRIPTION)
    url: str | None = Field(
        default=None,
        description="Full LinkedIn company URL, as an alternative to company.",
    )


class _CompanyPostsInput(BaseModel):
    """Input schema for ScavioLinkedInCompanyPostsTool."""

    company: str | None = Field(default=None, description=_COMPANY_DESCRIPTION)
    url: str | None = Field(
        default=None,
        description="Full LinkedIn company URL, as an alternative to company.",
    )
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class _SearchJobsInput(BaseModel):
    """Input schema for ScavioLinkedInSearchJobsTool."""

    search: str = Field(
        ...,
        description=(
            "Search keyword. The field is named 'search', not 'query' or "
            "'keywords'."
        ),
    )
    location: str | None = Field(
        default=None,
        description="Geographic filter; omit to search everywhere.",
    )
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class _JobInput(BaseModel):
    """Input schema for ScavioLinkedInJobTool."""

    job_id: str | None = Field(
        default=None, description="Job id (e.g. '4415427228')."
    )
    url: str | None = Field(
        default=None,
        description="Full LinkedIn job URL, as an alternative to job_id.",
    )


class _PostInput(BaseModel):
    """Input schema for ScavioLinkedInPostTool."""

    post_id: str | None = Field(
        default=None,
        description=(
            "Post id or activity urn -- a bare id, urn:li:activity:<id>, "
            "urn:li:ugcPost:<id> or urn:li:share:<id> all work."
        ),
    )
    url: str | None = Field(
        default=None,
        description="Full LinkedIn post URL, as an alternative to post_id.",
    )


class _PostCommentsInput(BaseModel):
    """Input schema for ScavioLinkedInPostCommentsTool."""

    post_id: str | None = Field(
        default=None, description="Post id or activity urn."
    )
    url: str | None = Field(
        default=None,
        description="Full LinkedIn post URL, as an alternative to post_id.",
    )
    page: int | None = Field(
        default=None,
        description=(
            "1-based page number (default 1). This endpoint pages by integer, "
            "not by cursor."
        ),
    )


# ---------------------------------------------------------------------------
# 1. Person
# ---------------------------------------------------------------------------


class ScavioLinkedInPersonTool(ScavioBaseTool):
    """Fetch a full LinkedIn member profile.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio LinkedIn Person"
    description: str = (
        "Fetch a full LinkedIn member profile by username or profile URL. "
        "Returns full_name, headline, about, location, follower_count, "
        "connection_count, current_company, experiences, educations, "
        "honors_and_awards, bio_links and similar_profiles. Contact details "
        "such as email and phone are not available from any Scavio endpoint. "
        "Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _PersonInput

    def _run(
        self,
        username: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a member profile synchronously.

        Args:
            username: Public identifier.
            url: Full profile URL.

        Returns:
            JSON-serialised profile.
        """
        raw = self.client.linkedin.person(username=username, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a member profile asynchronously.

        Args:
            username: Public identifier.
            url: Full profile URL.

        Returns:
            JSON-serialised profile.
        """
        raw = await self.async_client.linkedin.person(
            username=username, url=url
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 2. Person About
# ---------------------------------------------------------------------------


class ScavioLinkedInPersonAboutTool(ScavioBaseTool):
    """Fetch the about/overview block of a LinkedIn member profile.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio LinkedIn Person About"
    description: str = (
        "Fetch just the about/overview block of a LinkedIn profile: about, "
        "headline, education_summary, experiences, educations, "
        "honors_and_awards and bio_links. Same upstream call as the full "
        "person tool, shaped down. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _PersonInput

    def _run(
        self,
        username: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch the about block synchronously.

        Args:
            username: Public identifier.
            url: Full profile URL.

        Returns:
            JSON-serialised about block.
        """
        raw = self.client.linkedin.person_about(username=username, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch the about block asynchronously.

        Args:
            username: Public identifier.
            url: Full profile URL.

        Returns:
            JSON-serialised about block.
        """
        raw = await self.async_client.linkedin.person_about(
            username=username, url=url
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 3. Person Posts
# ---------------------------------------------------------------------------


class ScavioLinkedInPersonPostsTool(ScavioBaseTool):
    """Fetch a member's posts, comments or reactions feed.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio LinkedIn Person Posts"
    description: str = (
        "Fetch a LinkedIn member's posts, or the posts they commented on or "
        "reacted to, via the type parameter. 50 per page under data.data; "
        "paginate with next_cursor. Costs 10 credits per page."
    )
    args_schema: Type[BaseModel] = _PersonPostsInput

    def _run(
        self,
        username: str | None = None,
        url: str | None = None,
        type: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a member feed synchronously.

        Args:
            username: Public identifier.
            url: Full profile URL.
            type: 'posts', 'comments' or 'reactions'.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised feed page.
        """
        raw = self.client.linkedin.person_posts(
            username=username, url=url, type=type, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "data")
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        url: str | None = None,
        type: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a member feed asynchronously.

        Args:
            username: Public identifier.
            url: Full profile URL.
            type: 'posts', 'comments' or 'reactions'.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised feed page.
        """
        raw = await self.async_client.linkedin.person_posts(
            username=username, url=url, type=type, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "data")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 4. Company
# ---------------------------------------------------------------------------


class ScavioLinkedInCompanyTool(ScavioBaseTool):
    """Fetch a LinkedIn company profile.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio LinkedIn Company"
    description: str = (
        "Fetch a LinkedIn company profile by slug or company URL. Returns "
        "name, description, about, website, industries, specialties, "
        "company_size, employee_count, follower_count, headquarters, "
        "locations, similar_companies, affiliated_companies and "
        "recent_updates. featured_employees is a 4-6 person staff sample and "
        "is the only employee data available -- the employee directory was "
        "retired upstream. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _CompanyInput

    def _run(
        self,
        company: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a company profile synchronously.

        Args:
            company: Company slug.
            url: Full company URL.

        Returns:
            JSON-serialised company profile.
        """
        raw = self.client.linkedin.company(company=company, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        company: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a company profile asynchronously.

        Args:
            company: Company slug.
            url: Full company URL.

        Returns:
            JSON-serialised company profile.
        """
        raw = await self.async_client.linkedin.company(
            company=company, url=url
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 5. Company Posts
# ---------------------------------------------------------------------------


class ScavioLinkedInCompanyPostsTool(ScavioBaseTool):
    """Fetch a company's recent posts.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio LinkedIn Company Posts"
    description: str = (
        "Fetch a LinkedIn company's recent posts by slug or company URL. 50 "
        "per page under data.data; paginate with next_cursor. Costs 10 "
        "credits per page."
    )
    args_schema: Type[BaseModel] = _CompanyPostsInput

    def _run(
        self,
        company: str | None = None,
        url: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a company feed synchronously.

        Args:
            company: Company slug.
            url: Full company URL.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised feed page.
        """
        raw = self.client.linkedin.company_posts(
            company=company, url=url, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "data")
        return self._format_response(raw)

    async def _arun(
        self,
        company: str | None = None,
        url: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a company feed asynchronously.

        Args:
            company: Company slug.
            url: Full company URL.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised feed page.
        """
        raw = await self.async_client.linkedin.company_posts(
            company=company, url=url, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "data")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 6. Search Jobs
# ---------------------------------------------------------------------------


class ScavioLinkedInSearchJobsTool(ScavioBaseTool):
    """Search LinkedIn job listings.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio LinkedIn Search Jobs"
    description: str = (
        "Search LinkedIn job listings by keyword and optional location. The "
        "keyword field is named 'search'. Pass a company name as the search "
        "term to approximate a per-company listing. 25 per page under "
        "data.data; the provider rotates its result set, so pages overlap and "
        "repeat calls differ -- dedupe by job id. Costs 10 credits per page."
    )
    args_schema: Type[BaseModel] = _SearchJobsInput

    def _run(
        self,
        search: str,
        location: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Search job listings synchronously.

        Args:
            search: Search keyword.
            location: Geographic filter.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised job listing page.
        """
        raw = self.client.linkedin.search_jobs(
            search=search, location=location, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "data")
        return self._format_response(raw)

    async def _arun(
        self,
        search: str,
        location: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Search job listings asynchronously.

        Args:
            search: Search keyword.
            location: Geographic filter.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised job listing page.
        """
        raw = await self.async_client.linkedin.search_jobs(
            search=search, location=location, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "data")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 7. Job
# ---------------------------------------------------------------------------


class ScavioLinkedInJobTool(ScavioBaseTool):
    """Fetch full detail for a single LinkedIn job listing.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio LinkedIn Job"
    description: str = (
        "Fetch full detail for a single LinkedIn job listing by job_id or "
        "job URL: description, employment_type, experience_level, skills, "
        "benefits, salary, applicant_count and the hiring company. Costs 30 "
        "credits -- the most expensive call in the Scavio API, so fetch "
        "detail only for listings you have already shortlisted. Roughly one "
        "job id in five from job search has no detail record upstream and "
        "returns an unbilled 404; skip those rather than retrying."
    )
    args_schema: Type[BaseModel] = _JobInput

    def _run(
        self,
        job_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch job detail synchronously.

        Args:
            job_id: Job id.
            url: Full job URL.

        Returns:
            JSON-serialised job detail.
        """
        raw = self.client.linkedin.job(job_id=job_id, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        job_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch job detail asynchronously.

        Args:
            job_id: Job id.
            url: Full job URL.

        Returns:
            JSON-serialised job detail.
        """
        raw = await self.async_client.linkedin.job(job_id=job_id, url=url)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 8. Post
# ---------------------------------------------------------------------------


class ScavioLinkedInPostTool(ScavioBaseTool):
    """Fetch a single LinkedIn post.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio LinkedIn Post"
    description: str = (
        "Fetch a single LinkedIn post by post_id, activity urn or post URL. "
        "Returns text, url, created_at, hashtags, images, videos, num_likes, "
        "num_comments, tagged_companies, tagged_people, the author block and "
        "top_comments (the visible sample). Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _PostInput

    def _run(
        self,
        post_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a post synchronously.

        Args:
            post_id: Post id or activity urn.
            url: Full post URL.

        Returns:
            JSON-serialised post.
        """
        raw = self.client.linkedin.post(post_id=post_id, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        post_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch a post asynchronously.

        Args:
            post_id: Post id or activity urn.
            url: Full post URL.

        Returns:
            JSON-serialised post.
        """
        raw = await self.async_client.linkedin.post(post_id=post_id, url=url)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 9. Post Comments
# ---------------------------------------------------------------------------


class ScavioLinkedInPostCommentsTool(ScavioBaseTool):
    """Fetch comments on a LinkedIn post, with their replies.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio LinkedIn Post Comments"
    description: str = (
        "Fetch comments on a LinkedIn post, each with its replies. This is "
        "the one LinkedIn endpoint that pages by a 1-based integer page "
        "rather than a cursor, and page size varies upstream (8-10), so keep "
        "paging until a page comes back empty rather than dividing by a "
        "fixed size. total is only returned on page 1. Costs 10 credits per "
        "page."
    )
    args_schema: Type[BaseModel] = _PostCommentsInput

    def _run(
        self,
        post_id: str | None = None,
        url: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch post comments synchronously.

        Args:
            post_id: Post id or activity urn.
            url: Full post URL.
            page: 1-based page number.

        Returns:
            JSON-serialised comment page.
        """
        raw = self.client.linkedin.post_comments(
            post_id=post_id, url=url, page=page
        )
        raw = self._truncate_nested(raw, "data", "data")
        return self._format_response(raw)

    async def _arun(
        self,
        post_id: str | None = None,
        url: str | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch post comments asynchronously.

        Args:
            post_id: Post id or activity urn.
            url: Full post URL.
            page: 1-based page number.

        Returns:
            JSON-serialised comment page.
        """
        raw = await self.async_client.linkedin.post_comments(
            post_id=post_id, url=url, page=page
        )
        raw = self._truncate_nested(raw, "data", "data")
        return self._format_response(raw)
