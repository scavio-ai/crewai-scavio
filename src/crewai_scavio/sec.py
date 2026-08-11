"""Scavio SEC EDGAR tools for CrewAI.

1 credit flat on all six endpoints (SEC_CREDIT_COST = scrapedoCreditCost(1)) --
official free JSON API. include_history can buy up to 10 upstream fetches and
is DELIBERATELY still 1 credit.

- LOOKUP FIRST. Callers hold a ticker (AAPL); the API is keyed by CIK
  (0000320193). Same problem class as TripAdvisor geo_id. Docs must lead with
  /sec/lookup. (Both cik and ticker fields accept either spelling, which
  softens it but does not remove the need.)
- Requires a descriptive User-Agent -- the SEC rejects undeclared clients. Sent
  via customHeaders. The shared scrapedo-client still needs a `headers` option;
  three platforms duplicate a local getter (yelp, sec, googleads).
- filings.recent is COLUMNAR -- parallel arrays zipped by index. A ragged column
  would misalign filing dates against accession numbers; adversarially checked.
- `include_history` is the ONE call that can buy more than one upstream fetch
  (up to 10 archived shards, MAX_HISTORY_SHARDS) and is deliberately still ONE
  Scavio credit. history_truncated flags when a filer had more.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _SECLookupInput(BaseModel):
    """Input schema for ScavioSECLookupTool."""

    query: str = Field(
        ...,
        description=(
            "Ticker ('AAPL', 'BRK.B'), company name, or a fragment of one (1-200 "
            "characters); each row carries its match tier as 'match'."
        ),
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Rows to return, 1-100. Defaults to 10. Sizes the response; it is not a "
            "page param."
        ),
    )
    exchange: Literal["NASDAQ", "NYSE", "OTC", "CBOE"] | None = Field(
        default=None,
        description=(
            "Restrict to one listing venue; matched case-insensitively, so 'Nasdaq' "
            "also works. Filers the SEC lists with no exchange at all are excluded by "
            "any value."
        ),
    )


class _SECCompanyInput(BaseModel):
    """Input schema for ScavioSECCompanyTool."""

    cik: str | None = Field(
        default=None,
        description=(
            "Filer CIK in any spelling (1-20 characters): 320193, 0000320193 or "
            "CIK0000320193. A ticker is accepted here too."
        ),
    )
    ticker: str | None = Field(
        default=None,
        description=(
            "Ticker symbol (1-20 characters), dotted or dashed (BRK.B / BRK-B). Wins "
            "over cik when both are given."
        ),
    )


class _SECFilingsInput(BaseModel):
    """Input schema for ScavioSECFilingsTool."""

    cik: str | None = Field(
        default=None,
        description=(
            "Filer CIK, zero-padded or bare (1-20 characters). A ticker is accepted "
            "here too."
        ),
    )
    ticker: str | None = Field(
        default=None,
        description="Ticker symbol (1-20 characters), as an alternative to cik.",
    )
    form: str | list[str] | None = Field(
        default=None,
        description=(
            "Form types to keep: '10-K', ['10-K', '10-Q'] or the comma-joined "
            "'10-K,8-K'; each value 1-50 characters, at most 25 values. Matched "
            "against the form AND its root form, so 10-K also returns 10-K/A "
            "amendments; ask for '10-K/A' to get only amendments."
        ),
    )
    date_from: str | None = Field(
        default=None,
        description="Earliest filing date, inclusive (YYYY-MM-DD).",
    )
    date_to: str | None = Field(
        default=None,
        description="Latest filing date, inclusive (YYYY-MM-DD).",
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based; page size is whatever limit is set to. No upper "
            "bound."
        ),
    )
    limit: int | None = Field(
        default=None,
        description="Filings per page, 1-500. Defaults to 50.",
    )
    include_history: bool | None = Field(
        default=None,
        description=(
            "Also fetch the archived filing history beyond EDGAR's 'recent' block, "
            "which is not a fixed window (a decade for a quiet filer, about a year for "
            "a prolific one). Off by default; at most 10 archived shards are fetched, "
            "history_truncated says when a filer had more, and it is still 1 credit."
        ),
    )


class _SECConceptInput(BaseModel):
    """Input schema for ScavioSECConceptTool."""

    concept: str = Field(
        ...,
        description=(
            "XBRL concept tag, CASE-SENSITIVE (1-120 characters, "
            "^[A-Za-z][A-Za-z0-9]*$): 'NetIncomeLoss' matches, 'netincomeloss' is a "
            "404 upstream. Use facts() to list what a filer actually reports."
        ),
    )
    cik: str | None = Field(
        default=None,
        description=(
            "Filer CIK, zero-padded or bare (1-20 characters). A ticker is accepted "
            "here too."
        ),
    )
    ticker: str | None = Field(
        default=None,
        description="Ticker symbol (1-20 characters), as an alternative to cik.",
    )
    taxonomy: str | None = Field(
        default=None,
        description=(
            "Reporting taxonomy (1-40 characters, ^[A-Za-z][A-Za-z0-9-]*$): us-gaap, "
            "dei, ifrs-full or srt. Defaults to 'us-gaap'."
        ),
    )
    unit: str | None = Field(
        default=None,
        description=(
            "Unit of measure to keep (1-40 characters), e.g. 'USD' vs 'USD/shares'."
        ),
    )
    form: str | None = Field(
        default=None,
        description=(
            "Form to keep (1-50 characters). EXACT match here, unlike filings(), so "
            "'10-K' excludes 10-K/A."
        ),
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Rows to return, 1-2000. Defaults to 250. Sizes the response; it is not a "
            "page param."
        ),
    )


class _SECFactsInput(BaseModel):
    """Input schema for ScavioSECFactsTool."""

    cik: str | None = Field(
        default=None,
        description=(
            "Filer CIK, zero-padded or bare (1-20 characters). A ticker is accepted "
            "here too."
        ),
    )
    ticker: str | None = Field(
        default=None,
        description="Ticker symbol (1-20 characters), as an alternative to cik.",
    )
    taxonomy: str | None = Field(
        default=None,
        description=(
            "Restrict to one taxonomy (1-40 characters), e.g. 'us-gaap' or 'dei'."
        ),
    )
    query: str | None = Field(
        default=None,
        description=(
            "Case-insensitive substring matched against the tag name and label (1-200 "
            "characters)."
        ),
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Rows to return, 1-2000. Defaults to 250. Sizes the response; it is not a "
            "page param."
        ),
    )


class _SECSearchInput(BaseModel):
    """Input schema for ScavioSECSearchTool."""

    query: str | None = Field(
        default=None,
        description=(
            "Full-text query over filing documents (1-500 characters); a quoted phrase "
            "is matched exactly, bare words as a bag of terms. Optional - a cik, "
            "ticker, form or date filter on its own is a valid search."
        ),
    )
    cik: str | list[str] | None = Field(
        default=None,
        description=(
            "Restrict to one or more filers by CIK: a single value, a list, or a "
            "comma-joined string; each 1-20 characters, at most 25 values. Tickers are "
            "accepted here too."
        ),
    )
    ticker: str | list[str] | None = Field(
        default=None,
        description=(
            "Restrict to one or more filers by ticker symbol: a single value, a list, "
            "or a comma-joined string; each 1-20 characters, at most 25 values."
        ),
    )
    form: str | list[str] | None = Field(
        default=None,
        description=(
            "Form types to keep: '8-K', ['10-K', '10-Q'] or the comma-joined "
            "'10-K,10-Q'; each 1-50 characters, at most 25 values."
        ),
    )
    date_from: str | None = Field(
        default=None,
        description=(
            "Earliest filing date, inclusive (YYYY-MM-DD). Full-text coverage starts "
            "in 2001."
        ),
    )
    date_to: str | None = Field(
        default=None,
        description="Latest filing date, inclusive (YYYY-MM-DD).",
    )
    location: str | list[str] | None = Field(
        default=None,
        description=(
            "Filer business-address locations as EDGAR's own 2-character codes (CA, "
            "NY, and its alphanumeric codes for foreign jurisdictions): a single "
            "value, a list, or a comma-joined string; at most 25 values."
        ),
    )
    sort: Literal["relevance", "newest", "oldest"] | None = Field(
        default=None,
        description="Result ordering. Defaults to the index's own relevance ranking.",
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based, 1-100, 100 documents per page. The SEC's index "
            "refuses a result window past 10,000, so 100 is the last page for any "
            "query."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioSECLookupTool(ScavioBaseTool):
    """START HERE. Resolve a company name or ticker (AAPL) to the CIK (0000320193) every
    other SEC EDGAR endpoint is keyed by.
    """

    name: str = "Scavio SEC Lookup"
    description: str = (
        "START HERE. Resolve a company name or ticker (AAPL) to the CIK (0000320193) "
        "every other SEC EDGAR endpoint is keyed by. Up to 100 rows, tiered by match "
        "quality. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _SECLookupInput

    def _run(
        self,
        query: str,
        limit: int | None = None,
        exchange: Literal["NASDAQ", "NYSE", "OTC", "CBOE"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/lookup synchronously.

        Args:
            query: Ticker ('AAPL', 'BRK.B'), company name, or a fragment of one (1-200
                characters); each row carries its match tier as 'match'.
            limit: Rows to return, 1-100. Defaults to 10.
            exchange: Restrict to one listing venue; matched case-insensitively, so
                'Nasdaq' also works.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.sec.lookup(query=query, limit=limit, exchange=exchange)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        limit: int | None = None,
        exchange: Literal["NASDAQ", "NYSE", "OTC", "CBOE"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/lookup asynchronously.

        Args:
            query: Ticker ('AAPL', 'BRK.B'), company name, or a fragment of one (1-200
                characters); each row carries its match tier as 'match'.
            limit: Rows to return, 1-100. Defaults to 10.
            exchange: Restrict to one listing venue; matched case-insensitively, so
                'Nasdaq' also works.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.sec.lookup(
            query=query,
            limit=limit,
            exchange=exchange,
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


class ScavioSECCompanyTool(ScavioBaseTool):
    """SEC filer profile: legal and former names, SIC industry, filer category, EIN,
    LEI, state of incorporation, fiscal year end, addresses, every ticker with its
    exchange, and a preview of its 10 most recent filings.
    """

    name: str = "Scavio SEC Company"
    description: str = (
        "SEC filer profile: legal and former names, SIC industry, filer category, EIN, "
        "LEI, state of incorporation, fiscal year end, addresses, every ticker with "
        "its exchange, and a preview of its 10 most recent filings. Provide cik or "
        "ticker. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _SECCompanyInput

    def _run(
        self,
        cik: str | None = None,
        ticker: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/company synchronously.

        Args:
            cik: Filer CIK in any spelling (1-20 characters): 320193, 0000320193 or
                CIK0000320193.
            ticker: Ticker symbol (1-20 characters), dotted or dashed (BRK.B / BRK-B).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.sec.company(cik=cik, ticker=ticker)
        return self._format_response(raw)

    async def _arun(
        self,
        cik: str | None = None,
        ticker: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/company asynchronously.

        Args:
            cik: Filer CIK in any spelling (1-20 characters): 320193, 0000320193 or
                CIK0000320193.
            ticker: Ticker symbol (1-20 characters), dotted or dashed (BRK.B / BRK-B).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.sec.company(cik=cik, ticker=ticker)
        return self._format_response(raw)


class ScavioSECFilingsTool(ScavioBaseTool):
    """A page of one filer's filings: accession number, form and root form, filing and
    period dates, 8-K item codes, direct links to the primary document, filing index and
    attachment directory.
    """

    name: str = "Scavio SEC Filings"
    description: str = (
        "A page of one filer's filings: accession number, form and root form, filing "
        "and period dates, 8-K item codes, direct links to the primary document, "
        "filing index and attachment directory. Up to 500 per page. Provide cik or "
        "ticker. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _SECFilingsInput

    def _run(
        self,
        cik: str | None = None,
        ticker: str | None = None,
        form: str | list[str] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        include_history: bool | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/filings synchronously.

        Args:
            cik: Filer CIK, zero-padded or bare (1-20 characters).
            ticker: Ticker symbol (1-20 characters), as an alternative to cik.
            form: Form types to keep: '10-K', ['10-K', '10-Q'] or the comma-joined
                '10-K,8-K'; each value 1-50 characters, at most 25 values.
            date_from: Earliest filing date, inclusive (YYYY-MM-DD).
            date_to: Latest filing date, inclusive (YYYY-MM-DD).
            page: Results page, 1-based; page size is whatever limit is set to.
            limit: Filings per page, 1-500. Defaults to 50.
            include_history: Also fetch the archived filing history beyond EDGAR's
                'recent' block, which is not a fixed window (a decade for a quiet filer,
                about a year for a prolific one).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.sec.filings(
            cik=cik,
            ticker=ticker,
            form=form,
            date_from=date_from,
            date_to=date_to,
            page=page,
            limit=limit,
            include_history=include_history,
        )
        raw = self._truncate_nested(raw, "data", "filings")
        return self._format_response(raw)

    async def _arun(
        self,
        cik: str | None = None,
        ticker: str | None = None,
        form: str | list[str] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        include_history: bool | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/filings asynchronously.

        Args:
            cik: Filer CIK, zero-padded or bare (1-20 characters).
            ticker: Ticker symbol (1-20 characters), as an alternative to cik.
            form: Form types to keep: '10-K', ['10-K', '10-Q'] or the comma-joined
                '10-K,8-K'; each value 1-50 characters, at most 25 values.
            date_from: Earliest filing date, inclusive (YYYY-MM-DD).
            date_to: Latest filing date, inclusive (YYYY-MM-DD).
            page: Results page, 1-based; page size is whatever limit is set to.
            limit: Filings per page, 1-500. Defaults to 50.
            include_history: Also fetch the archived filing history beyond EDGAR's
                'recent' block, which is not a fixed window (a decade for a quiet filer,
                about a year for a prolific one).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.sec.filings(
            cik=cik,
            ticker=ticker,
            form=form,
            date_from=date_from,
            date_to=date_to,
            page=page,
            limit=limit,
            include_history=include_history,
        )
        raw = self._truncate_nested(raw, "data", "filings")
        return self._format_response(raw)


class ScavioSECConceptTool(ScavioBaseTool):
    """Every value a filer reported for one XBRL concept, newest period first, with the
    form and filing each number came from.
    """

    name: str = "Scavio SEC Concept"
    description: str = (
        "Every value a filer reported for one XBRL concept, newest period first, with "
        "the form and filing each number came from. Restatements are kept, not "
        "collapsed. Up to 2000 rows. Provide cik or ticker. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _SECConceptInput

    def _run(
        self,
        concept: str,
        cik: str | None = None,
        ticker: str | None = None,
        taxonomy: str | None = None,
        unit: str | None = None,
        form: str | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/concept synchronously.

        Args:
            concept: XBRL concept tag, CASE-SENSITIVE (1-120 characters,
                ^[A-Za-z][A-Za-z0-9]*$): 'NetIncomeLoss' matches, 'netincomeloss' is a
                404 upstream.
            cik: Filer CIK, zero-padded or bare (1-20 characters).
            ticker: Ticker symbol (1-20 characters), as an alternative to cik.
            taxonomy: Reporting taxonomy (1-40 characters, ^[A-Za-z][A-Za-z0-9-]*$):
                us-gaap, dei, ifrs-full or srt.
            unit: Unit of measure to keep (1-40 characters), e.g. 'USD' vs 'USD/shares'.
            form: Form to keep (1-50 characters).
            limit: Rows to return, 1-2000. Defaults to 250.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.sec.concept(
            concept=concept,
            cik=cik,
            ticker=ticker,
            taxonomy=taxonomy,
            unit=unit,
            form=form,
            limit=limit,
        )
        raw = self._truncate_nested(raw, "data", "facts")
        return self._format_response(raw)

    async def _arun(
        self,
        concept: str,
        cik: str | None = None,
        ticker: str | None = None,
        taxonomy: str | None = None,
        unit: str | None = None,
        form: str | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/concept asynchronously.

        Args:
            concept: XBRL concept tag, CASE-SENSITIVE (1-120 characters,
                ^[A-Za-z][A-Za-z0-9]*$): 'NetIncomeLoss' matches, 'netincomeloss' is a
                404 upstream.
            cik: Filer CIK, zero-padded or bare (1-20 characters).
            ticker: Ticker symbol (1-20 characters), as an alternative to cik.
            taxonomy: Reporting taxonomy (1-40 characters, ^[A-Za-z][A-Za-z0-9-]*$):
                us-gaap, dei, ifrs-full or srt.
            unit: Unit of measure to keep (1-40 characters), e.g. 'USD' vs 'USD/shares'.
            form: Form to keep (1-50 characters).
            limit: Rows to return, 1-2000. Defaults to 250.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.sec.concept(
            concept=concept,
            cik=cik,
            ticker=ticker,
            taxonomy=taxonomy,
            unit=unit,
            form=form,
            limit=limit,
        )
        raw = self._truncate_nested(raw, "data", "facts")
        return self._format_response(raw)


class ScavioSECFactsTool(ScavioBaseTool):
    """The index of every XBRL concept a filer reports - tag, label, description, units
    and most recent value - across us-gaap, dei and any other taxonomy it uses.
    """

    name: str = "Scavio SEC Facts"
    description: str = (
        "The index of every XBRL concept a filer reports - tag, label, description, "
        "units and most recent value - across us-gaap, dei and any other taxonomy it "
        "uses. This is how you find what to ask concept() for. Up to 2000 rows. "
        "Provide cik or ticker. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _SECFactsInput

    def _run(
        self,
        cik: str | None = None,
        ticker: str | None = None,
        taxonomy: str | None = None,
        query: str | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/facts synchronously.

        Args:
            cik: Filer CIK, zero-padded or bare (1-20 characters).
            ticker: Ticker symbol (1-20 characters), as an alternative to cik.
            taxonomy: Restrict to one taxonomy (1-40 characters), e.g. 'us-gaap' or
                'dei'.
            query: Case-insensitive substring matched against the tag name and label
                (1-200 characters).
            limit: Rows to return, 1-2000. Defaults to 250.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.sec.facts(
            cik=cik,
            ticker=ticker,
            taxonomy=taxonomy,
            query=query,
            limit=limit,
        )
        raw = self._truncate_nested(raw, "data", "concepts")
        return self._format_response(raw)

    async def _arun(
        self,
        cik: str | None = None,
        ticker: str | None = None,
        taxonomy: str | None = None,
        query: str | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/facts asynchronously.

        Args:
            cik: Filer CIK, zero-padded or bare (1-20 characters).
            ticker: Ticker symbol (1-20 characters), as an alternative to cik.
            taxonomy: Restrict to one taxonomy (1-40 characters), e.g. 'us-gaap' or
                'dei'.
            query: Case-insensitive substring matched against the tag name and label
                (1-200 characters).
            limit: Rows to return, 1-2000. Defaults to 250.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.sec.facts(
            cik=cik,
            ticker=ticker,
            taxonomy=taxonomy,
            query=query,
            limit=limit,
        )
        raw = self._truncate_nested(raw, "data", "concepts")
        return self._format_response(raw)


class ScavioSECSearchTool(ScavioBaseTool):
    """EDGAR full-text search, coverage starting 2001: each hit is the matching DOCUMENT
    with its URL, form, filing date and filer identity, plus facets by company, form,
    industry and state.
    """

    name: str = "Scavio SEC Search"
    description: str = (
        "EDGAR full-text search, coverage starting 2001: each hit is the matching "
        "DOCUMENT with its URL, form, filing date and filer identity, plus facets by "
        "company, form, industry and state. 100 documents per page, last page is 100. "
        "Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _SECSearchInput

    def _run(
        self,
        query: str | None = None,
        cik: str | list[str] | None = None,
        ticker: str | list[str] | None = None,
        form: str | list[str] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        location: str | list[str] | None = None,
        sort: Literal["relevance", "newest", "oldest"] | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/search synchronously.

        Args:
            query: Full-text query over filing documents (1-500 characters); a quoted
                phrase is matched exactly, bare words as a bag of terms.
            cik: Restrict to one or more filers by CIK: a single value, a list, or a
                comma-joined string; each 1-20 characters, at most 25 values.
            ticker: Restrict to one or more filers by ticker symbol: a single value, a
                list, or a comma-joined string; each 1-20 characters, at most 25 values.
            form: Form types to keep: '8-K', ['10-K', '10-Q'] or the comma-joined
                '10-K,10-Q'; each 1-50 characters, at most 25 values.
            date_from: Earliest filing date, inclusive (YYYY-MM-DD).
            date_to: Latest filing date, inclusive (YYYY-MM-DD).
            location: Filer business-address locations as EDGAR's own 2-character codes
                (CA, NY, and its alphanumeric codes for foreign jurisdictions): a single
                value, a list, or a comma-joined string; at most 25 values.
            sort: Result ordering. Defaults to the index's own relevance ranking.
            page: Results page, 1-based, 1-100, 100 documents per page.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.sec.search(
            query=query,
            cik=cik,
            ticker=ticker,
            form=form,
            date_from=date_from,
            date_to=date_to,
            location=location,
            sort=sort,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str | None = None,
        cik: str | list[str] | None = None,
        ticker: str | list[str] | None = None,
        form: str | list[str] | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        location: str | list[str] | None = None,
        sort: Literal["relevance", "newest", "oldest"] | None = None,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/sec/search asynchronously.

        Args:
            query: Full-text query over filing documents (1-500 characters); a quoted
                phrase is matched exactly, bare words as a bag of terms.
            cik: Restrict to one or more filers by CIK: a single value, a list, or a
                comma-joined string; each 1-20 characters, at most 25 values.
            ticker: Restrict to one or more filers by ticker symbol: a single value, a
                list, or a comma-joined string; each 1-20 characters, at most 25 values.
            form: Form types to keep: '8-K', ['10-K', '10-Q'] or the comma-joined
                '10-K,10-Q'; each 1-50 characters, at most 25 values.
            date_from: Earliest filing date, inclusive (YYYY-MM-DD).
            date_to: Latest filing date, inclusive (YYYY-MM-DD).
            location: Filer business-address locations as EDGAR's own 2-character codes
                (CA, NY, and its alphanumeric codes for foreign jurisdictions): a single
                value, a list, or a comma-joined string; at most 25 values.
            sort: Result ordering. Defaults to the index's own relevance ranking.
            page: Results page, 1-based, 1-100, 100 documents per page.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.sec.search(
            query=query,
            cik=cik,
            ticker=ticker,
            form=form,
            date_from=date_from,
            date_to=date_to,
            location=location,
            sort=sort,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)
