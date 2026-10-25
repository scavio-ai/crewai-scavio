"""Scavio Decathlon tools for CrewAI.

2 credits per call. Supports 7 country domains: FR, ES, IT, IN, UK, PT
and NET (international).
"""

from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


class _DecathlonSearchInput(BaseModel):
    """Input schema for ScavioDecathlonSearchTool."""

    query: str = Field(
        ...,
        description="Search keywords, e.g. 'running shoes'.",
    )
    country: Literal["fr", "es", "it", "in", "uk", "pt", "net"] = Field(
        ...,
        description="Country domain.",
    )
    page: int | None = Field(
        default=None,
        description="Page, 1-based.",
    )


class _DecathlonProductInput(BaseModel):
    """Input schema for ScavioDecathlonProductTool."""

    product_url: str | None = Field(
        default=None,
        description="Full or relative product URL from any Decathlon domain. Preferred.",
    )
    product_id: str | None = Field(
        default=None,
        description="Decathlon numeric product ID (from the /p/{slug}/{id}/... URL pattern).",
    )
    country: Literal["fr", "es", "it", "in", "uk", "pt", "net"] = Field(
        ...,
        description="Country domain.",
    )


class ScavioDecathlonSearchTool(ScavioBaseTool):
    """Search Decathlon products: name, brand, price, availability, rating."""

    name: str = "Scavio Decathlon Search"
    description: str = (
        "Search Decathlon products by keyword across 7 country domains "
        "(FR, ES, IT, IN, UK, PT, NET). Returns product name, brand, "
        "price (cents), currency, availability, rating, review count and "
        "image. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _DecathlonSearchInput

    def _run(
        self,
        query: str,
        country: str,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        raw = self.client.decathlon.search(query=query, country=country, page=page)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        country: str,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        raw = await self.async_client.decathlon.search(query=query, country=country, page=page)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioDecathlonProductTool(ScavioBaseTool):
    """Full Decathlon product detail: description, images, SKU, price, variants,
    rating, category."""

    name: str = "Scavio Decathlon Product"
    description: str = (
        "Full Decathlon product detail by URL or product ID: description, "
        "images, SKU, GTIN, color, price (cents), list price, availability, "
        "offers/variants, rating, review count, category and breadcrumbs. "
        "Supports all 7 country domains. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _DecathlonProductInput

    def _run(
        self,
        country: str,
        product_url: str | None = None,
        product_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = self.client.decathlon.product(
            country=country,
            product_url=product_url,
            product_id=product_id,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        country: str,
        product_url: str | None = None,
        product_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = await self.async_client.decathlon.product(
            country=country,
            product_url=product_url,
            product_id=product_id,
        )
        return self._format_response(raw)
