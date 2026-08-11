"""Scavio eBay tools for CrewAI.

1 credit flat on all three endpoints (EBAY_CREDIT_COST =
scrapedoCreditCost(1)).

- `seller` is a PROFILE endpoint -- it cannot enumerate a catalogue. The
  paginated way to list a seller's inventory is /search with `seller` set,
  which works with NO keyword.
- `sold` searches completed listings that actually sold -- the differentiating
  price-research feature and the one that deserves a doc example. On the sold
  view eBay publishes no headline count, so total_results is null.
- per_page accepts only 60, 120 or 240; eBay silently falls back to 60 for
  anything else.
- sort 'Distance: nearest first' is deliberately absent (ranks against our
  proxy exit, not the caller).
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_EbaySearchSortBy = Literal[
    "best_match", "ending_soonest", "newly_listed", "price_low",
    "price_high"
]
_EbaySearchCondition = Literal[
    "new", "open_box", "refurbished", "used", "for_parts"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _EbaySearchInput(BaseModel):
    """Input schema for ScavioEbaySearchTool."""

    query: str | None = Field(
        default=None,
        description=(
            "Keyword to search (1-500 characters). Optional: a seller-only search "
            "pages that seller's whole catalogue."
        ),
    )
    seller: str | None = Field(
        default=None,
        description=(
            "Restrict results to one seller's listings (1-64 characters), as in "
            "ebay.com/usr/<name>. Can be sent with no query."
        ),
    )
    page: int | None = Field(
        default=None,
        description="Results page, 1-based.",
    )
    sort_by: _EbaySearchSortBy | None = Field(
        default=None,
        description=(
            "Result sort order. Defaults to 'best_match'. eBay's 'Distance: nearest "
            "first' is deliberately unsupported (it ranks against our proxy exit, not "
            "the caller)."
        ),
    )
    min_price: float | None = Field(
        default=None,
        description="Minimum price, inclusive. Must be 0 or greater.",
    )
    max_price: float | None = Field(
        default=None,
        description="Maximum price, inclusive. Must be 0 or greater.",
    )
    condition: _EbaySearchCondition | None = Field(
        default=None,
        description=(
            "Item condition filter. 'refurbished' is eBay's parent condition, not one "
            "of its three graded tiers."
        ),
    )
    buying_format: Literal["auction", "buy_it_now", "best_offer"] | None = Field(
        default=None,
        description=(
            "Listing format: auction, fixed price (buy_it_now), or fixed price "
            "accepting offers (best_offer)."
        ),
    )
    free_shipping: bool | None = Field(
        default=None,
        description="Only listings with free shipping.",
    )
    sold: bool | None = Field(
        default=None,
        description=(
            "Search completed listings that actually SOLD, for price research. eBay "
            "publishes no headline count on this view, so total_results is null."
        ),
    )
    category_id: str | None = Field(
        default=None,
        description=(
            "eBay category id; must be numeric (e.g. '112529'). An unrecognised id "
            "returns the UNFILTERED set under a 200."
        ),
    )
    per_page: Literal[60, 120, 240] | None = Field(
        default=None,
        description=(
            "Listings per page: 60, 120 or 240 only. Defaults to 60; eBay silently "
            "falls back to 60 for anything else."
        ),
    )


class _EbayProductInput(BaseModel):
    """Input schema for ScavioEbayProductTool."""

    item_id: str = Field(
        ...,
        description=(
            "eBay item number (e.g. '168591664725'), or a full ebay.com/itm/... "
            "listing URL; tracking parameters on a pasted URL are discarded."
        ),
    )


class _EbaySellerInput(BaseModel):
    """Input schema for ScavioEbaySellerTool."""

    seller: str = Field(
        ...,
        description=(
            "eBay username as it appears in ebay.com/usr/<name> (1-64 characters), "
            "which is what seller_name on a search or product result returns."
        ),
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioEbaySearchTool(ScavioBaseTool):
    """Search live or SOLD eBay listings: price, condition, bids, shipping, seller,
    feedback.
    """

    name: str = "Scavio eBay Search"
    description: str = (
        "Search live or SOLD eBay listings: price, condition, bids, shipping, seller, "
        "feedback. Provide query or seller; per_page accepts only 60, 120 or 240. "
        "Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _EbaySearchInput

    def _run(
        self,
        query: str | None = None,
        seller: str | None = None,
        page: int | None = None,
        sort_by: _EbaySearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        condition: _EbaySearchCondition | None = None,
        buying_format: Literal["auction", "buy_it_now", "best_offer"] | None = None,
        free_shipping: bool | None = None,
        sold: bool | None = None,
        category_id: str | None = None,
        per_page: Literal[60, 120, 240] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/ebay/search synchronously.

        Args:
            query: Keyword to search (1-500 characters).
            seller: Restrict results to one seller's listings (1-64 characters), as in
                ebay.com/usr/<name>.
            page: Results page, 1-based.
            sort_by: Result sort order. Defaults to 'best_match'. eBay's 'Distance:
                nearest first' is deliberately unsupported (it ranks against our proxy
                exit, not the caller).
            min_price: Minimum price, inclusive. Must be 0 or greater.
            max_price: Maximum price, inclusive. Must be 0 or greater.
            condition: Item condition filter. 'refurbished' is eBay's parent condition,
                not one of its three graded tiers.
            buying_format: Listing format: auction, fixed price (buy_it_now), or fixed
                price accepting offers (best_offer).
            free_shipping: Only listings with free shipping.
            sold: Search completed listings that actually SOLD, for price research. eBay
                publishes no headline count on this view, so total_results is null.
            category_id: eBay category id; must be numeric (e.g. '112529').
            per_page: Listings per page: 60, 120 or 240 only.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.ebay.search(
            query=query,
            seller=seller,
            page=page,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
            condition=condition,
            buying_format=buying_format,
            free_shipping=free_shipping,
            sold=sold,
            category_id=category_id,
            per_page=per_page,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str | None = None,
        seller: str | None = None,
        page: int | None = None,
        sort_by: _EbaySearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        condition: _EbaySearchCondition | None = None,
        buying_format: Literal["auction", "buy_it_now", "best_offer"] | None = None,
        free_shipping: bool | None = None,
        sold: bool | None = None,
        category_id: str | None = None,
        per_page: Literal[60, 120, 240] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/ebay/search asynchronously.

        Args:
            query: Keyword to search (1-500 characters).
            seller: Restrict results to one seller's listings (1-64 characters), as in
                ebay.com/usr/<name>.
            page: Results page, 1-based.
            sort_by: Result sort order. Defaults to 'best_match'. eBay's 'Distance:
                nearest first' is deliberately unsupported (it ranks against our proxy
                exit, not the caller).
            min_price: Minimum price, inclusive. Must be 0 or greater.
            max_price: Maximum price, inclusive. Must be 0 or greater.
            condition: Item condition filter. 'refurbished' is eBay's parent condition,
                not one of its three graded tiers.
            buying_format: Listing format: auction, fixed price (buy_it_now), or fixed
                price accepting offers (best_offer).
            free_shipping: Only listings with free shipping.
            sold: Search completed listings that actually SOLD, for price research. eBay
                publishes no headline count on this view, so total_results is null.
            category_id: eBay category id; must be numeric (e.g. '112529').
            per_page: Listings per page: 60, 120 or 240 only.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.ebay.search(
            query=query,
            seller=seller,
            page=page,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
            condition=condition,
            buying_format=buying_format,
            free_shipping=free_shipping,
            sold=sold,
            category_id=category_id,
            per_page=per_page,
        )
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


class ScavioEbayProductTool(ScavioBaseTool):
    """One eBay listing in full: price, condition, images, item specifics, shipping,
    returns, auction state, seller.
    """

    name: str = "Scavio eBay Product"
    description: str = (
        "One eBay listing in full: price, condition, images, item specifics, shipping, "
        "returns, auction state, seller. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _EbayProductInput

    def _run(self, item_id: str, **kwargs: Any) -> str:
        """Call /api/v1/ebay/product synchronously.

        Args:
            item_id: eBay item number (e.g. '168591664725'), or a full ebay.com/itm/...
                listing URL; tracking parameters on a pasted URL are discarded.

        Returns:
            JSON-serialised product details.
        """
        raw = self.client.ebay.product(item_id=item_id)
        return self._format_response(raw)

    async def _arun(self, item_id: str, **kwargs: Any) -> str:
        """Call /api/v1/ebay/product asynchronously.

        Args:
            item_id: eBay item number (e.g. '168591664725'), or a full ebay.com/itm/...
                listing URL; tracking parameters on a pasted URL are discarded.

        Returns:
            JSON-serialised product details.
        """
        raw = await self.async_client.ebay.product(item_id=item_id)
        return self._format_response(raw)


class ScavioEbaySellerTool(ScavioBaseTool):
    """eBay seller profile card: store name, feedback score and %, items sold,
    followers, location, categories.
    """

    name: str = "Scavio eBay Seller"
    description: str = (
        "eBay seller profile card: store name, feedback score and %, items sold, "
        "followers, location, categories. Profile only: page a catalogue with "
        "search(seller=...). Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _EbaySellerInput

    def _run(self, seller: str, **kwargs: Any) -> str:
        """Call /api/v1/ebay/seller synchronously.

        Args:
            seller: eBay username as it appears in ebay.com/usr/<name> (1-64
                characters), which is what seller_name on a search or product result
                returns.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.ebay.seller(seller=seller)
        return self._format_response(raw)

    async def _arun(self, seller: str, **kwargs: Any) -> str:
        """Call /api/v1/ebay/seller asynchronously.

        Args:
            seller: eBay username as it appears in ebay.com/usr/<name> (1-64
                characters), which is what seller_name on a search or product result
                returns.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.ebay.seller(seller=seller)
        return self._format_response(raw)
