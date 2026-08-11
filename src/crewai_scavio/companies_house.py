"""Scavio Companies House tools for CrewAI.

1 credit flat on all four endpoints (COMPANIESHOUSE_CREDIT_COST =
scrapedoCreditCost(1)) -- official UK registry.

- LOOKUP (search) FIRST -- everything else is keyed by company number.
- A free API key would give cleaner JSON; worth registering if this gets
  traffic.
- company_number is deliberately LOOSE (no regex): the register 404s on
  /company/445790 and /company/sc090312 for companies that exist, so the
  transport pads and upper-cases. A route regex would reject the very inputs
  normalisation exists to rescue (numbers off a letterhead, spreadsheets that
  ate leading zeros).
- Registry prefixes supported: SC (Scotland), NI (Northern Ireland), OC/SO/NC
  (LLPs), FC (overseas), BR (UK establishment), CE (charitable incorporated
  organisation).
"""


from typing import Any, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _CompaniesHouseSearchInput(BaseModel):
    """Input schema for ScavioCompaniesHouseSearchTool."""

    query: str = Field(
        ...,
        description=(
            "Company name or fragment (1-200 characters, non-blank). Matches CURRENT "
            "AND FORMER names."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based, 1-50, 20 results per page. Defaults to 1. The "
            "register serves only a 1000-result window per term whatever hit count it "
            "prints, and answers page 51 with HTTP 416."
        ),
    )


class _CompaniesHouseCompanyInput(BaseModel):
    """Input schema for ScavioCompaniesHouseCompanyTool."""

    company_number: str = Field(
        ...,
        description=(
            "UK company number (1-20 characters), zero-padded and upper-cased for you, "
            "so '445790' and 'sc090312' both work. Registry prefixes supported: SC, "
            "NI, OC, SO, NC, FC, BR, CE."
        ),
    )


class _CompaniesHouseOfficersInput(BaseModel):
    """Input schema for ScavioCompaniesHouseOfficersTool."""

    company_number: str = Field(
        ...,
        description=(
            "UK company number (1-20 characters), zero-padded and upper-cased for you."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based, 35 per page. Defaults to 1. No upper bound: past "
            "the last page the register answers an ordinary 200 with an empty list, "
            "identical to a company with no officers."
        ),
    )


class _CompaniesHouseFilingHistoryInput(BaseModel):
    """Input schema for ScavioCompaniesHouseFilingHistoryTool."""

    company_number: str = Field(
        ...,
        description=(
            "UK company number (1-20 characters), zero-padded and upper-cased for you."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based. Defaults to 1. No upper bound: past the last page "
            "the register answers an ordinary 200 with an empty list."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioCompaniesHouseSearchTool(ScavioBaseTool):
    """START HERE. Search the UK register by name and get the company_number every other
    Companies House endpoint is keyed by, plus status, incorporation or dissolution
    date, registered office and matched former names.
    """

    name: str = "Scavio Companies House Search"
    description: str = (
        "START HERE. Search the UK register by name and get the company_number every "
        "other Companies House endpoint is keyed by, plus status, incorporation or "
        "dissolution date, registered office and matched former names. 20 per page, "
        "last page is 50. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _CompaniesHouseSearchInput

    def _run(self, query: str, page: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/companieshouse/search synchronously.

        Args:
            query: Company name or fragment (1-200 characters, non-blank).
            page: Results page, 1-based, 1-50, 20 results per page.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.companies_house.search(query=query, page=page)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(self, query: str, page: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/companieshouse/search asynchronously.

        Args:
            query: Company name or fragment (1-200 characters, non-blank).
            page: Results page, 1-based, 1-50, 20 results per page.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.companies_house.search(query=query, page=page)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


class ScavioCompaniesHouseCompanyTool(ScavioBaseTool):
    """Full UK register entry: status, type, incorporation and dissolution dates,
    registered office, SIC codes, previous names, accounts and confirmation-statement
    due dates with overdue flags, and whether it has charges, insolvency history,
    officers or UK establishments.
    """

    name: str = "Scavio Companies House Company"
    description: str = (
        "Full UK register entry: status, type, incorporation and dissolution dates, "
        "registered office, SIC codes, previous names, accounts and "
        "confirmation-statement due dates with overdue flags, and whether it has "
        "charges, insolvency history, officers or UK establishments. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _CompaniesHouseCompanyInput

    def _run(self, company_number: str, **kwargs: Any) -> str:
        """Call /api/v1/companieshouse/company synchronously.

        Args:
            company_number: UK company number (1-20 characters), zero-padded and
                upper-cased for you, so '445790' and 'sc090312' both work.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.companies_house.company(company_number=company_number)
        return self._format_response(raw)

    async def _arun(self, company_number: str, **kwargs: Any) -> str:
        """Call /api/v1/companieshouse/company asynchronously.

        Args:
            company_number: UK company number (1-20 characters), zero-padded and
                upper-cased for you, so '445790' and 'sc090312' both work.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.companies_house.company(
            company_number=company_number,
        )
        return self._format_response(raw)


class ScavioCompaniesHouseOfficersTool(ScavioBaseTool):
    """UK company officers, current and resigned, 35 per page: name, role, appointment
    and resignation dates, correspondence address, nationality, country of residence,
    month-and-year date of birth and identity-verification status.
    """

    name: str = "Scavio Companies House Officers"
    description: str = (
        "UK company officers, current and resigned, 35 per page: name, role, "
        "appointment and resignation dates, correspondence address, nationality, "
        "country of residence, month-and-year date of birth and identity-verification "
        "status. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _CompaniesHouseOfficersInput

    def _run(self, company_number: str, page: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/companieshouse/officers synchronously.

        Args:
            company_number: UK company number (1-20 characters), zero-padded and
                upper-cased for you.
            page: Results page, 1-based, 35 per page.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.companies_house.officers(
            company_number=company_number,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "officers")
        return self._format_response(raw)

    async def _arun(
        self,
        company_number: str,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/companieshouse/officers asynchronously.

        Args:
            company_number: UK company number (1-20 characters), zero-padded and
                upper-cased for you.
            page: Results page, 1-based, 35 per page.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.companies_house.officers(
            company_number=company_number,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "officers")
        return self._format_response(raw)


class ScavioCompaniesHouseFilingHistoryTool(ScavioBaseTool):
    """UK filings, most recent first: date, filing type code (AA, CS01, SH03),
    description, register annotations and child documents, and a link to the filed PDF
    with its page count.
    """

    name: str = "Scavio Companies House Filing History"
    description: str = (
        "UK filings, most recent first: date, filing type code (AA, CS01, SH03), "
        "description, register annotations and child documents, and a link to the "
        "filed PDF with its page count. A filing the register has not finished "
        "processing carries a processing_note instead of a document. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _CompaniesHouseFilingHistoryInput

    def _run(self, company_number: str, page: int | None = None, **kwargs: Any) -> str:
        """Call /api/v1/companieshouse/filing-history synchronously.

        Args:
            company_number: UK company number (1-20 characters), zero-padded and
                upper-cased for you.
            page: Results page, 1-based. Defaults to 1.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.companies_house.filing_history(
            company_number=company_number,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "filings")
        return self._format_response(raw)

    async def _arun(
        self,
        company_number: str,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/companieshouse/filing-history asynchronously.

        Args:
            company_number: UK company number (1-20 characters), zero-padded and
                upper-cased for you.
            page: Results page, 1-based. Defaults to 1.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.companies_house.filing_history(
            company_number=company_number,
            page=page,
        )
        raw = self._truncate_nested(raw, "data", "filings")
        return self._format_response(raw)
