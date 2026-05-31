"""Scavio Amazon tools for CrewAI."""


from typing import Any, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class ScavioAmazonSearchInput(BaseModel):
    """Input schema for ScavioAmazonSearchTool."""

    query: str = Field(..., description="The product search query.")


class ScavioAmazonProductInput(BaseModel):
    """Input schema for ScavioAmazonProductTool."""

    asin: str = Field(..., description="The Amazon Standard Identification Number.")
    domain: str | None = Field(
        default=None,
        description=(
            "Amazon domain suffix (e.g. 'com', 'co.uk'). "
            "Defaults to 'com' when not provided."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class ScavioAmazonSearchTool(ScavioBaseTool):
    """Amazon product search tool powered by the Scavio Amazon API.

    Attributes:
        domain: Amazon domain suffix (e.g. 'com', 'co.uk').
        sort_by: Sort order for search results.
        pages: Number of result pages to fetch.
        autoselect_variant: Automatically select a product variant.
    """

    name: str = "Scavio Amazon Search"
    description: str = (
        "Search for products on Amazon using the Scavio Amazon API. "
        "Returns product listings with titles, prices, ratings, and more."
    )
    args_schema: Type[BaseModel] = ScavioAmazonSearchInput

    domain: str = "com"
    sort_by: str | None = None
    pages: int | None = None
    autoselect_variant: bool | None = None

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous Amazon product search.

        Args:
            query: The product search query.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.amazon.search(
            query=query,
            domain=self.domain,
            sort_by=self.sort_by,
            pages=self.pages,
            autoselect_variant=self.autoselect_variant,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous Amazon product search.

        Args:
            query: The product search query.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.amazon.search(
            query=query,
            domain=self.domain,
            sort_by=self.sort_by,
            pages=self.pages,
            autoselect_variant=self.autoselect_variant,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioAmazonProductTool(ScavioBaseTool):
    """Amazon product detail tool powered by the Scavio Amazon API.

    Retrieves detailed information for a single product by its ASIN.
    """

    name: str = "Scavio Amazon Product"
    description: str = (
        "Get detailed product information from Amazon by ASIN "
        "using the Scavio Amazon API."
    )
    args_schema: Type[BaseModel] = ScavioAmazonProductInput

    def _run(self, asin: str, domain: str | None = None, **kwargs: Any) -> str:
        """Fetch product details by ASIN synchronously.

        Args:
            asin: The Amazon Standard Identification Number.
            domain: Amazon domain suffix. Defaults to 'com'.

        Returns:
            JSON-serialised product details.
        """
        raw = self.client.amazon.product(
            asin=asin,
            domain=domain or "com",
        )
        return self._format_response(raw)

    async def _arun(
        self, asin: str, domain: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch product details by ASIN asynchronously.

        Args:
            asin: The Amazon Standard Identification Number.
            domain: Amazon domain suffix. Defaults to 'com'.

        Returns:
            JSON-serialised product details.
        """
        raw = await self.async_client.amazon.product(
            asin=asin,
            domain=domain or "com",
        )
        return self._format_response(raw)
