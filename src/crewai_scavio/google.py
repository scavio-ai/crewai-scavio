"""Scavio Google Search tool for CrewAI."""


from typing import Any, Literal, Type

from pydantic import BaseModel, Field

from crewai_scavio._base import ScavioBaseTool


class ScavioSearchInput(BaseModel):
    """Input schema for ScavioSearchTool."""

    query: str = Field(..., description="The search query string.")


# Mapping from include_* field names to their corresponding response keys.
_INCLUDE_FIELD_TO_KEY: dict[str, str] = {
    "include_knowledge_graph": "knowledge_graph",
    "include_questions": "questions",
    "include_related": "related",
    "include_maps_results": "maps_results",
    "include_ai_overviews": "ai_overviews",
    "include_local_results": "local_results",
    "include_top_stories": "top_stories",
    "include_hotel_results": "hotel_results",
    "include_news_results": "news_results",
    "include_shopping_ads": "shopping_ads",
    "include_top_ads": "top_ads",
    "include_bottom_ads": "bottom_ads",
}

# Response keys that contain truncatable lists.
_LIST_KEYS: list[str] = [
    "results",
    "maps_results",
    "local_results",
    "news_results",
]


class ScavioSearchTool(ScavioBaseTool):
    """Web search tool powered by the Scavio Google Search API.

    Attributes:
        search_type: Type of search to perform.
        country_code: Two-letter country code for localised results.
        language: Language code for result language preference.
        device: Device type to emulate.
        include_knowledge_graph: Include knowledge-graph panel in response.
        include_questions: Include "People also ask" questions.
        include_related: Include related searches.
        include_maps_results: Include map-pack results.
        include_ai_overviews: Include AI overview snippets.
        include_local_results: Include local business results.
        include_top_stories: Include top-stories carousel.
        include_hotel_results: Include hotel results.
        include_news_results: Include news results.
        include_shopping_ads: Include shopping ad results.
        include_top_ads: Include top ad results.
        include_bottom_ads: Include bottom ad results.
        nfpr: Disable automatic spelling correction.
        light_request: Use the lightweight request mode when set.
    """

    name: str = "Scavio Search"
    description: str = (
        "Search the web using the Scavio Google Search API. "
        "Returns organic results, knowledge graph, related questions, "
        "and more depending on configuration."
    )
    args_schema: Type[BaseModel] = ScavioSearchInput

    search_type: Literal["classic", "news", "maps", "images"] = "classic"
    country_code: str | None = None
    language: str | None = None
    device: Literal["desktop", "mobile"] = "desktop"
    include_knowledge_graph: bool = True
    include_questions: bool = True
    include_related: bool = False
    include_maps_results: bool = False
    include_ai_overviews: bool = False
    include_local_results: bool = False
    include_top_stories: bool = False
    include_hotel_results: bool = False
    include_news_results: bool = False
    include_shopping_ads: bool = False
    include_top_ads: bool = False
    include_bottom_ads: bool = False
    nfpr: bool = False
    light_request: bool | None = None

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous Google search.

        Args:
            query: The search query string.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.google.search(
            query=query,
            search_type=self.search_type,
            country_code=self.country_code,
            language=self.language,
            device=self.device,
            nfpr=self.nfpr,
            light_request=self.light_request,
        )
        return self._format_response(self._post_process(raw))

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous Google search.

        Args:
            query: The search query string.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.google.search(
            query=query,
            search_type=self.search_type,
            country_code=self.country_code,
            language=self.language,
            device=self.device,
            nfpr=self.nfpr,
            light_request=self.light_request,
        )
        return self._format_response(self._post_process(raw))

    def _post_process(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Truncate list fields and strip disabled include sections.

        Args:
            raw: Raw response dictionary from the API.

        Returns:
            Processed response dictionary.
        """
        for key in _LIST_KEYS:
            raw = self._truncate_results(raw, key)

        for field_name, response_key in _INCLUDE_FIELD_TO_KEY.items():
            if not getattr(self, field_name, False):
                raw.pop(response_key, None)

        return raw
