"""Scavio Walmart tools for CrewAI.

Provides tools to search Walmart product listings and fetch individual
product details via the Scavio API.
"""


from typing import Any, Literal

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool

_DOMAIN_DESCRIPTION = "Walmart domain to search (e.g. 'walmart.com')."
_DEVICE_DESCRIPTION = "Device to emulate: desktop, mobile or tablet."
_DELIVERY_ZIP_DESCRIPTION = "ZIP code for localized pricing and delivery."
_STORE_ID_DESCRIPTION = "Walmart store id for in-store availability."


class ScavioWalmartSearchToolSchema(BaseModel):
    """Input schema for ScavioWalmartSearchTool."""

    query: str = Field(..., description="Product search query (e.g., 'wireless headphones').")
    start_page: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Page to start from, 1-based. Walmart has no 'page' param -- "
            "this is the only pagination field."
        ),
    )
    sort_by: Literal[
        "best_match",
        "price_low",
        "price_high",
        "best_seller",
    ] | None = Field(
        default=None,
        description="Sort order; falls back to the tool default.",
    )
    domain: str | None = Field(
        default=None, description=_DOMAIN_DESCRIPTION
    )
    device: Literal["desktop", "mobile", "tablet"] | None = Field(
        default=None, description=_DEVICE_DESCRIPTION
    )
    min_price: int | None = Field(
        default=None, description="Minimum price filter in USD."
    )
    max_price: int | None = Field(
        default=None, description="Maximum price filter in USD."
    )
    fulfillment_speed: Literal[
        "today", "tomorrow", "2_days", "anytime"
    ] | None = Field(
        default=None, description="Delivery speed filter."
    )
    fulfillment_type: Literal["in_store"] | None = Field(
        default=None,
        description="Fulfillment type filter; 'in_store' is the only value.",
    )
    delivery_zip: str | None = Field(
        default=None, description=_DELIVERY_ZIP_DESCRIPTION
    )
    store_id: str | None = Field(
        default=None, description=_STORE_ID_DESCRIPTION
    )


# Search params an agent may set per call. A value passed here wins over the
# developer-set constructor default of the same name.
_SEARCH_PARAM_NAMES: tuple[str, ...] = (
    "start_page",
    "sort_by",
    "domain",
    "device",
    "min_price",
    "max_price",
    "fulfillment_speed",
    "fulfillment_type",
    "delivery_zip",
    "store_id",
)


class ScavioWalmartSearchTool(ScavioBaseTool):
    """Tool that searches Walmart product listings using the Scavio API.

    Every search param lives in ``args_schema`` so an agent can vary it per
    call. ``domain`` and ``sort_by`` stay as developer-set defaults for when
    the agent omits them.

    Attributes:
        name: The name of the tool.
        description: A description of the tool's purpose.
        args_schema: The schema for the tool's arguments.
        domain: Default Walmart marketplace domain to search.
        sort_by: Default sort order for results.
    """

    name: str = "Scavio Walmart Search"
    description: str = (
        "A tool that searches Walmart product listings using the Scavio API. "
        "Returns product names, prices, ratings, and fulfillment options "
        "as a JSON string. Page with start_page."
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

    def _build_params(self, **overrides: Any) -> dict[str, Any]:
        """Layer per-call arguments over the developer-set defaults.

        Args:
            **overrides: Search params supplied for this call.

        Returns:
            Keyword arguments for ``client.walmart.search``.
        """
        params: dict[str, Any] = {
            "domain": self.domain,
            "sort_by": self.sort_by,
        }
        for name in _SEARCH_PARAM_NAMES:
            value = overrides.get(name)
            if value is not None:
                params[name] = value
        return params

    def _run(self, query: str, **kwargs: Any) -> str:
        """Synchronously search Walmart product listings.

        Args:
            query: Product search query.
            **kwargs: Optional paging / sort / filter / locale params.

        Returns:
            A JSON string containing product search results.
        """
        raw = self.client.walmart.search(
            query=query, **self._build_params(**kwargs)
        )
        self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Asynchronously search Walmart product listings.

        Args:
            query: Product search query.
            **kwargs: Optional paging / sort / filter / locale params.

        Returns:
            A JSON string containing product search results.
        """
        raw = await self.async_client.walmart.search(
            query=query, **self._build_params(**kwargs)
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
    device: Literal["desktop", "mobile", "tablet"] | None = Field(
        default=None, description=_DEVICE_DESCRIPTION
    )
    delivery_zip: str | None = Field(
        default=None, description=_DELIVERY_ZIP_DESCRIPTION
    )
    store_id: str | None = Field(
        default=None, description=_STORE_ID_DESCRIPTION
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

    def _run(
        self,
        product_id: str,
        domain: str | None = None,
        device: Literal["desktop", "mobile", "tablet"] | None = None,
        delivery_zip: str | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Synchronously fetch Walmart product details.

        Args:
            product_id: Walmart product ID.
            domain: Walmart marketplace domain.
            device: Device to emulate.
            delivery_zip: ZIP code for localized pricing.
            store_id: Walmart store id for in-store availability.

        Returns:
            A JSON string containing the product details.
        """
        raw = self.client.walmart.product(
            product_id=product_id,
            domain=domain,
            device=device,
            delivery_zip=delivery_zip,
            store_id=store_id,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        product_id: str,
        domain: str | None = None,
        device: Literal["desktop", "mobile", "tablet"] | None = None,
        delivery_zip: str | None = None,
        store_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Asynchronously fetch Walmart product details.

        Args:
            product_id: Walmart product ID.
            domain: Walmart marketplace domain.
            device: Device to emulate.
            delivery_zip: ZIP code for localized pricing.
            store_id: Walmart store id for in-store availability.

        Returns:
            A JSON string containing the product details.
        """
        raw = await self.async_client.walmart.product(
            product_id=product_id,
            domain=domain,
            device=device,
            delivery_zip=delivery_zip,
            store_id=store_id,
        )
        return self._format_response(raw)
