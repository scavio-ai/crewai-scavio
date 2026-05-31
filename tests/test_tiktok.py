"""Tests for Scavio TikTok tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.tiktok import (
    ScavioTikTokHashtagTool,
    ScavioTikTokProfileTool,
    ScavioTikTokSearchUsersTool,
    ScavioTikTokSearchVideosTool,
    ScavioTikTokUserFollowersTool,
    ScavioTikTokUserFollowingsTool,
    ScavioTikTokUserPostsTool,
    ScavioTikTokVideoCommentsTool,
)
from tests.conftest import (
    mock_tiktok_comments_response,
    mock_tiktok_followers_response,
    mock_tiktok_hashtag_response,
    mock_tiktok_profile_response,
    mock_tiktok_search_videos_response,
    mock_tiktok_users_response,
    mock_tiktok_video_list_response,
)

MOCK_API_KEY = "sk_live_test_key_12345"


class TestScavioTikTokProfileTool:
    """Tests for ScavioTikTokProfileTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_profile(self, mock_async, mock_client_cls):
        """Test that profile data is returned."""
        mock_client = MagicMock()
        mock_client.tiktok.profile.return_value = mock_tiktok_profile_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokProfileTool(api_key=MOCK_API_KEY)
        result = tool._run(username="testuser")
        parsed = json.loads(result)
        assert parsed["data"]["user"]["username"] == "testuser"


class TestScavioTikTokUserPostsTool:
    """Tests for ScavioTikTokUserPostsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_posts(self, mock_async, mock_client_cls):
        """Test that posts are truncated to max_results."""
        mock_client = MagicMock()
        mock_client.tiktok.user_posts.return_value = mock_tiktok_video_list_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokUserPostsTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(sec_user_id="MS4wLjAB")
        parsed = json.loads(result)
        assert len(parsed["data"]["aweme_list"]) == 3


class TestScavioTikTokVideoCommentsTool:
    """Tests for ScavioTikTokVideoCommentsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_comments(self, mock_async, mock_client_cls):
        """Test that comments are truncated."""
        mock_client = MagicMock()
        mock_client.tiktok.video_comments.return_value = mock_tiktok_comments_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokVideoCommentsTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(video_id="vid_1")
        parsed = json.loads(result)
        assert len(parsed["data"]["comments"]) == 3


class TestScavioTikTokSearchVideosTool:
    """Tests for ScavioTikTokSearchVideosTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_search_results(self, mock_async, mock_client_cls):
        """Test that search results are truncated."""
        mock_client = MagicMock()
        mock_client.tiktok.search_videos.return_value = mock_tiktok_search_videos_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokSearchVideosTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(keyword="python")
        parsed = json.loads(result)
        assert len(parsed["data"]["search_item_list"]) == 3


class TestScavioTikTokSearchUsersTool:
    """Tests for ScavioTikTokSearchUsersTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_users(self, mock_async, mock_client_cls):
        """Test that user list is truncated."""
        mock_client = MagicMock()
        mock_client.tiktok.search_users.return_value = mock_tiktok_users_response(10)
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokSearchUsersTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(keyword="cooking")
        parsed = json.loads(result)
        assert len(parsed["data"]["user_list"]) == 3


class TestScavioTikTokHashtagTool:
    """Tests for ScavioTikTokHashtagTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_returns_hashtag(self, mock_async, mock_client_cls):
        """Test that hashtag data is returned."""
        mock_client = MagicMock()
        mock_client.tiktok.hashtag.return_value = mock_tiktok_hashtag_response()
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokHashtagTool(api_key=MOCK_API_KEY)
        result = tool._run(hashtag_name="python")
        parsed = json.loads(result)
        assert "challengeInfo" in parsed["data"]


class TestScavioTikTokUserFollowersTool:
    """Tests for ScavioTikTokUserFollowersTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_followers(self, mock_async, mock_client_cls):
        """Test that followers are truncated."""
        mock_client = MagicMock()
        mock_client.tiktok.user_followers.return_value = mock_tiktok_followers_response(10, "followers")
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokUserFollowersTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(sec_user_id="MS4wLjAB")
        parsed = json.loads(result)
        assert len(parsed["data"]["followers"]) == 3


class TestScavioTikTokUserFollowingsTool:
    """Tests for ScavioTikTokUserFollowingsTool."""

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_truncates_followings(self, mock_async, mock_client_cls):
        """Test that followings are truncated."""
        mock_client = MagicMock()
        mock_client.tiktok.user_followings.return_value = mock_tiktok_followers_response(10, "followings")
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokUserFollowingsTool(api_key=MOCK_API_KEY, max_results=3)
        result = tool._run(sec_user_id="MS4wLjAB")
        parsed = json.loads(result)
        assert len(parsed["data"]["followings"]) == 3
