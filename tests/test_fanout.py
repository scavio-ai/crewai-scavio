"""Contract tests for the 23-surface fanout batch.

Every tool added in this batch wraps exactly one endpoint in ``scavio._spec``.
These tests re-derive the expected surface from that spec at import time
rather than restating it, so an SDK upgrade that adds a parameter, renames a
method or moves a path fails here instead of silently shipping a tool an agent
cannot drive.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from scavio._spec import ENDPOINTS

import crewai_scavio

MOCK_API_KEY = "sk_live_test_key_12345"

# namespace -> frozen class-name base (gtm/fanout-naming.json,
# python_ns_meta_base). Multi-word brands intercap; SEC and G2 stay upper.
CLASS_BASE = {
    "walmart": "Walmart",
    "threads": "Threads",
    "kuaishou": "Kuaishou",
    "ebay": "Ebay",
    "target": "Target",
    "home_depot": "HomeDepot",
    "zillow": "Zillow",
    "booking": "Booking",
    "tripadvisor": "Tripadvisor",
    "indeed": "Indeed",
    "airbnb": "Airbnb",
    "glassdoor": "Glassdoor",
    "yelp": "Yelp",
    "app_store": "AppStore",
    "google_play": "GooglePlay",
    "sec": "SEC",
    "redfin": "Redfin",
    "companies_house": "CompaniesHouse",
    "g2": "G2",
    "capterra": "Capterra",
    "google_ads": "GoogleAds",
    "meta_ads": "MetaAds",
}

# Cost is a function of the request body on these four, so no tool of theirs
# may advertise a single flat price.
BODY_PRICED = {"walmart", "threads", "kuaishou", "_core"}

FANOUT = [
    endpoint
    for endpoint in ENDPOINTS.values()
    if endpoint.namespace in CLASS_BASE or endpoint.namespace == "_core"
]


def _camel(method: str) -> str:
    return "".join(word.capitalize() for word in method.split("_"))


def _tool_for(endpoint) -> type:
    if endpoint.namespace == "_core":
        return crewai_scavio.ScavioExtractTool
    name = f"Scavio{CLASS_BASE[endpoint.namespace]}{_camel(endpoint.method)}Tool"
    return getattr(crewai_scavio, name)


def _method_mock(client: MagicMock, endpoint, *, is_async: bool):
    """The mock standing in for the SDK call this tool must make."""
    owner = client if endpoint.namespace == "_core" else getattr(
        client, endpoint.namespace
    )
    factory = AsyncMock if is_async else MagicMock
    mock = factory(return_value={"data": {}, "credits_used": 1})
    setattr(owner, endpoint.method, mock)
    return mock


def _sample_args(endpoint) -> dict:
    """A distinct sentinel per parameter, so a swap cannot pass unnoticed."""
    return {param.name: f"v_{param.name}" for param in endpoint.params}


def _required_args(endpoint) -> dict:
    """Values pydantic will accept for the required fields, and nothing else."""
    return {
        param.name: ["v"] if param.annotation.startswith("list[") else "v"
        for param in endpoint.params
        if param.required
    }


def test_fanout_is_the_expected_size():
    """93 endpoints across 22 platforms plus the top-level extract."""
    assert len(FANOUT) == 93
    assert len({endpoint.namespace for endpoint in FANOUT}) == 23


@pytest.mark.parametrize("namespace, base", sorted(CLASS_BASE.items()))
def test_every_platform_endpoint_has_a_tool(namespace, base):
    """One tool per endpoint, per platform, so a gap names its own platform."""
    endpoints = [e for e in FANOUT if e.namespace == namespace]
    tools = [_tool_for(endpoint) for endpoint in endpoints]
    assert len(set(tools)) == len(endpoints)


@pytest.mark.parametrize("endpoint", FANOUT, ids=lambda e: e.key)
def test_tool_is_exported(endpoint):
    """A tool the package does not export is a tool nobody can use."""
    assert _tool_for(endpoint).__name__ in crewai_scavio.__all__


@pytest.mark.parametrize("endpoint", FANOUT, ids=lambda e: e.key)
def test_schema_matches_the_spec_parameters(endpoint):
    """Every wire parameter is agent-visible, and none is invented."""
    fields = _tool_for(endpoint).model_fields["args_schema"].default.model_fields
    assert set(fields) == {param.name for param in endpoint.params}
    for param in endpoint.params:
        assert fields[param.name].is_required() is param.required, param.name


@pytest.mark.parametrize("endpoint", FANOUT, ids=lambda e: e.key)
def test_optional_fields_accept_the_null_they_default_to(endpoint):
    """An optional field must be typed ``| None``, not just defaulted to it.

    An enum field annotated ``Literal[...]`` with ``default=None`` looks fine
    until an agent passes the value explicitly and pydantic rejects it, and
    the JSON schema handed to the model never admits null at all.
    """
    schema = _tool_for(endpoint).model_fields["args_schema"].default
    payload = dict(_required_args(endpoint))
    payload.update(
        {param.name: None for param in endpoint.params if not param.required}
    )
    schema(**payload)


@pytest.mark.parametrize("endpoint", FANOUT, ids=lambda e: e.key)
def test_docstring_quotes_the_path_verbatim(endpoint):
    """Paths are copied, never derived: /api/v1/meta-ads is not /metaads."""
    tool = _tool_for(endpoint)
    assert endpoint.path in tool._run.__doc__
    assert endpoint.path in tool._arun.__doc__


@pytest.mark.parametrize("endpoint", FANOUT, ids=lambda e: e.key)
@patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
@patch("crewai_scavio._base.AsyncScavioClient")
@patch("crewai_scavio._base.ScavioClient")
def test_run_forwards_every_parameter(client_cls, async_cls, endpoint):
    """The sync path reaches the right SDK method with every argument."""
    client = MagicMock()
    client_cls.return_value = client
    call = _method_mock(client, endpoint, is_async=False)

    args = _sample_args(endpoint)
    result = _tool_for(endpoint)(api_key=MOCK_API_KEY)._run(**args)

    call.assert_called_once()
    positional, keywords = call.call_args
    assert positional == ()
    assert keywords == args
    assert json.loads(result)["credits_used"] == 1


@pytest.mark.parametrize("endpoint", FANOUT, ids=lambda e: e.key)
@patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
@patch("crewai_scavio._base.AsyncScavioClient")
@patch("crewai_scavio._base.ScavioClient")
async def test_arun_forwards_every_parameter(client_cls, async_cls, endpoint):
    """The async path is a real twin, not a copy that drifted."""
    async_client = MagicMock()
    async_cls.return_value = async_client
    call = _method_mock(async_client, endpoint, is_async=True)

    args = _sample_args(endpoint)
    result = await _tool_for(endpoint)(api_key=MOCK_API_KEY)._arun(**args)

    call.assert_awaited_once()
    positional, keywords = call.call_args
    assert positional == ()
    assert keywords == args
    assert json.loads(result)["credits_used"] == 1


@pytest.mark.parametrize(
    "endpoint",
    [e for e in FANOUT if e.namespace in BODY_PRICED],
    ids=lambda e: e.key,
)
def test_body_priced_tools_never_advertise_a_flat_price(endpoint):
    """Walmart, Threads, Kuaishou and extract are priced by the request body.

    A description reading only "Costs 1 credit." on one of these would be a
    quote the API does not honour, so each must carry the pricing rule.
    """
    tool = _tool_for(endpoint)
    description = tool.model_fields["description"].default
    assert "credit" in description.lower()
    qualifiers = (
        "body-priced",
        "per endpoint",
        "function of the request body",
        "tier-priced",
        "credits on",
        "addressed by",
    )
    assert any(q in description.lower() for q in qualifiers), description


# The collection each list endpoint returns, sampled from the captured live
# responses in dashboard/public/playground-samples. max_results must trim the
# real key, not a plausible-sounding one.
TRUNCATION_CASES = [
    ("ScavioWalmartSearchTool", "walmart", "search", "products"),
    ("ScavioWalmartSellerProductsTool", "walmart", "seller_products", "products"),
    ("ScavioThreadsUserPostsTool", "threads", "user_posts", "posts"),
    ("ScavioKuaishouUserPostsTool", "kuaishou", "user_posts", "feeds"),
    ("ScavioKuaishouSearchVideosTool", "kuaishou", "search_videos", "mixFeeds"),
    ("ScavioEbaySearchTool", "ebay", "search", "products"),
    ("ScavioZillowSearchTool", "zillow", "search", "properties"),
    ("ScavioBookingSearchTool", "booking", "search", "properties"),
    ("ScavioIndeedSearchTool", "indeed", "search", "jobs"),
    ("ScavioAirbnbSearchTool", "airbnb", "search", "listings"),
    ("ScavioYelpSearchTool", "yelp", "search", "businesses"),
    ("ScavioAppStoreSearchTool", "app_store", "search", "apps"),
    ("ScavioSECFilingsTool", "sec", "filings", "filings"),
    ("ScavioCompaniesHouseOfficersTool", "companies_house", "officers", "officers"),
    ("ScavioGoogleAdsSearchTool", "google_ads", "search", "creatives"),
    ("ScavioMetaAdsSearchTool", "meta_ads", "search", "ads"),
]


@pytest.mark.parametrize(
    "tool_name, namespace, method, key",
    TRUNCATION_CASES,
    ids=[case[0] for case in TRUNCATION_CASES],
)
@patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
@patch("crewai_scavio._base.AsyncScavioClient")
@patch("crewai_scavio._base.ScavioClient")
def test_max_results_trims_the_real_collection(
    client_cls, async_cls, tool_name, namespace, method, key
):
    """max_results trims the key the live response actually uses."""
    client = MagicMock()
    client_cls.return_value = client
    payload = {"credits_used": 1, "data": {key: [{"i": i} for i in range(12)]}}
    getattr(getattr(client, namespace), method).return_value = payload

    tool = getattr(crewai_scavio, tool_name)(api_key=MOCK_API_KEY, max_results=3)
    endpoint = next(e for e in FANOUT if e.namespace == namespace and e.method == method)
    parsed = json.loads(tool._run(**_sample_args(endpoint)))

    assert len(parsed["data"][key]) == 3


@patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
@patch("crewai_scavio._base.AsyncScavioClient")
@patch("crewai_scavio._base.ScavioClient")
def test_extract_is_a_top_level_call_not_a_namespace(client_cls, async_cls):
    """``client.extract(...)``, never ``client.extract.extract(...)``."""
    client = MagicMock()
    client_cls.return_value = client
    client.extract.return_value = {"credits_used": 1, "data": {"content": "hi"}}

    tool = crewai_scavio.ScavioExtractTool(api_key=MOCK_API_KEY)
    tool._run(url="https://example.com", format="markdown", mode="ultra")

    client.extract.assert_called_once_with(
        url="https://example.com", format="markdown", mode="ultra"
    )
    assert not client.extract.extract.called
