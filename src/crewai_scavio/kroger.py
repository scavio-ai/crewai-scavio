"""Scavio Kroger tools for CrewAI.

2 credits per call. Kroger operates Kroger, Ralphs, Fred Meyer, Harris Teeter,
King Soopers, Fry's and other banners.
"""

from typing import Any, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


class _KrogerSearchInput(BaseModel):
    """Input schema for ScavioKrogerSearchTool."""

    query: str = Field(
        ...,
        description="Search keywords, e.g. 'organic milk'.",
    )
    page: int | None = Field(
        default=None,
        description="Page, 1-based.",
    )


class _KrogerProductInput(BaseModel):
    """Input schema for ScavioKrogerProductTool."""

    product_url: str | None = Field(
        default=None,
        description=(
            "Full or relative product URL from kroger.com, e.g. "
            "'/p/kroger-2-reduced-fat-milk-gallon/0001111041700'. Preferred."
        ),
    )
    upc: str | None = Field(
        default=None,
        description="Kroger product UPC (from search or product URLs: /p/{slug}/{upc}).",
    )
    slug: str | None = Field(
        default=None,
        description="Product slug for readable URL. Optional with upc.",
    )


class ScavioKrogerSearchTool(ScavioBaseTool):
    """Search Kroger grocery products: prices (cents), promo, UPC, stock, SNAP, dietary."""

    name: str = "Scavio Kroger Search"
    description: str = (
        "Search Kroger grocery products by keyword. Kroger operates Kroger, Ralphs, "
        "Fred Meyer, Harris Teeter, King Soopers, Fry's and other banners. Returns "
        "price (cents), promo price, n-for deals, unit price, size, UPC, stock, SNAP "
        "eligibility, dietary info, rating and category. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _KrogerSearchInput

    def _run(
        self,
        query: str,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        raw = self.client.kroger.search(query=query, page=page)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        page: int | None = None,
        **kwargs: Any,
    ) -> str:
        raw = await self.async_client.kroger.search(query=query, page=page)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioKrogerProductTool(ScavioBaseTool):
    """Full Kroger product detail: nutrition facts, allergens, dietary flags, rating
    distribution, stock, aisle."""

    name: str = "Scavio Kroger Product"
    description: str = (
        "Full Kroger product detail by URL or UPC: nutrition facts (allergens, "
        "ingredients, nutrients with daily values), description, images, rating "
        "distribution, store aisle location, stock level, dietary flags (organic, "
        "non-GMO, gluten-free), SNAP eligibility, dimensions and country of origin. "
        "Pass product_url or upc. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _KrogerProductInput

    def _run(
        self,
        product_url: str | None = None,
        upc: str | None = None,
        slug: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = self.client.kroger.product(
            product_url=product_url,
            upc=upc,
            slug=slug,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        product_url: str | None = None,
        upc: str | None = None,
        slug: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = await self.async_client.kroger.product(
            product_url=product_url,
            upc=upc,
            slug=slug,
        )
        return self._format_response(raw)
