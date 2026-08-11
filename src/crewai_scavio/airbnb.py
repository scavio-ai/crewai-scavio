"""Scavio Airbnb tools for CrewAI.

1 credit flat on all three endpoints (AIRBNB_CREDIT_COST =
scrapedoCreditCost(1); render was tested and returns the same body for 5x the
price).

- STALE QUEUE CAVEAT: the queue says /reviews returns NO review bodies. The
  BACKEND NOW RETURNS BODIES -- getScrapedoAirbnbReviews hits the legacy v2 REST
  endpoint (api/v2/homes_pdp_reviews) with real comments, per-review rating,
  localized_date and reviewer, verified live 2026-08-09 on three listings. Docs
  should describe real review bodies with limit/offset paging.
- The `limit`/`offset` param names are load-bearing: the underscored
  `_limit`/`_offset` used elsewhere in Airbnb's v2 API are silently ignored
  here and return a fixed 7 rows at every offset.
- LISTING HAS NO PRICE FIELD. The room page carries no nightly rate under any
  parameters, with or without dates, and under render. Prices are SEARCH-ONLY.
- The rating breakdown (six category ratings, five-bucket star distribution,
  AI-synthesised review tags) lives on /listing, which server-renders it -- NOT
  on /reviews.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_AirbnbSearchRoomType = Literal[
    "entire_home", "private_room", "shared_room", "hotel_room"
]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _AirbnbSearchInput(BaseModel):
    """Input schema for ScavioAirbnbSearchTool."""

    location: str = Field(
        ...,
        description=(
            "City, region, ZIP, or a pasted airbnb.com/s/ URL (1-200 characters). An "
            "unresolvable location is a 404."
        ),
    )
    check_in: str | None = Field(
        default=None,
        description=(
            "Check-in date, YYYY-MM-DD. Must be sent with check_out; omitting both "
            "defaults to +30 days and flags dates_are_defaulted in the response."
        ),
    )
    check_out: str | None = Field(
        default=None,
        description=(
            "Check-out date, YYYY-MM-DD. Must be later than check_in; defaults to "
            "check_in plus 5 nights when omitted."
        ),
    )
    adults: int | None = Field(
        default=None,
        description="Adult guests, >= 1.",
    )
    children: int | None = Field(
        default=None,
        description="Children aged 2-12, >= 0.",
    )
    infants: int | None = Field(
        default=None,
        description="Infants under 2, >= 0.",
    )
    pets: int | None = Field(
        default=None,
        description="Pets, >= 0.",
    )
    min_price: float | None = Field(
        default=None,
        description=(
            "Minimum price for the WHOLE STAY in `currency`, not per night, >= 0. Must "
            "not exceed max_price."
        ),
    )
    max_price: float | None = Field(
        default=None,
        description=(
            "Maximum price for the WHOLE STAY in `currency`, not per night, >= 0."
        ),
    )
    room_type: _AirbnbSearchRoomType | None = Field(
        default=None,
        description=(
            "Room type. Validated before the scrape, because an unrecognised value "
            "returns the UNFILTERED set under a 200."
        ),
    )
    min_bedrooms: int | None = Field(
        default=None,
        description="Minimum bedrooms, >= 0.",
    )
    min_beds: int | None = Field(
        default=None,
        description="Minimum beds, >= 0.",
    )
    min_bathrooms: int | None = Field(
        default=None,
        description="Minimum bathrooms, >= 0.",
    )
    superhost: bool | None = Field(
        default=None,
        description="Superhost listings only.",
    )
    instant_book: bool | None = Field(
        default=None,
        description="Instant Book listings only.",
    )
    guest_favorite: bool | None = Field(
        default=None,
        description="Guest Favorite listings only.",
    )
    free_cancellation: bool | None = Field(
        default=None,
        description="Listings with free cancellation only.",
    )
    amenities: str | None = Field(
        default=None,
        description=(
            "Comma-separated amenities (1-200 characters): wifi, air_conditioning, "
            "pool, kitchen, free_parking, washer, self_check_in, tv, or raw numeric "
            "Airbnb amenity ids. An unrecognised NAME is rejected before the scrape."
        ),
    )
    currency: str | None = Field(
        default=None,
        description=(
            "ISO 4217 currency for prices, 3 letters (default 'USD'). Without it "
            "Airbnb prices off the proxy exit and identical requests disagree."
        ),
    )
    page: int | None = Field(
        default=None,
        description=(
            "Results page, 1-based. 18 listings per page. Cannot be combined with "
            "cursor."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "next_cursor from a previous response (1-500 characters); wins over page, "
            "so sending both is rejected."
        ),
    )


class _AirbnbListingInput(BaseModel):
    """Input schema for ScavioAirbnbListingTool."""

    listing_id: str = Field(
        ...,
        description=(
            "Airbnb listing id or a full /rooms/ URL (1-500 characters); query params "
            "are discarded, since they carry someone else's dates."
        ),
    )
    check_in: str | None = Field(
        default=None,
        description=(
            "Check-in date, YYYY-MM-DD. Must be sent with check_out. Does not produce "
            "a price: the room page has no nightly rate."
        ),
    )
    check_out: str | None = Field(
        default=None,
        description=(
            "Check-out date, YYYY-MM-DD. Must be later than check_in and sent together "
            "with it."
        ),
    )
    adults: int | None = Field(
        default=None,
        description="Adult guests, >= 1.",
    )
    children: int | None = Field(
        default=None,
        description="Children aged 2-12, >= 0.",
    )
    infants: int | None = Field(
        default=None,
        description="Infants under 2, >= 0.",
    )
    pets: int | None = Field(
        default=None,
        description="Pets, >= 0.",
    )
    currency: str | None = Field(
        default=None,
        description="ISO 4217 currency, 3 letters (default 'USD').",
    )


class _AirbnbReviewsInput(BaseModel):
    """Input schema for ScavioAirbnbReviewsTool."""

    listing_id: str = Field(
        ...,
        description="Airbnb listing id or a full /rooms/ URL (1-500 characters).",
    )
    currency: str | None = Field(
        default=None,
        description="ISO 4217 currency, 3 letters (default 'USD').",
    )
    limit: int | None = Field(
        default=None,
        description=(
            "Reviews to return, 1-50 (default 30). Upstream returns a fixed 7 when no "
            "explicit limit is sent."
        ),
    )
    offset: int | None = Field(
        default=None,
        description="Reviews to skip before this page, >= 0 (default 0).",
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioAirbnbSearchTool(ScavioBaseTool):
    """Airbnb stays: stay-total and per-night price with the full discount ledger,
    rating and review count, bedrooms/beds/baths, coordinates, badges, images,
    dates_are_defaulted.
    """

    name: str = "Scavio Airbnb Search"
    description: str = (
        "Airbnb stays: stay-total and per-night price with the full discount ledger, "
        "rating and review count, bedrooms/beds/baths, coordinates, badges, images, "
        "dates_are_defaulted. 18 listings per page; page and cursor are mutually "
        "exclusive. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _AirbnbSearchInput

    def _run(
        self,
        location: str,
        check_in: str | None = None,
        check_out: str | None = None,
        adults: int | None = None,
        children: int | None = None,
        infants: int | None = None,
        pets: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        room_type: _AirbnbSearchRoomType | None = None,
        min_bedrooms: int | None = None,
        min_beds: int | None = None,
        min_bathrooms: int | None = None,
        superhost: bool | None = None,
        instant_book: bool | None = None,
        guest_favorite: bool | None = None,
        free_cancellation: bool | None = None,
        amenities: str | None = None,
        currency: str | None = None,
        page: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/airbnb/search synchronously.

        Args:
            location: City, region, ZIP, or a pasted airbnb.com/s/ URL (1-200
                characters).
            check_in: Check-in date, YYYY-MM-DD. Must be sent with check_out; omitting
                both defaults to +30 days and flags dates_are_defaulted in the response.
            check_out: Check-out date, YYYY-MM-DD. Must be later than check_in; defaults
                to check_in plus 5 nights when omitted.
            adults: Adult guests, >= 1.
            children: Children aged 2-12, >= 0.
            infants: Infants under 2, >= 0.
            pets: Pets, >= 0.
            min_price: Minimum price for the WHOLE STAY in `currency`, not per night, >=
                0.
            max_price: Maximum price for the WHOLE STAY in `currency`, not per night, >=
                0.
            room_type: Room type. Validated before the scrape, because an unrecognised
                value returns the UNFILTERED set under a 200.
            min_bedrooms: Minimum bedrooms, >= 0.
            min_beds: Minimum beds, >= 0.
            min_bathrooms: Minimum bathrooms, >= 0.
            superhost: Superhost listings only.
            instant_book: Instant Book listings only.
            guest_favorite: Guest Favorite listings only.
            free_cancellation: Listings with free cancellation only.
            amenities: Comma-separated amenities (1-200 characters): wifi,
                air_conditioning, pool, kitchen, free_parking, washer, self_check_in,
                tv, or raw numeric Airbnb amenity ids.
            currency: ISO 4217 currency for prices, 3 letters (default 'USD').
            page: Results page, 1-based. 18 listings per page.
            cursor: next_cursor from a previous response (1-500 characters); wins over
                page, so sending both is rejected.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.airbnb.search(
            location=location,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            children=children,
            infants=infants,
            pets=pets,
            min_price=min_price,
            max_price=max_price,
            room_type=room_type,
            min_bedrooms=min_bedrooms,
            min_beds=min_beds,
            min_bathrooms=min_bathrooms,
            superhost=superhost,
            instant_book=instant_book,
            guest_favorite=guest_favorite,
            free_cancellation=free_cancellation,
            amenities=amenities,
            currency=currency,
            page=page,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "listings")
        return self._format_response(raw)

    async def _arun(
        self,
        location: str,
        check_in: str | None = None,
        check_out: str | None = None,
        adults: int | None = None,
        children: int | None = None,
        infants: int | None = None,
        pets: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        room_type: _AirbnbSearchRoomType | None = None,
        min_bedrooms: int | None = None,
        min_beds: int | None = None,
        min_bathrooms: int | None = None,
        superhost: bool | None = None,
        instant_book: bool | None = None,
        guest_favorite: bool | None = None,
        free_cancellation: bool | None = None,
        amenities: str | None = None,
        currency: str | None = None,
        page: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/airbnb/search asynchronously.

        Args:
            location: City, region, ZIP, or a pasted airbnb.com/s/ URL (1-200
                characters).
            check_in: Check-in date, YYYY-MM-DD. Must be sent with check_out; omitting
                both defaults to +30 days and flags dates_are_defaulted in the response.
            check_out: Check-out date, YYYY-MM-DD. Must be later than check_in; defaults
                to check_in plus 5 nights when omitted.
            adults: Adult guests, >= 1.
            children: Children aged 2-12, >= 0.
            infants: Infants under 2, >= 0.
            pets: Pets, >= 0.
            min_price: Minimum price for the WHOLE STAY in `currency`, not per night, >=
                0.
            max_price: Maximum price for the WHOLE STAY in `currency`, not per night, >=
                0.
            room_type: Room type. Validated before the scrape, because an unrecognised
                value returns the UNFILTERED set under a 200.
            min_bedrooms: Minimum bedrooms, >= 0.
            min_beds: Minimum beds, >= 0.
            min_bathrooms: Minimum bathrooms, >= 0.
            superhost: Superhost listings only.
            instant_book: Instant Book listings only.
            guest_favorite: Guest Favorite listings only.
            free_cancellation: Listings with free cancellation only.
            amenities: Comma-separated amenities (1-200 characters): wifi,
                air_conditioning, pool, kitchen, free_parking, washer, self_check_in,
                tv, or raw numeric Airbnb amenity ids.
            currency: ISO 4217 currency for prices, 3 letters (default 'USD').
            page: Results page, 1-based. 18 listings per page.
            cursor: next_cursor from a previous response (1-500 characters); wins over
                page, so sending both is rejected.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.airbnb.search(
            location=location,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            children=children,
            infants=infants,
            pets=pets,
            min_price=min_price,
            max_price=max_price,
            room_type=room_type,
            min_bedrooms=min_bedrooms,
            min_beds=min_beds,
            min_bathrooms=min_bathrooms,
            superhost=superhost,
            instant_book=instant_book,
            guest_favorite=guest_favorite,
            free_cancellation=free_cancellation,
            amenities=amenities,
            currency=currency,
            page=page,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "listings")
        return self._format_response(raw)


class ScavioAirbnbListingTool(ScavioBaseTool):
    """One Airbnb listing in full: description, property/room type, capacity and room
    counts, the complete grouped amenity list (including what the place does NOT have),
    host profile and stats, house rules, cancellation policy, sleeping arrangements,
    photo tour and the RATING BREAKDOWN.
    """

    name: str = "Scavio Airbnb Listing"
    description: str = (
        "One Airbnb listing in full: description, property/room type, capacity and "
        "room counts, the complete grouped amenity list (including what the place does "
        "NOT have), host profile and stats, house rules, cancellation policy, sleeping "
        "arrangements, photo tour and the RATING BREAKDOWN. Carries NO nightly price - "
        "prices are search-only. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _AirbnbListingInput

    def _run(
        self,
        listing_id: str,
        check_in: str | None = None,
        check_out: str | None = None,
        adults: int | None = None,
        children: int | None = None,
        infants: int | None = None,
        pets: int | None = None,
        currency: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/airbnb/listing synchronously.

        Args:
            listing_id: Airbnb listing id or a full /rooms/ URL (1-500 characters);
                query params are discarded, since they carry someone else's dates.
            check_in: Check-in date, YYYY-MM-DD. Must be sent with check_out.
            check_out: Check-out date, YYYY-MM-DD. Must be later than check_in and sent
                together with it.
            adults: Adult guests, >= 1.
            children: Children aged 2-12, >= 0.
            infants: Infants under 2, >= 0.
            pets: Pets, >= 0.
            currency: ISO 4217 currency, 3 letters (default 'USD').

        Returns:
            JSON-serialised results.
        """
        raw = self.client.airbnb.listing(
            listing_id=listing_id,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            children=children,
            infants=infants,
            pets=pets,
            currency=currency,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        listing_id: str,
        check_in: str | None = None,
        check_out: str | None = None,
        adults: int | None = None,
        children: int | None = None,
        infants: int | None = None,
        pets: int | None = None,
        currency: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/airbnb/listing asynchronously.

        Args:
            listing_id: Airbnb listing id or a full /rooms/ URL (1-500 characters);
                query params are discarded, since they carry someone else's dates.
            check_in: Check-in date, YYYY-MM-DD. Must be sent with check_out.
            check_out: Check-out date, YYYY-MM-DD. Must be later than check_in and sent
                together with it.
            adults: Adult guests, >= 1.
            children: Children aged 2-12, >= 0.
            infants: Infants under 2, >= 0.
            pets: Pets, >= 0.
            currency: ISO 4217 currency, 3 letters (default 'USD').

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.airbnb.listing(
            listing_id=listing_id,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            children=children,
            infants=infants,
            pets=pets,
            currency=currency,
        )
        return self._format_response(raw)


class ScavioAirbnbReviewsTool(ScavioBaseTool):
    """Airbnb review BODIES with per-review rating, date and reviewer
    name/photo/location, limit/offset paged at up to 50 per call. `count` is the
    listing's TOTAL review count, `returned` is how many this page holds.
    """

    name: str = "Scavio Airbnb Reviews"
    description: str = (
        "Airbnb review BODIES with per-review rating, date and reviewer "
        "name/photo/location, limit/offset paged at up to 50 per call. `count` is the "
        "listing's TOTAL review count, `returned` is how many this page holds. The "
        "rating breakdown lives on listing(), not here. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _AirbnbReviewsInput

    def _run(
        self,
        listing_id: str,
        currency: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/airbnb/reviews synchronously.

        Args:
            listing_id: Airbnb listing id or a full /rooms/ URL (1-500 characters).
            currency: ISO 4217 currency, 3 letters (default 'USD').
            limit: Reviews to return, 1-50 (default 30).
            offset: Reviews to skip before this page, >= 0 (default 0).

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.airbnb.reviews(
            listing_id=listing_id,
            currency=currency,
            limit=limit,
            offset=offset,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        listing_id: str,
        currency: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/airbnb/reviews asynchronously.

        Args:
            listing_id: Airbnb listing id or a full /rooms/ URL (1-500 characters).
            currency: ISO 4217 currency, 3 letters (default 'USD').
            limit: Reviews to return, 1-50 (default 30).
            offset: Reviews to skip before this page, >= 0 (default 0).

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.airbnb.reviews(
            listing_id=listing_id,
            currency=currency,
            limit=limit,
            offset=offset,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
