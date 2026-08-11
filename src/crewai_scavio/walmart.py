"""Scavio Walmart tools for CrewAI.

BODY-PRICED. walmartCreditCost(domain): domain=com -> 1, domain=ca -> 1,
domain=com.mx -> 2. Only /search and /category accept `domain`, so only those
two can cost 2; the other five are always 1. Never emit a flat 'Costs 1 credit'
on search or category -- state the domain rule.

- 5 of 7 endpoints are NEW since the last propagation and search/product
  CHANGED SHAPE -- every surface needs a revisit, not an append.
- Homepage docs walmart-api.tsx / walmart-product.tsx are STALE: they still
  document retired device / delivery_zip / store_id params.
- QUEUE-DOC ERROR: the queue lists `domain` among the retired params. It is NOT
  retired -- it is live, enum com|ca|com.mx, and it is the price-bearing param
  (com.mx = 2 credits).
- device / delivery_zip / store_id are the actually-retired params; sending
  them returns a warnings[] array explaining why, not an error.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_WalmartSearchSortBy = Literal[
    "best_match", "price_low", "price_high", "best_seller", "rating_high",
    "new"
]
_WalmartReviewsSort = Literal[
    "relevancy", "submission-desc", "submission-asc", "rating-desc",
    "rating-asc", "helpful-desc"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _WalmartSearchInput(BaseModel):
    """Input schema for ScavioWalmartSearchTool."""

    query: str = Field(
        ...,
        description="Product search query (1-500 characters).",
    )
    domain: Literal["com", "ca", "com.mx"] | None = Field(
        default=None,
        description=(
            "Marketplace: 'com' (US, default, 1 credit), 'ca' (1 credit), 'com.mx' (2 "
            "credits). Sets the currency and product URLs of the response."
        ),
    )
    page: int | None = Field(
        default=None,
        description="Results page, 1-based (integer >= 1). One page per call.",
    )
    start_page: int | None = Field(
        default=None,
        description="Deprecated alias for page; send page instead.",
    )
    sort_by: _WalmartSearchSortBy | None = Field(
        default=None,
        description="Result sort order. Defaults to 'best_match'.",
    )
    min_price: float | None = Field(
        default=None,
        description=(
            "Minimum price filter in the marketplace's own currency; decimals allowed "
            "(e.g. 19.99)."
        ),
    )
    max_price: float | None = Field(
        default=None,
        description=(
            "Maximum price filter in the marketplace's own currency; decimals allowed "
            "(e.g. 199.5)."
        ),
    )
    fulfillment_speed: Literal["today", "tomorrow"] | None = Field(
        default=None,
        description=(
            "Only items deliverable today, or by tomorrow. '2_days' and 'anytime' are "
            "not accepted - for anytime, omit this parameter."
        ),
    )
    fulfillment_type: Literal["in_store"] | None = Field(
        default=None,
        description=(
            "Set to 'in_store' to return only items available for in-store pickup."
        ),
    )


class _WalmartProductInput(BaseModel):
    """Input schema for ScavioWalmartProductTool."""

    product_id: str = Field(
        ...,
        description="Walmart item id (usItemId), e.g. '13544111159'.",
    )


class _WalmartReviewsInput(BaseModel):
    """Input schema for ScavioWalmartReviewsTool."""

    product_id: str = Field(
        ...,
        description="Walmart item id (usItemId), e.g. '13544111159'.",
    )
    page: int | None = Field(
        default=None,
        description="Reviews page, 1-based (integer >= 1). 10 reviews per page.",
    )
    sort: _WalmartReviewsSort | None = Field(
        default=None,
        description="Review sort order. Omit for Walmart's own default ordering.",
    )


class _WalmartCategoryInput(BaseModel):
    """Input schema for ScavioWalmartCategoryTool."""

    category_id: str = Field(
        ...,
        description=(
            "Walmart category id: either a leaf id ('1095191') or the full "
            "underscore-joined path ('3944_133251_1095191'). Both are accepted."
        ),
    )
    domain: Literal["com", "ca", "com.mx"] | None = Field(
        default=None,
        description=(
            "Marketplace: 'com' (US, default, 1 credit), 'ca' (1 credit), 'com.mx' (2 "
            "credits). Sets the currency and product URLs of the response."
        ),
    )
    page: int | None = Field(
        default=None,
        description="Results page, 1-based (integer >= 1). One page per call.",
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Trim the returned products to at most this many (integer >= 1). Applied "
            "after fetching, so it does not reduce the credit cost of the call."
        ),
    )
    sort_by: _WalmartSearchSortBy | None = Field(
        default=None,
        description="Result sort order. Defaults to 'best_match'.",
    )
    min_price: float | None = Field(
        default=None,
        description=(
            "Minimum price filter in the marketplace's own currency; decimals allowed "
            "(e.g. 19.99)."
        ),
    )
    max_price: float | None = Field(
        default=None,
        description=(
            "Maximum price filter in the marketplace's own currency; decimals allowed "
            "(e.g. 199.5)."
        ),
    )
    fulfillment_speed: Literal["today", "tomorrow"] | None = Field(
        default=None,
        description=(
            "Only items deliverable today, or by tomorrow. '2_days' and 'anytime' are "
            "not accepted - for anytime, omit this parameter."
        ),
    )


class _WalmartOffersInput(BaseModel):
    """Input schema for ScavioWalmartOffersTool."""

    product_id: str = Field(
        ...,
        description="Walmart item id (usItemId), e.g. '2979510112'.",
    )


class _WalmartSellerInput(BaseModel):
    """Input schema for ScavioWalmartSellerTool."""

    seller_id: str = Field(
        ...,
        description=(
            "Numeric Walmart catalog seller id, as returned in `seller_catalog_id` on "
            "a product, search or offers response (e.g. '101480084'). The GUID "
            "`seller_id` is not accepted here - it 404s."
        ),
    )


class _WalmartSellerProductsInput(BaseModel):
    """Input schema for ScavioWalmartSellerProductsTool."""

    seller_id: str = Field(
        ...,
        description=(
            "Numeric Walmart catalog seller id, as returned in `seller_catalog_id` on "
            "a product, search or offers response (e.g. '101480084'). The GUID "
            "`seller_id` 404s."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioWalmartSearchTool(ScavioBaseTool):
    """Search Walmart and get structured product rows (products, products_count and the
    store the results were priced against).
    """

    name: str = "Scavio Walmart Search"
    description: str = (
        "Search Walmart and get structured product rows (products, products_count and "
        "the store the results were priced against). Costs 1 credit on domain 'com' or "
        "'ca' and 2 credits on 'com.mx' - the price is a function of the request body, "
        "not a constant for the route."
    )
    args_schema: Type[BaseModel] = _WalmartSearchInput

    def _run(
        self,
        query: str,
        domain: Literal["com", "ca", "com.mx"] | None = None,
        page: int | None = None,
        start_page: int | None = None,
        sort_by: _WalmartSearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        fulfillment_speed: Literal["today", "tomorrow"] | None = None,
        fulfillment_type: Literal["in_store"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/walmart/search synchronously.

        Args:
            query: Product search query (1-500 characters).
            domain: Marketplace: 'com' (US, default, 1 credit), 'ca' (1 credit),
                'com.mx' (2 credits).
            page: Results page, 1-based (integer >= 1).
            start_page: Deprecated alias for page; send page instead.
            sort_by: Result sort order. Defaults to 'best_match'.
            min_price: Minimum price filter in the marketplace's own currency; decimals
                allowed (e.g. 19.99).
            max_price: Maximum price filter in the marketplace's own currency; decimals
                allowed (e.g. 199.5).
            fulfillment_speed: Only items deliverable today, or by tomorrow.
            fulfillment_type: Set to 'in_store' to return only items available for
                in-store pickup.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.walmart.search(
            query=query,
            domain=domain,
            page=page,
            start_page=start_page,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
            fulfillment_speed=fulfillment_speed,
            fulfillment_type=fulfillment_type,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        domain: Literal["com", "ca", "com.mx"] | None = None,
        page: int | None = None,
        start_page: int | None = None,
        sort_by: _WalmartSearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        fulfillment_speed: Literal["today", "tomorrow"] | None = None,
        fulfillment_type: Literal["in_store"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/walmart/search asynchronously.

        Args:
            query: Product search query (1-500 characters).
            domain: Marketplace: 'com' (US, default, 1 credit), 'ca' (1 credit),
                'com.mx' (2 credits).
            page: Results page, 1-based (integer >= 1).
            start_page: Deprecated alias for page; send page instead.
            sort_by: Result sort order. Defaults to 'best_match'.
            min_price: Minimum price filter in the marketplace's own currency; decimals
                allowed (e.g. 19.99).
            max_price: Maximum price filter in the marketplace's own currency; decimals
                allowed (e.g. 199.5).
            fulfillment_speed: Only items deliverable today, or by tomorrow.
            fulfillment_type: Set to 'in_store' to return only items available for
                in-store pickup.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.walmart.search(
            query=query,
            domain=domain,
            page=page,
            start_page=start_page,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
            fulfillment_speed=fulfillment_speed,
            fulfillment_type=fulfillment_type,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioWalmartProductTool(ScavioBaseTool):
    """Full detail for a single Walmart product: price, rating, images, specifications,
    availability and seller.
    """

    name: str = "Scavio Walmart Product"
    description: str = (
        "Full detail for a single Walmart product: price, rating, images, "
        "specifications, availability and seller. US marketplace only - walmart.ca "
        "product pages could not be fetched at all, so this endpoint takes no domain. "
        "Costs 1 credit. Walmart is body-priced through `domain`, but this endpoint "
        "takes no domain, so it is always 1."
    )
    args_schema: Type[BaseModel] = _WalmartProductInput

    def _run(self, product_id: str, **kwargs: Any) -> str:
        """Call /api/v1/walmart/product synchronously.

        Args:
            product_id: Walmart item id (usItemId), e.g. '13544111159'.

        Returns:
            JSON-serialised product details.
        """
        raw = self.client.walmart.product(product_id=product_id)
        return self._format_response(raw)

    async def _arun(self, product_id: str, **kwargs: Any) -> str:
        """Call /api/v1/walmart/product asynchronously.

        Args:
            product_id: Walmart item id (usItemId), e.g. '13544111159'.

        Returns:
            JSON-serialised product details.
        """
        raw = await self.async_client.walmart.product(product_id=product_id)
        return self._format_response(raw)


class ScavioWalmartReviewsTool(ScavioBaseTool):
    """Customer reviews for a Walmart product with ratings, text, author, date and the
    rating breakdown.
    """

    name: str = "Scavio Walmart Reviews"
    description: str = (
        "Customer reviews for a Walmart product with ratings, text, author, date and "
        "the rating breakdown. 10 reviews per page; paginate with page. Costs 1 "
        "credit. Walmart is body-priced through `domain`, but this endpoint takes no "
        "domain, so it is always 1."
    )
    args_schema: Type[BaseModel] = _WalmartReviewsInput

    def _run(
        self,
        product_id: str,
        page: int | None = None,
        sort: _WalmartReviewsSort | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/walmart/reviews synchronously.

        Args:
            product_id: Walmart item id (usItemId), e.g. '13544111159'.
            page: Reviews page, 1-based (integer >= 1).
            sort: Review sort order. Omit for Walmart's own default ordering.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.walmart.reviews(product_id=product_id, page=page, sort=sort)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        product_id: str,
        page: int | None = None,
        sort: _WalmartReviewsSort | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/walmart/reviews asynchronously.

        Args:
            product_id: Walmart item id (usItemId), e.g. '13544111159'.
            page: Reviews page, 1-based (integer >= 1).
            sort: Review sort order. Omit for Walmart's own default ordering.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.walmart.reviews(
            product_id=product_id,
            page=page,
            sort=sort,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)


class ScavioWalmartCategoryTool(ScavioBaseTool):
    """Products within a Walmart category, in the same product shape as search."""

    name: str = "Scavio Walmart Category"
    description: str = (
        "Products within a Walmart category, in the same product shape as search. "
        "Costs 1 credit on domain 'com' or 'ca' and 2 credits on 'com.mx' - the price "
        "is a function of the request body, not a constant for the route."
    )
    args_schema: Type[BaseModel] = _WalmartCategoryInput

    def _run(
        self,
        category_id: str,
        domain: Literal["com", "ca", "com.mx"] | None = None,
        page: int | None = None,
        limit: int | None = None,
        sort_by: _WalmartSearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        fulfillment_speed: Literal["today", "tomorrow"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/walmart/category synchronously.

        Args:
            category_id: Walmart category id: either a leaf id ('1095191') or the full
                underscore-joined path ('3944_133251_1095191').
            domain: Marketplace: 'com' (US, default, 1 credit), 'ca' (1 credit),
                'com.mx' (2 credits).
            page: Results page, 1-based (integer >= 1).
            limit: Trim the returned products to at most this many (integer >= 1).
            sort_by: Result sort order. Defaults to 'best_match'.
            min_price: Minimum price filter in the marketplace's own currency; decimals
                allowed (e.g. 19.99).
            max_price: Maximum price filter in the marketplace's own currency; decimals
                allowed (e.g. 199.5).
            fulfillment_speed: Only items deliverable today, or by tomorrow.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.walmart.category(
            category_id=category_id,
            domain=domain,
            page=page,
            limit=limit,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
            fulfillment_speed=fulfillment_speed,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        category_id: str,
        domain: Literal["com", "ca", "com.mx"] | None = None,
        page: int | None = None,
        limit: int | None = None,
        sort_by: _WalmartSearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        fulfillment_speed: Literal["today", "tomorrow"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/walmart/category asynchronously.

        Args:
            category_id: Walmart category id: either a leaf id ('1095191') or the full
                underscore-joined path ('3944_133251_1095191').
            domain: Marketplace: 'com' (US, default, 1 credit), 'ca' (1 credit),
                'com.mx' (2 credits).
            page: Results page, 1-based (integer >= 1).
            limit: Trim the returned products to at most this many (integer >= 1).
            sort_by: Result sort order. Defaults to 'best_match'.
            min_price: Minimum price filter in the marketplace's own currency; decimals
                allowed (e.g. 19.99).
            max_price: Maximum price filter in the marketplace's own currency; decimals
                allowed (e.g. 199.5).
            fulfillment_speed: Only items deliverable today, or by tomorrow.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.walmart.category(
            category_id=category_id,
            domain=domain,
            page=page,
            limit=limit,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
            fulfillment_speed=fulfillment_speed,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioWalmartOffersTool(ScavioBaseTool):
    """The buy-box offer for a Walmart product: price, seller, condition and buy-box
    flag.
    """

    name: str = "Scavio Walmart Offers"
    description: str = (
        "The buy-box offer for a Walmart product: price, seller, condition and buy-box "
        "flag. BUY-BOX SELLER ONLY - this is not the full offer list, and there is no "
        "way to page through the other sellers. Costs 1 credit. Walmart is body-priced "
        "through `domain`, but this endpoint takes no domain, so it is always 1."
    )
    args_schema: Type[BaseModel] = _WalmartOffersInput

    def _run(self, product_id: str, **kwargs: Any) -> str:
        """Call /api/v1/walmart/offers synchronously.

        Args:
            product_id: Walmart item id (usItemId), e.g. '2979510112'.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.walmart.offers(product_id=product_id)
        raw = self._truncate_nested(raw, "data", "offers")
        return self._format_response(raw)

    async def _arun(self, product_id: str, **kwargs: Any) -> str:
        """Call /api/v1/walmart/offers asynchronously.

        Args:
            product_id: Walmart item id (usItemId), e.g. '2979510112'.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.walmart.offers(product_id=product_id)
        raw = self._truncate_nested(raw, "data", "offers")
        return self._format_response(raw)


class ScavioWalmartSellerTool(ScavioBaseTool):
    """Marketplace seller storefront: name, rating, review count, Pro Seller badge and
    business details.
    """

    name: str = "Scavio Walmart Seller"
    description: str = (
        "Marketplace seller storefront: name, rating, review count, Pro Seller badge "
        "and business details. Costs 1 credit. Walmart is body-priced through "
        "`domain`, but this endpoint takes no domain, so it is always 1."
    )
    args_schema: Type[BaseModel] = _WalmartSellerInput

    def _run(self, seller_id: str, **kwargs: Any) -> str:
        """Call /api/v1/walmart/seller synchronously.

        Args:
            seller_id: Numeric Walmart catalog seller id, as returned in
                `seller_catalog_id` on a product, search or offers response (e.g.
                '101480084').

        Returns:
            JSON-serialised results.
        """
        raw = self.client.walmart.seller(seller_id=seller_id)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(self, seller_id: str, **kwargs: Any) -> str:
        """Call /api/v1/walmart/seller asynchronously.

        Args:
            seller_id: Numeric Walmart catalog seller id, as returned in
                `seller_catalog_id` on a product, search or offers response (e.g.
                '101480084').

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.walmart.seller(seller_id=seller_id)
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)


class ScavioWalmartSellerProductsTool(ScavioBaseTool):
    """A marketplace seller's catalog."""

    name: str = "Scavio Walmart Seller Products"
    description: str = (
        "A marketplace seller's catalog. Roughly the first 40 items are "
        "server-rendered and returned; total_count reports the seller's real catalog "
        "size. There is no pagination - the rest of the catalog is not reachable. "
        "Costs 1 credit. Walmart is body-priced through `domain`, but this endpoint "
        "takes no domain, so it is always 1."
    )
    args_schema: Type[BaseModel] = _WalmartSellerProductsInput

    def _run(self, seller_id: str, **kwargs: Any) -> str:
        """Call /api/v1/walmart/seller-products synchronously.

        Args:
            seller_id: Numeric Walmart catalog seller id, as returned in
                `seller_catalog_id` on a product, search or offers response (e.g.
                '101480084').

        Returns:
            JSON-serialised results.
        """
        raw = self.client.walmart.seller_products(seller_id=seller_id)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(self, seller_id: str, **kwargs: Any) -> str:
        """Call /api/v1/walmart/seller-products asynchronously.

        Args:
            seller_id: Numeric Walmart catalog seller id, as returned in
                `seller_catalog_id` on a product, search or offers response (e.g.
                '101480084').

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.walmart.seller_products(seller_id=seller_id)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)
