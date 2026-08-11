"""Scavio Reddit tools for CrewAI.

All twelve Reddit endpoints cost 1 credit each (they were 2 before Reddit moved
to its current upstream source). A few shapes are worth knowing before wiring
these together:

* ``/reddit/search`` accepts ONLY ``query`` and ``cursor``, and returns its hits
  under ``data.results`` with ``next_cursor`` / ``has_more``.
* ``/reddit/post`` returns a FLAT post object with NO comments -- fetch those
  separately from ``/reddit/post/comments``.
* The subreddit and user feeds return ``data.posts``, not ``data.results``.
* Sort values are UPPERCASE and passed upstream verbatim. ``RISING`` exists on
  the subreddit feed only; every other feed uses the five-value set.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool

_CURSOR_DESCRIPTION = (
    "Pagination cursor -- pass next_cursor from a previous response."
)
_POST_ID_DESCRIPTION = "Post fullname (t3_...) or bare id, e.g. 't3_1v6ngaf'."
_SUBREDDIT_DESCRIPTION = "Subreddit name without the r/ prefix, e.g. 'AskReddit'."
_USERNAME_DESCRIPTION = "Reddit username without the u/ prefix, e.g. 'spez'."

_Sort = Literal["HOT", "NEW", "TOP", "BEST", "CONTROVERSIAL"]
_FeedSort = Literal["BEST", "HOT", "NEW", "TOP", "CONTROVERSIAL", "RISING"]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class ScavioRedditSearchToolSchema(BaseModel):
    """Input schema for ScavioRedditSearchTool."""

    query: str = Field(..., description="Reddit search query.")
    cursor: str | None = Field(
        default=None,
        description=_CURSOR_DESCRIPTION,
    )


class ScavioRedditSearchSuggestionsToolSchema(BaseModel):
    """Input schema for ScavioRedditSearchSuggestionsTool."""

    query: str = Field(..., description="Partial Reddit search query.")


class ScavioRedditPostToolSchema(BaseModel):
    """Input schema for ScavioRedditPostTool."""

    url: str | None = Field(
        default=None, description="Full URL of the Reddit post."
    )
    post_id: str | None = Field(
        default=None, description=_POST_ID_DESCRIPTION
    )


class ScavioRedditPostCommentsToolSchema(BaseModel):
    """Input schema for ScavioRedditPostCommentsTool."""

    post_id: str = Field(..., description=_POST_ID_DESCRIPTION)
    sort: _Sort | None = Field(
        default=None,
        description="Comment sort order, uppercase (server default 'TOP').",
    )
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class ScavioRedditCommentRepliesToolSchema(BaseModel):
    """Input schema for ScavioRedditCommentRepliesTool."""

    post_id: str = Field(..., description=_POST_ID_DESCRIPTION)
    cursor: str = Field(
        ...,
        description=(
            "Required here -- the reply_cursor of a comment returned by the "
            "post comments tool, not a next_cursor."
        ),
    )
    sort: _Sort | None = Field(
        default=None,
        description="Comment sort order, uppercase (server default 'TOP').",
    )


class ScavioRedditSubredditToolSchema(BaseModel):
    """Input schema for ScavioRedditSubredditTool."""

    subreddit: str = Field(..., description=_SUBREDDIT_DESCRIPTION)


class ScavioRedditSubredditPostsToolSchema(BaseModel):
    """Input schema for ScavioRedditSubredditPostsTool."""

    subreddit: str = Field(..., description=_SUBREDDIT_DESCRIPTION)
    sort: _FeedSort | None = Field(
        default=None,
        description=(
            "Feed sort order, uppercase (server default 'HOT'). This is the "
            "only feed that accepts 'RISING'."
        ),
    )
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class ScavioRedditUserToolSchema(BaseModel):
    """Input schema for ScavioRedditUserTool."""

    username: str = Field(..., description=_USERNAME_DESCRIPTION)


class ScavioRedditUserFeedToolSchema(BaseModel):
    """Input schema shared by the user posts / user comments tools."""

    username: str = Field(..., description=_USERNAME_DESCRIPTION)
    sort: _Sort | None = Field(
        default=None,
        description="Sort order, uppercase (server default 'NEW').",
    )
    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class ScavioRedditPopularToolSchema(BaseModel):
    """Input schema for ScavioRedditPopularTool."""

    cursor: str | None = Field(default=None, description=_CURSOR_DESCRIPTION)


class ScavioRedditTrendingToolSchema(BaseModel):
    """Input schema for ScavioRedditTrendingTool. Takes no arguments."""


# ---------------------------------------------------------------------------
# 1. Search
# ---------------------------------------------------------------------------

class ScavioRedditSearchTool(ScavioBaseTool):
    """Tool that searches Reddit posts using the Scavio API.

    Attributes:
        name: The name of the tool.
        description: A description of the tool's purpose.
        args_schema: The schema for the tool's arguments.
    """

    name: str = "Scavio Reddit Search"
    description: str = (
        "A tool that searches Reddit posts using the Scavio API. "
        "Returns post titles, URLs, subreddits, authors, scores, and "
        "timestamps as a JSON string, plus next_cursor for pagination."
    )
    args_schema: type[BaseModel] = ScavioRedditSearchToolSchema

    def _run(self, query: str, cursor: str | None = None) -> str:
        """Synchronously search Reddit posts.

        Args:
            query: Reddit search query.
            cursor: Pagination cursor from a previous response.

        Returns:
            A JSON string containing Reddit search results.
        """
        raw = self.client.reddit.search(query=query, cursor=cursor)
        self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(self, query: str, cursor: str | None = None) -> str:
        """Asynchronously search Reddit posts.

        Args:
            query: Reddit search query.
            cursor: Pagination cursor from a previous response.

        Returns:
            A JSON string containing Reddit search results.
        """
        raw = await self.async_client.reddit.search(query=query, cursor=cursor)
        self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 2. Search suggestions
# ---------------------------------------------------------------------------

class ScavioRedditSearchSuggestionsTool(ScavioBaseTool):
    """Autocomplete suggestions for a Reddit search query.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit Search Suggestions"
    description: str = (
        "Get autocomplete suggestions for a Reddit search query. Returns "
        "data.suggestions (a list of strings) and total_count. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditSearchSuggestionsToolSchema

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous suggestions lookup.

        Args:
            query: Partial Reddit search query.

        Returns:
            JSON-serialised suggestions.
        """
        raw = self.client.reddit.search_suggestions(query=query)
        raw = self._truncate_nested(raw, "data", "suggestions")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous suggestions lookup.

        Args:
            query: Partial Reddit search query.

        Returns:
            JSON-serialised suggestions.
        """
        raw = await self.async_client.reddit.search_suggestions(query=query)
        raw = self._truncate_nested(raw, "data", "suggestions")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 3. Post
# ---------------------------------------------------------------------------

class ScavioRedditPostTool(ScavioBaseTool):
    """Tool that fetches a Reddit post by URL or post id.

    Attributes:
        name: The name of the tool.
        description: A description of the tool's purpose.
        args_schema: The schema for the tool's arguments.
    """

    name: str = "Scavio Reddit Post"
    description: str = (
        "A tool that fetches a single Reddit post by url or post_id (one of "
        "the two is required) using the Scavio API. Returns a flat post "
        "object -- title, text, score, upvote_ratio, num_comments, and media. "
        "Comments are not included; use the post comments tool for those."
    )
    args_schema: type[BaseModel] = ScavioRedditPostToolSchema

    def _run(
        self,
        url: str | None = None,
        post_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Synchronously fetch Reddit post details.

        Args:
            url: URL of the Reddit post.
            post_id: Post fullname or bare id, as an alternative to url.

        Returns:
            A JSON string containing the post object.
        """
        raw = self.client.reddit.post(url=url, post_id=post_id)
        return self._format_response(raw)

    async def _arun(
        self,
        url: str | None = None,
        post_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Asynchronously fetch Reddit post details.

        Args:
            url: URL of the Reddit post.
            post_id: Post fullname or bare id, as an alternative to url.

        Returns:
            A JSON string containing the post object.
        """
        raw = await self.async_client.reddit.post(url=url, post_id=post_id)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 4. Post comments
# ---------------------------------------------------------------------------

class ScavioRedditPostCommentsTool(ScavioBaseTool):
    """Top-level comments on a Reddit post.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit Post Comments"
    description: str = (
        "Retrieve top-level comments on a Reddit post by post_id. Returns "
        "data.comments with comment_id, text, author, score, depth and a "
        "reply_cursor to feed the comment replies tool. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditPostCommentsToolSchema

    def _run(
        self,
        post_id: str,
        sort: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous comments lookup.

        Args:
            post_id: Post fullname or bare id.
            sort: Comment sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of comments.
        """
        raw = self.client.reddit.post_comments(
            post_id=post_id, sort=sort, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)

    async def _arun(
        self,
        post_id: str,
        sort: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous comments lookup.

        Args:
            post_id: Post fullname or bare id.
            sort: Comment sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of comments.
        """
        raw = await self.async_client.reddit.post_comments(
            post_id=post_id, sort=sort, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 5. Comment replies
# ---------------------------------------------------------------------------

class ScavioRedditCommentRepliesTool(ScavioBaseTool):
    """Replies to a specific Reddit comment.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit Comment Replies"
    description: str = (
        "Retrieve replies to a Reddit comment. Both post_id and cursor are "
        "required, and cursor must be the reply_cursor of a comment returned "
        "by the post comments tool. Returns data.replies. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditCommentRepliesToolSchema

    def _run(
        self,
        post_id: str,
        cursor: str,
        sort: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous replies lookup.

        Args:
            post_id: Post fullname or bare id.
            cursor: reply_cursor of the parent comment.
            sort: Comment sort order.

        Returns:
            JSON-serialised list of replies.
        """
        raw = self.client.reddit.comment_replies(
            post_id=post_id, cursor=cursor, sort=sort
        )
        raw = self._truncate_nested(raw, "data", "replies")
        return self._format_response(raw)

    async def _arun(
        self,
        post_id: str,
        cursor: str,
        sort: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous replies lookup.

        Args:
            post_id: Post fullname or bare id.
            cursor: reply_cursor of the parent comment.
            sort: Comment sort order.

        Returns:
            JSON-serialised list of replies.
        """
        raw = await self.async_client.reddit.comment_replies(
            post_id=post_id, cursor=cursor, sort=sort
        )
        raw = self._truncate_nested(raw, "data", "replies")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 6. Subreddit
# ---------------------------------------------------------------------------

class ScavioRedditSubredditTool(ScavioBaseTool):
    """Metadata for a subreddit.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit Subreddit"
    description: str = (
        "Retrieve metadata for a subreddit by name (no r/ prefix). Returns a "
        "flat object with title, description, subscribers, active_count, "
        "type, icon and banner. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditSubredditToolSchema

    def _run(self, subreddit: str, **kwargs: Any) -> str:
        """Execute a synchronous subreddit lookup.

        Args:
            subreddit: Subreddit name without the r/ prefix.

        Returns:
            JSON-serialised subreddit metadata.
        """
        raw = self.client.reddit.subreddit(subreddit=subreddit)
        return self._format_response(raw)

    async def _arun(self, subreddit: str, **kwargs: Any) -> str:
        """Execute an asynchronous subreddit lookup.

        Args:
            subreddit: Subreddit name without the r/ prefix.

        Returns:
            JSON-serialised subreddit metadata.
        """
        raw = await self.async_client.reddit.subreddit(subreddit=subreddit)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 7. Subreddit posts
# ---------------------------------------------------------------------------

class ScavioRedditSubredditPostsTool(ScavioBaseTool):
    """A subreddit's post feed.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit Subreddit Posts"
    description: str = (
        "Retrieve a subreddit's post feed. Returns data.posts (not results) "
        "with next_cursor and has_more. Sort values are uppercase and this "
        "is the only feed accepting 'RISING'. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditSubredditPostsToolSchema

    def _run(
        self,
        subreddit: str,
        sort: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous subreddit feed lookup.

        Args:
            subreddit: Subreddit name without the r/ prefix.
            sort: Feed sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of posts.
        """
        raw = self.client.reddit.subreddit_posts(
            subreddit=subreddit, sort=sort, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)

    async def _arun(
        self,
        subreddit: str,
        sort: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous subreddit feed lookup.

        Args:
            subreddit: Subreddit name without the r/ prefix.
            sort: Feed sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of posts.
        """
        raw = await self.async_client.reddit.subreddit_posts(
            subreddit=subreddit, sort=sort, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 8. User
# ---------------------------------------------------------------------------

class ScavioRedditUserTool(ScavioBaseTool):
    """A redditor's profile.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit User"
    description: str = (
        "Retrieve a redditor's profile by username (no u/ prefix). Returns a "
        "flat object with karma, post_karma, comment_karma, description, "
        "avatar and account flags. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditUserToolSchema

    def _run(self, username: str, **kwargs: Any) -> str:
        """Execute a synchronous user lookup.

        Args:
            username: Reddit username without the u/ prefix.

        Returns:
            JSON-serialised profile data.
        """
        raw = self.client.reddit.user(username=username)
        return self._format_response(raw)

    async def _arun(self, username: str, **kwargs: Any) -> str:
        """Execute an asynchronous user lookup.

        Args:
            username: Reddit username without the u/ prefix.

        Returns:
            JSON-serialised profile data.
        """
        raw = await self.async_client.reddit.user(username=username)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 9. User posts
# ---------------------------------------------------------------------------

class ScavioRedditUserPostsTool(ScavioBaseTool):
    """A redditor's submitted posts.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit User Posts"
    description: str = (
        "Retrieve the posts a redditor has submitted. Returns data.posts "
        "(not results) with next_cursor and has_more. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditUserFeedToolSchema

    def _run(
        self,
        username: str,
        sort: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous user posts lookup.

        Args:
            username: Reddit username without the u/ prefix.
            sort: Sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of posts.
        """
        raw = self.client.reddit.user_posts(
            username=username, sort=sort, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)

    async def _arun(
        self,
        username: str,
        sort: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous user posts lookup.

        Args:
            username: Reddit username without the u/ prefix.
            sort: Sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of posts.
        """
        raw = await self.async_client.reddit.user_posts(
            username=username, sort=sort, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 10. User comments
# ---------------------------------------------------------------------------

class ScavioRedditUserCommentsTool(ScavioBaseTool):
    """A redditor's comments.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit User Comments"
    description: str = (
        "Retrieve the comments a redditor has left. Returns data.comments, "
        "each with a nested post {id, title}. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditUserFeedToolSchema

    def _run(
        self,
        username: str,
        sort: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous user comments lookup.

        Args:
            username: Reddit username without the u/ prefix.
            sort: Sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of comments.
        """
        raw = self.client.reddit.user_comments(
            username=username, sort=sort, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)

    async def _arun(
        self,
        username: str,
        sort: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous user comments lookup.

        Args:
            username: Reddit username without the u/ prefix.
            sort: Sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of comments.
        """
        raw = await self.async_client.reddit.user_comments(
            username=username, sort=sort, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 11. Popular
# ---------------------------------------------------------------------------

class ScavioRedditPopularTool(ScavioBaseTool):
    """The site-wide popular feed.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit Popular"
    description: str = (
        "Retrieve Reddit's site-wide popular feed. Takes an optional cursor "
        "only. Returns data.posts with next_cursor and has_more. "
        "Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditPopularToolSchema

    def _run(self, cursor: str | None = None, **kwargs: Any) -> str:
        """Execute a synchronous popular feed lookup.

        Args:
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of posts.
        """
        raw = self.client.reddit.popular(cursor=cursor)
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)

    async def _arun(self, cursor: str | None = None, **kwargs: Any) -> str:
        """Execute an asynchronous popular feed lookup.

        Args:
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of posts.
        """
        raw = await self.async_client.reddit.popular(cursor=cursor)
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 12. Trending
# ---------------------------------------------------------------------------

class ScavioRedditTrendingTool(ScavioBaseTool):
    """Current trending Reddit search queries.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Reddit Trending"
    description: str = (
        "Retrieve the Reddit searches trending right now. Takes no "
        "arguments. Returns data.trending, each item {query, raw_query}. "
        "Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioRedditTrendingToolSchema

    def _run(self, **kwargs: Any) -> str:
        """Execute a synchronous trending lookup.

        Returns:
            JSON-serialised trending queries.
        """
        raw = self.client.reddit.trending()
        raw = self._truncate_nested(raw, "data", "trending")
        return self._format_response(raw)

    async def _arun(self, **kwargs: Any) -> str:
        """Execute an asynchronous trending lookup.

        Returns:
            JSON-serialised trending queries.
        """
        raw = await self.async_client.reddit.trending()
        raw = self._truncate_nested(raw, "data", "trending")
        return self._format_response(raw)
