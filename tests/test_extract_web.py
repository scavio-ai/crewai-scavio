"""Map, crawl and batch: the multi-page members of the Extract family."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from scavio._spec import ENDPOINTS

import crewai_scavio
from crewai_scavio import extract as extract_module

MOCK_API_KEY = "sk_live_test_key_12345"
CRAWL_ID = "crawl_01a12d21-fb42-7000-88cf-6887f653ee5d"
BATCH_ID = "batch_01a12d22-1d54-7000-9210-4263f1735ce9"

WAIT_FIELDS = {"wait_seconds", "limit"}


def _created(job_id: str = CRAWL_ID) -> dict:
    return {"data": {"id": job_id, "status": "queued"}, "credits_used": 0}


def _status(status: str, job_id: str = CRAWL_ID) -> dict:
    return {
        "data": {
            "id": job_id,
            "status": status,
            "pages": {"succeeded": 2},
            "credits_used": 2,
            "results": [{"url": "https://hono.dev/docs", "status": "succeeded"}],
            "next_cursor": None,
        }
    }


@pytest.fixture(autouse=True)
def _fast(monkeypatch):
    monkeypatch.setattr(extract_module, "JOB_POLL_INTERVAL", 0.0)


@pytest.fixture
def client():
    with (
        patch("crewai_scavio._base.SCAVIO_AVAILABLE", True),
        patch("crewai_scavio._base.AsyncScavioClient") as async_cls,
        patch("crewai_scavio._base.ScavioClient") as client_cls,
    ):
        sync_client, async_client = MagicMock(), MagicMock()
        client_cls.return_value = sync_client
        async_cls.return_value = async_client
        yield sync_client, async_client


@pytest.mark.parametrize(
    "tool_cls, key",
    [
        (crewai_scavio.ScavioExtractMapTool, "extract_map"),
        (crewai_scavio.ScavioExtractCrawlTool, "extract_crawl"),
        (crewai_scavio.ScavioExtractBatchTool, "extract_batch"),
    ],
)
def test_schemas_carry_the_spec_body_minus_webhook(tool_cls, key):
    """Every wire parameter except webhook_url is agent-visible; none is invented."""
    fields = set(tool_cls.model_fields["args_schema"].default.model_fields)
    spec = {p.name for p in ENDPOINTS[key].params} - {"webhook_url"}
    added = set() if key == "extract_map" else WAIT_FIELDS
    assert fields == spec | added
    assert ENDPOINTS[key].path in tool_cls._run.__doc__
    assert ENDPOINTS[key].path in tool_cls._arun.__doc__


def test_map_calls_extract_map_and_drops_none(client):
    sync_client, _ = client
    sync_client.extract.map.return_value = {"data": {"links": []}, "credits_used": 1}
    tool = crewai_scavio.ScavioExtractMapTool(api_key=MOCK_API_KEY)
    out = tool._run(url="scavio.dev", limit=3, search=None)
    sync_client.extract.map.assert_called_once_with("scavio.dev", limit=3)
    assert json.loads(out)["credits_used"] == 1


def test_crawl_waits_until_completed_then_reads_results(client):
    sync_client, _ = client
    ext = sync_client.extract
    ext.crawl.return_value = _created()
    ext.crawl_status.side_effect = [
        _status("running"),
        _status("completed"),
        _status("completed"),
    ]
    tool = crewai_scavio.ScavioExtractCrawlTool(api_key=MOCK_API_KEY)
    out = json.loads(tool._run(url="https://hono.dev/docs", max_pages=2, mode=None))
    ext.crawl.assert_called_once_with("https://hono.dev/docs", max_pages=2)
    calls = ext.crawl_status.call_args_list
    assert calls[0].args == (CRAWL_ID,) and calls[0].kwargs == {
        "limit": 1,
        "include_content": False,
    }
    assert calls[-1].kwargs == {"limit": 10}
    assert len(calls) == 3
    assert out["data"]["status"] == "completed"


def test_crawl_wait_zero_returns_the_queued_job(client):
    sync_client, _ = client
    sync_client.extract.crawl.return_value = _created()
    tool = crewai_scavio.ScavioExtractCrawlTool(api_key=MOCK_API_KEY)
    out = json.loads(tool._run(url="https://hono.dev/docs", wait_seconds=0))
    assert out["data"]["status"] == "queued"
    sync_client.extract.crawl_status.assert_not_called()


def test_crawl_stops_waiting_when_time_runs_out(client, monkeypatch):
    sync_client, _ = client
    ticks = iter(range(0, 10_000, 10))
    monkeypatch.setattr(extract_module.time, "monotonic", lambda: float(next(ticks)))
    sync_client.extract.crawl.return_value = _created()
    sync_client.extract.crawl_status.return_value = _status("running")
    tool = crewai_scavio.ScavioExtractCrawlTool(api_key=MOCK_API_KEY)
    out = json.loads(tool._run(url="https://hono.dev/docs", wait_seconds=15))
    assert out["data"]["status"] == "running"
    assert sync_client.extract.crawl_status.call_count == 2  # one probe, final read


async def test_async_crawl_waits_for_completion(client):
    _, async_client = client
    ext = async_client.extract
    ext.crawl = AsyncMock(return_value=_created())
    ext.crawl_status = AsyncMock(
        side_effect=[_status("completed"), _status("completed")]
    )
    tool = crewai_scavio.ScavioExtractCrawlTool(api_key=MOCK_API_KEY)
    out = json.loads(await tool._arun(url="https://hono.dev/docs"))
    assert out["data"]["status"] == "completed"
    assert ext.crawl_status.await_count == 2


def test_status_tools_pass_paging_through(client):
    sync_client, _ = client
    sync_client.extract.crawl_status.return_value = _status("completed")
    sync_client.extract.batch_status.return_value = _status("completed", BATCH_ID)
    crewai_scavio.ScavioExtractCrawlStatusTool(api_key=MOCK_API_KEY)._run(
        id=CRAWL_ID, cursor="25", limit=10, include_content=False, status=None
    )
    sync_client.extract.crawl_status.assert_called_once_with(
        CRAWL_ID, cursor="25", limit=10, include_content=False
    )
    crewai_scavio.ScavioExtractBatchStatusTool(api_key=MOCK_API_KEY)._run(
        id=BATCH_ID, limit=5
    )
    sync_client.extract.batch_status.assert_called_once_with(BATCH_ID, limit=5)


def test_batch_starts_and_waits_on_the_batch_job(client):
    sync_client, _ = client
    ext = sync_client.extract
    ext.batch.return_value = _created(BATCH_ID)
    ext.batch_status.return_value = _status("completed", BATCH_ID)
    urls = ["https://example.com/", "https://hono.dev/docs"]
    out = json.loads(
        crewai_scavio.ScavioExtractBatchTool(api_key=MOCK_API_KEY)._run(
            urls=urls, mode="normal"
        )
    )
    ext.batch.assert_called_once_with(urls, mode="normal")
    assert out["data"]["id"] == BATCH_ID
    ext.crawl_status.assert_not_called()


@pytest.mark.parametrize(
    "tool_cls",
    [
        crewai_scavio.ScavioExtractTool,
        crewai_scavio.ScavioExtractMapTool,
        crewai_scavio.ScavioExtractCrawlTool,
        crewai_scavio.ScavioExtractCrawlStatusTool,
        crewai_scavio.ScavioExtractBatchTool,
        crewai_scavio.ScavioExtractBatchStatusTool,
    ],
)
def test_descriptions_state_price_and_never_the_fetch_method(tool_cls):
    banned = (
        "proxy",
        "proxies",
        "residential",
        "datacenter",
        "headless",
        "browser",
        "scrape.do",
    )
    schema = tool_cls.model_fields["args_schema"].default.model_json_schema()
    text = (tool_cls.model_fields["description"].default + json.dumps(schema)).lower()
    assert "credit" in text
    for word in banned:
        assert word not in text, word
    import inspect

    source = inspect.getsource(extract_module).lower()
    for word in banned:
        assert word not in source, word
