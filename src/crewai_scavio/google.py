"""Scavio Google tools for CrewAI.

All fourteen Google endpoints run on v2 (``/api/v2/google*``) and cost 1 credit
each. Google v1 was retired on 2026-08-04 and now answers HTTP 410, so its
parameter names -- ``light_request``, ``country_code``, ``language``,
``search_type``, ``page`` -- are gone. v2 speaks ``gl``, ``hl``, ``start``,
``google_domain`` and ``device`` instead, and the v1 response block ``results[]``
with ``url``/``content`` is now ``organic_results[]`` with ``link``/``snippet``.

Google responses are FLAT: the payload sits at the top level next to
``response_time``, ``credits_used``, ``credits_remaining`` and ``cached``.
There is no ``data`` wrapper anywhere in this family, unlike every other Scavio
product area.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool

# ---------------------------------------------------------------------------
# Shared parameter descriptions
# ---------------------------------------------------------------------------

_HL_DESCRIPTION = "UI language (ISO 639-1, e.g. 'en')."
_GL_DESCRIPTION = "Country of the search (ISO 3166-1 alpha-2, e.g. 'us')."
_GOOGLE_DOMAIN_DESCRIPTION = "Regional Google domain (e.g. 'google.co.uk')."
_LOCATION_DESCRIPTION = (
    "Canonical location name; auto-encoded to a UULE string."
)
_UULE_DESCRIPTION = (
    "Pre-encoded UULE location string (takes priority over location)."
)
_CURRENCY_DESCRIPTION = "Currency code (ISO 4217, e.g. 'USD')."


class ScavioSearchInput(BaseModel):
    """Input schema for ScavioSearchTool."""

    query: str = Field(..., description="The search query string.")
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    start: int | None = Field(
        default=None,
        description=(
            "Result offset, NOT a page number: 0 = page 1, 10 = page 2, "
            "20 = page 3, up to 990."
        ),
    )
    google_domain: str | None = Field(
        default=None, description=_GOOGLE_DOMAIN_DESCRIPTION
    )
    device: Literal["desktop", "mobile"] | None = Field(
        default=None,
        description="Device to emulate; falls back to the tool default.",
    )
    location: str | None = Field(
        default=None, description=_LOCATION_DESCRIPTION
    )
    uule: str | None = Field(default=None, description=_UULE_DESCRIPTION)
    lr: str | None = Field(
        default=None,
        description="Restrict results to one language (e.g. 'lang_en').",
    )
    cr: str | None = Field(
        default=None,
        description="Restrict results to one country (e.g. 'countryUS').",
    )
    safe: Literal["active"] | None = Field(
        default=None,
        description="SafeSearch filter; 'active' is the only value.",
    )
    filter: Literal["0", "1"] | None = Field(
        default=None,
        description=(
            "'0' returns the near-duplicate results Google normally omits; "
            "'1' keeps the filter on."
        ),
    )
    time_period: Literal[
        "last_hour", "last_day", "last_week", "last_month", "last_year"
    ] | None = Field(
        default=None,
        description="Restrict results to a recent time window.",
    )
    nfpr: bool | None = Field(
        default=None,
        description=(
            "True searches the query verbatim, without Google's spelling "
            "correction."
        ),
    )
    include_html: bool | None = Field(
        default=None,
        description="Include the raw Google HTML in the response (large).",
    )
    resolve_ai_overview: bool | None = Field(
        default=None,
        description=(
            "Resolve a deferred AI Overview with a second fetch "
            "(server default True)."
        ),
    )


# Native v2 params an agent may set per call. Anything set here wins over the
# developer-set constructor defaults below.
_SEARCH_PARAM_NAMES: tuple[str, ...] = (
    "gl",
    "hl",
    "start",
    "google_domain",
    "device",
    "location",
    "uule",
    "lr",
    "cr",
    "safe",
    "filter",
    "time_period",
    "nfpr",
    "include_html",
    "resolve_ai_overview",
)

# Mapping from include_* field names to their corresponding response keys.
_INCLUDE_FIELD_TO_KEY: dict[str, str] = {
    "include_knowledge_graph": "knowledge_graph",
    "include_questions": "questions",
    "include_related": "related",
    "include_maps_results": "maps_results",
    "include_ai_overviews": "ai_overviews",
    "include_local_results": "local_results",
    "include_top_stories": "top_stories",
    "include_hotel_results": "hotel_results",
    "include_news_results": "news_results",
    "include_shopping_ads": "shopping_ads",
    "include_top_ads": "top_ads",
    "include_bottom_ads": "bottom_ads",
}

# Response keys that contain truncatable lists.
_LIST_KEYS: list[str] = [
    "organic_results",
    "maps_results",
    "local_results",
    "news_results",
]


class ScavioSearchTool(ScavioBaseTool):
    """Web search tool powered by the Scavio Google Search API (v2).

    Every native v2 param lives in ``args_schema`` so an agent can vary it per
    call. The attributes below are developer-set defaults used when the agent
    omits the matching argument; ``country_code``, ``language`` and ``page``
    are v1 spellings kept for backwards compatibility and seed ``gl``, ``hl``
    and ``start``.

    Attributes:
        country_code: Two-letter country code for localised results (maps to gl).
        language: Language code for result language preference (maps to hl).
        page: 1-based result page; page 2+ maps to a result offset (start).
        device: Device type to emulate.
        include_knowledge_graph: Include knowledge-graph panel in response.
        include_questions: Include "People also ask" questions.
        include_related: Include related searches.
        include_maps_results: Include map-pack results.
        include_ai_overviews: Include AI overview snippets.
        include_local_results: Include local business results.
        include_top_stories: Include top-stories carousel.
        include_hotel_results: Include hotel results.
        include_news_results: Include news results.
        include_shopping_ads: Include shopping ad results.
        include_top_ads: Include top ad results.
        include_bottom_ads: Include bottom ad results.
        nfpr: Disable automatic spelling correction.
    """

    name: str = "Scavio Search"
    description: str = (
        "Search the web using the Scavio Google Search API (v2). "
        "Returns organic results (title, link, snippet), knowledge graph, "
        "related questions, and more depending on configuration. "
        "Costs 1 credit per search."
    )
    args_schema: Type[BaseModel] = ScavioSearchInput

    country_code: str | None = None
    language: str | None = None
    page: int | None = None
    device: Literal["desktop", "mobile"] = "desktop"
    include_knowledge_graph: bool = True
    include_questions: bool = True
    include_related: bool = False
    include_maps_results: bool = False
    include_ai_overviews: bool = False
    include_local_results: bool = False
    include_top_stories: bool = False
    include_hotel_results: bool = False
    include_news_results: bool = False
    include_shopping_ads: bool = False
    include_top_ads: bool = False
    include_bottom_ads: bool = False
    nfpr: bool = False

    def _build_params(self, **overrides: Any) -> dict[str, Any]:
        """Layer per-call arguments over the developer-set defaults.

        Args:
            **overrides: Native v2 params supplied for this call.

        Returns:
            Keyword arguments for ``client.google.search``.
        """
        params: dict[str, Any] = {
            "device": self.device,
            "nfpr": self.nfpr,
        }
        if self.country_code:
            params["gl"] = self.country_code
        if self.language:
            params["hl"] = self.language
        if self.page and self.page > 1:
            params["start"] = (self.page - 1) * 10
        for name in _SEARCH_PARAM_NAMES:
            value = overrides.get(name)
            if value is not None:
                params[name] = value
        return params

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous Google search.

        Args:
            query: The search query string.
            **kwargs: Optional native v2 locale / paging / filter params.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.google.search(
            query=query, **self._build_params(**kwargs)
        )
        return self._format_response(self._post_process(raw))

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous Google search.

        Args:
            query: The search query string.
            **kwargs: Optional native v2 locale / paging / filter params.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.google.search(
            query=query, **self._build_params(**kwargs)
        )
        return self._format_response(self._post_process(raw))

    def _post_process(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Truncate list fields and strip disabled include sections.

        Args:
            raw: Raw response dictionary from the API.

        Returns:
            Processed response dictionary.
        """
        for key in _LIST_KEYS:
            raw = self._truncate_results(raw, key)

        for field_name, response_key in _INCLUDE_FIELD_TO_KEY.items():
            if not getattr(self, field_name, False):
                raw.pop(response_key, None)

        return raw


# ---------------------------------------------------------------------------
# Input schemas for the rest of the Google v2 family
# ---------------------------------------------------------------------------

class ScavioGoogleAiModeInput(BaseModel):
    """Input schema for ScavioGoogleAiModeTool."""

    query: str = Field(..., description="Question or prompt, 1-500 characters.")
    device: Literal["desktop", "mobile"] | None = Field(
        default=None, description="Device to emulate."
    )
    include_html: bool | None = Field(
        default=None, description="Include the raw Google HTML in the response."
    )
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    google_domain: str | None = Field(
        default=None, description=_GOOGLE_DOMAIN_DESCRIPTION
    )
    location: str | None = Field(
        default=None, description=_LOCATION_DESCRIPTION
    )
    uule: str | None = Field(default=None, description=_UULE_DESCRIPTION)
    safe: Literal["active"] | None = Field(
        default=None, description="SafeSearch filter."
    )


class ScavioGoogleMapsSearchInput(BaseModel):
    """Input schema for ScavioGoogleMapsSearchTool."""

    query: str = Field(..., description="Search query, 1-500 characters.")
    start: int | None = Field(
        default=None,
        description="Result offset; must be a multiple of 20 (0, 20, 40, ...).",
    )
    ll: str | None = Field(
        default=None,
        description=(
            "Map center as '@lat,lng,zoomz'. Maps localises by map center, "
            "not gl -- when omitted a centroid is derived from gl."
        ),
    )
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    google_domain: str | None = Field(
        default=None, description=_GOOGLE_DOMAIN_DESCRIPTION
    )


class ScavioGoogleMapsPlaceInput(BaseModel):
    """Input schema for ScavioGoogleMapsPlaceTool."""

    place_id: str | None = Field(
        default=None, description="Place ID (ChIJ...)."
    )
    data_cid: str | None = Field(default=None, description="Numeric CID.")


class ScavioGoogleMapsReviewsInput(BaseModel):
    """Input schema for ScavioGoogleMapsReviewsTool."""

    data_id: str | None = Field(
        default=None, description="Data ID in the form 0xHEX:0xHEX."
    )
    place_id: str | None = Field(
        default=None, description="Place ID (ChIJ...)."
    )
    num: int | None = Field(
        default=None, description="Reviews per page (1-20)."
    )
    next_page_token: str | None = Field(
        default=None, description="Pagination cursor from a previous response."
    )
    sort_by: Literal[
        "relevance", "newest", "highest_rating", "lowest_rating"
    ] | None = Field(default=None, description="Review sort order.")
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    google_domain: str | None = Field(
        default=None, description=_GOOGLE_DOMAIN_DESCRIPTION
    )


class ScavioGoogleShoppingInput(BaseModel):
    """Input schema for ScavioGoogleShoppingTool."""

    query: str = Field(
        ..., description="Product search query, 1-500 characters."
    )
    device: Literal["desktop", "mobile"] | None = Field(
        default=None, description="Device to emulate."
    )
    start: int | None = Field(default=None, description="Result offset.")
    min_price: int | None = Field(
        default=None, description="Minimum price filter."
    )
    max_price: int | None = Field(
        default=None, description="Maximum price filter."
    )
    sort_by: int | None = Field(
        default=None,
        description="0 = relevance, 1 = price ascending, 2 = price descending.",
    )
    free_shipping: bool | None = Field(
        default=None, description="Only items with free shipping."
    )
    on_sale: bool | None = Field(
        default=None, description="Only items on sale."
    )
    shoprs: str | None = Field(
        default=None, description="Opaque Google Shopping filter token."
    )
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    google_domain: str | None = Field(
        default=None, description=_GOOGLE_DOMAIN_DESCRIPTION
    )
    location: str | None = Field(
        default=None, description=_LOCATION_DESCRIPTION
    )
    uule: str | None = Field(default=None, description=_UULE_DESCRIPTION)


class ScavioGoogleShoppingProductInput(BaseModel):
    """Input schema for ScavioGoogleShoppingProductTool."""

    catalog_id: str | None = Field(
        default=None, description="Durable product catalog id."
    )
    query: str | None = Field(
        default=None,
        description="Product query; required when catalog_id is set.",
    )
    immersive_product_page_token: str | None = Field(
        default=None, description="Immersive product page token."
    )
    page_token: str | None = Field(
        default=None, description="Alias for immersive_product_page_token."
    )
    product_id: str | None = Field(default=None, description="Product id.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(
        default=None, description="Device to emulate."
    )
    google_domain: str | None = Field(
        default=None, description=_GOOGLE_DOMAIN_DESCRIPTION
    )
    sort_by: Literal[
        "base_price", "total_price", "promotion", "seller_rating"
    ] | None = Field(default=None, description="Seller sort order.")
    load_all_stores: bool | None = Field(
        default=None, description="Load all available stores."
    )
    more_stores: bool | None = Field(
        default=None, description="Fetch additional stores."
    )
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    location: str | None = Field(
        default=None, description=_LOCATION_DESCRIPTION
    )
    uule: str | None = Field(default=None, description=_UULE_DESCRIPTION)


class ScavioGoogleShoppingStoresInput(BaseModel):
    """Input schema for ScavioGoogleShoppingStoresTool."""

    catalog_id: str = Field(
        ...,
        description=(
            "Durable product catalog id -- must be the same one used on the "
            "shopping product call."
        ),
    )
    next_page_token: str = Field(
        ...,
        description="Continuation cursor from a shopping product response.",
    )


class ScavioGoogleFlightsInput(BaseModel):
    """Input schema for ScavioGoogleFlightsTool."""

    departure_id: str = Field(
        ..., description="Departure IATA code(s); comma-separated allowed."
    )
    arrival_id: str = Field(
        ..., description="Arrival IATA code(s); comma-separated allowed."
    )
    outbound_date: str = Field(
        ..., description="Outbound date (YYYY-MM-DD)."
    )
    type: int | None = Field(
        default=None,
        description="1 = round trip, 2 = one way, 3 = multi-city.",
    )
    return_date: str | None = Field(
        default=None,
        description="Return date (YYYY-MM-DD); required when type=1.",
    )
    adults: int | None = Field(
        default=None, description="Number of adults (1-9)."
    )
    children: int | None = Field(
        default=None, description="Number of children (0-9)."
    )
    infants_in_seat: int | None = Field(
        default=None, description="Infants in seat (0-4)."
    )
    infants_on_lap: int | None = Field(
        default=None, description="Infants on lap (0-4)."
    )
    travel_class: int | None = Field(
        default=None,
        description="1 = economy, 2 = premium, 3 = business, 4 = first.",
    )
    stops: int | None = Field(
        default=None,
        description="0 = any, 1 = nonstop, 2 = <=1 stop, 3 = <=2 stops.",
    )
    sort_by: int | None = Field(
        default=None,
        description=(
            "1 = top, 2 = price, 3 = departure, 4 = arrival, 5 = duration, "
            "6 = emissions."
        ),
    )
    include_airlines: str | None = Field(
        default=None,
        description="Comma-separated airline codes/alliances to include.",
    )
    exclude_airlines: str | None = Field(
        default=None,
        description="Comma-separated airline codes/alliances to exclude.",
    )
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    currency: str | None = Field(
        default=None, description=_CURRENCY_DESCRIPTION
    )


class ScavioGoogleHotelsInput(BaseModel):
    """Input schema for ScavioGoogleHotelsTool."""

    query: str = Field(
        ..., description="Search query; use a '<City> hotels' form."
    )
    check_in_date: str = Field(
        ..., description="Check-in date (YYYY-MM-DD)."
    )
    check_out_date: str = Field(
        ..., description="Check-out date (YYYY-MM-DD)."
    )
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    currency: str | None = Field(
        default=None, description=_CURRENCY_DESCRIPTION
    )
    sort_by: int | None = Field(
        default=None,
        description="3 = lowest price, 8 = highest rating, 13 = most reviewed.",
    )
    min_price: int | None = Field(
        default=None, description="Minimum nightly price."
    )
    max_price: int | None = Field(
        default=None, description="Maximum nightly price."
    )
    rating: int | None = Field(
        default=None, description="7 = 3.5+, 8 = 4.0+, 9 = 4.5+."
    )
    hotel_class: str | None = Field(
        default=None, description="Comma-separated star ratings (2-5)."
    )
    amenities: str | None = Field(
        default=None, description="Comma-separated amenity ids."
    )
    property_types: str | None = Field(
        default=None,
        description=(
            "Comma-separated property-type ids (e.g. '12' for vacation "
            "rentals)."
        ),
    )
    free_cancellation: bool | None = Field(
        default=None, description="Only properties with free cancellation."
    )
    eco_certified: bool | None = Field(
        default=None, description="Only eco-certified properties."
    )
    special_offers: bool | None = Field(
        default=None, description="Only properties with special offers."
    )
    next_page_token: str | None = Field(
        default=None, description="Pagination cursor from a previous response."
    )
    limit: int | None = Field(
        default=None, description="Number of properties to return (1-20)."
    )


class ScavioGoogleHotelsDetailInput(BaseModel):
    """Input schema for ScavioGoogleHotelsDetailTool."""

    detail_token: str = Field(
        ...,
        description=(
            "Property detail_token taken from a hotels listing property."
        ),
    )
    check_in_date: str = Field(
        ..., description="Check-in date (YYYY-MM-DD)."
    )
    check_out_date: str = Field(
        ..., description="Check-out date (YYYY-MM-DD)."
    )
    currency: str | None = Field(
        default=None, description=_CURRENCY_DESCRIPTION
    )
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)


class ScavioGoogleNewsInput(BaseModel):
    """Input schema for ScavioGoogleNewsTool."""

    query: str | None = Field(default=None, description="Keyword search.")
    topic_token: str | None = Field(
        default=None, description="Browse a news topic."
    )
    section_token: str | None = Field(
        default=None, description="Browse a topic section."
    )
    story_token: str | None = Field(
        default=None, description="Fetch full coverage of a story."
    )
    publication_token: str | None = Field(
        default=None, description="Browse a publication."
    )
    kgmid: str | None = Field(
        default=None, description="Knowledge Graph entity id."
    )
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    gl: str | None = Field(default=None, description=_GL_DESCRIPTION)
    google_domain: str | None = Field(
        default=None, description=_GOOGLE_DOMAIN_DESCRIPTION
    )
    so: int | None = Field(
        default=None,
        description=(
            "Sort order: 0 = relevance, 1 = date. Only valid with query or "
            "kgmid."
        ),
    )


class ScavioGoogleTrendsInput(BaseModel):
    """Input schema for ScavioGoogleTrendsTool."""

    query: str = Field(
        ..., description="Search term(s); comma-separated for comparisons."
    )
    geo: str | None = Field(
        default=None, description="Location code (e.g. 'US', 'GB', 'US-CA')."
    )
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    date: str | None = Field(
        default=None, description="Time range (e.g. 'today 12-m', 'now 7-d')."
    )
    tz: str | None = Field(
        default=None, description="Timezone offset in minutes."
    )
    data_type: Literal[
        "TIMESERIES", "GEO_MAP", "GEO_MAP_0", "RELATED_QUERIES",
        "RELATED_TOPICS",
    ] | None = Field(default=None, description="Which trends dataset to return.")
    cat: str | None = Field(default=None, description="Category id.")
    gprop: Literal["images", "news", "youtube", "froogle"] | None = Field(
        default=None, description="Google property filter."
    )
    region: Literal["COUNTRY", "REGION", "DMA", "CITY"] | None = Field(
        default=None, description="Resolution for GEO_MAP data."
    )


class ScavioGoogleTrendingInput(BaseModel):
    """Input schema for ScavioGoogleTrendingTool."""

    geo: str = Field(..., description="Country code (e.g. 'US').")
    hl: str | None = Field(default=None, description=_HL_DESCRIPTION)
    hours: int | None = Field(
        default=None, description="Trending window: 4, 24, 48, or 168."
    )
    cat: int | None = Field(default=None, description="Category id (0-20).")
    sort: Literal["relevance", "search_volume", "recency", "title"] | None = (
        Field(default=None, description="Sort order.")
    )
    status: Literal["all", "active"] | None = Field(
        default=None, description="Filter by trend status."
    )


# ---------------------------------------------------------------------------
# 2. AI Mode
# ---------------------------------------------------------------------------

class ScavioGoogleAiModeTool(ScavioBaseTool):
    """Google AI Mode conversational answer with references.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google AI Mode"
    description: str = (
        "Ask Google AI Mode a question and get its conversational answer. "
        "Returns text_blocks, references and shopping_results at the top "
        "level (Google responses have no data wrapper). Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleAiModeInput

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous AI Mode query.

        Args:
            query: Question or prompt.
            **kwargs: Optional device / locale params.

        Returns:
            JSON-serialised AI Mode answer.
        """
        raw = self.client.google.ai_mode(query=query, **kwargs)
        raw = self._truncate_results(raw, "references")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous AI Mode query.

        Args:
            query: Question or prompt.
            **kwargs: Optional device / locale params.

        Returns:
            JSON-serialised AI Mode answer.
        """
        raw = await self.async_client.google.ai_mode(query=query, **kwargs)
        raw = self._truncate_results(raw, "references")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 3. Maps search
# ---------------------------------------------------------------------------

class ScavioGoogleMapsSearchTool(ScavioBaseTool):
    """Google Maps local business results.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Maps Search"
    description: str = (
        "Find local businesses on Google Maps. Returns local_results at the "
        "top level, each with a place_id and data_id for the place and "
        "reviews tools. start must be a multiple of 20. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleMapsSearchInput

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous Maps search.

        Args:
            query: Search query.
            **kwargs: Optional paging / locale params.

        Returns:
            JSON-serialised local results.
        """
        raw = self.client.google.maps_search(query=query, **kwargs)
        raw = self._truncate_results(raw, "local_results")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous Maps search.

        Args:
            query: Search query.
            **kwargs: Optional paging / locale params.

        Returns:
            JSON-serialised local results.
        """
        raw = await self.async_client.google.maps_search(query=query, **kwargs)
        raw = self._truncate_results(raw, "local_results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 4. Maps place
# ---------------------------------------------------------------------------

class ScavioGoogleMapsPlaceTool(ScavioBaseTool):
    """Google Maps place details.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Maps Place"
    description: str = (
        "Get full details for a Google Maps place by place_id or data_cid "
        "(one is required). Returns place_results at the top level. There "
        "are no locale params on this endpoint. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleMapsPlaceInput

    def _run(
        self,
        place_id: str | None = None,
        data_cid: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous place lookup.

        Args:
            place_id: Place ID (ChIJ...).
            data_cid: Numeric CID.

        Returns:
            JSON-serialised place details.
        """
        raw = self.client.google.maps_place(
            place_id=place_id, data_cid=data_cid
        )
        return self._format_response(raw)

    async def _arun(
        self,
        place_id: str | None = None,
        data_cid: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous place lookup.

        Args:
            place_id: Place ID (ChIJ...).
            data_cid: Numeric CID.

        Returns:
            JSON-serialised place details.
        """
        raw = await self.async_client.google.maps_place(
            place_id=place_id, data_cid=data_cid
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 5. Maps reviews
# ---------------------------------------------------------------------------

class ScavioGoogleMapsReviewsTool(ScavioBaseTool):
    """Google Maps reviews for a place.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Maps Reviews"
    description: str = (
        "Get Google Maps reviews for a place by data_id or place_id (one is "
        "required). Returns reviews, topics and pagination at the top level. "
        "num is capped at 20 per page. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleMapsReviewsInput

    def _run(self, **kwargs: Any) -> str:
        """Execute a synchronous reviews lookup.

        Args:
            **kwargs: data_id / place_id plus optional paging and locale
                params.

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.google.maps_reviews(**kwargs)
        raw = self._truncate_results(raw, "reviews")
        return self._format_response(raw)

    async def _arun(self, **kwargs: Any) -> str:
        """Execute an asynchronous reviews lookup.

        Args:
            **kwargs: data_id / place_id plus optional paging and locale
                params.

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.google.maps_reviews(**kwargs)
        raw = self._truncate_results(raw, "reviews")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 6. Shopping
# ---------------------------------------------------------------------------

class ScavioGoogleShoppingTool(ScavioBaseTool):
    """Google Shopping product listings.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Shopping"
    description: str = (
        "Search Google Shopping product listings. Returns shopping_results "
        "at the top level, each carrying a catalog_id for the shopping "
        "product tool. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleShoppingInput

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous Shopping search.

        Args:
            query: Product search query.
            **kwargs: Optional filter / locale params.

        Returns:
            JSON-serialised shopping results.
        """
        raw = self.client.google.shopping(query=query, **kwargs)
        raw = self._truncate_results(raw, "shopping_results")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous Shopping search.

        Args:
            query: Product search query.
            **kwargs: Optional filter / locale params.

        Returns:
            JSON-serialised shopping results.
        """
        raw = await self.async_client.google.shopping(query=query, **kwargs)
        raw = self._truncate_results(raw, "shopping_results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 7. Shopping product
# ---------------------------------------------------------------------------

class ScavioGoogleShoppingProductTool(ScavioBaseTool):
    """Google Shopping product detail and sellers.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Shopping Product"
    description: str = (
        "Get a Google Shopping product's detail and seller list. Requires "
        "one of catalog_id, immersive_product_page_token, page_token or "
        "product_id; catalog_id also needs query. Returns product_results "
        "with a stores list. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleShoppingProductInput

    def _run(self, **kwargs: Any) -> str:
        """Execute a synchronous product lookup.

        Args:
            **kwargs: One product identifier plus optional locale params.

        Returns:
            JSON-serialised product details.
        """
        raw = self.client.google.shopping_product(**kwargs)
        return self._format_response(raw)

    async def _arun(self, **kwargs: Any) -> str:
        """Execute an asynchronous product lookup.

        Args:
            **kwargs: One product identifier plus optional locale params.

        Returns:
            JSON-serialised product details.
        """
        raw = await self.async_client.google.shopping_product(**kwargs)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 8. Shopping product stores
# ---------------------------------------------------------------------------

class ScavioGoogleShoppingStoresTool(ScavioBaseTool):
    """More sellers for a Google Shopping product.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Shopping Stores"
    description: str = (
        "Page through additional sellers for a Google Shopping product. "
        "Both catalog_id and next_page_token are required and must come "
        "from the same shopping product call. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleShoppingStoresInput

    def _run(
        self, catalog_id: str, next_page_token: str, **kwargs: Any
    ) -> str:
        """Execute a synchronous stores lookup.

        Args:
            catalog_id: Durable product catalog id.
            next_page_token: Continuation cursor.

        Returns:
            JSON-serialised store list.
        """
        raw = self.client.google.shopping_stores(
            catalog_id=catalog_id, next_page_token=next_page_token
        )
        return self._format_response(raw)

    async def _arun(
        self, catalog_id: str, next_page_token: str, **kwargs: Any
    ) -> str:
        """Execute an asynchronous stores lookup.

        Args:
            catalog_id: Durable product catalog id.
            next_page_token: Continuation cursor.

        Returns:
            JSON-serialised store list.
        """
        raw = await self.async_client.google.shopping_stores(
            catalog_id=catalog_id, next_page_token=next_page_token
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 9. Flights
# ---------------------------------------------------------------------------

class ScavioGoogleFlightsTool(ScavioBaseTool):
    """Google Flights search.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Flights"
    description: str = (
        "Search Google Flights between two airports. Returns best_flights "
        "and other_flights at the top level. return_date is required when "
        "type=1 (round trip). Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleFlightsInput

    def _run(
        self,
        departure_id: str,
        arrival_id: str,
        outbound_date: str,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous flights search.

        Args:
            departure_id: Departure IATA code(s).
            arrival_id: Arrival IATA code(s).
            outbound_date: Outbound date (YYYY-MM-DD).
            **kwargs: Optional passenger / filter params.

        Returns:
            JSON-serialised flight itineraries.
        """
        raw = self.client.google.flights(
            departure_id=departure_id,
            arrival_id=arrival_id,
            outbound_date=outbound_date,
            **kwargs,
        )
        raw = self._truncate_results(raw, "best_flights")
        raw = self._truncate_results(raw, "other_flights")
        return self._format_response(raw)

    async def _arun(
        self,
        departure_id: str,
        arrival_id: str,
        outbound_date: str,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous flights search.

        Args:
            departure_id: Departure IATA code(s).
            arrival_id: Arrival IATA code(s).
            outbound_date: Outbound date (YYYY-MM-DD).
            **kwargs: Optional passenger / filter params.

        Returns:
            JSON-serialised flight itineraries.
        """
        raw = await self.async_client.google.flights(
            departure_id=departure_id,
            arrival_id=arrival_id,
            outbound_date=outbound_date,
            **kwargs,
        )
        raw = self._truncate_results(raw, "best_flights")
        raw = self._truncate_results(raw, "other_flights")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 10. Hotels
# ---------------------------------------------------------------------------

class ScavioGoogleHotelsTool(ScavioBaseTool):
    """Google Hotels search.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Hotels"
    description: str = (
        "Search Google Hotels for a destination and date range. Returns "
        "properties at the top level, each carrying a detail_token for the "
        "hotels detail tool. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleHotelsInput

    def _run(
        self,
        query: str,
        check_in_date: str,
        check_out_date: str,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous hotels search.

        Args:
            query: Search query, '<City> hotels' form.
            check_in_date: Check-in date (YYYY-MM-DD).
            check_out_date: Check-out date (YYYY-MM-DD).
            **kwargs: Optional filter / locale params.

        Returns:
            JSON-serialised hotel properties.
        """
        raw = self.client.google.hotels(
            query=query,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            **kwargs,
        )
        raw = self._truncate_results(raw, "properties")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        check_in_date: str,
        check_out_date: str,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous hotels search.

        Args:
            query: Search query, '<City> hotels' form.
            check_in_date: Check-in date (YYYY-MM-DD).
            check_out_date: Check-out date (YYYY-MM-DD).
            **kwargs: Optional filter / locale params.

        Returns:
            JSON-serialised hotel properties.
        """
        raw = await self.async_client.google.hotels(
            query=query,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            **kwargs,
        )
        raw = self._truncate_results(raw, "properties")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 11. Hotels detail
# ---------------------------------------------------------------------------

class ScavioGoogleHotelsDetailTool(ScavioBaseTool):
    """Google Hotels property details.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Hotels Detail"
    description: str = (
        "Get details and booking sources for a single hotel property, using "
        "the detail_token from a hotels listing plus the same date range. "
        "Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleHotelsDetailInput

    def _run(
        self,
        detail_token: str,
        check_in_date: str,
        check_out_date: str,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous hotel detail lookup.

        Args:
            detail_token: Property detail token from a hotels listing.
            check_in_date: Check-in date (YYYY-MM-DD).
            check_out_date: Check-out date (YYYY-MM-DD).
            **kwargs: Optional currency / locale params.

        Returns:
            JSON-serialised property details.
        """
        raw = self.client.google.hotels_detail(
            detail_token=detail_token,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            **kwargs,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        detail_token: str,
        check_in_date: str,
        check_out_date: str,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous hotel detail lookup.

        Args:
            detail_token: Property detail token from a hotels listing.
            check_in_date: Check-in date (YYYY-MM-DD).
            check_out_date: Check-out date (YYYY-MM-DD).
            **kwargs: Optional currency / locale params.

        Returns:
            JSON-serialised property details.
        """
        raw = await self.async_client.google.hotels_detail(
            detail_token=detail_token,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            **kwargs,
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 12. News
# ---------------------------------------------------------------------------

class ScavioGoogleNewsTool(ScavioBaseTool):
    """Google News results.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google News"
    description: str = (
        "Get Google News results. Supply EXACTLY ONE driver: query, "
        "topic_token, section_token, story_token, publication_token or "
        "kgmid -- two or more is a hard error. Returns news_results at the "
        "top level. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleNewsInput

    def _run(self, **kwargs: Any) -> str:
        """Execute a synchronous news lookup.

        Args:
            **kwargs: Exactly one driver plus optional locale params.

        Returns:
            JSON-serialised news results.
        """
        raw = self.client.google.news(**kwargs)
        raw = self._truncate_results(raw, "news_results")
        return self._format_response(raw)

    async def _arun(self, **kwargs: Any) -> str:
        """Execute an asynchronous news lookup.

        Args:
            **kwargs: Exactly one driver plus optional locale params.

        Returns:
            JSON-serialised news results.
        """
        raw = await self.async_client.google.news(**kwargs)
        raw = self._truncate_results(raw, "news_results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 13. Trends
# ---------------------------------------------------------------------------

class ScavioGoogleTrendsTool(ScavioBaseTool):
    """Google Trends interest data.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Trends"
    description: str = (
        "Get Google Trends interest data for one or more terms (comma-"
        "separate to compare). Returns interest_over_time and "
        "interest_by_region at the top level, depending on data_type. "
        "Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleTrendsInput

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous trends lookup.

        Args:
            query: Search term(s).
            **kwargs: Optional geo / date / data_type params.

        Returns:
            JSON-serialised trends data.
        """
        raw = self.client.google.trends(query=query, **kwargs)
        raw = self._truncate_results(raw, "interest_by_region")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous trends lookup.

        Args:
            query: Search term(s).
            **kwargs: Optional geo / date / data_type params.

        Returns:
            JSON-serialised trends data.
        """
        raw = await self.async_client.google.trends(query=query, **kwargs)
        raw = self._truncate_results(raw, "interest_by_region")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 14. Trending now
# ---------------------------------------------------------------------------

class ScavioGoogleTrendingTool(ScavioBaseTool):
    """Google Trending Now for a country.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Google Trending"
    description: str = (
        "Get Google Trending Now searches for a country. geo is required "
        "(e.g. 'US'). Returns trends at the top level. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioGoogleTrendingInput

    def _run(self, geo: str, **kwargs: Any) -> str:
        """Execute a synchronous trending lookup.

        Args:
            geo: Country code.
            **kwargs: Optional window / category / sort params.

        Returns:
            JSON-serialised trending searches.
        """
        raw = self.client.google.trending(geo=geo, **kwargs)
        raw = self._truncate_results(raw, "trends")
        return self._format_response(raw)

    async def _arun(self, geo: str, **kwargs: Any) -> str:
        """Execute an asynchronous trending lookup.

        Args:
            geo: Country code.
            **kwargs: Optional window / category / sort params.

        Returns:
            JSON-serialised trending searches.
        """
        raw = await self.async_client.google.trending(geo=geo, **kwargs)
        raw = self._truncate_results(raw, "trends")
        return self._format_response(raw)
