"""Scavio Reddit tools for CrewAI.

Provides tools to search Reddit posts and comments and fetch individual
post details via the Scavio API.
"""


from typing import Literal

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


class ScavioRedditSearchToolSchema(BaseModel):
    """Input schema for ScavioRedditSearchTool."""

    query: str = Field(..., description="Reddit search query.")


class ScavioRedditSearchTool(ScavioBaseTool):
    """Tool that searches Reddit posts and comments using the Scavio API.

    Attributes:
        name: The name of the tool.
        description: A description of the tool's purpose.
        args_schema: The schema for the tool's arguments.
        type: Type of Reddit content to search for.
        sort: Sort order for results.
    """

    name: str = "Scavio Reddit Search"
    description: str = (
        "A tool that searches Reddit posts and comments using the Scavio API. "
        "Returns post titles, URLs, subreddits, authors, and timestamps "
        "as a JSON string."
    )
    args_schema: type[BaseModel] = ScavioRedditSearchToolSchema

    type: Literal["posts", "comments"] | None = Field(
        default=None,
        description="Type of Reddit content to search for.",
    )
    sort: Literal["new", "relevance", "hot", "top", "comments"] | None = Field(
        default=None,
        description="Sort order for results.",
    )

    def _run(self, query: str) -> str:
        """Synchronously search Reddit posts and comments.

        Args:
            query: Reddit search query.

        Returns:
            A JSON string containing Reddit search results.
        """
        raw = self.client.reddit.search(
            query=query,
            type=self.type,
            sort=self.sort,
        )
        self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)

    async def _arun(self, query: str) -> str:
        """Asynchronously search Reddit posts and comments.

        Args:
            query: Reddit search query.

        Returns:
            A JSON string containing Reddit search results.
        """
        raw = await self.async_client.reddit.search(
            query=query,
            type=self.type,
            sort=self.sort,
        )
        self._truncate_nested(raw, "data", "posts")
        return self._format_response(raw)


class ScavioRedditPostToolSchema(BaseModel):
    """Input schema for ScavioRedditPostTool."""

    url: str = Field(..., description="URL of the Reddit post.")


class ScavioRedditPostTool(ScavioBaseTool):
    """Tool that fetches a Reddit post's metadata and comment thread by URL.

    Attributes:
        name: The name of the tool.
        description: A description of the tool's purpose.
        args_schema: The schema for the tool's arguments.
    """

    name: str = "Scavio Reddit Post"
    description: str = (
        "A tool that fetches a Reddit post's metadata and comment thread "
        "by URL using the Scavio API."
    )
    args_schema: type[BaseModel] = ScavioRedditPostToolSchema

    def _run(self, url: str) -> str:
        """Synchronously fetch Reddit post details.

        Args:
            url: URL of the Reddit post.

        Returns:
            A JSON string containing the post metadata and comments.
        """
        raw = self.client.reddit.post(url=url)
        return self._format_response(raw)

    async def _arun(self, url: str) -> str:
        """Asynchronously fetch Reddit post details.

        Args:
            url: URL of the Reddit post.

        Returns:
            A JSON string containing the post metadata and comments.
        """
        raw = await self.async_client.reddit.post(url=url)
        return self._format_response(raw)
