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
