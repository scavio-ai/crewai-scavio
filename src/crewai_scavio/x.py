"""Scavio X (Twitter) tools for CrewAI.

Every X endpoint costs 1 credit. Two wire quirks are worth knowing before
wiring these together: the search field is ``search`` (not ``query``), and the
followings endpoint returns its list under ``data.following`` -- singular --
while followers returns ``data.followers``.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


_CURSOR_DESCRIPTION = (
    "Pagination cursor -- pass next_cursor from a previous response."
)
_SCREEN_NAME_DESCRIPTION = "An X handle, without the leading @ (e.g. 'elonmusk')."
_TWEET_ID_DESCRIPTION = "Tweet id as a string (e.g. '1808168603721650364')."


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _XSearchInput(BaseModel):
    """Input schema for ScavioXSearchTool."""

    search: str = Field(..., description="Search query, 1-500 characters.")
    search_type: Literal["Top", "Latest", "People", "Photos", "Videos"] | None = Field(
        default=None,
        description=(
            "Result category (default 'Top'). Values are capitalised and "
            "case-sensitive."
        ),
    )
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class _XTweetInput(BaseModel):
    """Input schema for ScavioXTweetTool."""

    tweet_id: str = Field(..., description=_TWEET_ID_DESCRIPTION)


class _XTweetCommentsInput(BaseModel):
    """Input schema for ScavioXTweetCommentsTool."""

    tweet_id: str = Field(..., description=_TWEET_ID_DESCRIPTION)
    rank: Literal["top", "latest"] | None = Field(
        default=None,
        description=(
            "'top' returns the ranked reply thread (default), 'latest' returns "
            "replies chronologically. Lowercase."
        ),
    )
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class _XTweetRetweetersInput(BaseModel):
    """Input schema for ScavioXTweetRetweetersTool."""

    tweet_id: str = Field(..., description=_TWEET_ID_DESCRIPTION)
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class _XUserInput(BaseModel):
    """Input schema for ScavioXUserTool."""

    screen_name: str = Field(..., description=_SCREEN_NAME_DESCRIPTION)


class _XUserTimelineInput(BaseModel):
    """Input schema shared by the user tweets / replies / media tools."""

    screen_name: str = Field(..., description=_SCREEN_NAME_DESCRIPTION)
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class _XTrendingInput(BaseModel):
    """Input schema for ScavioXTrendingTool."""

    country: str | None = Field(
        default=None,
        description=(
            "Country NAME, not an ISO code -- e.g. 'UnitedStates' (default), "
            "'Japan', 'Brazil'."
        ),
    )


# ---------------------------------------------------------------------------
# 1. Search
# ---------------------------------------------------------------------------


class ScavioXSearchTool(ScavioBaseTool):
    """Search tweets and people on X.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X Search"
    description: str = (
        "Search X (Twitter) for tweets or people. The query field is named "
        "'search', not 'query'. Returns matching tweets under data.timeline "
        "with next_cursor and prev_cursor for paging. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XSearchInput

    def _run(
        self,
        search: str,
        search_type: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous X search.

        Args:
            search: Search query.
            search_type: Result category.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.x.search(
            search=search, search_type=search_type, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)

    async def _arun(
        self,
        search: str,
        search_type: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous X search.

        Args:
            search: Search query.
            search_type: Result category.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.x.search(
            search=search, search_type=search_type, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 2. Tweet
# ---------------------------------------------------------------------------


class ScavioXTweetTool(ScavioBaseTool):
    """Fetch a single tweet by id.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X Tweet"
    description: str = (
        "Fetch a single tweet by id. Returns the tweet object plus reply_to, "
        "in_reply_to_screen_name, in_reply_to_status_id, in_reply_to_user_id "
        "and sensitive. Engagement counts are favorites, retweets, replies, "
        "quotes, bookmarks and views. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XTweetInput

    def _run(self, tweet_id: str, **kwargs: Any) -> str:
        """Fetch tweet details synchronously.

        Args:
            tweet_id: Tweet id.

        Returns:
            JSON-serialised tweet.
        """
        raw = self.client.x.tweet(tweet_id=tweet_id)
        return self._format_response(raw)

    async def _arun(self, tweet_id: str, **kwargs: Any) -> str:
        """Fetch tweet details asynchronously.

        Args:
            tweet_id: Tweet id.

        Returns:
            JSON-serialised tweet.
        """
        raw = await self.async_client.x.tweet(tweet_id=tweet_id)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 3. Tweet Comments
# ---------------------------------------------------------------------------


class ScavioXTweetCommentsTool(ScavioBaseTool):
    """Fetch replies to a tweet.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X Tweet Comments"
    description: str = (
        "Fetch replies to a tweet. rank='top' returns the ranked thread, "
        "rank='latest' returns replies chronologically. Both are flattened "
        "into data.timeline. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XTweetCommentsInput

    def _run(
        self,
        tweet_id: str,
        rank: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch tweet replies synchronously.

        Args:
            tweet_id: Tweet id.
            rank: 'top' or 'latest'.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised replies.
        """
        raw = self.client.x.tweet_comments(
            tweet_id=tweet_id, rank=rank, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)

    async def _arun(
        self,
        tweet_id: str,
        rank: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Fetch tweet replies asynchronously.

        Args:
            tweet_id: Tweet id.
            rank: 'top' or 'latest'.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised replies.
        """
        raw = await self.async_client.x.tweet_comments(
            tweet_id=tweet_id, rank=rank, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 4. Tweet Retweeters
# ---------------------------------------------------------------------------


class ScavioXTweetRetweetersTool(ScavioBaseTool):
    """Fetch the users who retweeted a tweet.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X Tweet Retweeters"
    description: str = (
        "List the accounts that retweeted a tweet. Returns user briefs under "
        "data.retweeters with next_cursor for paging. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XTweetRetweetersInput

    def _run(
        self, tweet_id: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch retweeters synchronously.

        Args:
            tweet_id: Tweet id.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised retweeter list.
        """
        raw = self.client.x.tweet_retweeters(tweet_id=tweet_id, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "retweeters")
        return self._format_response(raw)

    async def _arun(
        self, tweet_id: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch retweeters asynchronously.

        Args:
            tweet_id: Tweet id.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised retweeter list.
        """
        raw = await self.async_client.x.tweet_retweeters(
            tweet_id=tweet_id, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "retweeters")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 5. User
# ---------------------------------------------------------------------------


class ScavioXUserTool(ScavioBaseTool):
    """Fetch an X profile by handle.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X User"
    description: str = (
        "Fetch an X profile by handle. Returns user_id, screen_name, name, "
        "description, followers_count, friends_count, statuses_count, "
        "media_count, blue_verified, location, website, avatar and "
        "created_at. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XUserInput

    def _run(self, screen_name: str, **kwargs: Any) -> str:
        """Fetch a profile synchronously.

        Args:
            screen_name: An X handle without the @.

        Returns:
            JSON-serialised profile.
        """
        raw = self.client.x.user(screen_name=screen_name)
        return self._format_response(raw)

    async def _arun(self, screen_name: str, **kwargs: Any) -> str:
        """Fetch a profile asynchronously.

        Args:
            screen_name: An X handle without the @.

        Returns:
            JSON-serialised profile.
        """
        raw = await self.async_client.x.user(screen_name=screen_name)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 6. User Tweets
# ---------------------------------------------------------------------------


class ScavioXUserTweetsTool(ScavioBaseTool):
    """Fetch a user's tweet timeline.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X User Tweets"
    description: str = (
        "Fetch a user's tweets by handle. Returns data.timeline plus a pinned "
        "tweet and the full profile under data.user. This endpoint has no "
        "has_more key -- page until next_cursor stops changing. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XUserTimelineInput

    def _run(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch a user's tweets synchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised timeline.
        """
        raw = self.client.x.user_tweets(screen_name=screen_name, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)

    async def _arun(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch a user's tweets asynchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised timeline.
        """
        raw = await self.async_client.x.user_tweets(
            screen_name=screen_name, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 7. User Replies
# ---------------------------------------------------------------------------


class ScavioXUserRepliesTool(ScavioBaseTool):
    """Fetch a user's tweets-and-replies timeline.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X User Replies"
    description: str = (
        "Fetch a user's tweets and replies by handle. Returns data.timeline "
        "with next_cursor and prev_cursor. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XUserTimelineInput

    def _run(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch a user's replies synchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised timeline.
        """
        raw = self.client.x.user_replies(screen_name=screen_name, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)

    async def _arun(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch a user's replies asynchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised timeline.
        """
        raw = await self.async_client.x.user_replies(
            screen_name=screen_name, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 8. User Media
# ---------------------------------------------------------------------------


class ScavioXUserMediaTool(ScavioBaseTool):
    """Fetch a user's media tweets.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X User Media"
    description: str = (
        "Fetch a user's media tweets by handle. Each tweet carries a media "
        "object with photos[] and videos[] (video url is the highest-bitrate "
        "mp4). Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XUserTimelineInput

    def _run(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch a user's media tweets synchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised timeline.
        """
        raw = self.client.x.user_media(screen_name=screen_name, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)

    async def _arun(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch a user's media tweets asynchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised timeline.
        """
        raw = await self.async_client.x.user_media(
            screen_name=screen_name, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "timeline")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 9. User Followers
# ---------------------------------------------------------------------------


class ScavioXUserFollowersTool(ScavioBaseTool):
    """Fetch a user's followers.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X User Followers"
    description: str = (
        "Fetch a user's followers by handle. Returns user briefs under "
        "data.followers plus followers_count and next_cursor. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XUserTimelineInput

    def _run(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch followers synchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised follower list.
        """
        raw = self.client.x.user_followers(
            screen_name=screen_name, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "followers")
        return self._format_response(raw)

    async def _arun(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch followers asynchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised follower list.
        """
        raw = await self.async_client.x.user_followers(
            screen_name=screen_name, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "followers")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 10. User Followings
# ---------------------------------------------------------------------------


class ScavioXUserFollowingsTool(ScavioBaseTool):
    """Fetch the accounts a user follows.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X User Followings"
    description: str = (
        "Fetch the accounts an X user follows. The list comes back under "
        "data.following -- singular, unlike the followers endpoint -- and "
        "there is no following_count counterpart. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XUserTimelineInput

    def _run(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch followings synchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised following list.
        """
        raw = self.client.x.user_followings(
            screen_name=screen_name, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "following")
        return self._format_response(raw)

    async def _arun(
        self, screen_name: str, cursor: str | None = None, **kwargs: Any
    ) -> str:
        """Fetch followings asynchronously.

        Args:
            screen_name: An X handle without the @.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised following list.
        """
        raw = await self.async_client.x.user_followings(
            screen_name=screen_name, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "following")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 11. Trending
# ---------------------------------------------------------------------------


class ScavioXTrendingTool(ScavioBaseTool):
    """Fetch trending topics on X for a country.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio X Trending"
    description: str = (
        "Fetch trending topics on X for a country. The country parameter is a "
        "country NAME such as 'UnitedStates' (default), not an ISO code. "
        "Returns data.trends with name, description and context. No "
        "pagination. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = _XTrendingInput

    def _run(self, country: str | None = None, **kwargs: Any) -> str:
        """Fetch trending topics synchronously.

        Args:
            country: Country name.

        Returns:
            JSON-serialised trend list.
        """
        raw = self.client.x.trending(country=country)
        raw = self._truncate_nested(raw, "data", "trends")
        return self._format_response(raw)

    async def _arun(self, country: str | None = None, **kwargs: Any) -> str:
        """Fetch trending topics asynchronously.

        Args:
            country: Country name.

        Returns:
            JSON-serialised trend list.
        """
        raw = await self.async_client.x.trending(country=country)
        raw = self._truncate_nested(raw, "data", "trends")
        return self._format_response(raw)
