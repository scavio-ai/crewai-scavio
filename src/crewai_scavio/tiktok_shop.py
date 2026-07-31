"""Scavio TikTok Shop tools for CrewAI."""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool

# The two facts every caller has to know about this product area. They are
# repeated in the tool descriptions so an agent reading only the tool manifest
# still sees them.
PRODUCT_COVERAGE_NOTE = (
    "Only about 44% of the product ids returned by the TikTok Shop search tool "
    "resolve on the product detail tool. Upstream has no detail data for the "
    "rest, so a not-found result is a normal outcome rather than an error: skip "
    "that product instead of retrying. Search is a listing source, not the "
    "first leg of a reliable search-then-detail pipeline."
)
PRODUCT_PRICE_NOTE = (
    "The product detail tool does NOT return a price -- upstream masks it on "
    "the product page, so price.current and price.original come back null. "
    "Exact prices are returned by the TikTok Shop search, shop products and "
    "category products tools; read prices from those."
)

Region = Literal["US", "GB", "SG", "MY", "PH", "TH", "VN", "ID"]
ListingRegion = Literal["US", "GB"]


def _is_not_found(err: Exception) -> bool:
    """Report whether ``err`` is a TikTok Shop 404.

    A 404 here means the provider answered and there is genuinely no record:
    the id does not resolve, the shop has no products, or the link is dead.
    That is a determinate answer, not a failure, so it is surfaced as a
    structured result rather than raised.
    """
    return getattr(err, "status_code", None) == 404


def _not_found_payload(reason: str, guidance: str) -> dict[str, Any]:
    """Build the structured not-found result returned instead of raising."""
    return {"data": None, "not_found": True, "reason": reason, "guidance": guidance}


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _ShopSearchInput(BaseModel):
    """Input schema for ScavioTikTokShopSearchTool."""

    search: str = Field(..., description="Search keyword, 1-200 characters.")
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque cursor from a previous response's data.next_cursor. "
            "Omit for the first page."
        ),
    )


class _ShopSuggestionsInput(BaseModel):
    """Input schema for ScavioTikTokShopSearchSuggestionsTool."""

    search: str = Field(..., description="Partial search keyword, 1-100 characters.")
    region: Region | None = Field(
        default=None,
        description="Marketplace region (default US). All 8 regions work here.",
    )


class _ShopProductInput(BaseModel):
    """Input schema for ScavioTikTokShopProductTool."""

    product_id: str = Field(..., description="TikTok Shop product id, 6-25 digits.")
    region: Region | None = Field(
        default=None, description="Marketplace region (default US)."
    )


class _ShopProductReviewsInput(BaseModel):
    """Input schema for ScavioTikTokShopProductReviewsTool."""

    product_id: str = Field(..., description="TikTok Shop product id, 6-25 digits.")
    page: int | None = Field(
        default=None, description="1-based page number, 1-500 (default 1)."
    )
    page_size: int | None = Field(
        default=None, description="Reviews per page, 1-200 (default 20)."
    )
    sort: Literal["relevant", "recent"] | None = Field(
        default=None,
        description=(
            '"relevant" (default) returns text-complete, image-heavy reviews. '
            '"recent" is fresher but far more text-sparse.'
        ),
    )
    rating: int | None = Field(
        default=None, description="Only reviews with this star rating, 1-5."
    )
    has_media: bool | None = Field(
        default=None, description="Only reviews with a photo or video."
    )
    verified_only: bool | None = Field(
        default=None,
        description=(
            "Only verified purchases. Upstream allows one filter at a time, so "
            "this is ignored when has_media is true; data.filters_applied "
            "echoes what was really applied."
        ),
    )
    region: Region | None = Field(
        default=None, description="Marketplace region (default US)."
    )


class _ShopCategoriesInput(BaseModel):
    """Input schema for ScavioTikTokShopCategoriesTool. Takes no parameters."""


class _ShopCategoryProductsInput(BaseModel):
    """Input schema for ScavioTikTokShopCategoryProductsTool."""

    category_id: str = Field(
        ...,
        description=(
            "Category id from the TikTok Shop categories tool. "
            "Level 1 and level 2 ids both work."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque cursor from a previous response's data.next_cursor. "
            "Omit for the first page."
        ),
    )
    region: ListingRegion | None = Field(
        default=None,
        description=(
            "Marketplace region (default US). Category listings are served for "
            "US and GB only."
        ),
    )


class _ShopShopProductsInput(BaseModel):
    """Input schema for ScavioTikTokShopShopProductsTool."""

    shop_id: str = Field(
        ...,
        description=(
            "TikTok Shop seller id, 6-25 digits "
            "(also called seller_id elsewhere on TikTok)."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque cursor from a previous response's data.next_cursor. "
            "Omit for the first page."
        ),
    )
    region: Region | None = Field(
        default=None, description="Marketplace region (default US)."
    )


class _ShopResolveInput(BaseModel):
    """Input schema for ScavioTikTokShopResolveTool."""

    url: str = Field(
        ...,
        description=(
            "A TikTok Shop URL or share link. Accepted: shop.tiktok.com product "
            "or store pages, tiktok.com/view/product or /view/shop links, "
            "affiliate-*.tiktok.com share links, and vt.tiktok.com or "
            "tiktok.com/t short links."
        ),
    )


# ---------------------------------------------------------------------------
# 1. Search
# ---------------------------------------------------------------------------


class ScavioTikTokShopSearchTool(ScavioBaseTool):
    """Search TikTok Shop products by keyword (US catalog).

    Returns up to 30 product cards per page with exact prices, ratings,
    sold counts and shop details. Paginate with data.next_cursor and dedupe
    by product_id across pages, which can overlap. data.degraded is true when
    the retry budget was exhausted and the page came back short -- a thin page,
    not the end of results.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Shop Search"
    description: str = (
        "Search TikTok Shop products by keyword (US catalog only). Returns up "
        "to 30 products per page with exact prices, ratings, sold counts and "
        "shop details. Paginate with data.next_cursor and dedupe by product_id "
        "across pages. Product ids returned here are not guaranteed to resolve "
        "on the TikTok Shop product tool: only about 44% do, so treat this as a "
        "listing source, not the first leg of a search-then-detail pipeline. "
        "This tool returns exact prices; the product detail tool does not."
    )
    args_schema: Type[BaseModel] = _ShopSearchInput

    def _run(self, search: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Execute a synchronous TikTok Shop product search.

        Args:
            search: Search keyword.
            cursor: Opaque pagination cursor from a previous response.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.tiktok_shop.search(search, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(self, search: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Execute an asynchronous TikTok Shop product search.

        Args:
            search: Search keyword.
            cursor: Opaque pagination cursor from a previous response.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.tiktok_shop.search(search, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 2. Search Suggestions
# ---------------------------------------------------------------------------


class ScavioTikTokShopSearchSuggestionsTool(ScavioBaseTool):
    """Keyword autocomplete and expansion for a partial TikTok Shop query.

    Returns data.suggestions, a list of plain strings -- upstream provides no
    search volume and no score, so none is invented. Suggestions are not
    guaranteed prefix matches: a misspelling returns typo corrections, and
    results can include brand and shop names.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Shop Search Suggestions"
    description: str = (
        "Keyword autocomplete and expansion for a partial TikTok Shop query, "
        "across 8 marketplace regions. Returns a plain list of suggestion "
        "strings with no search volume or score. Suggestions are not guaranteed "
        "prefix matches: a misspelling returns typo corrections, and results "
        "can include brand and shop names."
    )
    args_schema: Type[BaseModel] = _ShopSuggestionsInput

    def _run(self, search: str, region: str | None = None, **kwargs: Any) -> str:
        """Execute a synchronous keyword suggestion lookup.

        Args:
            search: Partial search keyword.
            region: Marketplace region.

        Returns:
            JSON-serialised suggestion list.
        """
        raw = self.client.tiktok_shop.search_suggestions(search, region=region)
        return self._format_response(raw)

    async def _arun(self, search: str, region: str | None = None, **kwargs: Any) -> str:
        """Execute an asynchronous keyword suggestion lookup.

        Args:
            search: Partial search keyword.
            region: Marketplace region.

        Returns:
            JSON-serialised suggestion list.
        """
        raw = await self.async_client.tiktok_shop.search_suggestions(
            search, region=region
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 3. Product Details
# ---------------------------------------------------------------------------


class ScavioTikTokShopProductTool(ScavioBaseTool):
    """Fetch full TikTok Shop product detail.

    Returns description, images, variants with stock, shipping, the full shop
    profile, category path, breadcrumbs and up to 3 top reviews.

    Two limits worth knowing before wiring this after a search: it resolves
    only about 44% of the product ids search returns, and it carries no price
    at all because upstream masks the digits on the product page.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Shop Product"
    description: str = (
        "Fetch full TikTok Shop product detail: description, images, variants "
        "with stock, shipping, shop profile, category path and top reviews. "
        + PRODUCT_PRICE_NOTE
        + " "
        + PRODUCT_COVERAGE_NOTE
        + " A not-found answer comes back as data null with not_found true; "
        "treat it as a normal result and move on."
    )
    args_schema: Type[BaseModel] = _ShopProductInput

    def _run(self, product_id: str, region: str | None = None, **kwargs: Any) -> str:
        """Execute a synchronous product detail lookup.

        Args:
            product_id: TikTok Shop product id.
            region: Marketplace region.

        Returns:
            JSON-serialised product detail, or a structured not-found result.
        """
        try:
            raw = self.client.tiktok_shop.product(product_id, region=region)
        except Exception as err:
            if _is_not_found(err):
                return self._format_response(self._missing(product_id, err))
            raise
        return self._format_response(raw)

    async def _arun(
        self, product_id: str, region: str | None = None, **kwargs: Any
    ) -> str:
        """Execute an asynchronous product detail lookup.

        Args:
            product_id: TikTok Shop product id.
            region: Marketplace region.

        Returns:
            JSON-serialised product detail, or a structured not-found result.
        """
        try:
            raw = await self.async_client.tiktok_shop.product(product_id, region=region)
        except Exception as err:
            if _is_not_found(err):
                return self._format_response(self._missing(product_id, err))
            raise
        return self._format_response(raw)

    @staticmethod
    def _missing(product_id: str, err: Exception) -> dict[str, Any]:
        """Build the not-found payload for a product with no upstream detail."""
        return _not_found_payload(
            f"No TikTok Shop detail data upstream for product '{product_id}': {err}",
            PRODUCT_COVERAGE_NOTE + " " + PRODUCT_PRICE_NOTE,
        )


# ---------------------------------------------------------------------------
# 4. Product Reviews
# ---------------------------------------------------------------------------


class ScavioTikTokShopProductReviewsTool(ScavioBaseTool):
    """Fetch paginated TikTok Shop product reviews.

    Returns review text, images, star histogram, verified-purchase and
    incentivized flags, up to 200 rows per call. data.total_reviews drifts
    between calls minutes apart and must not be used to compute a page count --
    page with data.has_more instead. Reviewer names arrive pre-masked by the
    platform and image URLs are signed and expire.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Shop Product Reviews"
    description: str = (
        "Fetch paginated TikTok Shop product reviews with text, images, star "
        "histogram and verified-purchase flags, up to 200 per call. "
        "data.total_reviews drifts between calls and must not be used to "
        "compute a page count; page with data.has_more instead. sort='recent' "
        "is fresher but far more text-sparse than the default 'relevant'. "
        "Reviewer names are pre-masked by the platform and image URLs are "
        "signed and expire."
    )
    args_schema: Type[BaseModel] = _ShopProductReviewsInput

    def _run(
        self,
        product_id: str,
        page: int | None = None,
        page_size: int | None = None,
        sort: str | None = None,
        rating: int | None = None,
        has_media: bool | None = None,
        verified_only: bool | None = None,
        region: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous product reviews lookup.

        Args:
            product_id: TikTok Shop product id.
            page: 1-based page number.
            page_size: Reviews per page.
            sort: Review ordering.
            rating: Star-rating filter.
            has_media: Restrict to reviews with a photo or video.
            verified_only: Restrict to verified purchases.
            region: Marketplace region.

        Returns:
            JSON-serialised review page.
        """
        raw = self.client.tiktok_shop.product_reviews(
            product_id,
            page=page,
            page_size=page_size,
            sort=sort,
            rating=rating,
            has_media=has_media,
            verified_only=verified_only,
            region=region,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        product_id: str,
        page: int | None = None,
        page_size: int | None = None,
        sort: str | None = None,
        rating: int | None = None,
        has_media: bool | None = None,
        verified_only: bool | None = None,
        region: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous product reviews lookup.

        Args:
            product_id: TikTok Shop product id.
            page: 1-based page number.
            page_size: Reviews per page.
            sort: Review ordering.
            rating: Star-rating filter.
            has_media: Restrict to reviews with a photo or video.
            verified_only: Restrict to verified purchases.
            region: Marketplace region.

        Returns:
            JSON-serialised review page.
        """
        raw = await self.async_client.tiktok_shop.product_reviews(
            product_id,
            page=page,
            page_size=page_size,
            sort=sort,
            rating=rating,
            has_media=has_media,
            verified_only=verified_only,
            region=region,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 5. Categories
# ---------------------------------------------------------------------------


class ScavioTikTokShopCategoriesTool(ScavioBaseTool):
    """Fetch the global TikTok Shop category tree.

    Returns 28 top-level categories, 240 nodes, exactly two levels deep -- that
    is all upstream provides, the depth is not faked. Category ids are identical
    in every region and names are always English, so this tool takes no
    parameters. The tree is stable: cache it rather than calling it per request.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Shop Categories"
    description: str = (
        "Fetch the global TikTok Shop category tree: 28 top-level categories, "
        "240 nodes, two levels deep. Category ids are identical in every region "
        "and names are always English, so this tool takes no parameters. Feed a "
        "category_id from here into the TikTok Shop category products tool. The "
        "tree is stable; cache it."
    )
    args_schema: Type[BaseModel] = _ShopCategoriesInput

    def _run(self, **kwargs: Any) -> str:
        """Execute a synchronous category tree fetch.

        Returns:
            JSON-serialised category tree.
        """
        raw = self.client.tiktok_shop.categories()
        return self._format_response(raw)

    async def _arun(self, **kwargs: Any) -> str:
        """Execute an asynchronous category tree fetch.

        Returns:
            JSON-serialised category tree.
        """
        raw = await self.async_client.tiktok_shop.categories()
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 6. Category Products
# ---------------------------------------------------------------------------


class ScavioTikTokShopCategoryProductsTool(ScavioBaseTool):
    """List TikTok Shop products under a category id, with exact prices.

    Page size is inconsistent upstream (15 to 20 per page), so always paginate
    with data.next_cursor rather than assuming a fixed size. Category listings
    are shallow: after a few pages the source stops returning new products and
    has_more turns false, which is the end of the listing rather than an error.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Shop Category Products"
    description: str = (
        "List TikTok Shop products under a category id from the TikTok Shop "
        "categories tool, with exact prices. US and GB only. Page size is "
        "inconsistent upstream (15 to 20 per page), so paginate with "
        "data.next_cursor and never assume a fixed size. Listings are shallow: "
        "has_more turning false after a few pages is the end of the listing, "
        "not an error. This tool returns exact prices; the product detail tool "
        "does not."
    )
    args_schema: Type[BaseModel] = _ShopCategoryProductsInput

    def _run(
        self,
        category_id: str,
        cursor: str | None = None,
        region: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous category listing.

        Args:
            category_id: Category id from the categories tool.
            cursor: Opaque pagination cursor from a previous response.
            region: Marketplace region (US or GB).

        Returns:
            JSON-serialised product listing, or a structured not-found result.
        """
        try:
            raw = self.client.tiktok_shop.category_products(
                category_id, cursor=cursor, region=region
            )
        except Exception as err:
            if _is_not_found(err):
                return self._format_response(self._missing(category_id, err))
            raise
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        category_id: str,
        cursor: str | None = None,
        region: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous category listing.

        Args:
            category_id: Category id from the categories tool.
            cursor: Opaque pagination cursor from a previous response.
            region: Marketplace region (US or GB).

        Returns:
            JSON-serialised product listing, or a structured not-found result.
        """
        try:
            raw = await self.async_client.tiktok_shop.category_products(
                category_id, cursor=cursor, region=region
            )
        except Exception as err:
            if _is_not_found(err):
                return self._format_response(self._missing(category_id, err))
            raise
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    @staticmethod
    def _missing(category_id: str, err: Exception) -> dict[str, Any]:
        """Build the not-found payload for an unknown category id."""
        return _not_found_payload(
            f"No TikTok Shop products found for category '{category_id}': {err}",
            "Check the category_id against the TikTok Shop categories tool. "
            "Category listings are served for US and GB only.",
        )


# ---------------------------------------------------------------------------
# 7. Shop Products
# ---------------------------------------------------------------------------


class ScavioTikTokShopShopProductsTool(ScavioBaseTool):
    """Fetch a TikTok Shop seller's product catalog, with exact prices.

    Returns 30 product cards per page. data.shop carries only the shop id, name
    and logo: follower count, shop location and shop-level rating are not
    available from this endpoint -- the product detail tool has the full shop
    profile.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Shop Shop Products"
    description: str = (
        "Fetch a TikTok Shop seller's product catalog, 30 per page, with exact "
        "prices. Paginate with data.next_cursor. Shop follower count, location "
        "and shop-level rating are not available here -- use the TikTok Shop "
        "product detail tool for the full shop profile. This tool returns exact "
        "prices; the product detail tool does not."
    )
    args_schema: Type[BaseModel] = _ShopShopProductsInput

    def _run(
        self,
        shop_id: str,
        cursor: str | None = None,
        region: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous shop catalog listing.

        Args:
            shop_id: TikTok Shop seller id.
            cursor: Opaque pagination cursor from a previous response.
            region: Marketplace region.

        Returns:
            JSON-serialised product listing, or a structured not-found result.
        """
        try:
            raw = self.client.tiktok_shop.shop_products(
                shop_id, cursor=cursor, region=region
            )
        except Exception as err:
            if _is_not_found(err):
                return self._format_response(self._missing(shop_id, err))
            raise
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    async def _arun(
        self,
        shop_id: str,
        cursor: str | None = None,
        region: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous shop catalog listing.

        Args:
            shop_id: TikTok Shop seller id.
            cursor: Opaque pagination cursor from a previous response.
            region: Marketplace region.

        Returns:
            JSON-serialised product listing, or a structured not-found result.
        """
        try:
            raw = await self.async_client.tiktok_shop.shop_products(
                shop_id, cursor=cursor, region=region
            )
        except Exception as err:
            if _is_not_found(err):
                return self._format_response(self._missing(shop_id, err))
            raise
        raw = self._truncate_nested(raw, "data", "products")
        return self._format_response(raw)

    @staticmethod
    def _missing(shop_id: str, err: Exception) -> dict[str, Any]:
        """Build the not-found payload for an unknown or empty shop."""
        return _not_found_payload(
            f"No TikTok Shop products found for shop '{shop_id}': {err}",
            "Check the shop_id, or resolve a storefront URL with the TikTok "
            "Shop resolve tool first.",
        )


# ---------------------------------------------------------------------------
# 8. URL Resolver
# ---------------------------------------------------------------------------


class ScavioTikTokShopResolveTool(ScavioBaseTool):
    """Resolve a TikTok Shop URL or share link to a product_id or shop_id.

    Returns data.type ("product" or "shop"), the id, a canonical
    https://shop.tiktok.com/... URL, and resolved_by ("url_pattern" when the id
    was read straight out of the link, "share_link" when the link had to be
    followed). A dead or expired share link comes back as a structured
    not-found result.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Shop Resolve"
    description: str = (
        "Resolve any TikTok Shop URL or share link to a product_id or shop_id, "
        "ready to pass to the other TikTok Shop tools. Accepts shop.tiktok.com "
        "product and store pages, tiktok.com/view links, affiliate share links "
        "and vt.tiktok.com short links. Returns the id, a canonical https URL "
        "and whether it was read from the URL pattern or by following the share "
        "link. A dead link comes back as not_found."
    )
    args_schema: Type[BaseModel] = _ShopResolveInput

    def _run(self, url: str, **kwargs: Any) -> str:
        """Execute a synchronous URL resolution.

        Args:
            url: A TikTok Shop URL or share link.

        Returns:
            JSON-serialised reference, or a structured not-found result.
        """
        try:
            raw = self.client.tiktok_shop.resolve(url)
        except Exception as err:
            if _is_not_found(err):
                return self._format_response(self._missing(url, err))
            raise
        return self._format_response(raw)

    async def _arun(self, url: str, **kwargs: Any) -> str:
        """Execute an asynchronous URL resolution.

        Args:
            url: A TikTok Shop URL or share link.

        Returns:
            JSON-serialised reference, or a structured not-found result.
        """
        try:
            raw = await self.async_client.tiktok_shop.resolve(url)
        except Exception as err:
            if _is_not_found(err):
                return self._format_response(self._missing(url, err))
            raise
        return self._format_response(raw)

    @staticmethod
    def _missing(url: str, err: Exception) -> dict[str, Any]:
        """Build the not-found payload for a dead or expired link."""
        return _not_found_payload(
            f"Could not resolve '{url}': {err}",
            "The link may have expired or may not point to a product or shop. "
            "Try the canonical shop.tiktok.com URL instead.",
        )
