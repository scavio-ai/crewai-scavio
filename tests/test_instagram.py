"""Contract tests for the Instagram tools added with SDK 0.24.0.

Spec-derived like test_fanout: the schema, the SDK call and the advertised
price are checked against ``scavio._spec`` so a renamed method or a repriced
endpoint fails here instead of shipping a tool an agent cannot drive.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from scavio._spec import ENDPOINTS

import crewai_scavio

MOCK_API_KEY = "sk_live_test_key_12345"

NEW_TOOLS = {
    "instagram_user_highlights": "ScavioInstagramUserHighlightsTool",
    "instagram_highlight_stories": "ScavioInstagramHighlightStoriesTool",
    "instagram_search_reels": "ScavioInstagramSearchReelsTool",
    "instagram_search_music": "ScavioInstagramSearchMusicTool",
    "instagram_music_posts": "ScavioInstagramMusicPostsTool",
    "instagram_search_locations": "ScavioInstagramSearchLocationsTool",
    "instagram_user_similar": "ScavioInstagramUserSimilarTool",
    "instagram_post_likers": "ScavioInstagramPostLikersTool",
}

CASES = [(ENDPOINTS[key], name) for key, name in NEW_TOOLS.items()]
IDS = list(NEW_TOOLS)


def _tool(name: str) -> type:
    return getattr(crewai_scavio, name)


def _sample_args(endpoint) -> dict:
    return {param.name: f"v_{param.name}" for param in endpoint.params}


@pytest.mark.parametrize("endpoint, name", CASES, ids=IDS)
def test_schema_matches_the_spec_parameters(endpoint, name):
    fields = _tool(name).model_fields["args_schema"].default.model_fields
    assert set(fields) == {param.name for param in endpoint.params}
    for param in endpoint.params:
        assert fields[param.name].is_required() is param.required, param.name


@pytest.mark.parametrize("endpoint, name", CASES, ids=IDS)
def test_description_states_the_spec_price(endpoint, name):
    description = _tool(name).model_fields["description"].default
    unit = "credit" if endpoint.credits == 1 else "credits"
    assert f"Costs {endpoint.credits} {unit}" in description


@pytest.mark.parametrize("endpoint, name", CASES, ids=IDS)
def test_docstring_quotes_the_path_verbatim(endpoint, name):
    tool = _tool(name)
    assert endpoint.path in tool._run.__doc__
    assert endpoint.path in tool._arun.__doc__


@pytest.mark.parametrize("endpoint, name", CASES, ids=IDS)
@patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
@patch("crewai_scavio._base.AsyncScavioClient")
@patch("crewai_scavio._base.ScavioClient")
def test_run_forwards_every_parameter(client_cls, async_cls, endpoint, name):
    client = MagicMock()
    client_cls.return_value = client
    call = MagicMock(return_value={"data": {}, "credits_used": 1})
    setattr(client.instagram, endpoint.method, call)

    args = _sample_args(endpoint)
    result = _tool(name)(api_key=MOCK_API_KEY)._run(**args)

    call.assert_called_once_with(**args)
    assert json.loads(result)["credits_used"] == 1


@pytest.mark.parametrize("endpoint, name", CASES, ids=IDS)
@patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
@patch("crewai_scavio._base.AsyncScavioClient")
@patch("crewai_scavio._base.ScavioClient")
async def test_arun_forwards_every_parameter(
    client_cls, async_cls, endpoint, name
):
    async_client = MagicMock()
    async_cls.return_value = async_client
    call = AsyncMock(return_value={"data": {}, "credits_used": 1})
    setattr(async_client.instagram, endpoint.method, call)

    args = _sample_args(endpoint)
    result = await _tool(name)(api_key=MOCK_API_KEY)._arun(**args)

    call.assert_awaited_once_with(**args)
    assert json.loads(result)["credits_used"] == 1
