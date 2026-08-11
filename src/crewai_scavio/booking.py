"""Scavio Booking.com tools for CrewAI.

1 credit flat on all three endpoints (BOOKING_CREDIT_COST =
scrapedoCreditCost(1)).

- checkin and checkout must be sent TOGETHER -- Booking ignores a lone checkin
  and prices its own default range, returning real prices for dates the caller
  never asked for.
- The property endpoint takes dates for the same reason search does: Booking
  prices a STAY. Omitting them returns prices for a two-night range Booking
  chose; the response echoes whichever dates were used.
- currency defaults to USD in the transport. With no currency Booking prices
  off the proxy exit and two identical requests disagree.
- min_review_score is an enum ('6','7','8','9') -- an arbitrary threshold is
  silently dropped upstream.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# Enum unions long enough that inlining them would bury the
# signature they belong to.
_BookingSearchDestType = Literal[
    "city", "region", "country", "district", "landmark", "airport", "hotel"
]
_BookingSearchSortBy = Literal[
    "popularity", "price_low", "price_high", "stars_high", "stars_low",
    "stars_and_price", "distance", "review_score"
]
_BookingSearchPropertyType = (
    Literal["apartments", "hostels", "hotels", "motels", "resorts",
    "bed_and_breakfasts", "villas", "campgrounds", "vacation_homes",
    "lodges", "homestays"] | int
)


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _BookingSearchInput(BaseModel):
    """Input schema for ScavioBookingSearchTool."""

    destination: str | None = Field(
        default=None,
        description=(
            "Destination to search, e.g. 'Paris' (1-200 characters). Required unless "
            "dest_id is given."
        ),
    )
    dest_id: str | None = Field(
        default=None,
        description=(
            "Numeric Booking.com destination id, as an alternative to destination."
        ),
    )
    dest_type: _BookingSearchDestType | None = Field(
        default=None,
        description=(
            "What dest_id refers to. Requires dest_id and is rejected without it, "
            "because Booking silently ignores a lone dest_type."
        ),
    )
    page: int | None = Field(
        default=None,
        description="Results page, 1-based. 25 properties per page, 1 credit each.",
    )
    sort_by: _BookingSearchSortBy | None = Field(
        default=None,
        description="Result sort order (default 'popularity').",
    )
    min_price: float | None = Field(
        default=None,
        description=(
            "Minimum price PER NIGHT in `currency`, >= 0. Must not exceed max_price."
        ),
    )
    max_price: float | None = Field(
        default=None,
        description="Maximum price PER NIGHT in `currency`, >= 0.",
    )
    stars: list[int] | None = Field(
        default=None,
        description=(
            "Star ratings to include, each 1-5, 1-5 values, OR'd together (e.g. [4, "
            "5])."
        ),
    )
    min_review_score: Literal["6", "7", "8", "9"] | None = Field(
        default=None,
        description=(
            "Minimum guest review score. Only '6', '7', '8' and '9' exist upstream; "
            "any other threshold is silently dropped."
        ),
    )
    property_type: _BookingSearchPropertyType | None = Field(
        default=None,
        description=(
            "Accommodation type by name, or a raw numeric Booking accommodation-type "
            "id (>= 1)."
        ),
    )
    free_cancellation: bool | None = Field(
        default=None,
        description="Only properties offering free cancellation.",
    )
    no_prepayment: bool | None = Field(
        default=None,
        description="Only properties that take no prepayment.",
    )
    breakfast_included: bool | None = Field(
        default=None,
        description="Only rates that include breakfast.",
    )
    checkin: str | None = Field(
        default=None,
        description=(
            "Check-in date, YYYY-MM-DD. Must be sent together with checkout: a lone "
            "checkin is ignored and Booking prices a default range of its own."
        ),
    )
    checkout: str | None = Field(
        default=None,
        description=(
            "Check-out date, YYYY-MM-DD. Must be later than checkin and sent together "
            "with it."
        ),
    )
    adults: int | None = Field(
        default=None,
        description="Adult guests, >= 1 (default 2).",
    )
    children_ages: list[int] | None = Field(
        default=None,
        description=(
            "AGES of accompanying children, each 0-17, max 10 entries. Ages, not a "
            "count."
        ),
    )
    rooms: int | None = Field(
        default=None,
        description="Rooms required, >= 1 (default 1).",
    )
    currency: str | None = Field(
        default=None,
        description=(
            "ISO 4217 currency for prices, 3 letters (default 'USD'). Without it "
            "Booking prices off the proxy exit and identical requests disagree."
        ),
    )


class _BookingHotelInput(BaseModel):
    """Input schema for ScavioBookingHotelTool."""

    hotel: str = Field(
        ...,
        description=(
            "Booking.com property URL or the bare page slug (1-500 characters); query "
            "params are discarded."
        ),
    )
    country_code: str | None = Field(
        default=None,
        description=(
            "Two-letter country code for the property page (default 'us'). Only "
            "consulted for a bare slug, where a wrong one is a real, BILLED 404."
        ),
    )
    checkin: str | None = Field(
        default=None,
        description=(
            "Check-in date, YYYY-MM-DD. Must be sent together with checkout; omitting "
            "both prices a two-night range Booking chose, echoed back in the response."
        ),
    )
    checkout: str | None = Field(
        default=None,
        description=(
            "Check-out date, YYYY-MM-DD. Must be later than checkin and sent together "
            "with it."
        ),
    )
    adults: int | None = Field(
        default=None,
        description="Adult guests, >= 1 (default 2).",
    )
    children_ages: list[int] | None = Field(
        default=None,
        description=(
            "AGES of accompanying children, each 0-17, max 10 entries. Ages, not a "
            "count."
        ),
    )
    rooms: int | None = Field(
        default=None,
        description="Rooms required, >= 1 (default 1).",
    )
    currency: str | None = Field(
        default=None,
        description=(
            "ISO 4217 currency for prices, 3 letters (default 'USD'). Without it "
            "Booking prices off the proxy exit and identical requests disagree."
        ),
    )


class _BookingReviewsInput(BaseModel):
    """Input schema for ScavioBookingReviewsTool."""

    hotel: str = Field(
        ...,
        description=(
            "Booking.com property URL or the bare page slug (1-500 characters); query "
            "params are discarded."
        ),
    )
    country_code: str | None = Field(
        default=None,
        description=(
            "Two-letter country code for the property page (default 'us'). Only "
            "consulted for a bare slug, where a wrong one is a real, BILLED 404."
        ),
    )
    checkin: str | None = Field(
        default=None,
        description=(
            "Check-in date, YYYY-MM-DD. Must be sent together with checkout; it prices "
            "the stay the review page is rendered for."
        ),
    )
    checkout: str | None = Field(
        default=None,
        description=(
            "Check-out date, YYYY-MM-DD. Must be later than checkin and sent together "
            "with it."
        ),
    )
    adults: int | None = Field(
        default=None,
        description="Adult guests, >= 1 (default 2).",
    )
    children_ages: list[int] | None = Field(
        default=None,
        description=(
            "AGES of accompanying children, each 0-17, max 10 entries. Ages, not a "
            "count."
        ),
    )
    rooms: int | None = Field(
        default=None,
        description="Rooms required, >= 1 (default 1).",
    )
    currency: str | None = Field(
        default=None,
        description="ISO 4217 currency for prices, 3 letters (default 'USD').",
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioBookingSearchTool(ScavioBaseTool):
    """Booking.com properties for a destination and stay: live nightly price, review
    score, star rating, location, room type, deal badges.
    """

    name: str = "Scavio Booking.com Search"
    description: str = (
        "Booking.com properties for a destination and stay: live nightly price, review "
        "score, star rating, location, room type, deal badges. 25 properties per page. "
        "Provide destination or dest_id. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _BookingSearchInput

    def _run(
        self,
        destination: str | None = None,
        dest_id: str | None = None,
        dest_type: _BookingSearchDestType | None = None,
        page: int | None = None,
        sort_by: _BookingSearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        stars: list[int] | None = None,
        min_review_score: Literal["6", "7", "8", "9"] | None = None,
        property_type: _BookingSearchPropertyType | None = None,
        free_cancellation: bool | None = None,
        no_prepayment: bool | None = None,
        breakfast_included: bool | None = None,
        checkin: str | None = None,
        checkout: str | None = None,
        adults: int | None = None,
        children_ages: list[int] | None = None,
        rooms: int | None = None,
        currency: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/booking/search synchronously.

        Args:
            destination: Destination to search, e.g. 'Paris' (1-200 characters).
            dest_id: Numeric Booking.com destination id, as an alternative to
                destination.
            dest_type: What dest_id refers to. Requires dest_id and is rejected without
                it, because Booking silently ignores a lone dest_type.
            page: Results page, 1-based. 25 properties per page, 1 credit each.
            sort_by: Result sort order (default 'popularity').
            min_price: Minimum price PER NIGHT in `currency`, >= 0.
            max_price: Maximum price PER NIGHT in `currency`, >= 0.
            stars: Star ratings to include, each 1-5, 1-5 values, OR'd together (e.g.
                [4, 5]).
            min_review_score: Minimum guest review score. Only '6', '7', '8' and '9'
                exist upstream; any other threshold is silently dropped.
            property_type: Accommodation type by name, or a raw numeric Booking
                accommodation-type id (>= 1).
            free_cancellation: Only properties offering free cancellation.
            no_prepayment: Only properties that take no prepayment.
            breakfast_included: Only rates that include breakfast.
            checkin: Check-in date, YYYY-MM-DD. Must be sent together with checkout: a
                lone checkin is ignored and Booking prices a default range of its own.
            checkout: Check-out date, YYYY-MM-DD. Must be later than checkin and sent
                together with it.
            adults: Adult guests, >= 1 (default 2).
            children_ages: AGES of accompanying children, each 0-17, max 10 entries.
            rooms: Rooms required, >= 1 (default 1).
            currency: ISO 4217 currency for prices, 3 letters (default 'USD').

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.booking.search(
            destination=destination,
            dest_id=dest_id,
            dest_type=dest_type,
            page=page,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
            stars=stars,
            min_review_score=min_review_score,
            property_type=property_type,
            free_cancellation=free_cancellation,
            no_prepayment=no_prepayment,
            breakfast_included=breakfast_included,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            children_ages=children_ages,
            rooms=rooms,
            currency=currency,
        )
        raw = self._truncate_nested(raw, "data", "properties")
        return self._format_response(raw)

    async def _arun(
        self,
        destination: str | None = None,
        dest_id: str | None = None,
        dest_type: _BookingSearchDestType | None = None,
        page: int | None = None,
        sort_by: _BookingSearchSortBy | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        stars: list[int] | None = None,
        min_review_score: Literal["6", "7", "8", "9"] | None = None,
        property_type: _BookingSearchPropertyType | None = None,
        free_cancellation: bool | None = None,
        no_prepayment: bool | None = None,
        breakfast_included: bool | None = None,
        checkin: str | None = None,
        checkout: str | None = None,
        adults: int | None = None,
        children_ages: list[int] | None = None,
        rooms: int | None = None,
        currency: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/booking/search asynchronously.

        Args:
            destination: Destination to search, e.g. 'Paris' (1-200 characters).
            dest_id: Numeric Booking.com destination id, as an alternative to
                destination.
            dest_type: What dest_id refers to. Requires dest_id and is rejected without
                it, because Booking silently ignores a lone dest_type.
            page: Results page, 1-based. 25 properties per page, 1 credit each.
            sort_by: Result sort order (default 'popularity').
            min_price: Minimum price PER NIGHT in `currency`, >= 0.
            max_price: Maximum price PER NIGHT in `currency`, >= 0.
            stars: Star ratings to include, each 1-5, 1-5 values, OR'd together (e.g.
                [4, 5]).
            min_review_score: Minimum guest review score. Only '6', '7', '8' and '9'
                exist upstream; any other threshold is silently dropped.
            property_type: Accommodation type by name, or a raw numeric Booking
                accommodation-type id (>= 1).
            free_cancellation: Only properties offering free cancellation.
            no_prepayment: Only properties that take no prepayment.
            breakfast_included: Only rates that include breakfast.
            checkin: Check-in date, YYYY-MM-DD. Must be sent together with checkout: a
                lone checkin is ignored and Booking prices a default range of its own.
            checkout: Check-out date, YYYY-MM-DD. Must be later than checkin and sent
                together with it.
            adults: Adult guests, >= 1 (default 2).
            children_ages: AGES of accompanying children, each 0-17, max 10 entries.
            rooms: Rooms required, >= 1 (default 1).
            currency: ISO 4217 currency for prices, 3 letters (default 'USD').

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.booking.search(
            destination=destination,
            dest_id=dest_id,
            dest_type=dest_type,
            page=page,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
            stars=stars,
            min_review_score=min_review_score,
            property_type=property_type,
            free_cancellation=free_cancellation,
            no_prepayment=no_prepayment,
            breakfast_included=breakfast_included,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            children_ages=children_ages,
            rooms=rooms,
            currency=currency,
        )
        raw = self._truncate_nested(raw, "data", "properties")
        return self._format_response(raw)


class ScavioBookingHotelTool(ScavioBaseTool):
    """One Booking.com property in full: rooms and rate plans, facilities, house rules,
    check-in windows, policies, images, location and review scores, priced for the stay
    asked for.
    """

    name: str = "Scavio Booking.com Hotel"
    description: str = (
        "One Booking.com property in full: rooms and rate plans, facilities, house "
        "rules, check-in windows, policies, images, location and review scores, priced "
        "for the stay asked for. Chaining the `url` a search row returns is cheaper "
        "than a bare slug. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _BookingHotelInput

    def _run(
        self,
        hotel: str,
        country_code: str | None = None,
        checkin: str | None = None,
        checkout: str | None = None,
        adults: int | None = None,
        children_ages: list[int] | None = None,
        rooms: int | None = None,
        currency: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/booking/hotel synchronously.

        Args:
            hotel: Booking.com property URL or the bare page slug (1-500 characters);
                query params are discarded.
            country_code: Two-letter country code for the property page (default 'us').
            checkin: Check-in date, YYYY-MM-DD. Must be sent together with checkout;
                omitting both prices a two-night range Booking chose, echoed back in the
                response.
            checkout: Check-out date, YYYY-MM-DD. Must be later than checkin and sent
                together with it.
            adults: Adult guests, >= 1 (default 2).
            children_ages: AGES of accompanying children, each 0-17, max 10 entries.
            rooms: Rooms required, >= 1 (default 1).
            currency: ISO 4217 currency for prices, 3 letters (default 'USD').

        Returns:
            JSON-serialised results.
        """
        raw = self.client.booking.hotel(
            hotel=hotel,
            country_code=country_code,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            children_ages=children_ages,
            rooms=rooms,
            currency=currency,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        hotel: str,
        country_code: str | None = None,
        checkin: str | None = None,
        checkout: str | None = None,
        adults: int | None = None,
        children_ages: list[int] | None = None,
        rooms: int | None = None,
        currency: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/booking/hotel asynchronously.

        Args:
            hotel: Booking.com property URL or the bare page slug (1-500 characters);
                query params are discarded.
            country_code: Two-letter country code for the property page (default 'us').
            checkin: Check-in date, YYYY-MM-DD. Must be sent together with checkout;
                omitting both prices a two-night range Booking chose, echoed back in the
                response.
            checkout: Check-out date, YYYY-MM-DD. Must be later than checkin and sent
                together with it.
            adults: Adult guests, >= 1 (default 2).
            children_ages: AGES of accompanying children, each 0-17, max 10 entries.
            rooms: Rooms required, >= 1 (default 1).
            currency: ISO 4217 currency for prices, 3 letters (default 'USD').

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.booking.hotel(
            hotel=hotel,
            country_code=country_code,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            children_ages=children_ages,
            rooms=rooms,
            currency=currency,
        )
        return self._format_response(raw)


class ScavioBookingReviewsTool(ScavioBaseTool):
    """Booking.com guest reviews for a property with the score breakdown by category and
    Booking's own praise/complaint summary.
    """

    name: str = "Scavio Booking.com Reviews"
    description: str = (
        "Booking.com guest reviews for a property with the score breakdown by category "
        "and Booking's own praise/complaint summary. No page param: total_count is the "
        "whole review history, count is what this response holds. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _BookingReviewsInput

    def _run(
        self,
        hotel: str,
        country_code: str | None = None,
        checkin: str | None = None,
        checkout: str | None = None,
        adults: int | None = None,
        children_ages: list[int] | None = None,
        rooms: int | None = None,
        currency: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/booking/reviews synchronously.

        Args:
            hotel: Booking.com property URL or the bare page slug (1-500 characters);
                query params are discarded.
            country_code: Two-letter country code for the property page (default 'us').
            checkin: Check-in date, YYYY-MM-DD. Must be sent together with checkout; it
                prices the stay the review page is rendered for.
            checkout: Check-out date, YYYY-MM-DD. Must be later than checkin and sent
                together with it.
            adults: Adult guests, >= 1 (default 2).
            children_ages: AGES of accompanying children, each 0-17, max 10 entries.
            rooms: Rooms required, >= 1 (default 1).
            currency: ISO 4217 currency for prices, 3 letters (default 'USD').

        Returns:
            JSON-serialised reviews.
        """
        raw = self.client.booking.reviews(
            hotel=hotel,
            country_code=country_code,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            children_ages=children_ages,
            rooms=rooms,
            currency=currency,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)

    async def _arun(
        self,
        hotel: str,
        country_code: str | None = None,
        checkin: str | None = None,
        checkout: str | None = None,
        adults: int | None = None,
        children_ages: list[int] | None = None,
        rooms: int | None = None,
        currency: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/booking/reviews asynchronously.

        Args:
            hotel: Booking.com property URL or the bare page slug (1-500 characters);
                query params are discarded.
            country_code: Two-letter country code for the property page (default 'us').
            checkin: Check-in date, YYYY-MM-DD. Must be sent together with checkout; it
                prices the stay the review page is rendered for.
            checkout: Check-out date, YYYY-MM-DD. Must be later than checkin and sent
                together with it.
            adults: Adult guests, >= 1 (default 2).
            children_ages: AGES of accompanying children, each 0-17, max 10 entries.
            rooms: Rooms required, >= 1 (default 1).
            currency: ISO 4217 currency for prices, 3 letters (default 'USD').

        Returns:
            JSON-serialised reviews.
        """
        raw = await self.async_client.booking.reviews(
            hotel=hotel,
            country_code=country_code,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            children_ages=children_ages,
            rooms=rooms,
            currency=currency,
        )
        raw = self._truncate_nested(raw, "data", "reviews")
        return self._format_response(raw)
