"""Scavio HEB tools for CrewAI.

2 credits per call. HEB is a Texas-based grocery chain.
"""

from typing import Any, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


class _HebSearchInput(BaseModel):
    """Input schema for ScavioHebSearchTool."""

    query: str = Field(
        ...,
        description="Search keywords, e.g. 'organic milk'.",
    )
    page: int | None = Field(
        default=None,
        description="Page, 1-based.",
    )
    page_size: int | None = Field(
        default=None,
        description="Results per page, 1-60. Defaults to 60.",
    )
    store_id: str | None = Field(
        default=None,
        description=(
            "HEB store number from Scavio HEB Stores (store_number), e.g. '441'. Prices, "
            "stock, aisle location and assortment come from that store; the store used is "
            "echoed in data.store {store_id, name}. US only. Omit for HEB's default store."
        ),
    )


class _HebProductInput(BaseModel):
    """Input schema for ScavioHebProductTool."""

    product_url: str | None = Field(
        default=None,
        description=(
            "Full or relative product URL from heb.com, e.g. "
            "'/product-detail/central-market-organics-whole-milk-1-gal/931316'. Preferred."
        ),
    )
    product_id: str | None = Field(
        default=None,
        description=(
            "HEB product id (numeric id at the end of a product URL). Needs slug, "
            "unless store_id is set (then product_id alone works)."
        ),
    )
    slug: str | None = Field(
        default=None,
        description="Product slug (readable part of the URL). Required with product_id unless store_id is set.",
    )
    store_id: str | None = Field(
        default=None,
        description=(
            "HEB store number from Scavio HEB Stores (store_number), e.g. '441'. Prices, "
            "stock, aisle location and assortment come from that store; the store used is "
            "echoed in data.store {store_id, name}. US only. Omit for HEB's default store."
        ),
    )


class _HebStoresInput(BaseModel):
    """Input schema for ScavioHebStoresTool."""

    zip: str | None = Field(
        default=None,
        description="5-digit US ZIP code, e.g. '78701'.",
    )
    city: str | None = Field(
        default=None,
        description="City name, e.g. 'Austin'. Pass zip or city.",
    )


class ScavioHebSearchTool(ScavioBaseTool):
    """Search HEB grocery products: prices (cents), unit price, UPC, stock, EBT/SNAP,
    aisle location."""

    name: str = "Scavio HEB Search"
    description: str = (
        "Search HEB grocery products by keyword. Returns price (cents), list price, "
        "sale status, unit price, size, UPC, stock, EBT/SNAP eligibility, category, "
        "aisle location and product URL. Pass store_id (store_number from Scavio HEB "
        "Stores) for one store's prices, stock and assortment. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _HebSearchInput

    def _run(
        self,
        query: str,
        page: int | None = None,
        page_size: int | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = self.client.heb.search(
            query=query,
            page=page,
            page_size=page_size,
            store_id=store_id,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        page: int | None = None,
        page_size: int | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = await self.async_client.heb.search(
            query=query,
            page=page,
            page_size=page_size,
            store_id=store_id,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioHebProductTool(ScavioBaseTool):
    """Full HEB product detail: nutrition facts, ingredients, images, coupons, EBT/SNAP."""

    name: str = "Scavio HEB Product"
    description: str = (
        "Full HEB product detail: nutrition facts (serving size, calories, nutrients "
        "with daily values), ingredients, description, images, similar products, "
        "coupons, EBT/SNAP eligibility, breadcrumbs, aisle location. "
        "Pass product_url or slug + product_id; with store_id (store_number from Scavio "
        "HEB Stores) product_id alone works and price, stock and aisle are for that "
        "store. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _HebProductInput

    def _run(
        self,
        product_url: str | None = None,
        product_id: str | None = None,
        slug: str | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = self.client.heb.product(
            product_url=product_url,
            product_id=product_id,
            slug=slug,
            store_id=store_id,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        product_url: str | None = None,
        product_id: str | None = None,
        slug: str | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = await self.async_client.heb.product(
            product_url=product_url,
            product_id=product_id,
            slug=slug,
            store_id=store_id,
        )
        return self._format_response(raw)


class ScavioHebStoresTool(ScavioBaseTool):
    """Find HEB stores near a US ZIP or city: address, hours, pharmacy, fulfillment."""

    name: str = "Scavio HEB Stores"
    description: str = (
        "Find HEB stores near a US ZIP code or city. Returns store number, address, "
        "phone, hours, pharmacy availability, fulfillment channels (curbside, delivery, "
        "in-store), distance and store URL. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = _HebStoresInput

    def _run(
        self,
        zip: str | None = None,
        city: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = self.client.heb.stores(zip=zip, city=city)
        raw = self._truncate_nested(raw, "data", "stores")
        return self._format_response(raw)

    async def _arun(
        self,
        zip: str | None = None,
        city: str | None = None,
        **kwargs: Any,
    ) -> str:
        raw = await self.async_client.heb.stores(zip=zip, city=city)
        raw = self._truncate_nested(raw, "data", "stores")
        return self._format_response(raw)
