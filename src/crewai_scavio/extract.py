"""Scavio Extract tools for CrewAI.

Extract is a CORE endpoint family, not a platform: it reads any URL.

- ``ScavioExtractTool`` reads one page. Tier-priced by mode: normal 1 credit,
  advanced 1, ultra 2. Only a successful extraction is billed - a dead link,
  bot wall or timeout costs nothing. Never advertise a flat price.
- ``ScavioExtractMapTool`` lists a site's page URLs (1 credit on normal; up to
  2 on advanced, up to 10 on ultra, priced by what the call needed).
- ``ScavioExtractCrawlTool`` / ``ScavioExtractBatchTool`` start a background
  job, wait up to ``wait_seconds`` (default 45) for it to finish and return its
  status with the first page of results either way. A job still running when
  the wait ends keeps going; read it with ``ScavioExtractCrawlStatusTool`` /
  ``ScavioExtractBatchStatusTool`` (free). Jobs bill per SUCCESSFUL page at
  extract's price for the mode; failed and skipped pages are free.
"""

import asyncio
import time
from typing import Any, Callable, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool

# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _ExtractInput(BaseModel):
    """Input schema for ScavioExtractTool."""

    url: str = Field(
        ...,
        description=(
            "Page to read (1-2048 characters). http(s) only; a bare host is upgraded "
            "to https, and loopback, private, link-local and metadata hosts are "
            "rejected with a 400."
        ),
    )
    format: Literal["html", "markdown", "text"] | None = Field(
        default=None,
        description=(
            "Output format: 'html' is the raw page, 'markdown' a readability "
            "extraction, 'text' that markdown flattened to plain text (server default "
            "'markdown')."
        ),
    )
    mode: Literal["normal", "advanced", "ultra"] | None = Field(
        default=None,
        description=(
            "Fetch tier, and the price-bearing parameter: 'normal' is the standard "
            "fetch (1 credit), 'advanced' renders JavaScript-built pages (1 credit), "
            "'ultra' reaches the hardest pages (2 credits). Server default 'normal'."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioExtractTool(ScavioBaseTool):
    """Read any URL and get the page back as raw HTML, readability Markdown or plain
    text: { url, format, mode, content, content_length }.
    """

    name: str = "Scavio Extract"
    description: str = (
        "Read any URL and get the page back as raw HTML, readability Markdown or plain "
        "text: { url, format, mode, content, content_length }. Tier-priced by mode: "
        "'normal' and 'advanced' cost 1 credit, 'ultra' costs 2. Only a successful "
        "extraction is billed - a dead link, bot wall or timeout costs nothing."
    )
    args_schema: Type[BaseModel] = _ExtractInput

    def _run(
        self,
        url: str,
        format: Literal["html", "markdown", "text"] | None = None,
        mode: Literal["normal", "advanced", "ultra"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/extract synchronously.

        Args:
            url: Page to read (1-2048 characters). http(s) only; a bare host is upgraded
                to https, and loopback, private, link-local and metadata hosts are
                rejected with a 400.
            format: Output format: 'html' is the raw page, 'markdown' a readability
                extraction, 'text' that markdown flattened to plain text (server default
                'markdown').
            mode: Fetch tier, and the price-bearing parameter: 'normal' is the standard
                fetch (1 credit), 'advanced' renders JavaScript-built pages (1 credit),
                'ultra' reaches the hardest pages (2 credits).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.extract(url=url, format=format, mode=mode)
        return self._format_response(raw)

    async def _arun(
        self,
        url: str,
        format: Literal["html", "markdown", "text"] | None = None,
        mode: Literal["normal", "advanced", "ultra"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/extract asynchronously.

        Args:
            url: Page to read (1-2048 characters). http(s) only; a bare host is upgraded
                to https, and loopback, private, link-local and metadata hosts are
                rejected with a 400.
            format: Output format: 'html' is the raw page, 'markdown' a readability
                extraction, 'text' that markdown flattened to plain text (server default
                'markdown').
            mode: Fetch tier, and the price-bearing parameter: 'normal' is the standard
                fetch (1 credit), 'advanced' renders JavaScript-built pages (1 credit),
                'ultra' reaches the hardest pages (2 credits).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.extract(url=url, format=format, mode=mode)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# Map, crawl and batch
# ---------------------------------------------------------------------------

JOB_TERMINAL_STATUSES = frozenset({"completed", "failed", "cancelled"})
JOB_POLL_INTERVAL = 3.0
JOB_MAX_WAIT = 300
JOB_DEFAULT_WAIT = 45
JOB_DEFAULT_LIMIT = 10

Mode = Literal["normal", "advanced", "ultra"]
Format = Literal["html", "markdown", "text"]

_MODE_DESCRIPTION = (
    "Fetch tier: 'normal' is the standard fetch, 'advanced' renders JavaScript-built "
    "pages, 'ultra' reaches the hardest pages. Server default 'normal'."
)
_PATHS_DESCRIPTION = (
    "Path globs (max 20). '*' matches within one path segment, '**' across "
    "segments, e.g. ['/blog/**']."
)
_JOB_PRICE = (
    "Billed per SUCCESSFUL page at extract's price for the mode: normal and advanced "
    "1 credit, ultra 2 credits. Failed and skipped pages are free, and the job "
    "stops cleanly if the balance runs out."
)


def _clean(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}


def _wait_field() -> Any:
    return Field(
        default=JOB_DEFAULT_WAIT,
        ge=0,
        le=JOB_MAX_WAIT,
        description=(
            "Seconds to wait for the job to finish, 0-300 (default 45). 0 returns the "
            "job id at once. A job still running when the wait ends keeps going; read "
            "it later with its status tool."
        ),
    )


def _limit_field() -> Any:
    return Field(
        default=JOB_DEFAULT_LIMIT,
        ge=1,
        le=100,
        description="Results per response, 1-100 (default 10); page with next_cursor.",
    )


class _ExtractMapInput(BaseModel):
    """Input schema for ScavioExtractMapTool."""

    url: str = Field(
        ..., description="The site to map. A bare host is upgraded to https."
    )
    search: str | None = Field(
        default=None,
        description="Only return URLs containing every word of this text.",
    )
    limit: int | None = Field(
        default=None,
        ge=1,
        le=5000,
        description=(
            "Maximum links to return, 1-5000. Default 1000 (or the plan's limit if "
            "lower: "
            "Free 500, PAYG 1,000, paid plans 5,000)."
        ),
    )
    sitemap: Literal["include", "only", "skip"] | None = Field(
        default=None,
        description=(
            "'include' (default) combines the site's sitemaps with the start page's "
            "links; 'only' uses sitemaps alone; 'skip' uses page links alone."
        ),
    )
    include_subdomains: bool | None = Field(
        default=None, description="Also return URLs on subdomains. Default false."
    )
    include_paths: list[str] | None = Field(
        default=None, description="Keep only URLs matching these. " + _PATHS_DESCRIPTION
    )
    exclude_paths: list[str] | None = Field(
        default=None, description="Drop URLs matching these. " + _PATHS_DESCRIPTION
    )
    ignore_query_parameters: bool | None = Field(
        default=None,
        description="Treat URLs differing only by query string as one. Default true.",
    )
    mode: Mode | None = Field(default=None, description=_MODE_DESCRIPTION)


class _ExtractCrawlInput(BaseModel):
    """Input schema for ScavioExtractCrawlTool."""

    url: str = Field(
        ...,
        description="Where the crawl starts. Only pages on the same site are crawled.",
    )
    max_pages: int | None = Field(
        default=None,
        ge=1,
        le=10000,
        description=(
            "Maximum pages to fetch. Default 100. Plan limits: Free 10, PAYG 100, "
            "Project 500, Bootstrap 2,000, Startup 5,000, Growth 10,000."
        ),
    )
    max_depth: int | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Links away from the start page to follow, 0-10 (default 3).",
    )
    include_paths: list[str] | None = Field(
        default=None,
        description="Crawl only paths matching these. " + _PATHS_DESCRIPTION,
    )
    exclude_paths: list[str] | None = Field(
        default=None, description="Skip paths matching these. " + _PATHS_DESCRIPTION
    )
    allow_subdomains: bool | None = Field(
        default=None, description="Also crawl subdomains of the site. Default false."
    )
    ignore_query_parameters: bool | None = Field(
        default=None,
        description="Treat URLs differing only by query as one page. Default true.",
    )
    sitemap: Literal["include", "skip", "only"] | None = Field(
        default=None,
        description=(
            "'include' (default) also starts from the site's sitemap; 'skip' follows "
            "links only; 'only' fetches sitemap pages without following links."
        ),
    )
    format: Format | None = Field(
        default=None,
        description="Format for each page: html, markdown (default) or text.",
    )
    mode: Mode | None = Field(default=None, description=_MODE_DESCRIPTION)
    wait_seconds: int = _wait_field()
    limit: int = _limit_field()


class _ExtractBatchInput(BaseModel):
    """Input schema for ScavioExtractBatchTool."""

    urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description=(
            "The pages to extract (duplicates removed). Plan limits: Free 10, PAYG 50, "
            "Project 100, Bootstrap 500, Startup and Growth 1,000."
        ),
    )
    format: Format | None = Field(
        default=None,
        description="Format for each page: html, markdown (default) or text.",
    )
    mode: Mode | None = Field(default=None, description=_MODE_DESCRIPTION)
    wait_seconds: int = _wait_field()
    limit: int = _limit_field()


class _ExtractJobStatusInput(BaseModel):
    """Input schema for the crawl and batch status tools."""

    id: str = Field(
        ..., description="The job id returned when the job was started (data.id)."
    )
    cursor: str | None = Field(
        default=None, description="next_cursor from the previous response."
    )
    limit: int = _limit_field()
    status: Literal["succeeded", "failed", "skipped"] | None = Field(
        default=None, description="Only results with this status."
    )
    include_content: bool | None = Field(
        default=None,
        description="False lists results without their page content. Default true.",
    )


def _job_id(created: dict[str, Any]) -> str | None:
    data = created.get("data")
    return data.get("id") if isinstance(data, dict) else None


def _finished(payload: dict[str, Any]) -> bool:
    data = payload.get("data")
    return isinstance(data, dict) and data.get("status") in JOB_TERMINAL_STATUSES


def _wait_sync(
    status_fn: Callable[..., dict[str, Any]],
    created: dict[str, Any],
    wait_seconds: int,
    limit: int,
) -> dict[str, Any]:
    """Poll a started job until it finishes or the wait runs out, then read it."""
    job_id = _job_id(created)
    if not job_id or wait_seconds <= 0:
        return created
    deadline = time.monotonic() + min(wait_seconds, JOB_MAX_WAIT)
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(JOB_POLL_INTERVAL, remaining))
        if _finished(status_fn(job_id, limit=1, include_content=False)):
            break
    return status_fn(job_id, limit=limit)


async def _wait_async(
    status_fn: Callable[..., Any],
    created: dict[str, Any],
    wait_seconds: int,
    limit: int,
) -> dict[str, Any]:
    """Async twin of :func:`_wait_sync`."""
    job_id = _job_id(created)
    if not job_id or wait_seconds <= 0:
        return created
    deadline = time.monotonic() + min(wait_seconds, JOB_MAX_WAIT)
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        await asyncio.sleep(min(JOB_POLL_INTERVAL, remaining))
        if _finished(await status_fn(job_id, limit=1, include_content=False)):
            break
    return await status_fn(job_id, limit=limit)


class ScavioExtractMapTool(ScavioBaseTool):
    """List a website's page URLs from its sitemaps and start page."""

    name: str = "Scavio Map Website"
    description: str = (
        "List a website's page URLs, gathered from its sitemaps and its start page, "
        "deduplicated, filtered by path or search words and limited: { url, links: "
        "[{ url, source, lastmod }], total_found, returned, truncated }. Pages the "
        "site's robots.txt disallows are left out. Use it to find the right pages "
        "before extracting or crawling. Tier-priced: 1 credit on mode 'normal'; "
        "'advanced' costs up to 2 credits and 'ultra' up to 10, priced by what the "
        "call needed."
    )
    args_schema: Type[BaseModel] = _ExtractMapInput

    def _run(self, url: str, **kwargs: Any) -> str:
        """Call POST /api/v1/extract/map synchronously.

        Returns:
            JSON-serialised { url, links, total_found, returned, truncated }.
        """
        return self._format_response(self.client.extract.map(url, **_clean(kwargs)))

    async def _arun(self, url: str, **kwargs: Any) -> str:
        """Call POST /api/v1/extract/map asynchronously.

        Returns:
            JSON-serialised { url, links, total_found, returned, truncated }.
        """
        raw = await self.async_client.extract.map(url, **_clean(kwargs))
        return self._format_response(raw)


class ScavioExtractCrawlTool(ScavioBaseTool):
    """Crawl a website from one URL; every page as Markdown, text or HTML."""

    name: str = "Scavio Crawl Website"
    description: str = (
        "Crawl a website from one start URL: same-site pages are discovered and "
        "extracted breadth-first within the page, depth and path limits, each as "
        "Markdown, text or HTML. Pages the site's robots.txt disallows are skipped. "
        "Waits up to wait_seconds (default 45) and returns { id, status, pages, "
        "credits_used, results, next_cursor }; if status is still queued or running, "
        "use Scavio Crawl Status with the id later. Tier-priced: " + _JOB_PRICE
    )
    args_schema: Type[BaseModel] = _ExtractCrawlInput

    def _run(
        self,
        url: str,
        wait_seconds: int = JOB_DEFAULT_WAIT,
        limit: int = JOB_DEFAULT_LIMIT,
        **kwargs: Any,
    ) -> str:
        """Start a crawl (POST /api/v1/extract/crawl) and wait for it.

        Polls GET /api/v1/extract/crawl/{id} until the crawl finishes or
        ``wait_seconds`` pass, then returns the latest status page.
        """
        created = self.client.extract.crawl(url, **_clean(kwargs))
        raw = _wait_sync(self.client.extract.crawl_status, created, wait_seconds, limit)
        return self._format_response(raw)

    async def _arun(
        self,
        url: str,
        wait_seconds: int = JOB_DEFAULT_WAIT,
        limit: int = JOB_DEFAULT_LIMIT,
        **kwargs: Any,
    ) -> str:
        """Start a crawl (POST /api/v1/extract/crawl) and wait for it, asynchronously.

        Polls GET /api/v1/extract/crawl/{id} until the crawl finishes or
        ``wait_seconds`` pass, then returns the latest status page.
        """
        created = await self.async_client.extract.crawl(url, **_clean(kwargs))
        raw = await _wait_async(
            self.async_client.extract.crawl_status, created, wait_seconds, limit
        )
        return self._format_response(raw)


class ScavioExtractCrawlStatusTool(ScavioBaseTool):
    """A crawl's progress and page results, paged by cursor. Free."""

    name: str = "Scavio Crawl Status"
    description: str = (
        "Read a crawl's progress and its page results by job id, paged by cursor: "
        "{ status, stopped_reason, pages, credits_used, results: [{ url, status, "
        "content }], next_cursor }. Results are kept for 3 days after the crawl "
        "finishes. Free: costs 0 credits."
    )
    args_schema: Type[BaseModel] = _ExtractJobStatusInput

    def _run(self, id: str, **kwargs: Any) -> str:
        """Call GET /api/v1/extract/crawl/{id} synchronously."""
        return self._format_response(
            self.client.extract.crawl_status(id, **_clean(kwargs))
        )

    async def _arun(self, id: str, **kwargs: Any) -> str:
        """Call GET /api/v1/extract/crawl/{id} asynchronously."""
        raw = await self.async_client.extract.crawl_status(id, **_clean(kwargs))
        return self._format_response(raw)


class ScavioExtractBatchTool(ScavioBaseTool):
    """Extract a list of URLs in one job."""

    name: str = "Scavio Batch Extract"
    description: str = (
        "Extract a list of URLs (up to 1,000, plan-limited) in one job, each returned "
        "as Markdown, text or HTML exactly like Scavio Extract, in input order. Waits "
        "up to wait_seconds (default 45) and returns { id, status, pages, "
        "credits_used, results, next_cursor }; if status is still queued or running, "
        "use Scavio Batch Status with the id later. Tier-priced: " + _JOB_PRICE
    )
    args_schema: Type[BaseModel] = _ExtractBatchInput

    def _run(
        self,
        urls: list[str],
        wait_seconds: int = JOB_DEFAULT_WAIT,
        limit: int = JOB_DEFAULT_LIMIT,
        **kwargs: Any,
    ) -> str:
        """Start a batch (POST /api/v1/extract/batch) and wait for it.

        Polls GET /api/v1/extract/batch/{id} until the batch finishes or
        ``wait_seconds`` pass, then returns the latest status page.
        """
        created = self.client.extract.batch(urls, **_clean(kwargs))
        raw = _wait_sync(self.client.extract.batch_status, created, wait_seconds, limit)
        return self._format_response(raw)

    async def _arun(
        self,
        urls: list[str],
        wait_seconds: int = JOB_DEFAULT_WAIT,
        limit: int = JOB_DEFAULT_LIMIT,
        **kwargs: Any,
    ) -> str:
        """Start a batch (POST /api/v1/extract/batch) and wait for it, asynchronously.

        Polls GET /api/v1/extract/batch/{id} until the batch finishes or
        ``wait_seconds`` pass, then returns the latest status page.
        """
        created = await self.async_client.extract.batch(urls, **_clean(kwargs))
        raw = await _wait_async(
            self.async_client.extract.batch_status, created, wait_seconds, limit
        )
        return self._format_response(raw)


class ScavioExtractBatchStatusTool(ScavioBaseTool):
    """A batch's progress and page results, paged by cursor. Free."""

    name: str = "Scavio Batch Status"
    description: str = (
        "Read a batch extract's progress and its page results by job id, paged by "
        "cursor: { status, pages, credits_used, results: [{ url, status, content }], "
        "next_cursor }. Results are kept for 3 days after the batch finishes. Free: "
        "costs 0 credits."
    )
    args_schema: Type[BaseModel] = _ExtractJobStatusInput

    def _run(self, id: str, **kwargs: Any) -> str:
        """Call GET /api/v1/extract/batch/{id} synchronously."""
        return self._format_response(
            self.client.extract.batch_status(id, **_clean(kwargs))
        )

    async def _arun(self, id: str, **kwargs: Any) -> str:
        """Call GET /api/v1/extract/batch/{id} asynchronously."""
        raw = await self.async_client.extract.batch_status(id, **_clean(kwargs))
        return self._format_response(raw)
