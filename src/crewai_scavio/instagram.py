"""Scavio Instagram tools for CrewAI."""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------


class _ProfileInput(BaseModel):
    """Input schema for ScavioInstagramProfileTool."""

    username: str | None = Field(
        default=None, description="Instagram username to look up."
    )
    user_id: str | None = Field(
        default=None, description="Instagram user_id to look up."
    )


class _UserPostsInput(BaseModel):
    """Input schema for ScavioInstagramUserPostsTool."""

    username: str | None = Field(
        default=None, description="Instagram username of the user."
    )
    user_id: str | None = Field(
        default=None, description="Instagram user_id of the user."
    )
    count: int | None = Field(
        default=None, description="Number of posts to fetch."
    )
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class _UserReelsInput(BaseModel):
    """Input schema for ScavioInstagramUserReelsTool."""

    username: str | None = Field(
        default=None, description="Instagram username of the user."
    )
    user_id: str | None = Field(
        default=None, description="Instagram user_id of the user."
    )
    count: int | None = Field(
        default=None, description="Number of reels to fetch."
    )
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class _TaggedPostsInput(BaseModel):
    """Input schema for ScavioInstagramTaggedPostsTool."""

    username: str | None = Field(
        default=None, description="Instagram username of the user."
    )
    user_id: str | None = Field(
        default=None, description="Instagram user_id of the user."
    )
    count: int | None = Field(
        default=None, description="Number of tagged posts to fetch."
    )
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class _StoriesInput(BaseModel):
    """Input schema for ScavioInstagramStoriesTool."""

    username: str | None = Field(
        default=None, description="Instagram username of the user."
    )
    user_id: str | None = Field(
        default=None, description="Instagram user_id of the user."
    )


class _PostInput(BaseModel):
    """Input schema for ScavioInstagramPostTool."""

    url: str | None = Field(
        default=None, description="URL of the Instagram post."
    )
    media_id: str | None = Field(
        default=None, description="The Instagram media ID of the post."
    )
    shortcode: str | None = Field(
        default=None, description="The shortcode of the Instagram post."
    )


class _PostCommentsInput(BaseModel):
    """Input schema for ScavioInstagramPostCommentsTool."""

    shortcode: str | None = Field(
        default=None, description="The shortcode of the Instagram post."
    )
    url: str | None = Field(
        default=None, description="URL of the Instagram post."
    )
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )
    sort_order: Literal["popular", "newest"] | None = Field(
        default=None,
        description='Comment sort order -- "popular" or "newest".',
    )


class _CommentRepliesInput(BaseModel):
    """Input schema for ScavioInstagramCommentRepliesTool."""

    media_id: str = Field(
        ..., description="The Instagram media ID containing the comment."
    )
    comment_id: str = Field(
        ..., description="The comment ID to fetch replies for."
    )
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class _SearchUsersInput(BaseModel):
    """Input schema for ScavioInstagramSearchUsersTool."""

    keyword: str = Field(..., description="The search keyword.")
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class _SearchHashtagsInput(BaseModel):
    """Input schema for ScavioInstagramSearchHashtagsTool."""

    keyword: str = Field(..., description="The search keyword.")
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class _UserFollowersInput(BaseModel):
    """Input schema for ScavioInstagramUserFollowersTool."""

    username: str | None = Field(
        default=None, description="Instagram username of the user."
    )
    user_id: str | None = Field(
        default=None, description="Instagram user_id of the user."
    )
    count: int | None = Field(
        default=None, description="Number of followers to fetch."
    )
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class _UserFollowingsInput(BaseModel):
    """Input schema for ScavioInstagramUserFollowingsTool."""

    username: str | None = Field(
        default=None, description="Instagram username of the user."
    )
    user_id: str | None = Field(
        default=None, description="Instagram user_id of the user."
    )
    count: int | None = Field(
        default=None, description="Number of followings to fetch."
    )
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


# ---------------------------------------------------------------------------
# 1. Profile
# ---------------------------------------------------------------------------


class ScavioInstagramProfileTool(ScavioBaseTool):
    """Fetch an Instagram user profile by username or user_id.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram Profile"
    description: str = (
        "Retrieve an Instagram user profile by username or user_id."
    )
    args_schema: Type[BaseModel] = _ProfileInput

    def _run(
        self,
        username: str | None = None,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous profile lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.

        Returns:
            JSON-serialised profile data.
        """
        raw = self.client.instagram.profile(
            username=username, user_id=user_id
        )
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous profile lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.

        Returns:
            JSON-serialised profile data.
        """
        raw = await self.async_client.instagram.profile(
            username=username, user_id=user_id
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 2. User Posts
# ---------------------------------------------------------------------------


class ScavioInstagramUserPostsTool(ScavioBaseTool):
    """Fetch posts published by an Instagram user.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram User Posts"
    description: str = (
        "Retrieve posts from an Instagram user by username or user_id."
    )
    args_schema: Type[BaseModel] = _UserPostsInput

    def _run(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous user posts lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of posts to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of user posts.
        """
        raw = self.client.instagram.user_posts(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous user posts lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of posts to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of user posts.
        """
        raw = await self.async_client.instagram.user_posts(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 3. User Reels
# ---------------------------------------------------------------------------


class ScavioInstagramUserReelsTool(ScavioBaseTool):
    """Fetch reels published by an Instagram user.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram User Reels"
    description: str = (
        "Retrieve reels from an Instagram user by username or user_id."
    )
    args_schema: Type[BaseModel] = _UserReelsInput

    def _run(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous user reels lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of reels to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of user reels.
        """
        raw = self.client.instagram.user_reels(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous user reels lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of reels to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of user reels.
        """
        raw = await self.async_client.instagram.user_reels(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 4. Tagged Posts
# ---------------------------------------------------------------------------


class ScavioInstagramTaggedPostsTool(ScavioBaseTool):
    """Fetch posts an Instagram user is tagged in.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram Tagged Posts"
    description: str = (
        "Retrieve posts an Instagram user is tagged in by username or "
        "user_id."
    )
    args_schema: Type[BaseModel] = _TaggedPostsInput

    def _run(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous tagged posts lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of tagged posts to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of tagged posts.
        """
        raw = self.client.instagram.user_tagged(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous tagged posts lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of tagged posts to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of tagged posts.
        """
        raw = await self.async_client.instagram.user_tagged(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 5. Stories
# ---------------------------------------------------------------------------


class ScavioInstagramStoriesTool(ScavioBaseTool):
    """Fetch the active stories of an Instagram user.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram Stories"
    description: str = (
        "Retrieve the active stories of an Instagram user by username or "
        "user_id."
    )
    args_schema: Type[BaseModel] = _StoriesInput

    def _run(
        self,
        username: str | None = None,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous stories lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.

        Returns:
            JSON-serialised list of stories.
        """
        raw = self.client.instagram.user_stories(
            username=username, user_id=user_id
        )
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous stories lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.

        Returns:
            JSON-serialised list of stories.
        """
        raw = await self.async_client.instagram.user_stories(
            username=username, user_id=user_id
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 6. Post
# ---------------------------------------------------------------------------


class ScavioInstagramPostTool(ScavioBaseTool):
    """Fetch details about a single Instagram post.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram Post"
    description: str = (
        "Retrieve details of an Instagram post by url, media_id, or "
        "shortcode."
    )
    args_schema: Type[BaseModel] = _PostInput

    def _run(
        self,
        url: str | None = None,
        media_id: str | None = None,
        shortcode: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous post lookup.

        Args:
            url: URL of the Instagram post.
            media_id: The Instagram media ID.
            shortcode: The shortcode of the post.

        Returns:
            JSON-serialised post data.
        """
        raw = self.client.instagram.post(
            url=url, media_id=media_id, shortcode=shortcode
        )
        return self._format_response(raw)

    async def _arun(
        self,
        url: str | None = None,
        media_id: str | None = None,
        shortcode: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous post lookup.

        Args:
            url: URL of the Instagram post.
            media_id: The Instagram media ID.
            shortcode: The shortcode of the post.

        Returns:
            JSON-serialised post data.
        """
        raw = await self.async_client.instagram.post(
            url=url, media_id=media_id, shortcode=shortcode
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 7. Post Comments
# ---------------------------------------------------------------------------


class ScavioInstagramPostCommentsTool(ScavioBaseTool):
    """Fetch comments on an Instagram post.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram Post Comments"
    description: str = (
        "Retrieve comments on an Instagram post by shortcode or url."
    )
    args_schema: Type[BaseModel] = _PostCommentsInput

    def _run(
        self,
        shortcode: str | None = None,
        url: str | None = None,
        cursor: str | None = None,
        sort_order: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous post comments lookup.

        Args:
            shortcode: The shortcode of the Instagram post.
            url: URL of the Instagram post.
            cursor: Pagination cursor.
            sort_order: Comment sort order ("popular" or "newest").

        Returns:
            JSON-serialised list of comments.
        """
        raw = self.client.instagram.post_comments(
            shortcode=shortcode,
            url=url,
            cursor=cursor,
            sort_order=sort_order,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        shortcode: str | None = None,
        url: str | None = None,
        cursor: str | None = None,
        sort_order: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous post comments lookup.

        Args:
            shortcode: The shortcode of the Instagram post.
            url: URL of the Instagram post.
            cursor: Pagination cursor.
            sort_order: Comment sort order ("popular" or "newest").

        Returns:
            JSON-serialised list of comments.
        """
        raw = await self.async_client.instagram.post_comments(
            shortcode=shortcode,
            url=url,
            cursor=cursor,
            sort_order=sort_order,
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 8. Comment Replies
# ---------------------------------------------------------------------------


class ScavioInstagramCommentRepliesTool(ScavioBaseTool):
    """Fetch replies to a specific comment on an Instagram post.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram Comment Replies"
    description: str = (
        "Retrieve replies to a comment on an Instagram post."
    )
    args_schema: Type[BaseModel] = _CommentRepliesInput

    def _run(
        self,
        media_id: str,
        comment_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous comment replies lookup.

        Args:
            media_id: The Instagram media ID.
            comment_id: The comment ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of replies.
        """
        raw = self.client.instagram.comment_replies(
            media_id=media_id, comment_id=comment_id, cursor=cursor
        )
        return self._format_response(raw)

    async def _arun(
        self,
        media_id: str,
        comment_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous comment replies lookup.

        Args:
            media_id: The Instagram media ID.
            comment_id: The comment ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of replies.
        """
        raw = await self.async_client.instagram.comment_replies(
            media_id=media_id, comment_id=comment_id, cursor=cursor
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 9. Search Users
# ---------------------------------------------------------------------------


class ScavioInstagramSearchUsersTool(ScavioBaseTool):
    """Search for Instagram users by keyword.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram Search Users"
    description: str = "Search for Instagram users by keyword."
    args_schema: Type[BaseModel] = _SearchUsersInput

    def _run(
        self,
        keyword: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous user search.

        Args:
            keyword: The search keyword.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.instagram.search_users(
            keyword=keyword, cursor=cursor
        )
        return self._format_response(raw)

    async def _arun(
        self,
        keyword: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous user search.

        Args:
            keyword: The search keyword.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.instagram.search_users(
            keyword=keyword, cursor=cursor
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 10. Search Hashtags
# ---------------------------------------------------------------------------


class ScavioInstagramSearchHashtagsTool(ScavioBaseTool):
    """Search for Instagram hashtags by keyword.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram Search Hashtags"
    description: str = "Search for Instagram hashtags by keyword."
    args_schema: Type[BaseModel] = _SearchHashtagsInput

    def _run(
        self,
        keyword: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous hashtag search.

        Args:
            keyword: The search keyword.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.instagram.search_hashtags(
            keyword=keyword, cursor=cursor
        )
        return self._format_response(raw)

    async def _arun(
        self,
        keyword: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous hashtag search.

        Args:
            keyword: The search keyword.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.instagram.search_hashtags(
            keyword=keyword, cursor=cursor
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 11. User Followers
# ---------------------------------------------------------------------------


class ScavioInstagramUserFollowersTool(ScavioBaseTool):
    """Fetch followers of an Instagram user.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram User Followers"
    description: str = (
        "Retrieve followers of an Instagram user by username or user_id."
    )
    args_schema: Type[BaseModel] = _UserFollowersInput

    def _run(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous user followers lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of followers to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of followers.
        """
        raw = self.client.instagram.user_followers(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous user followers lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of followers to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of followers.
        """
        raw = await self.async_client.instagram.user_followers(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 12. User Followings
# ---------------------------------------------------------------------------


class ScavioInstagramUserFollowingsTool(ScavioBaseTool):
    """Fetch users that an Instagram user is following.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio Instagram User Followings"
    description: str = (
        "Retrieve the list of users an Instagram user follows by username "
        "or user_id."
    )
    args_schema: Type[BaseModel] = _UserFollowingsInput

    def _run(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous user followings lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of followings to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of followings.
        """
        raw = self.client.instagram.user_followings(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)

    async def _arun(
        self,
        username: str | None = None,
        user_id: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous user followings lookup.

        Args:
            username: Instagram username.
            user_id: Instagram user_id.
            count: Number of followings to fetch.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of followings.
        """
        raw = await self.async_client.instagram.user_followings(
            username=username,
            user_id=user_id,
            count=count,
            cursor=cursor,
        )
        return self._format_response(raw)
