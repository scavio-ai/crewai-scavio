"""Scavio Reddit tools for CrewAI.

Provides tools to search Reddit posts and fetch individual post details
via the Scavio API.
"""


from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


class ScavioRedditSearchToolSchema(BaseModel):
    """Input schema for ScavioRedditSearchTool."""

    query: str = Field(..., description="Reddit search query.")
    cursor: str | None = Field(
        default=None,
        description="Pagination cursor -- pass next_cursor from a previous response.",
    )


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


class ScavioRedditPostToolSchema(BaseModel):
    """Input schema for ScavioRedditPostTool."""

    url: str = Field(..., description="URL of the Reddit post.")


class ScavioRedditPostTool(ScavioBaseTool):
    """Tool that fetches a Reddit post by URL.

    Attributes:
        name: The name of the tool.
        description: A description of the tool's purpose.
        args_schema: The schema for the tool's arguments.
    """

    name: str = "Scavio Reddit Post"
    description: str = (
        "A tool that fetches a single Reddit post by URL using the Scavio "
        "API. Returns a flat post object -- title, text, score, "
        "upvote_ratio, num_comments, and media. Comments are not included."
    )
    args_schema: type[BaseModel] = ScavioRedditPostToolSchema

    def _run(self, url: str) -> str:
        """Synchronously fetch Reddit post details.

        Args:
            url: URL of the Reddit post.

        Returns:
            A JSON string containing the post object.
        """
        raw = self.client.reddit.post(url=url)
        return self._format_response(raw)

    async def _arun(self, url: str) -> str:
        """Asynchronously fetch Reddit post details.

        Args:
            url: URL of the Reddit post.

        Returns:
            A JSON string containing the post object.
        """
        raw = await self.async_client.reddit.post(url=url)
        return self._format_response(raw)
