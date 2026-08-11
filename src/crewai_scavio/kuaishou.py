"""Scavio Kuaishou (China) tools for CrewAI.

PER-ENDPOINT, not flat: kuaishouCreditCost(path). profile=10, video=2,
videos/batch=40, all four search endpoints=10, everything else=1. Every SDK
docstring, MCP description, n8n hint and docs page must carry ITS OWN cost -- a
single 'Costs N credits' line for the platform is wrong by up to 40x.

- NAME IT KUAISHOU (CHINA), NEVER KWAI. TikHub does not serve Kwai
  international (kwai.com) -- a real kwai.com photo id returns an empty
  envelope. Any surface calling this 'Kwai' attracts users it cannot serve.
- Pricing is per-endpoint. Every SDK/doc must carry the per-endpoint cost, not
  a constant. profile=10, video=2, videos/batch=40, all four search
  endpoints=10, everything else=1.
- videos/batch is capped at 20 photo ids (MAX_BATCH_IDS) precisely because it
  is the one call that can fan out upstream spend.
- Kuaishou hides errors inside HTTP 200 (result != 1); the transport's assertOk
  surfaces these as 502.
"""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _KuaishouProfileInput(BaseModel):
    """Input schema for ScavioKuaishouProfileTool."""

    user_id: str = Field(
        ...,
        description=(
            "Kuaishou user id (non-empty); get one from user_resolve or search_users."
        ),
    )


class _KuaishouUserPostsInput(BaseModel):
    """Input schema for ScavioKuaishouUserPostsTool."""

    user_id: str = Field(
        ...,
        description=(
            "Kuaishou user id (non-empty); get one from user_resolve or search_users."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque next_cursor from a prior response; omit for the first page."
        ),
    )


class _KuaishouUserLiveInput(BaseModel):
    """Input schema for ScavioKuaishouUserLiveTool."""

    user_id: str = Field(
        ...,
        description=(
            "Kuaishou user id (non-empty); get one from user_resolve or search_users."
        ),
    )


class _KuaishouUserResolveInput(BaseModel):
    """Input schema for ScavioKuaishouUserResolveTool."""

    share_link: str = Field(
        ...,
        description=(
            "A kuaishou.com or v.kuaishou.com URL; kwai.com links are rejected."
        ),
    )


class _KuaishouVideoInput(BaseModel):
    """Input schema for ScavioKuaishouVideoTool."""

    photo_id: str | None = Field(
        default=None,
        description="Kuaishou photo (video) id, non-empty.",
    )
    url: str | None = Field(
        default=None,
        description="Full kuaishou.com video URL, as an alternative to photo_id.",
    )


class _KuaishouVideoCommentsInput(BaseModel):
    """Input schema for ScavioKuaishouVideoCommentsTool."""

    photo_id: str = Field(
        ...,
        description="Kuaishou photo (video) id, non-empty.",
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque next_cursor from a prior response; omit for the first page."
        ),
    )


class _KuaishouCommentRepliesInput(BaseModel):
    """Input schema for ScavioKuaishouCommentRepliesTool."""

    photo_id: str = Field(
        ...,
        description="Kuaishou photo (video) id, non-empty.",
    )
    root_comment_id: str = Field(
        ...,
        description=(
            "Id of the top-level comment whose replies you want, from video_comments."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque next_cursor from a prior response; omit for the first page."
        ),
    )
    count: int | None = Field(
        default=None,
        description="Replies per page, 1-50. Omit to use the upstream default.",
    )


class _KuaishouVideosBatchInput(BaseModel):
    """Input schema for ScavioKuaishouVideosBatchTool."""

    photo_ids: list[str] = Field(
        ...,
        description=(
            "Kuaishou photo (video) ids, 1-20 per call; more than 20 is rejected."
        ),
    )


class _KuaishouSearchInput(BaseModel):
    """Input schema for ScavioKuaishouSearchTool."""

    keyword: str = Field(
        ...,
        description="Search keyword, 1-200 characters.",
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque next_cursor from a prior response; omit for the first page."
        ),
    )


class _KuaishouSearchVideosInput(BaseModel):
    """Input schema for ScavioKuaishouSearchVideosTool."""

    keyword: str = Field(
        ...,
        description="Search keyword, 1-200 characters.",
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque next_cursor from a prior response; omit for the first page."
        ),
    )


class _KuaishouSearchUsersInput(BaseModel):
    """Input schema for ScavioKuaishouSearchUsersTool."""

    keyword: str = Field(
        ...,
        description="Search keyword, 1-200 characters.",
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque next_cursor from a prior response; omit for the first page."
        ),
    )


class _KuaishouSearchLiveInput(BaseModel):
    """Input schema for ScavioKuaishouSearchLiveTool."""

    keyword: str = Field(
        ...,
        description="Search keyword, 1-200 characters.",
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque next_cursor from a prior response; omit for the first page."
        ),
    )


class _KuaishouTagFeedInput(BaseModel):
    """Input schema for ScavioKuaishouTagFeedTool."""

    tag: str = Field(
        ...,
        description="Hashtag text without the leading '#', 1-200 characters.",
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Opaque next_cursor from a prior response; omit for the first page."
        ),
    )


class _KuaishouTrendingInput(BaseModel):
    """Input schema for ScavioKuaishouTrendingTool."""

    board: Literal["hot", "live", "shopping", "brand", "music"] | None = Field(
        default=None,
        description="Leaderboard to return; defaults to 'hot' when omitted.",
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ScavioKuaishouProfileTool(ScavioBaseTool):
    """Profile details for a Kuaishou user."""

    name: str = "Scavio Kuaishou Profile"
    description: str = (
        "Profile details for a Kuaishou user. Costs 10 credits. Kuaishou is priced PER "
        "ENDPOINT (1, 2, 10 or 40), never per platform."
    )
    args_schema: Type[BaseModel] = _KuaishouProfileInput

    def _run(self, user_id: str, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/profile synchronously.

        Args:
            user_id: Kuaishou user id (non-empty); get one from user_resolve or
                search_users.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.profile(user_id=user_id)
        return self._format_response(raw)

    async def _arun(self, user_id: str, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/profile asynchronously.

        Args:
            user_id: Kuaishou user id (non-empty); get one from user_resolve or
                search_users.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.profile(user_id=user_id)
        return self._format_response(raw)


class ScavioKuaishouUserPostsTool(ScavioBaseTool):
    """A Kuaishou user's top posts, cursor-paginated via next_cursor."""

    name: str = "Scavio Kuaishou User Posts"
    description: str = (
        "A Kuaishou user's top posts, cursor-paginated via next_cursor. Costs 1 "
        "credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform."
    )
    args_schema: Type[BaseModel] = _KuaishouUserPostsInput

    def _run(self, user_id: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/user/posts synchronously.

        Args:
            user_id: Kuaishou user id (non-empty); get one from user_resolve or
                search_users.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.user_posts(user_id=user_id, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "feeds")
        return self._format_response(raw)

    async def _arun(
        self,
        user_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/user/posts asynchronously.

        Args:
            user_id: Kuaishou user id (non-empty); get one from user_resolve or
                search_users.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.user_posts(
            user_id=user_id,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "feeds")
        return self._format_response(raw)


class ScavioKuaishouUserLiveTool(ScavioBaseTool):
    """A Kuaishou user's current live-stream status."""

    name: str = "Scavio Kuaishou User Live"
    description: str = (
        "A Kuaishou user's current live-stream status. Not paginated. Costs 1 credit. "
        "Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform."
    )
    args_schema: Type[BaseModel] = _KuaishouUserLiveInput

    def _run(self, user_id: str, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/user/live synchronously.

        Args:
            user_id: Kuaishou user id (non-empty); get one from user_resolve or
                search_users.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.user_live(user_id=user_id)
        return self._format_response(raw)

    async def _arun(self, user_id: str, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/user/live asynchronously.

        Args:
            user_id: Kuaishou user id (non-empty); get one from user_resolve or
                search_users.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.user_live(user_id=user_id)
        return self._format_response(raw)


class ScavioKuaishouUserResolveTool(ScavioBaseTool):
    """Turns a Kuaishou share link into a user id."""

    name: str = "Scavio Kuaishou User Resolve"
    description: str = (
        "Turns a Kuaishou share link into a user id. Only kuaishou.com and "
        "v.kuaishou.com links are accepted; Kwai international (kwai.com) is not "
        "served upstream. Costs 1 credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or "
        "40), never per platform."
    )
    args_schema: Type[BaseModel] = _KuaishouUserResolveInput

    def _run(self, share_link: str, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/user/resolve synchronously.

        Args:
            share_link: A kuaishou.com or v.kuaishou.com URL; kwai.com links are
                rejected.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.user_resolve(share_link=share_link)
        return self._format_response(raw)

    async def _arun(self, share_link: str, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/user/resolve asynchronously.

        Args:
            share_link: A kuaishou.com or v.kuaishou.com URL; kwai.com links are
                rejected.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.user_resolve(share_link=share_link)
        return self._format_response(raw)


class ScavioKuaishouVideoTool(ScavioBaseTool):
    """A single Kuaishou video by photo id or URL."""

    name: str = "Scavio Kuaishou Video"
    description: str = (
        "A single Kuaishou video by photo id or URL. Provide photo_id or url. Costs 2 "
        "credits. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per "
        "platform."
    )
    args_schema: Type[BaseModel] = _KuaishouVideoInput

    def _run(
        self,
        photo_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/video synchronously.

        Args:
            photo_id: Kuaishou photo (video) id, non-empty.
            url: Full kuaishou.com video URL, as an alternative to photo_id.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.video(photo_id=photo_id, url=url)
        return self._format_response(raw)

    async def _arun(
        self,
        photo_id: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/video asynchronously.

        Args:
            photo_id: Kuaishou photo (video) id, non-empty.
            url: Full kuaishou.com video URL, as an alternative to photo_id.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.video(photo_id=photo_id, url=url)
        return self._format_response(raw)


class ScavioKuaishouVideoCommentsTool(ScavioBaseTool):
    """Comments on a Kuaishou video, cursor-paginated via next_cursor."""

    name: str = "Scavio Kuaishou Video Comments"
    description: str = (
        "Comments on a Kuaishou video, cursor-paginated via next_cursor. Costs 1 "
        "credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform."
    )
    args_schema: Type[BaseModel] = _KuaishouVideoCommentsInput

    def _run(self, photo_id: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/video/comments synchronously.

        Args:
            photo_id: Kuaishou photo (video) id, non-empty.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.video_comments(photo_id=photo_id, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "rootComments")
        return self._format_response(raw)

    async def _arun(
        self,
        photo_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/video/comments asynchronously.

        Args:
            photo_id: Kuaishou photo (video) id, non-empty.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.video_comments(
            photo_id=photo_id,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "rootComments")
        return self._format_response(raw)


class ScavioKuaishouCommentRepliesTool(ScavioBaseTool):
    """Replies under a root comment on a Kuaishou video, cursor-paginated via
    next_cursor; count sizes the page (1-50).
    """

    name: str = "Scavio Kuaishou Comment Replies"
    description: str = (
        "Replies under a root comment on a Kuaishou video, cursor-paginated via "
        "next_cursor; count sizes the page (1-50). Costs 1 credit. Kuaishou is priced "
        "PER ENDPOINT (1, 2, 10 or 40), never per platform."
    )
    args_schema: Type[BaseModel] = _KuaishouCommentRepliesInput

    def _run(
        self,
        photo_id: str,
        root_comment_id: str,
        cursor: str | None = None,
        count: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/video/sub-comments synchronously.

        Args:
            photo_id: Kuaishou photo (video) id, non-empty.
            root_comment_id: Id of the top-level comment whose replies you want, from
                video_comments.
            cursor: Opaque next_cursor from a prior response; omit for the first page.
            count: Replies per page, 1-50. Omit to use the upstream default.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.comment_replies(
            photo_id=photo_id,
            root_comment_id=root_comment_id,
            cursor=cursor,
            count=count,
        )
        raw = self._truncate_nested(raw, "data", "subComments")
        return self._format_response(raw)

    async def _arun(
        self,
        photo_id: str,
        root_comment_id: str,
        cursor: str | None = None,
        count: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/video/sub-comments asynchronously.

        Args:
            photo_id: Kuaishou photo (video) id, non-empty.
            root_comment_id: Id of the top-level comment whose replies you want, from
                video_comments.
            cursor: Opaque next_cursor from a prior response; omit for the first page.
            count: Replies per page, 1-50. Omit to use the upstream default.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.comment_replies(
            photo_id=photo_id,
            root_comment_id=root_comment_id,
            cursor=cursor,
            count=count,
        )
        raw = self._truncate_nested(raw, "data", "subComments")
        return self._format_response(raw)


class ScavioKuaishouVideosBatchTool(ScavioBaseTool):
    """Several Kuaishou videos in one call, hard-capped at 20 photo ids."""

    name: str = "Scavio Kuaishou Videos Batch"
    description: str = (
        "Several Kuaishou videos in one call, hard-capped at 20 photo ids. Costs 40 "
        "credits. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per "
        "platform."
    )
    args_schema: Type[BaseModel] = _KuaishouVideosBatchInput

    def _run(self, photo_ids: list[str], **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/videos/batch synchronously.

        Args:
            photo_ids: Kuaishou photo (video) ids, 1-20 per call; more than 20 is
                rejected.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.videos_batch(photo_ids=photo_ids)
        raw = self._truncate_nested(raw, "data", "photos")
        return self._format_response(raw)

    async def _arun(self, photo_ids: list[str], **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/videos/batch asynchronously.

        Args:
            photo_ids: Kuaishou photo (video) ids, 1-20 per call; more than 20 is
                rejected.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.videos_batch(photo_ids=photo_ids)
        raw = self._truncate_nested(raw, "data", "photos")
        return self._format_response(raw)


class ScavioKuaishouSearchTool(ScavioBaseTool):
    """Mixed-result search across Kuaishou, cursor-paginated via next_cursor."""

    name: str = "Scavio Kuaishou Search"
    description: str = (
        "Mixed-result search across Kuaishou, cursor-paginated via next_cursor. Costs "
        "10 credits. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per "
        "platform."
    )
    args_schema: Type[BaseModel] = _KuaishouSearchInput

    def _run(self, keyword: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/search synchronously.

        Args:
            keyword: Search keyword, 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.kuaishou.search(keyword=keyword, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)

    async def _arun(
        self,
        keyword: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/search asynchronously.

        Args:
            keyword: Search keyword, 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.kuaishou.search(keyword=keyword, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)


class ScavioKuaishouSearchVideosTool(ScavioBaseTool):
    """Kuaishou video search results, cursor-paginated via next_cursor."""

    name: str = "Scavio Kuaishou Search Videos"
    description: str = (
        "Kuaishou video search results, cursor-paginated via next_cursor. Costs 10 "
        "credits. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per "
        "platform."
    )
    args_schema: Type[BaseModel] = _KuaishouSearchVideosInput

    def _run(self, keyword: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/search/videos synchronously.

        Args:
            keyword: Search keyword, 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.search_videos(keyword=keyword, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)

    async def _arun(
        self,
        keyword: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/search/videos asynchronously.

        Args:
            keyword: Search keyword, 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.search_videos(
            keyword=keyword,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)


class ScavioKuaishouSearchUsersTool(ScavioBaseTool):
    """Kuaishou user search results, cursor-paginated via next_cursor."""

    name: str = "Scavio Kuaishou Search Users"
    description: str = (
        "Kuaishou user search results, cursor-paginated via next_cursor. Costs 10 "
        "credits. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per "
        "platform."
    )
    args_schema: Type[BaseModel] = _KuaishouSearchUsersInput

    def _run(self, keyword: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/search/users synchronously.

        Args:
            keyword: Search keyword, 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.search_users(keyword=keyword, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)

    async def _arun(
        self,
        keyword: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/search/users asynchronously.

        Args:
            keyword: Search keyword, 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.search_users(
            keyword=keyword,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)


class ScavioKuaishouSearchLiveTool(ScavioBaseTool):
    """Kuaishou live-stream search results, cursor-paginated via next_cursor."""

    name: str = "Scavio Kuaishou Search Live"
    description: str = (
        "Kuaishou live-stream search results, cursor-paginated via next_cursor. Costs "
        "10 credits. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per "
        "platform."
    )
    args_schema: Type[BaseModel] = _KuaishouSearchLiveInput

    def _run(self, keyword: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/search/live synchronously.

        Args:
            keyword: Search keyword, 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.search_live(keyword=keyword, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)

    async def _arun(
        self,
        keyword: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/search/live asynchronously.

        Args:
            keyword: Search keyword, 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.search_live(
            keyword=keyword,
            cursor=cursor,
        )
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)


class ScavioKuaishouTagFeedTool(ScavioBaseTool):
    """Posts under a Kuaishou hashtag, cursor-paginated via next_cursor."""

    name: str = "Scavio Kuaishou Tag Feed"
    description: str = (
        "Posts under a Kuaishou hashtag, cursor-paginated via next_cursor. Costs 1 "
        "credit. Kuaishou is priced PER ENDPOINT (1, 2, 10 or 40), never per platform."
    )
    args_schema: Type[BaseModel] = _KuaishouTagFeedInput

    def _run(self, tag: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/tag/feed synchronously.

        Args:
            tag: Hashtag text without the leading '#', 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.tag_feed(tag=tag, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)

    async def _arun(self, tag: str, cursor: str | None = None, **kwargs: Any) -> str:
        """Call /api/v1/kuaishou/tag/feed asynchronously.

        Args:
            tag: Hashtag text without the leading '#', 1-200 characters.
            cursor: Opaque next_cursor from a prior response; omit for the first page.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.tag_feed(tag=tag, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "mixFeeds")
        return self._format_response(raw)


class ScavioKuaishouTrendingTool(ScavioBaseTool):
    """Kuaishou hot / live / shopping / brand / music leaderboards."""

    name: str = "Scavio Kuaishou Trending"
    description: str = (
        "Kuaishou hot / live / shopping / brand / music leaderboards. One board per "
        "call, not paginated. Costs 1 credit. Kuaishou is priced PER ENDPOINT (1, 2, "
        "10 or 40), never per platform."
    )
    args_schema: Type[BaseModel] = _KuaishouTrendingInput

    def _run(
        self,
        board: Literal["hot", "live", "shopping", "brand", "music"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/trending synchronously.

        Args:
            board: Leaderboard to return; defaults to 'hot' when omitted.

        Returns:
            JSON-serialised results.
        """
        raw = self.client.kuaishou.trending(board=board)
        raw = self._truncate_nested(raw, "data", "hots")
        return self._format_response(raw)

    async def _arun(
        self,
        board: Literal["hot", "live", "shopping", "brand", "music"] | None = None,
        **kwargs: Any,
    ) -> str:
        """Call /api/v1/kuaishou/trending asynchronously.

        Args:
            board: Leaderboard to return; defaults to 'hot' when omitted.

        Returns:
            JSON-serialised results.
        """
        raw = await self.async_client.kuaishou.trending(board=board)
        raw = self._truncate_nested(raw, "data", "hots")
        return self._format_response(raw)
