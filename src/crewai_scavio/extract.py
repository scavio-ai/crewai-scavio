"""Scavio Extract tools for CrewAI.

BODY-PRICED / TIER-PRICED. extractCreditCost(mode): normal -> 1 credit (plain
datacenter, 1 upstream), advanced -> 1 credit (render=true, 5 upstream), ultra
-> 2 credits (super=true, 10 upstream). Never emit a flat 'Costs 1 credit'.
Billing is charged ONLY on a 2xx extraction -- a dead link, bot wall or timeout
costs nothing.

- NOT A PLATFORM -- a CORE endpoint (the Tavily-extract analogue). It does NOT
  belong under a per-platform docs dropdown; give it its own top-level docs
  entry.
- mode -> upstream -> credits: normal = plain datacenter (1 -> 1cr), advanced =
  render=true (5 -> 1cr), ultra = super=true (10 -> 2cr). Cost is a function of
  the BODY, not a per-route constant -- the one tier-priced entry in
  scrapedoPlayground, and the reason ScrapedoPgEndpoint.cost is now `number |
  ((b) => number)`.
- format: `html` is the raw page (scrape.do output=raw); `markdown` is
  scrape.do's readability extraction (output=markdown); `text` is that markdown
  flattened LOCALLY by markdownToPlainText -- scrape.do has NO text mode. The
  flattener is CommonMark-conservative so snake_case and inline code survive.
- Billing: charged only on a 2xx extraction. A dead link, bot wall or timeout
  costs nothing (scrape.do never bills a failed scrape).
"""


from typing import Any, Literal, Type

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
            "Fetch tier, and the price-bearing parameter: 'normal' plain datacenter "
            "fetch (1 credit), 'advanced' full browser render (1 credit), 'ultra' the "
            "hardest-target tier (2 credits). Server default 'normal'."
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
            mode: Fetch tier, and the price-bearing parameter: 'normal' plain datacenter
                fetch (1 credit), 'advanced' full browser render (1 credit), 'ultra' the
                hardest-target tier (2 credits).

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
            mode: Fetch tier, and the price-bearing parameter: 'normal' plain datacenter
                fetch (1 credit), 'advanced' full browser render (1 credit), 'ultra' the
                hardest-target tier (2 credits).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.extract(url=url, format=format, mode=mode)
        return self._format_response(raw)
