"""Scavio Walmart tools for CrewAI.

Provides tools to search Walmart product listings and fetch individual
product details via the Scavio API.
"""


from typing import Literal

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


class ScavioWalmartSearchToolSchema(BaseModel):
    """Input schema for ScavioWalmartSearchTool."""

    query: str = Field(..., description="Product search query (e.g., 'wireless headphones').")


class ScavioWalmartSearchTool(ScavioBaseTool):
    """Tool that searches Walmart product listings using the Scavio API.

    Attributes:
        name: The name of the tool.
        description: A description of the tool's purpose.
        args_schema: The schema for the tool's arguments.
        domain: The Walmart marketplace domain to search.
        sort_by: Sort order for results.
    """

    name: str = "Scavio Walmart Search"
    description: str = (
        "A tool that searches Walmart product listings using the Scavio API. "
        "Returns product names, prices, ratings, and fulfillment options "
        "as a JSON string."
    )
    args_schema: type[BaseModel] = ScavioWalmartSearchToolSchema

    domain: str | None = Field(
        default=None,
        description="Walmart marketplace domain to search.",
    )
    sort_by: Literal[
        "best_match",
        "price_low",
        "price_high",
        "best_seller",
    ] | None = Field(
        default=None,
        description="Sort order for results.",
    )

    def _run(self, query: str) -> str:
        """Synchronously search Walmart product listings.

        Args:
            query: Product search query.

        Returns:
            A JSON string containing product search results.
        """
        raw = self.client.walmart.search(
            query=query,
            domain=self.domain,
            sort_by=self.sort_by,
        )
        self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(self, query: str) -> str:
        """Asynchronously search Walmart product listings.

        Args:
            query: Product search query.

        Returns:
            A JSON string containing product search results.
        """
        raw = await self.async_client.walmart.search(
            query=query,
            domain=self.domain,
            sort_by=self.sort_by,
        )
        self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioWalmartProductToolSchema(BaseModel):
    """Input schema for ScavioWalmartProductTool."""

    product_id: str = Field(..., description="Walmart product ID.")
    domain: str | None = Field(
        default=None,
        description="Walmart marketplace domain.",
    )


class ScavioWalmartProductTool(ScavioBaseTool):
    """Tool that fetches full details for a Walmart product by ID.

    Attributes:
        name: The name of the tool.
        description: A description of the tool's purpose.
        args_schema: The schema for the tool's arguments.
    """

    name: str = "Scavio Walmart Product"
    description: str = (
        "A tool that fetches full details for a Walmart product by product ID "
        "using the Scavio API."
    )
    args_schema: type[BaseModel] = ScavioWalmartProductToolSchema

    def _run(self, product_id: str, domain: str | None = None) -> str:
        """Synchronously fetch Walmart product details.

        Args:
            product_id: Walmart product ID.
            domain: Walmart marketplace domain.

        Returns:
            A JSON string containing the product details.
        """
        raw = self.client.walmart.product(
            product_id=product_id,
            domain=domain,
        )
        return self._format_response(raw)

    async def _arun(self, product_id: str, domain: str | None = None) -> str:
        """Asynchronously fetch Walmart product details.

        Args:
            product_id: Walmart product ID.
            domain: Walmart marketplace domain.

        Returns:
            A JSON string containing the product details.
        """
        raw = await self.async_client.walmart.product(
            product_id=product_id,
            domain=domain,
        )
        return self._format_response(raw)
