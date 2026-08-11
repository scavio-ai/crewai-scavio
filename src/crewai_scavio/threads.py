"""Scavio Threads tools for CrewAI.

BODY-PRICED. threadsCreditCost(hasUsername): 2 credits when addressed by
user_id, 4 credits when addressed by username. Only /profile, /user/posts and
/user/replies are username-keyed; /post, /post/comments and /search/users are
always 2. Every surface must present user_id as the cheap path and say why
(TikHub's username lookup is dead, so a handle buys a second upstream call).

- HANDLE SURCHARGE: TikHub's username lookup (fetch_user_info) is dead, so a
  handle costs a second upstream call. 4 credits by username, 2 by user_id.
  Every doc/SDK must present user_id as the cheap path.
- THERE IS NO THREADS CONTENT SEARCH -- search_top and search_recent both 400 on
  every attempt. Only people search (/search/users) exists. Do not let any
  surface imply otherwise.
- Only profile, user/posts and user/replies are username-keyed (USERNAME_KEYED
  set); post/comments takes post_id only.
- Error codes differ from the scrape.do platforms: 404 (no matching user), 422
  (missing/conflicting identifier), 502. No 400 and no 503.
"""


from typing import Any, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _ThreadsProfileInput(BaseModel):
    """Input schema for ScavioThreadsProfileTool."""

    user_id: str | None = Field(
        default=None,
        description=(
            "Numeric Threads user id, e.g. '63625256886'. The cheap path: 2 credits."
        ),
    )
    username: str | None = Field(
        default=None,
        description=(
            "Threads handle without the @ (1-60 characters). Costs 2 extra credits (4 "
            "total): the upstream handle lookup is down, so the handle is resolved "
            "through people search first. Pass user_id instead to avoid that."
        ),
    )


class _ThreadsUserPostsInput(BaseModel):
    """Input schema for ScavioThreadsUserPostsTool."""

    user_id: str | None = Field(
        default=None,
        description=(
            "Numeric Threads user id, e.g. '63625256886'. The cheap path: 2 credits."
        ),
    )
    username: str | None = Field(
        default=None,
        description=(
            "Threads handle without the @ (1-60 characters). Costs 2 extra credits (4 "
            "total) because the handle has to be resolved through people search first."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Pagination cursor from a prior response's next_cursor. Omit for the first "
            "page."
        ),
    )


class _ThreadsUserRepliesInput(BaseModel):
    """Input schema for ScavioThreadsUserRepliesTool."""

    user_id: str | None = Field(
        default=None,
        description=(
            "Numeric Threads user id, e.g. '63625256886'. The cheap path: 2 credits."
        ),
    )
    username: str | None = Field(
        default=None,
        description=(
            "Threads handle without the @ (1-60 characters). Costs 2 extra credits (4 "
            "total) because the handle has to be resolved through people search first."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Pagination cursor from a prior response's next_cursor. Omit for the first "
            "page."
        ),
    )


class _ThreadsPostInput(BaseModel):
    """Input schema for ScavioThreadsPostTool."""

    post_id: str | None = Field(
        default=None,
        description="Threads post id, e.g. '3349029093483693129'.",
    )
    url: str | None = Field(
        default=None,
        description=(
            "Full threads.net post URL (e.g. "
            "'https://www.threads.net/@natgeo/post/C8xY'), as an alternative to "
            "post_id."
        ),
    )


class _ThreadsPostCommentsInput(BaseModel):
    """Input schema for ScavioThreadsPostCommentsTool."""

    post_id: str = Field(
        ...,
        description="Threads post id, e.g. '3349029093483693129'.",
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Pagination cursor from a prior response's next_cursor. Omit for the first "
            "page."
        ),
    )


class _ThreadsSearchUsersInput(BaseModel):
    """Input schema for ScavioThreadsSearchUsersTool."""

    query: str = Field(
        ...,
        description="Name or handle to search for (1-200 characters).",
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioThreadsProfileTool(ScavioBaseTool):
    """Profile details for a Threads user."""

    name: str = "Scavio Threads Profile"
    description: str = (
        "Profile details for a Threads user. Costs 2 credits addressed by user_id and "
        "4 credits addressed by username - the price is a function of the request "
        "body, not a constant for the route."
    )
    args_schema: Type[BaseModel] = _ThreadsProfileInput

    def _run(
        self,
        user_id: str | None = None,
        username: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/threads/profile synchronously.

        Args:
            user_id: Numeric Threads user id, e.g. '63625256886'.
            username: Threads handle without the @ (1-60 characters).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.threads.profile(user_id=user_id, username=username)
        return self._format_response(raw)

    async def _arun(
        self,
        user_id: str | None = None,
        username: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/threads/profile asynchronously.

        Args:
            user_id: Numeric Threads user id, e.g. '63625256886'.
            username: Threads handle without the @ (1-60 characters).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.threads.profile(
            user_id=user_id,
            username=username,
        )
        return self._format_response(raw)


class ScavioThreadsUserPostsTool(ScavioBaseTool):
    """A user's Threads posts, cursor-paginated via next_cursor."""

    name: str = "Scavio Threads User Posts"
    description: str = (
        "A user's Threads posts, cursor-paginated via next_cursor. Costs 2 credits "
        "addressed by user_id and 4 credits addressed by username - the price is a "
        "function of the request body, not a constant for the route."
    )
    args_schema: Type[BaseModel] = _ThreadsUserPostsInput

    def _run(
        self,
        user_id: str | None = None,
        username: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/threads/user/posts synchronously.

        Args:
            user_id: Numeric Threads user id, e.g. '63625256886'.
            username: Threads handle without the @ (1-60 characters).
            cursor: Pagination cursor from a prior response's next_cursor.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.threads.user_posts(
            user_id=user_id,
            username=username,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)

    async def _arun(
        self,
        user_id: str | None = None,
        username: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/threads/user/posts asynchronously.

        Args:
            user_id: Numeric Threads user id, e.g. '63625256886'.
            username: Threads handle without the @ (1-60 characters).
            cursor: Pagination cursor from a prior response's next_cursor.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.threads.user_posts(
            user_id=user_id,
            username=username,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)


class ScavioThreadsUserRepliesTool(ScavioBaseTool):
    """A user's Threads replies, cursor-paginated via next_cursor."""

    name: str = "Scavio Threads User Replies"
    description: str = (
        "A user's Threads replies, cursor-paginated via next_cursor. Costs 2 credits "
        "addressed by user_id and 4 credits addressed by username - the price is a "
        "function of the request body, not a constant for the route."
    )
    args_schema: Type[BaseModel] = _ThreadsUserRepliesInput

    def _run(
        self,
        user_id: str | None = None,
        username: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/threads/user/replies synchronously.

        Args:
            user_id: Numeric Threads user id, e.g. '63625256886'.
            username: Threads handle without the @ (1-60 characters).
            cursor: Pagination cursor from a prior response's next_cursor.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.threads.user_replies(
            user_id=user_id,
            username=username,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)

    async def _arun(
        self,
        user_id: str | None = None,
        username: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/threads/user/replies asynchronously.

        Args:
            user_id: Numeric Threads user id, e.g. '63625256886'.
            username: Threads handle without the @ (1-60 characters).
            cursor: Pagination cursor from a prior response's next_cursor.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.threads.user_replies(
            user_id=user_id,
            username=username,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)


class ScavioThreadsPostTool(ScavioBaseTool):
    """A single Threads post, addressed by post_id or by its threads.net URL."""

    name: str = "Scavio Threads Post"
    description: str = (
        "A single Threads post, addressed by post_id or by its threads.net URL. Costs "
        "2 credits. Threads is body-priced by identifier, but this endpoint has no "
        "username form, so it is always 2."
    )
    args_schema: Type[BaseModel] = _ThreadsPostInput

    def _run(
        self,
        post_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/threads/post synchronously.

        Args:
            post_id: Threads post id, e.g. '3349029093483693129'.
            url: Full threads.net post URL (e.g.
                'https://www.threads.net/@natgeo/post/C8xY'), as an alternative to
                post_id.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.threads.post(post_id=post_id, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        post_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/threads/post asynchronously.

        Args:
            post_id: Threads post id, e.g. '3349029093483693129'.
            url: Full threads.net post URL (e.g.
                'https://www.threads.net/@natgeo/post/C8xY'), as an alternative to
                post_id.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.threads.post(post_id=post_id, url=url)
        return self._format_response(raw)


class ScavioThreadsPostCommentsTool(ScavioBaseTool):
    """Replies to a Threads post, cursor-paginated via next_cursor."""

    name: str = "Scavio Threads Post Comments"
    description: str = (
        "Replies to a Threads post, cursor-paginated via next_cursor. Costs 2 credits. "
        "Threads is body-priced by identifier, but this endpoint has no username form, "
        "so it is always 2."
    )
    args_schema: Type[BaseModel] = _ThreadsPostCommentsInput

    def _run(self, post_id: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/threads/post/comments synchronously.

        Args:
            post_id: Threads post id, e.g. '3349029093483693129'.
            cursor: Pagination cursor from a prior response's next_cursor.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.threads.post_comments(post_id=post_id, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)

    async def _arun(
        self,
        post_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/threads/post/comments asynchronously.

        Args:
            post_id: Threads post id, e.g. '3349029093483693129'.
            cursor: Pagination cursor from a prior response's next_cursor.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.threads.post_comments(
            post_id=post_id,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)


class ScavioThreadsSearchUsersTool(ScavioBaseTool):
    """Search Threads profiles by name or handle."""

    name: str = "Scavio Threads Search Users"
    description: str = (
        "Search Threads profiles by name or handle. This is the only search Threads "
        "exposes - there is no post or content search - and it returns a single "
        "unpaginated page. Costs 2 credits. Threads is body-priced by identifier, but "
        "this endpoint has no username form, so it is always 2."
    )
    args_schema: Type[BaseModel] = _ThreadsSearchUsersInput

    def _run(self, query: str, **kwargs: Any) -> str:
        """Call /api/v1/threads/search/users synchronously.

        Args:
            query: Name or handle to search for (1-200 characters).

        Returns:
            JSON-serialised results.
        """
        raw = self.client.threads.search_users(query=query)
        raw = self._truncate_nested(raw, "data", "users")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Call /api/v1/threads/search/users asynchronously.

        Args:
            query: Name or handle to search for (1-200 characters).

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.threads.search_users(query=query)
        raw = self._truncate_nested(raw, "data", "users")
        return self._format_response(raw)
