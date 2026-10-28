"""HEB tools: store_id is forwarded, product_id works alone with store_id."""

from unittest.mock import MagicMock

from crewai_scavio import ScavioHebProductTool, ScavioHebSearchTool

_OK = {"credits_used": 2, "data": {"products": [], "store": {"store_id": "441", "name": "Uvalde H-E-B"}}}


def test_search_forwards_store_id():
    tool = ScavioHebSearchTool(api_key="test-key")
    tool.client = MagicMock()
    tool.client.heb.search.return_value = _OK
    tool._run(query="whole milk", store_id="441")
    kwargs = tool.client.heb.search.call_args.kwargs
    assert kwargs["store_id"] == "441"
    assert "store_id" in tool.args_schema.model_fields


def test_product_forwards_store_id():
    tool = ScavioHebProductTool(api_key="test-key")
    tool.client = MagicMock()
    tool.client.heb.product.return_value = _OK
    tool._run(product_id="314130", store_id="441")
    kwargs = tool.client.heb.product.call_args.kwargs
    assert kwargs["product_id"] == "314130" and kwargs["store_id"] == "441"
