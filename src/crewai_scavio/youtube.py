"""Scavio YouTube tools for CrewAI."""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class ScavioYouTubeSearchInput(BaseModel):
    """Input schema for ScavioYouTubeSearchTool."""

    query: str = Field(..., description="The YouTube search query.")


class ScavioYouTubeVideoInput(BaseModel):
    """Input schema for ScavioYouTubeVideoTool."""

    video_id: str = Field(
        ..., description="The YouTube video ID or full watch URL."
    )


class ScavioYouTubeCommentsInput(BaseModel):
    """Input schema for ScavioYouTubeCommentsTool."""

    video_id: str = Field(..., description="The YouTube video ID.")
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class ScavioYouTubeTranscriptInput(BaseModel):
    """Input schema for ScavioYouTubeTranscriptTool."""

    video_id: str = Field(..., description="The YouTube video ID.")
    language: str | None = Field(
        default=None, description="Caption language code (default 'en')."
    )
    format: Literal["text", "srt"] | None = Field(
        default=None,
        description=(
            "Transcript format -- 'text' for a plain transcript or 'srt' "
            "for timed subtitles."
        ),
    )


class ScavioYouTubeChannelInput(BaseModel):
    """Input schema for ScavioYouTubeChannelTool."""

    channel_id: str = Field(
        ..., description="Channel ID, @handle, or channel URL."
    )


class ScavioYouTubeChannelVideosInput(BaseModel):
    """Input schema for ScavioYouTubeChannelVideosTool."""

    channel_id: str = Field(..., description="The YouTube channel ID.")
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class ScavioYouTubeStreamsInput(BaseModel):
    """Input schema for ScavioYouTubeStreamsTool."""

    video_id: str = Field(..., description="The YouTube video ID.")


class ScavioYouTubeShortsInput(BaseModel):
    """Input schema for ScavioYouTubeShortsTool."""

    query: str = Field(..., description="The YouTube Shorts search query.")
    sort_by: Literal["relevance", "date", "view_count", "rating"] | None = Field(
        default=None,
        description=(
            "Sort order, passed through verbatim -- there is no date remap "
            "on this endpoint."
        ),
    )
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class ScavioYouTubeSuggestionsInput(BaseModel):
    """Input schema for ScavioYouTubeSuggestionsTool."""

    query: str = Field(..., description="Partial YouTube search query.")
    language: str | None = Field(
        default=None,
        description="Suggestion language (ISO 639-1, default 'en').",
    )
    region: str | None = Field(
        default=None,
        description="Region code (ISO 3166-1 alpha-2, default 'US').",
    )


class ScavioYouTubeCommentRepliesInput(BaseModel):
    """Input schema for ScavioYouTubeCommentRepliesTool."""

    video_id: str = Field(..., description="The YouTube video ID.")
    reply_cursor: str = Field(
        ...,
        description=(
            "Required -- the reply_cursor of a comment returned by the "
            "comments tool. This endpoint cannot be called from a video ID "
            "alone."
        ),
    )
    cursor: str | None = Field(
        default=None,
        description=(
            "Page-2+ cursor. Wins over reply_cursor when both are supplied."
        ),
    )


class ScavioYouTubeRelatedInput(BaseModel):
    """Input schema for ScavioYouTubeRelatedTool."""

    video_id: str = Field(..., description="The YouTube video ID.")
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class ScavioYouTubeChannelSearchInput(BaseModel):
    """Input schema for ScavioYouTubeChannelSearchTool."""

    query: str = Field(..., description="The channel search query.")
    cursor: str | None = Field(
        default=None, description="Pagination cursor from a previous page."
    )


class ScavioYouTubeChannelResolveInput(BaseModel):
    """Input schema for ScavioYouTubeChannelResolveTool."""

    channel: str = Field(
        ...,
        description=(
            "A @handle or channel URL to resolve, e.g. '@MrBeast'. The field "
            "is 'channel', not 'channel_id'."
        ),
    )


# ---------------------------------------------------------------------------
# 1. Search
# ---------------------------------------------------------------------------

class ScavioYouTubeSearchTool(ScavioBaseTool):
    """YouTube video search tool powered by the Scavio YouTube API.

    Attributes:
        upload_date: Filter by upload date (e.g. 'hour', 'today', 'week').
        sort_by: Sort order for search results.
        type: Content type filter (e.g. 'video', 'channel', 'playlist').
        duration: Duration filter (e.g. 'short', 'medium', 'long').
    """

    name: str = "Scavio YouTube Search"
    description: str = (
        "Search for videos on YouTube using the Scavio YouTube API. "
        "Returns video titles, channels, view counts, and more."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeSearchInput

    upload_date: str | None = None
    sort_by: str | None = None
    type: str | None = None
    duration: str | None = None

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous YouTube search.

        Args:
            query: The YouTube search query.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.youtube.search(
            query=query,
            upload_date=self.upload_date,
            sort_by=self.sort_by,
            type=self.type,
            duration=self.duration,
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous YouTube search.

        Args:
            query: The YouTube search query.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.youtube.search(
            query=query,
            upload_date=self.upload_date,
            sort_by=self.sort_by,
            type=self.type,
            duration=self.duration,
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 2. Video
# ---------------------------------------------------------------------------

class ScavioYouTubeVideoTool(ScavioBaseTool):
    """YouTube video tool powered by the Scavio YouTube API.

    Retrieves detailed metadata for a single YouTube video by its ID.
    Accepts either a video ID or a full watch URL.
    """

    name: str = "Scavio YouTube Video"
    description: str = (
        "Get detailed metadata for a YouTube video by its video ID or "
        "watch URL using the Scavio YouTube API."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeVideoInput

    def _run(self, video_id: str, **kwargs: Any) -> str:
        """Fetch video details synchronously.

        Args:
            video_id: The YouTube video ID or watch URL.

        Returns:
            JSON-serialised video metadata.
        """
        raw = self.client.youtube.video(video_id=video_id)
        return self._format_response(raw)

    async def _arun(self, video_id: str, **kwargs: Any) -> str:
        """Fetch video details asynchronously.

        Args:
            video_id: The YouTube video ID or watch URL.

        Returns:
            JSON-serialised video metadata.
        """
        raw = await self.async_client.youtube.video(video_id=video_id)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 3. Comments
# ---------------------------------------------------------------------------

class ScavioYouTubeCommentsTool(ScavioBaseTool):
    """Fetch top-level comments on a YouTube video.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Comments"
    description: str = (
        "Retrieve top-level comments on a YouTube video by its video ID."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeCommentsInput

    def _run(
        self,
        video_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous comments lookup.

        Args:
            video_id: The YouTube video ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of comments.
        """
        raw = self.client.youtube.comments(video_id=video_id, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)

    async def _arun(
        self,
        video_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous comments lookup.

        Args:
            video_id: The YouTube video ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of comments.
        """
        raw = await self.async_client.youtube.comments(
            video_id=video_id, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "comments")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 4. Transcript
# ---------------------------------------------------------------------------

class ScavioYouTubeTranscriptTool(ScavioBaseTool):
    """Fetch the transcript / captions for a YouTube video.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Transcript"
    description: str = (
        "Retrieve the transcript or timed captions for a YouTube video "
        "by its video ID. Use format 'text' for a plain transcript or "
        "'srt' for timed subtitles."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeTranscriptInput

    def _run(
        self,
        video_id: str,
        language: str | None = None,
        format: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous transcript lookup.

        Args:
            video_id: The YouTube video ID.
            language: Caption language code.
            format: Transcript format ("text" or "srt").

        Returns:
            JSON-serialised transcript.
        """
        raw = self.client.youtube.transcript(
            video_id=video_id, language=language, format=format
        )
        return self._format_response(raw)

    async def _arun(
        self,
        video_id: str,
        language: str | None = None,
        format: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous transcript lookup.

        Args:
            video_id: The YouTube video ID.
            language: Caption language code.
            format: Transcript format ("text" or "srt").

        Returns:
            JSON-serialised transcript.
        """
        raw = await self.async_client.youtube.transcript(
            video_id=video_id, language=language, format=format
        )
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 5. Channel
# ---------------------------------------------------------------------------

class ScavioYouTubeChannelTool(ScavioBaseTool):
    """Fetch details about a YouTube channel.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Channel"
    description: str = (
        "Retrieve details for a YouTube channel by its channel ID, "
        "@handle, or channel URL."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeChannelInput

    def _run(self, channel_id: str, **kwargs: Any) -> str:
        """Execute a synchronous channel lookup.

        Args:
            channel_id: Channel ID, @handle, or channel URL.

        Returns:
            JSON-serialised channel data.
        """
        raw = self.client.youtube.channel(channel_id=channel_id)
        return self._format_response(raw)

    async def _arun(self, channel_id: str, **kwargs: Any) -> str:
        """Execute an asynchronous channel lookup.

        Args:
            channel_id: Channel ID, @handle, or channel URL.

        Returns:
            JSON-serialised channel data.
        """
        raw = await self.async_client.youtube.channel(channel_id=channel_id)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 6. Channel Videos
# ---------------------------------------------------------------------------

class ScavioYouTubeChannelVideosTool(ScavioBaseTool):
    """Fetch videos uploaded by a YouTube channel.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Channel Videos"
    description: str = (
        "Retrieve videos uploaded by a YouTube channel by its channel ID."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeChannelVideosInput

    def _run(
        self,
        channel_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous channel videos lookup.

        Args:
            channel_id: The YouTube channel ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of channel videos.
        """
        raw = self.client.youtube.channel_videos(
            channel_id=channel_id, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(
        self,
        channel_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous channel videos lookup.

        Args:
            channel_id: The YouTube channel ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of channel videos.
        """
        raw = await self.async_client.youtube.channel_videos(
            channel_id=channel_id, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 7. Streams
# ---------------------------------------------------------------------------

class ScavioYouTubeStreamsTool(ScavioBaseTool):
    """Fetch playable / downloadable stream formats for a YouTube video.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Streams"
    description: str = (
        "Retrieve playable and downloadable stream formats for a YouTube "
        "video by its video ID, including direct media URLs and available "
        "qualities."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeStreamsInput

    def _run(self, video_id: str, **kwargs: Any) -> str:
        """Execute a synchronous streams lookup.

        Args:
            video_id: The YouTube video ID.

        Returns:
            JSON-serialised stream formats.
        """
        raw = self.client.youtube.streams(video_id=video_id)
        return self._format_response(raw)

    async def _arun(self, video_id: str, **kwargs: Any) -> str:
        """Execute an asynchronous streams lookup.

        Args:
            video_id: The YouTube video ID.

        Returns:
            JSON-serialised stream formats.
        """
        raw = await self.async_client.youtube.streams(video_id=video_id)
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 8. Shorts search
# ---------------------------------------------------------------------------

class ScavioYouTubeShortsTool(ScavioBaseTool):
    """Search YouTube Shorts.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Shorts"
    description: str = (
        "Search YouTube Shorts by keyword. Returns data.results with "
        "next_cursor and has_more. There are no type / duration / "
        "upload_date filters on this endpoint. Costs 2 credits."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeShortsInput

    def _run(
        self,
        query: str,
        sort_by: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous Shorts search.

        Args:
            query: The YouTube Shorts search query.
            sort_by: Sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised Shorts results.
        """
        raw = self.client.youtube.shorts(
            query=query, sort_by=sort_by, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        sort_by: str | None = None,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous Shorts search.

        Args:
            query: The YouTube Shorts search query.
            sort_by: Sort order.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised Shorts results.
        """
        raw = await self.async_client.youtube.shorts(
            query=query, sort_by=sort_by, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 9. Search suggestions
# ---------------------------------------------------------------------------

class ScavioYouTubeSuggestionsTool(ScavioBaseTool):
    """YouTube search autocomplete suggestions.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Suggestions"
    description: str = (
        "Get YouTube search autocomplete suggestions for a partial query. "
        "Returns data.suggestions (strings) and total_count. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeSuggestionsInput

    def _run(
        self,
        query: str,
        language: str | None = None,
        region: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous suggestions lookup.

        Args:
            query: Partial YouTube search query.
            language: Suggestion language.
            region: Region code.

        Returns:
            JSON-serialised suggestions.
        """
        raw = self.client.youtube.suggestions(
            query=query, language=language, region=region
        )
        raw = self._truncate_nested(raw, "data", "suggestions")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        language: str | None = None,
        region: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous suggestions lookup.

        Args:
            query: Partial YouTube search query.
            language: Suggestion language.
            region: Region code.

        Returns:
            JSON-serialised suggestions.
        """
        raw = await self.async_client.youtube.suggestions(
            query=query, language=language, region=region
        )
        raw = self._truncate_nested(raw, "data", "suggestions")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 10. Comment replies
# ---------------------------------------------------------------------------

class ScavioYouTubeCommentRepliesTool(ScavioBaseTool):
    """Fetch replies to a YouTube comment.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Comment Replies"
    description: str = (
        "Retrieve replies to a YouTube comment. Requires both video_id and "
        "the reply_cursor of a comment returned by the comments tool. "
        "Returns data.replies with next_cursor and has_more."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeCommentRepliesInput

    def _run(
        self,
        video_id: str,
        reply_cursor: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous replies lookup.

        Args:
            video_id: The YouTube video ID.
            reply_cursor: Reply cursor from a comment.
            cursor: Page-2+ cursor.

        Returns:
            JSON-serialised list of replies.
        """
        raw = self.client.youtube.comment_replies(
            video_id=video_id, reply_cursor=reply_cursor, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "replies")
        return self._format_response(raw)

    async def _arun(
        self,
        video_id: str,
        reply_cursor: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous replies lookup.

        Args:
            video_id: The YouTube video ID.
            reply_cursor: Reply cursor from a comment.
            cursor: Page-2+ cursor.

        Returns:
            JSON-serialised list of replies.
        """
        raw = await self.async_client.youtube.comment_replies(
            video_id=video_id, reply_cursor=reply_cursor, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "replies")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 11. Related videos
# ---------------------------------------------------------------------------

class ScavioYouTubeRelatedTool(ScavioBaseTool):
    """Fetch videos related to a YouTube video.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Related Videos"
    description: str = (
        "Retrieve videos related to a YouTube video. Returns data.results "
        "and total_count -- this endpoint accepts a cursor but returns no "
        "next_cursor. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeRelatedInput

    def _run(
        self,
        video_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous related videos lookup.

        Args:
            video_id: The YouTube video ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of related videos.
        """
        raw = self.client.youtube.related(video_id=video_id, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(
        self,
        video_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous related videos lookup.

        Args:
            video_id: The YouTube video ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of related videos.
        """
        raw = await self.async_client.youtube.related(
            video_id=video_id, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 12. Channel search
# ---------------------------------------------------------------------------

class ScavioYouTubeChannelSearchTool(ScavioBaseTool):
    """Search YouTube channels.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Channel Search"
    description: str = (
        "Search for YouTube channels by keyword. Returns data.results with "
        "channel_id, name, handle, subscriber_count and verified, plus "
        "next_cursor and has_more. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeChannelSearchInput

    def _run(
        self,
        query: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous channel search.

        Args:
            query: The channel search query.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of channels.
        """
        raw = self.client.youtube.channel_search(query=query, cursor=cursor)
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(
        self,
        query: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous channel search.

        Args:
            query: The channel search query.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of channels.
        """
        raw = await self.async_client.youtube.channel_search(
            query=query, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 13. Channel Shorts
# ---------------------------------------------------------------------------

class ScavioYouTubeChannelShortsTool(ScavioBaseTool):
    """Fetch Shorts posted by a YouTube channel.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Channel Shorts"
    description: str = (
        "Retrieve the Shorts a YouTube channel has posted. Returns "
        "data.results with video_id, title, url and thumbnail -- view_count "
        "is deliberately omitted because upstream is unreliable for Shorts."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeChannelVideosInput

    def _run(
        self,
        channel_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous channel Shorts lookup.

        Args:
            channel_id: The YouTube channel ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of Shorts.
        """
        raw = self.client.youtube.channel_shorts(
            channel_id=channel_id, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)

    async def _arun(
        self,
        channel_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous channel Shorts lookup.

        Args:
            channel_id: The YouTube channel ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of Shorts.
        """
        raw = await self.async_client.youtube.channel_shorts(
            channel_id=channel_id, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "results")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 14. Channel community posts
# ---------------------------------------------------------------------------

class ScavioYouTubeChannelCommunityTool(ScavioBaseTool):
    """Fetch community posts from a YouTube channel.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Channel Community"
    description: str = (
        "Retrieve a YouTube channel's community posts. This is the only "
        "YouTube endpoint whose list key is data.posts (not results); items "
        "carry text, vote_count, comment_count and images."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeChannelVideosInput

    def _run(
        self,
        channel_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute a synchronous community posts lookup.

        Args:
            channel_id: The YouTube channel ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of community posts.
        """
        raw = self.client.youtube.channel_community(
            channel_id=channel_id, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)

    async def _arun(
        self,
        channel_id: str,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Execute an asynchronous community posts lookup.

        Args:
            channel_id: The YouTube channel ID.
            cursor: Pagination cursor.

        Returns:
            JSON-serialised list of community posts.
        """
        raw = await self.async_client.youtube.channel_community(
            channel_id=channel_id, cursor=cursor
        )
        raw = self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)


# ---------------------------------------------------------------------------
# 15. Channel resolve
# ---------------------------------------------------------------------------

class ScavioYouTubeChannelResolveTool(ScavioBaseTool):
    """Resolve a YouTube @handle or channel URL to a channel ID.

    Attributes:
        name: Tool name.
        description: Tool description.
        args_schema: Input schema class.
    """

    name: str = "Scavio YouTube Channel Resolve"
    description: str = (
        "Resolve a YouTube @handle or channel URL to its channel ID. The "
        "input field is 'channel', not 'channel_id'. Returns channel_id and "
        "channel_url. Costs 1 credit."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeChannelResolveInput

    def _run(self, channel: str, **kwargs: Any) -> str:
        """Execute a synchronous channel resolve.

        Args:
            channel: A @handle or channel URL.

        Returns:
            JSON-serialised channel_id and channel_url.
        """
        raw = self.client.youtube.channel_resolve(channel=channel)
        return self._format_response(raw)

    async def _arun(self, channel: str, **kwargs: Any) -> str:
        """Execute an asynchronous channel resolve.

        Args:
            channel: A @handle or channel URL.

        Returns:
            JSON-serialised channel_id and channel_url.
        """
        raw = await self.async_client.youtube.channel_resolve(channel=channel)
        return self._format_response(raw)
