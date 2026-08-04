"""Tests for Scavio YouTube tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.youtube import (
    ScavioYouTubeChannelCommunityTool,
    ScavioYouTubeChannelResolveTool,
    ScavioYouTubeChannelSearchTool,
    ScavioYouTubeChannelShortsTool,
    ScavioYouTubeChannelTool,
    ScavioYouTubeChannelVideosTool,
    ScavioYouTubeCommentRepliesTool,
    ScavioYouTubeCommentsTool,
    ScavioYouTubeRelatedTool,
    ScavioYouTubeSearchTool,
    ScavioYouTubeShortsTool,
    ScavioYouTubeStreamsTool,
    ScavioYouTubeSuggestionsTool,
    ScavioYouTubeTranscriptTool,
    ScavioYouTubeVideoTool,
)
from tests.conftest import (
    mock_youtube_channel_community_response,
    mock_youtube_channel_resolve_response,
    mock_youtube_channel_response,
    mock_youtube_channel_search_response,
    mock_youtube_channel_shorts_response,
    mock_youtube_channel_videos_response,
    mock_youtube_comment_replies_response,
    mock_youtube_comments_response,
    mock_youtube_related_response,
    mock_youtube_search_response,
    mock_youtube_shorts_response,
    mock_youtube_streams_response,
    mock_youtube_suggestions_response,
    mock_youtube_transcript_response,
    mock_youtube_video_response,
)

MOCK_API_KEY = "sk_live_test_key_12345"


class TestScavioYouTubeSearchTool:
    """Tests for ScavioYouTubeSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioYouTubeSearchTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio YouTube Search"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_results(self, mock_async, mock_client_cls):
        """Test that results are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.youtube.search.return_value = mock_youtube_search_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeSearchTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="python tutorial")
        parsed = json.loads(result)
        assert len(parsed["data"]["results"]) == 3


class TestScavioYouTubeVideoTool:
    """Tests for ScavioYouTubeVideoTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioYouTubeVideoTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio YouTube Video"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_video(self, mock_async, mock_client_cls):
        """Test that video metadata is returned."""
        mock_client = MagicMock()
        mock_client.youtube.video.return_value = mock_youtube_video_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeVideoTool(api_key=MOCK_API_KEY)
        result = tool._run(video_id="vid_1")
        parsed = json.loads(result)
        assert parsed["data"]["video_id"] == "vid_1"
        mock_client.youtube.video.assert_called_once_with(video_id="vid_1")


class TestScavioYouTubeCommentsTool:
    """Tests for ScavioYouTubeCommentsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioYouTubeCommentsTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio YouTube Comments"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_comments(self, mock_async, mock_client_cls):
        """Test that comments are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.youtube.comments.return_value = (
            mock_youtube_comments_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeCommentsTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(video_id="vid_1")
        parsed = json.loads(result)
        assert len(parsed["data"]["comments"]) == 3
        mock_client.youtube.comments.assert_called_once_with(
            video_id="vid_1", cursor=None
        )


class TestScavioYouTubeTranscriptTool:
    """Tests for ScavioYouTubeTranscriptTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioYouTubeTranscriptTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio YouTube Transcript"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_transcript(self, mock_async, mock_client_cls):
        """Test that a transcript is returned."""
        mock_client = MagicMock()
        mock_client.youtube.transcript.return_value = (
            mock_youtube_transcript_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeTranscriptTool(api_key=MOCK_API_KEY)
        result = tool._run(video_id="vid_1", format="text")
        parsed = json.loads(result)
        assert parsed["data"]["content"]
        mock_client.youtube.transcript.assert_called_once_with(
            video_id="vid_1", language=None, format="text"
        )


class TestScavioYouTubeChannelTool:
    """Tests for ScavioYouTubeChannelTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioYouTubeChannelTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio YouTube Channel"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_channel(self, mock_async, mock_client_cls):
        """Test that channel details are returned."""
        mock_client = MagicMock()
        mock_client.youtube.channel.return_value = (
            mock_youtube_channel_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeChannelTool(api_key=MOCK_API_KEY)
        result = tool._run(channel_id="@testchannel")
        parsed = json.loads(result)
        assert parsed["data"]["channel_id"] == "chan_1"
        mock_client.youtube.channel.assert_called_once_with(
            channel_id="@testchannel"
        )


class TestScavioYouTubeChannelVideosTool:
    """Tests for ScavioYouTubeChannelVideosTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioYouTubeChannelVideosTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio YouTube Channel Videos"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_results(self, mock_async, mock_client_cls):
        """Test that channel videos are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.youtube.channel_videos.return_value = (
            mock_youtube_channel_videos_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeChannelVideosTool(
            api_key=MOCK_API_KEY, max_results=4
        )
        result = tool._run(channel_id="chan_1")
        parsed = json.loads(result)
        assert len(parsed["data"]["results"]) == 4
        mock_client.youtube.channel_videos.assert_called_once_with(
            channel_id="chan_1", cursor=None
        )


class TestScavioYouTubeStreamsTool:
    """Tests for ScavioYouTubeStreamsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_initialization(self, mock_async, mock_client):
        """Test default initialization values."""
        tool = ScavioYouTubeStreamsTool(api_key=MOCK_API_KEY)
        assert tool.name == "Scavio YouTube Streams"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_streams(self, mock_async, mock_client_cls):
        """Test that stream formats are returned."""
        mock_client = MagicMock()
        mock_client.youtube.streams.return_value = (
            mock_youtube_streams_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeStreamsTool(api_key=MOCK_API_KEY)
        result = tool._run(video_id="vid_1")
        parsed = json.loads(result)
        assert parsed["data"]["video_id"] == "vid_1"
        assert parsed["data"]["formats"]
        mock_client.youtube.streams.assert_called_once_with(video_id="vid_1")


class TestScavioYouTubeShortsTool:
    """Tests for ScavioYouTubeShortsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_results(self, mock_async, mock_client_cls):
        """Test that Shorts results are truncated and sort_by passes through."""
        mock_client = MagicMock()
        mock_client.youtube.shorts.return_value = mock_youtube_shorts_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeShortsTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="funny cats", sort_by="view_count")
        parsed = json.loads(result)
        assert tool.name == "Scavio YouTube Shorts"
        assert len(parsed["data"]["results"]) == 3
        mock_client.youtube.shorts.assert_called_once_with(
            query="funny cats", sort_by="view_count", cursor=None
        )


class TestScavioYouTubeSuggestionsTool:
    """Tests for ScavioYouTubeSuggestionsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_suggestions(self, mock_async, mock_client_cls):
        """Test that suggestions are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.youtube.suggestions.return_value = (
            mock_youtube_suggestions_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeSuggestionsTool(api_key=MOCK_API_KEY, max_results=4)
        result = tool._run(query="python", language="en", region="US")
        parsed = json.loads(result)
        assert len(parsed["data"]["suggestions"]) == 4
        mock_client.youtube.suggestions.assert_called_once_with(
            query="python", language="en", region="US"
        )


class TestScavioYouTubeCommentRepliesTool:
    """Tests for ScavioYouTubeCommentRepliesTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_forwards_reply_cursor(self, mock_async, mock_client_cls):
        """Test that reply_cursor is required and forwarded."""
        mock_client = MagicMock()
        mock_client.youtube.comment_replies.return_value = (
            mock_youtube_comment_replies_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeCommentRepliesTool(api_key=MOCK_API_KEY, max_results=2)
        result = tool._run(video_id="vid_1", reply_cursor="rc_1")
        parsed = json.loads(result)
        assert len(parsed["data"]["replies"]) == 2
        assert tool.args_schema.model_fields["reply_cursor"].is_required()
        mock_client.youtube.comment_replies.assert_called_once_with(
            video_id="vid_1", reply_cursor="rc_1", cursor=None
        )


class TestScavioYouTubeRelatedTool:
    """Tests for ScavioYouTubeRelatedTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_results(self, mock_async, mock_client_cls):
        """Test that related videos are truncated; there is no next_cursor."""
        mock_client = MagicMock()
        mock_client.youtube.related.return_value = mock_youtube_related_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeRelatedTool(api_key=MOCK_API_KEY, max_results=5)
        result = tool._run(video_id="vid_1")
        parsed = json.loads(result)
        assert len(parsed["data"]["results"]) == 5
        assert "next_cursor" not in parsed["data"]
        mock_client.youtube.related.assert_called_once_with(
            video_id="vid_1", cursor=None
        )


class TestScavioYouTubeChannelSearchTool:
    """Tests for ScavioYouTubeChannelSearchTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_results(self, mock_async, mock_client_cls):
        """Test that channel search results are truncated."""
        mock_client = MagicMock()
        mock_client.youtube.channel_search.return_value = (
            mock_youtube_channel_search_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeChannelSearchTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(query="mrbeast")
        parsed = json.loads(result)
        assert len(parsed["data"]["results"]) == 3
        mock_client.youtube.channel_search.assert_called_once_with(
            query="mrbeast", cursor=None
        )


class TestScavioYouTubeChannelShortsTool:
    """Tests for ScavioYouTubeChannelShortsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_results(self, mock_async, mock_client_cls):
        """Test that channel Shorts are truncated under data.results."""
        mock_client = MagicMock()
        mock_client.youtube.channel_shorts.return_value = (
            mock_youtube_channel_shorts_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeChannelShortsTool(api_key=MOCK_API_KEY, max_results=2)
        result = tool._run(channel_id="chan_1", cursor="c1")
        parsed = json.loads(result)
        assert len(parsed["data"]["results"]) == 2
        assert "view_count" not in parsed["data"]["results"][0]
        mock_client.youtube.channel_shorts.assert_called_once_with(
            channel_id="chan_1", cursor="c1"
        )


class TestScavioYouTubeChannelCommunityTool:
    """Tests for ScavioYouTubeChannelCommunityTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_posts(self, mock_async, mock_client_cls):
        """Test that community posts live under data.posts, not results."""
        mock_client = MagicMock()
        mock_client.youtube.channel_community.return_value = (
            mock_youtube_channel_community_response(10)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeChannelCommunityTool(
            api_key=MOCK_API_KEY, max_results=4
        )
        result = tool._run(channel_id="chan_1")
        parsed = json.loads(result)
        assert len(parsed["data"]["posts"]) == 4
        mock_client.youtube.channel_community.assert_called_once_with(
            channel_id="chan_1", cursor=None
        )


class TestScavioYouTubeChannelResolveTool:
    """Tests for ScavioYouTubeChannelResolveTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_resolves_handle(self, mock_async, mock_client_cls):
        """Test that the input field is channel, not channel_id."""
        mock_client = MagicMock()
        mock_client.youtube.channel_resolve.return_value = (
            mock_youtube_channel_resolve_response()
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioYouTubeChannelResolveTool(api_key=MOCK_API_KEY)
        result = tool._run(channel="@MrBeast")
        parsed = json.loads(result)
        assert parsed["data"]["channel_id"] == "UCX6OQ3DkcsbYNE6H8uQQuVA"
        assert "channel_id" not in tool.args_schema.model_fields
        mock_client.youtube.channel_resolve.assert_called_once_with(
            channel="@MrBeast"
        )
