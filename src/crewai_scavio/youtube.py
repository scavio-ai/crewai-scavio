"""Scavio YouTube tools for CrewAI."""


from typing import Any, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class ScavioYouTubeSearchInput(BaseModel):
    """Input schema for ScavioYouTubeSearchTool."""

    query: str = Field(..., description="The YouTube search query.")


class ScavioYouTubeMetadataInput(BaseModel):
    """Input schema for ScavioYouTubeMetadataTool."""

    video_id: str = Field(..., description="The YouTube video ID.")


# ---------------------------------------------------------------------------
# Tools
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


class ScavioYouTubeMetadataTool(ScavioBaseTool):
    """YouTube video metadata tool powered by the Scavio YouTube API.

    Retrieves detailed metadata for a single YouTube video by its ID.
    """

    name: str = "Scavio YouTube Metadata"
    description: str = (
        "Get detailed metadata for a YouTube video by its video ID "
        "using the Scavio YouTube API."
    )
    args_schema: Type[BaseModel] = ScavioYouTubeMetadataInput

    def _run(self, video_id: str, **kwargs: Any) -> str:
        """Fetch video metadata synchronously.

        Args:
            video_id: The YouTube video ID.

        Returns:
            JSON-serialised video metadata.
        """
        raw = self.client.youtube.metadata(video_id=video_id)
        return self._format_response(raw)

    async def _arun(self, video_id: str, **kwargs: Any) -> str:
        """Fetch video metadata asynchronously.

        Args:
            video_id: The YouTube video ID.

        Returns:
            JSON-serialised video metadata.
        """
        raw = await self.async_client.youtube.metadata(video_id=video_id)
        return self._format_response(raw)
