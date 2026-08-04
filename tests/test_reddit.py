"""Tests for Scavio Reddit tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from crewai_scavio.reddit import (
    ScavioRedditCommentRepliesTool,
    ScavioRedditPopularTool,
    ScavioRedditPostCommentsTool,
    ScavioRedditPostTool,
    ScavioRedditSearchSuggestionsTool,
    ScavioRedditSearchTool,
    ScavioRedditSubredditPostsTool,
    ScavioRedditSubredditTool,
    ScavioRedditTrendingTool,
    ScavioRedditUserCommentsTool,
    ScavioRedditUserPostsTool,
    ScavioRedditUserTool,
)
from tests.conftest import (
    mock_reddit_comments_response,
    mock_reddit_post_response,
    mock_reddit_posts_feed_response,
    mock_reddit_replies_response,
    mock_reddit_search_response,
    mock_reddit_subreddit_response,
    mock_reddit_suggestions_response,
    mock_reddit_trending_response,
    mock_reddit_user_comments_response,
    mock_reddit_user_response,
)

MOCK_API_KEY = "sk_live_test_key_12345"


class TestScavioRedditSearchTool:
    """Tests for ScavioRedditSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioRedditSearchTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio Reddit Search"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_results(self, mock_async, mock_client_cls):
        """Test that results are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.reddit.search.return_value = mock_reddit_search_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditSearchTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="python")
        parsed = json.loads(result)
        assert len(parsed["data"]["results"]) == 3
        mock_client.reddit.search.assert_called_once_with(
            query="python", cursor=None
        )


class TestScavioRedditPostTool:
    """Tests for ScavioRedditPostTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_post(self, mock_async, mock_client_cls):
        """Test that post data is returned."""
        mock_client = MagicMock()
        mock_client.reddit.post.return_value = mock_reddit_post_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditPostTool(api_key=MOCK_API_KEY)
        result = tool._run(url="https://reddit.com/r/test/comments/abc/test")
        parsed = json.loads(result)
        assert parsed["data"]["post_id"] == "t3_post_1"


class TestScavioRedditSearchSuggestionsTool:
    """Tests for ScavioRedditSearchSuggestionsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_suggestions(self, mock_async, mock_client_cls):
        """Test that suggestions are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.reddit.search_suggestions.return_value = (
            mock_reddit_suggestions_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditSearchSuggestionsTool(
            api_key=MOCK_API_KEY, max_results=3
        )
        result = tool._run(query="pyth")
        parsed = json.loads(result)
        assert tool.name == "Scavio Reddit Search Suggestions"
        assert len(parsed["data"]["suggestions"]) == 3
        mock_client.reddit.search_suggestions.assert_called_once_with(
            query="pyth"
        )


class TestScavioRedditPostCommentsTool:
    """Tests for ScavioRedditPostCommentsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_comments(self, mock_async, mock_client_cls):
        """Test that comments are truncated and sort is forwarded."""
        mock_client = MagicMock()
        mock_client.reddit.post_comments.return_value = (
            mock_reddit_comments_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditPostCommentsTool(api_key=MOCK_API_KEY, max_results=4)
        result = tool._run(post_id="t3_post_1", sort="TOP")
        parsed = json.loads(result)
        assert len(parsed["data"]["comments"]) == 4
        assert parsed["data"]["comments"][0]["reply_cursor"] == "reply_cursor_1"
        mock_client.reddit.post_comments.assert_called_once_with(
            post_id="t3_post_1", sort="TOP", cursor=None
        )


class TestScavioRedditCommentRepliesTool:
    """Tests for ScavioRedditCommentRepliesTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_requires_cursor(self, mock_async, mock_client_cls):
        """Test that the required reply cursor is forwarded verbatim."""
        mock_client = MagicMock()
        mock_client.reddit.comment_replies.return_value = (
            mock_reddit_replies_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditCommentRepliesTool(api_key=MOCK_API_KEY, max_results=2)
        result = tool._run(post_id="t3_post_1", cursor="reply_cursor_1")
        parsed = json.loads(result)
        assert len(parsed["data"]["replies"]) == 2
        mock_client.reddit.comment_replies.assert_called_once_with(
            post_id="t3_post_1", cursor="reply_cursor_1", sort=None
        )

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_cursor_is_required_in_schema(self, mock_async, mock_client_cls):
        """Test that the schema marks cursor as required, unlike other feeds."""
        tool = ScavioRedditCommentRepliesTool(api_key=MOCK_API_KEY)
        assert tool.args_schema.model_fields["cursor"].is_required()


class TestScavioRedditSubredditTool:
    """Tests for ScavioRedditSubredditTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_flat_metadata(self, mock_async, mock_client_cls):
        """Test that subreddit metadata is returned flat."""
        mock_client = MagicMock()
        mock_client.reddit.subreddit.return_value = (
            mock_reddit_subreddit_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditSubredditTool(api_key=MOCK_API_KEY)
        result = tool._run(subreddit="AskReddit")
        parsed = json.loads(result)
        assert parsed["data"]["subscribers"] == 45000000
        mock_client.reddit.subreddit.assert_called_once_with(
            subreddit="AskReddit"
        )


class TestScavioRedditSubredditPostsTool:
    """Tests for ScavioRedditSubredditPostsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_posts(self, mock_async, mock_client_cls):
        """Test that the feed key is posts, not results."""
        mock_client = MagicMock()
        mock_client.reddit.subreddit_posts.return_value = (
            mock_reddit_posts_feed_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditSubredditPostsTool(api_key=MOCK_API_KEY, max_results=5)
        result = tool._run(subreddit="AskReddit", sort="RISING")
        parsed = json.loads(result)
        assert len(parsed["data"]["posts"]) == 5
        mock_client.reddit.subreddit_posts.assert_called_once_with(
            subreddit="AskReddit", sort="RISING", cursor=None
        )

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_rising_only_on_subreddit_feed(self, mock_async, mock_client_cls):
        """Test that RISING is accepted here and rejected on user feeds."""
        posts_tool = ScavioRedditSubredditPostsTool(api_key=MOCK_API_KEY)
        user_tool = ScavioRedditUserPostsTool(api_key=MOCK_API_KEY)
        posts_tool.args_schema(subreddit="AskReddit", sort="RISING")
        with pytest.raises(ValidationError):
            user_tool.args_schema(username="spez", sort="RISING")


class TestScavioRedditUserTool:
    """Tests for ScavioRedditUserTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_profile(self, mock_async, mock_client_cls):
        """Test that a redditor profile is returned."""
        mock_client = MagicMock()
        mock_client.reddit.user.return_value = mock_reddit_user_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditUserTool(api_key=MOCK_API_KEY)
        result = tool._run(username="spez")
        parsed = json.loads(result)
        assert parsed["data"]["karma"] == 900000
        mock_client.reddit.user.assert_called_once_with(username="spez")


class TestScavioRedditUserPostsTool:
    """Tests for ScavioRedditUserPostsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_posts(self, mock_async, mock_client_cls):
        """Test that user posts are truncated under data.posts."""
        mock_client = MagicMock()
        mock_client.reddit.user_posts.return_value = (
            mock_reddit_posts_feed_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditUserPostsTool(api_key=MOCK_API_KEY, max_results=2)
        result = tool._run(username="spez")
        parsed = json.loads(result)
        assert len(parsed["data"]["posts"]) == 2
        mock_client.reddit.user_posts.assert_called_once_with(
            username="spez", sort=None, cursor=None
        )


class TestScavioRedditUserCommentsTool:
    """Tests for ScavioRedditUserCommentsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_comments(self, mock_async, mock_client_cls):
        """Test that user comments carry the nested post object."""
        mock_client = MagicMock()
        mock_client.reddit.user_comments.return_value = (
            mock_reddit_user_comments_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditUserCommentsTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(username="spez", sort="NEW", cursor="c1")
        parsed = json.loads(result)
        assert len(parsed["data"]["comments"]) == 3
        assert parsed["data"]["comments"][0]["post"]["id"] == "t3_post_1"
        mock_client.reddit.user_comments.assert_called_once_with(
            username="spez", sort="NEW", cursor="c1"
        )


class TestScavioRedditPopularTool:
    """Tests for ScavioRedditPopularTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_runs_without_arguments(self, mock_async, mock_client_cls):
        """Test that the popular feed works with no cursor."""
        mock_client = MagicMock()
        mock_client.reddit.popular.return_value = (
            mock_reddit_posts_feed_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditPopularTool(api_key=MOCK_API_KEY, max_results=6)
        result = tool._run()
        parsed = json.loads(result)
        assert len(parsed["data"]["posts"]) == 6
        mock_client.reddit.popular.assert_called_once_with(cursor=None)


class TestScavioRedditTrendingTool:
    """Tests for ScavioRedditTrendingTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_takes_no_arguments(self, mock_async, mock_client_cls):
        """Test that trending takes no arguments and truncates its list."""
        mock_client = MagicMock()
        mock_client.reddit.trending.return_value = (
            mock_reddit_trending_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioRedditTrendingTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run()
        parsed = json.loads(result)
        assert len(parsed["data"]["trending"]) == 3
        assert tool.args_schema.model_fields == {}
        mock_client.reddit.trending.assert_called_once_with()
