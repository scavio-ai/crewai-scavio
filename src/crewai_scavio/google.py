"""Scavio Google tools for CrewAI.

All fourteen Google endpoints run on v2 (``/api/v2/google*``) and cost 1 credit
each. Google v1 was retired on 2026-08-04 and now answers HTTP 410, so its
parameter names -- ``light_request``, ``country_code``, ``language``,
``search_type``, ``page`` -- are gone. v2 speaks ``gl``, ``hl``, ``start``,
``google_domain`` and ``device`` instead, and the v1 response block ``results[]``
with ``url``/``content`` is now ``organic_results[]`` with ``link``/``snippet``.

Google responses are FLAT: the payload sits at the top level next to
``response_time``, ``credits_used``, ``credits_remaining`` and ``cached``.
There is no ``data`` wrapper anywhere in this family, unlike every other Scavio
product area.
"""


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
    "organic_results",
    "maps_results",
    "local_results",
    "news_results",
]


class ScavioSearchTool(ScavioBaseTool):
    """Web search tool powered by the Scavio Google Search API (v2).

    Attributes:
        country_code: Two-letter country code for localised results (maps to gl).
        language: Language code for result language preference (maps to hl).
        page: 1-based result page; page 2+ maps to a result offset (start).
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
    """

    name: str = "Scavio Search"
    description: str = (
        "Search the web using the Scavio Google Search API (v2). "
        "Returns organic results (title, link, snippet), knowledge graph, "
        "related questions, and more depending on configuration. "
        "Costs 1 credit per search."
    )
    args_schema: Type[BaseModel] = ScavioSearchInput

    country_code: str | None = None
    language: str | None = None
    page: int | None = None
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

    def _build_params(self) -> dict[str, Any]:
        """Map public tool attributes to v2 Google Search wire params.

        Returns:
            Keyword arguments for ``client.google.search``.
        """
        params: dict[str, Any] = {
            "device": self.device,
            "nfpr": self.nfpr,
        }
        if self.country_code:
            params["gl"] = self.country_code
        if self.language:
            params["hl"] = self.language
        if self.page and self.page > 1:
            params["start"] = (self.page - 1) * 10
        return params

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute a synchronous Google search.

        Args:
            query: The search query string.

        Returns:
            JSON-serialised search results.
        """
        raw = self.client.google.search(query=query, **self._build_params())
        return self._format_response(self._post_process(raw))

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Execute an asynchronous Google search.

        Args:
            query: The search query string.

        Returns:
            JSON-serialised search results.
        """
        raw = await self.async_client.google.search(
            query=query, **self._build_params()
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
