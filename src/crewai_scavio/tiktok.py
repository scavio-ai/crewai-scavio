"""Scavio TikTok tools for CrewAI."""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _ProfileInput(BaseModel):
    """Input schema for ScavioTikTokProfileTool."""

    username: str | None = Field(
        default=None, description="TikTok username to look up."
    )
    sec_user_id: str | None = Field(
        default=None, description="TikTok sec_user_id to look up."
    )


class _UserPostsInput(BaseModel):
    """Input schema for ScavioTikTokUserPostsTool."""

    sec_user_id: str = Field(
        ..., description="The sec_user_id of the TikTok user."
    )


class _VideoInput(BaseModel):
    """Input schema for ScavioTikTokVideoTool."""

    video_id: str = Field(..., description="The TikTok video ID.")


class _VideoCommentsInput(BaseModel):
    """Input schema for ScavioTikTokVideoCommentsTool."""

    video_id: str = Field(
        ..., description="The TikTok video ID to fetch comments for."
    )


class _CommentRepliesInput(BaseModel):
    """Input schema for ScavioTikTokCommentRepliesTool."""

    video_id: str = Field(
        ..., description="The TikTok video ID containing the comment."
    )
    comment_id: str = Field(
        ..., description="The comment ID to fetch replies for."
    )


class _SearchVideosInput(BaseModel):
    """Input schema for ScavioTikTokSearchVideosTool."""

    keyword: str = Field(..., description="The search keyword.")


class _SearchUsersInput(BaseModel):
    """Input schema for ScavioTikTokSearchUsersTool."""

    keyword: str = Field(..., description="The search keyword.")


class _HashtagInput(BaseModel):
    """Input schema for ScavioTikTokHashtagTool."""

    hashtag_name: str | None = Field(
        default=None, description="The hashtag name to look up."
    )
    hashtag_id: str | None = Field(
        default=None, description="The hashtag ID to look up."
    )


class _HashtagVideosInput(BaseModel):
    """Input schema for ScavioTikTokHashtagVideosTool."""

    hashtag_id: str = Field(
        ..., description="The hashtag ID to fetch videos for."
    )


class _UserFollowersInput(BaseModel):
    """Input schema for ScavioTikTokUserFollowersTool."""

    sec_user_id: str = Field(
        ..., description="The sec_user_id of the TikTok user."
    )


class _UserFollowingsInput(BaseModel):
    """Input schema for ScavioTikTokUserFollowingsTool."""

    sec_user_id: str = Field(
        ..., description="The sec_user_id of the TikTok user."
    )


# ---------------------------------------------------------------------------
# 1. Profile
# ---------------------------------------------------------------------------


class ScavioTikTokProfileTool(ScavioBaseTool):
    """Fetch a TikTok user profile by username or sec_user_id.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Profile"
    description: str = (
        "Retrieve a TikTok user profile by username or sec_user_id."
    )
    args_schema: Type[BaseModel] = _ProfileInput

    def _run(
        self,
        username: str | None = None,
        sec_user_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous profile lookup.

        Args:
            username: TikTok username.
            sec_user_id: TikTok sec_user_id.

        Returns:
            JSON-serialised profile data.
        """
        raw = self.client.tiktok.profile(
            username=username, sec_user_id=sec_user_id
        )
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        sec_user_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous profile lookup.

        Args:
            username: TikTok username.
            sec_user_id: TikTok sec_user_id.

        Returns:
            JSON-serialised profile data.
        """
        raw = await self.async_client.tiktok.profile(
            username=username, sec_user_id=sec_user_id
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 2. User Posts
# ---------------------------------------------------------------------------


class ScavioTikTokUserPostsTool(ScavioBaseTool):
    """Fetch posts published by a TikTok user.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
        sort_type: Sort order -- "0" for latest, "1" for popular.
    """

    name: str = "Scavio TikTok User Posts"
    description: str = (
        "Retrieve posts from a TikTok user by their sec_user_id."
    )
    args_schema: Type[BaseModel] = _UserPostsInput

    sort_type: Literal["0", "1"] | None = None

    def _run(self, sec_user_id: str, **kwargs: Any) -> str:
        """Execute a synchronous user posts lookup.

        Args:
            sec_user_id: The sec_user_id of the TikTok user.

        Returns:
            JSON-serialised list of user posts.
        """
        raw = self.client.tiktok.user_posts(
            sec_user_id=sec_user_id, sort_type=self.sort_type
        )
        raw = self._truncate_nested(raw, "data", "aweme_list")
        return self._format_response(raw)

    async def _arun(self, sec_user_id: str, **kwargs: Any) -> str:
        """Execute an asynchronous user posts lookup.

        Args:
            sec_user_id: The sec_user_id of the TikTok user.

        Returns:
            JSON-serialised list of user posts.
        """
        raw = await self.async_client.tiktok.user_posts(
            sec_user_id=sec_user_id, sort_type=self.sort_type
        )
        raw = self._truncate_nested(raw, "data", "aweme_list")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 3. Video
# ---------------------------------------------------------------------------


class ScavioTikTokVideoTool(ScavioBaseTool):
    """Fetch details about a single TikTok video.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Video"
    description: str = "Retrieve details of a TikTok video by its video ID."
    args_schema: Type[BaseModel] = _VideoInput

    def _run(self, video_id: str, **kwargs: Any) -> str:
        """Execute a synchronous video lookup.

        Args:
            video_id: The TikTok video ID.

        Returns:
            JSON-serialised video data.
        """
        raw = self.client.tiktok.video(video_id=video_id)
        return self._format_response(raw)

    async def _arun(self, video_id: str, **kwargs: Any) -> str:
        """Execute an asynchronous video lookup.

        Args:
            video_id: The TikTok video ID.

        Returns:
            JSON-serialised video data.
        """
        raw = await self.async_client.tiktok.video(video_id=video_id)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 4. Video Comments
# ---------------------------------------------------------------------------


class ScavioTikTokVideoCommentsTool(ScavioBaseTool):
    """Fetch comments on a TikTok video.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
        max_results: Maximum number of comments to return.
    """

    name: str = "Scavio TikTok Video Comments"
    description: str = "Retrieve comments on a TikTok video by its video ID."
    args_schema: Type[BaseModel] = _VideoCommentsInput

    max_results: int = Field(
        default=10,
        ge=1,
        description="Maximum number of comments to return.",
    )

    def _run(self, video_id: str, **kwargs: Any) -> str:
        """Execute a synchronous video comments lookup.

        Args:
            video_id: The TikTok video ID.

        Returns:
            JSON-serialised list of comments.
        """
        raw = self.client.tiktok.video_comments(video_id=video_id)
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)

    async def _arun(self, video_id: str, **kwargs: Any) -> str:
        """Execute an asynchronous video comments lookup.

        Args:
            video_id: The TikTok video ID.

        Returns:
            JSON-serialised list of comments.
        """
        raw = await self.async_client.tiktok.video_comments(
            video_id=video_id
        )
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 5. Comment Replies
# ---------------------------------------------------------------------------


class ScavioTikTokCommentRepliesTool(ScavioBaseTool):
    """Fetch replies to a specific comment on a TikTok video.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
        max_results: Maximum number of replies to return.
    """

    name: str = "Scavio TikTok Comment Replies"
    description: str = (
        "Retrieve replies to a comment on a TikTok video."
    )
    args_schema: Type[BaseModel] = _CommentRepliesInput

    max_results: int = Field(
        default=10,
        ge=1,
        description="Maximum number of replies to return.",
    )

    def _run(
        self, video_id: str, comment_id: str, **kwargs: Any
    ) -> str:
        """Execute a synchronous comment replies lookup.

        Args:
            video_id: The TikTok video ID.
            comment_id: The comment ID.

        Returns:
            JSON-serialised list of replies.
        """
        raw = self.client.tiktok.comment_replies(
            video_id=video_id, comment_id=comment_id
        )
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)

    async def _arun(
        self, video_id: str, comment_id: str, **kwargs: Any
    ) -> str:
        """Execute an asynchronous comment replies lookup.

        Args:
            video_id: The TikTok video ID.
            comment_id: The comment ID.

        Returns:
            JSON-serialised list of replies.
        """
        raw = await self.async_client.tiktok.comment_replies(
            video_id=video_id, comment_id=comment_id
        )
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 6. Search Videos
# ---------------------------------------------------------------------------


class ScavioTikTokSearchVideosTool(ScavioBaseTool):
    """Search for TikTok videos by keyword.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
        sort_type: Sort order -- "0" for relevance, "1" for likes.
        publish_time: Filter by publish recency (days): "0" all, "1" day,
            "7" week, "30" month, "90" three months, "180" six months.
    """

    name: str = "Scavio TikTok Search Videos"
    description: str = "Search for TikTok videos by keyword."
    args_schema: Type[BaseModel] = _SearchVideosInput

    sort_type: Literal["0", "1"] | None = None
    publish_time: Literal["0", "1", "7", "30", "90", "180"] | None = None

    def _run(self, keyword: str, **kwargs: Any) -> str:
        """Execute a synchronous video search.

        Args:
            keyword: The search keyword.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.tiktok.search_videos(
            keyword=keyword,
            sort_type=self.sort_type,
            publish_time=self.publish_time,
        )
        raw = self._truncate_nested(raw, "data", "search_item_list")
        return self._format_response(raw)

    async def _arun(self, keyword: str, **kwargs: Any) -> str:
        """Execute an asynchronous video search.

        Args:
            keyword: The search keyword.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.tiktok.search_videos(
            keyword=keyword,
            sort_type=self.sort_type,
            publish_time=self.publish_time,
        )
        raw = self._truncate_nested(raw, "data", "search_item_list")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 7. Search Users
# ---------------------------------------------------------------------------


class ScavioTikTokSearchUsersTool(ScavioBaseTool):
    """Search for TikTok users by keyword.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Search Users"
    description: str = "Search for TikTok users by keyword."
    args_schema: Type[BaseModel] = _SearchUsersInput

    def _run(self, keyword: str, **kwargs: Any) -> str:
        """Execute a synchronous user search.

        Args:
            keyword: The search keyword.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.tiktok.search_users(keyword=keyword)
        raw = self._truncate_nested(raw, "data", "user_list")
        return self._format_response(raw)

    async def _arun(self, keyword: str, **kwargs: Any) -> str:
        """Execute an asynchronous user search.

        Args:
            keyword: The search keyword.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.tiktok.search_users(keyword=keyword)
        raw = self._truncate_nested(raw, "data", "user_list")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 8. Hashtag
# ---------------------------------------------------------------------------


class ScavioTikTokHashtagTool(ScavioBaseTool):
    """Look up a TikTok hashtag by name or ID.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Hashtag"
    description: str = (
        "Retrieve TikTok hashtag information by name or hashtag ID."
    )
    args_schema: Type[BaseModel] = _HashtagInput

    def _run(
        self,
        hashtag_name: str | None = None,
        hashtag_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous hashtag lookup.

        Args:
            hashtag_name: The hashtag name.
            hashtag_id: The hashtag ID.

        Returns:
            JSON-serialised hashtag data.
        """
        raw = self.client.tiktok.hashtag(
            hashtag_name=hashtag_name, hashtag_id=hashtag_id
        )
        return self._format_response(raw)

    async def _arun(
        self,
        hashtag_name: str | None = None,
        hashtag_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous hashtag lookup.

        Args:
            hashtag_name: The hashtag name.
            hashtag_id: The hashtag ID.

        Returns:
            JSON-serialised hashtag data.
        """
        raw = await self.async_client.tiktok.hashtag(
            hashtag_name=hashtag_name, hashtag_id=hashtag_id
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 9. Hashtag Videos
# ---------------------------------------------------------------------------


class ScavioTikTokHashtagVideosTool(ScavioBaseTool):
    """Fetch videos associated with a TikTok hashtag.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio TikTok Hashtag Videos"
    description: str = (
        "Retrieve videos associated with a TikTok hashtag by hashtag ID."
    )
    args_schema: Type[BaseModel] = _HashtagVideosInput

    def _run(self, hashtag_id: str, **kwargs: Any) -> str:
        """Execute a synchronous hashtag videos lookup.

        Args:
            hashtag_id: The TikTok hashtag ID.

        Returns:
            JSON-serialised list of videos.
        """
        raw = self.client.tiktok.hashtag_videos(hashtag_id=hashtag_id)
        raw = self._truncate_nested(raw, "data", "aweme_list")
        return self._format_response(raw)

    async def _arun(self, hashtag_id: str, **kwargs: Any) -> str:
        """Execute an asynchronous hashtag videos lookup.

        Args:
            hashtag_id: The TikTok hashtag ID.

        Returns:
            JSON-serialised list of videos.
        """
        raw = await self.async_client.tiktok.hashtag_videos(
            hashtag_id=hashtag_id
        )
        raw = self._truncate_nested(raw, "data", "aweme_list")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 10. User Followers
# ---------------------------------------------------------------------------


class ScavioTikTokUserFollowersTool(ScavioBaseTool):
    """Fetch followers of a TikTok user.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
        max_results: Maximum number of followers to return.
    """

    name: str = "Scavio TikTok User Followers"
    description: str = (
        "Retrieve followers of a TikTok user by their sec_user_id."
    )
    args_schema: Type[BaseModel] = _UserFollowersInput

    max_results: int = Field(
        default=10,
        ge=1,
        description="Maximum number of followers to return.",
    )

    def _run(self, sec_user_id: str, **kwargs: Any) -> str:
        """Execute a synchronous user followers lookup.

        Args:
            sec_user_id: The sec_user_id of the TikTok user.

        Returns:
            JSON-serialised list of followers.
        """
        raw = self.client.tiktok.user_followers(sec_user_id=sec_user_id)
        raw = self._truncate_nested(raw, "data", "followers")
        return self._format_response(raw)

    async def _arun(self, sec_user_id: str, **kwargs: Any) -> str:
        """Execute an asynchronous user followers lookup.

        Args:
            sec_user_id: The sec_user_id of the TikTok user.

        Returns:
            JSON-serialised list of followers.
        """
        raw = await self.async_client.tiktok.user_followers(
            sec_user_id=sec_user_id
        )
        raw = self._truncate_nested(raw, "data", "followers")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 11. User Followings
# ---------------------------------------------------------------------------


class ScavioTikTokUserFollowingsTool(ScavioBaseTool):
    """Fetch users that a TikTok user is following.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
        max_results: Maximum number of followings to return.
    """

    name: str = "Scavio TikTok User Followings"
    description: str = (
        "Retrieve the list of users a TikTok user follows by sec_user_id."
    )
    args_schema: Type[BaseModel] = _UserFollowingsInput

    max_results: int = Field(
        default=10,
        ge=1,
        description="Maximum number of followings to return.",
    )

    def _run(self, sec_user_id: str, **kwargs: Any) -> str:
        """Execute a synchronous user followings lookup.

        Args:
            sec_user_id: The sec_user_id of the TikTok user.

        Returns:
            JSON-serialised list of followings.
        """
        raw = self.client.tiktok.user_followings(sec_user_id=sec_user_id)
        raw = self._truncate_nested(raw, "data", "followings")
        return self._format_response(raw)

    async def _arun(self, sec_user_id: str, **kwargs: Any) -> str:
        """Execute an asynchronous user followings lookup.

        Args:
            sec_user_id: The sec_user_id of the TikTok user.

        Returns:
            JSON-serialised list of followings.
        """
        raw = await self.async_client.tiktok.user_followings(
            sec_user_id=sec_user_id
        )
        raw = self._truncate_nested(raw, "data", "followings")
        return self._format_response(raw)
