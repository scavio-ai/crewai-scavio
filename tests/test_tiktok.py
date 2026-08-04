"""Tests for Scavio TikTok tools."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from crewai_scavio.tiktok import (
    ScavioTikTokCommentRepliesTool,
    ScavioTikTokHashtagTool,
    ScavioTikTokHashtagVideosTool,
    ScavioTikTokProfileTool,
    ScavioTikTokSearchUsersTool,
    ScavioTikTokSearchVideosTool,
    ScavioTikTokUserFollowersTool,
    ScavioTikTokUserFollowingsTool,
    ScavioTikTokUserPostsTool,
    ScavioTikTokVideoCommentsTool,
    _CommentRepliesInput,
    _HashtagVideosInput,
    _SearchUsersInput,
    _SearchVideosInput,
    _UserFollowersInput,
    _UserFollowingsInput,
    _UserPostsInput,
    _VideoCommentsInput,
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


class TestTikTokPagination:
    """Pagination and page-size params must be agent-visible, not hidden."""

    def test_schemas_expose_pagination_params(self):
        """Every paginated TikTok tool exposes its own pagination params."""
        assert set(_UserPostsInput.model_fields) == {
            "sec_user_id",
            "cursor",
            "count",
            "sort_type",
        }
        assert set(_VideoCommentsInput.model_fields) == {
            "video_id",
            "cursor",
            "count",
        }
        assert set(_CommentRepliesInput.model_fields) == {
            "video_id",
            "comment_id",
            "cursor",
            "count",
        }
        assert set(_SearchVideosInput.model_fields) == {
            "keyword",
            "cursor",
            "count",
            "sort_type",
            "publish_time",
        }
        assert set(_SearchUsersInput.model_fields) == {
            "keyword",
            "cursor",
            "count",
        }
        assert set(_HashtagVideosInput.model_fields) == {
            "hashtag_id",
            "cursor",
            "count",
        }
        # Followers/followings break the family pattern: no cursor.
        for schema in (_UserFollowersInput, _UserFollowingsInput):
            assert set(schema.model_fields) == {
                "sec_user_id",
                "count",
                "page_token",
                "min_time",
            }

    def test_cursor_is_typed_as_a_string(self):
        """A numeric cursor is a 400 upstream, so the schema must say string."""
        for schema in (
            _UserPostsInput,
            _VideoCommentsInput,
            _CommentRepliesInput,
            _SearchVideosInput,
            _SearchUsersInput,
            _HashtagVideosInput,
        ):
            assert schema.model_fields["cursor"].annotation == (str | None)

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_user_posts_forwards_pagination(self, mock_async, mock_client_cls):
        """Test that user posts forwards cursor, count and sort_type."""
        mock_client = MagicMock()
        mock_client.tiktok.user_posts.return_value = mock_tiktok_video_list_response(2)
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokUserPostsTool(api_key=MOCK_API_KEY, sort_type="0")
        tool._run(
            sec_user_id="MS4wLjAB", cursor="1720000000000", count=30, sort_type="1"
        )

        _, kwargs = mock_client.tiktok.user_posts.call_args
        assert kwargs["cursor"] == "1720000000000"
        assert kwargs["count"] == 30
        # The per-call value wins over the constructor default.
        assert kwargs["sort_type"] == "1"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_user_posts_falls_back_to_tool_sort_type(
        self, mock_async, mock_client_cls
    ):
        """Test that the constructor sort_type still applies when omitted."""
        mock_client = MagicMock()
        mock_client.tiktok.user_posts.return_value = mock_tiktok_video_list_response(2)
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokUserPostsTool(api_key=MOCK_API_KEY, sort_type="1")
        tool._run(sec_user_id="MS4wLjAB")

        _, kwargs = mock_client.tiktok.user_posts.call_args
        assert kwargs["sort_type"] == "1"
        assert kwargs["cursor"] is None

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_comments_forward_pagination(self, mock_async, mock_client_cls):
        """Test that comments and replies forward cursor and count."""
        mock_client = MagicMock()
        comments = mock_tiktok_comments_response(2)
        mock_client.tiktok.video_comments.return_value = comments
        mock_client.tiktok.comment_replies.return_value = comments
        mock_client_cls.return_value = mock_client

        ScavioTikTokVideoCommentsTool(api_key=MOCK_API_KEY)._run(
            video_id="vid_1", cursor="20", count=50
        )
        _, kwargs = mock_client.tiktok.video_comments.call_args
        assert kwargs["cursor"] == "20"
        assert kwargs["count"] == 50

        ScavioTikTokCommentRepliesTool(api_key=MOCK_API_KEY)._run(
            video_id="vid_1", comment_id="c_1", cursor="20", count=50
        )
        _, kwargs = mock_client.tiktok.comment_replies.call_args
        assert kwargs["comment_id"] == "c_1"
        assert kwargs["cursor"] == "20"
        assert kwargs["count"] == 50

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_search_videos_forwards_filters(self, mock_async, mock_client_cls):
        """Test that search forwards cursor, count, sort_type and publish_time."""
        mock_client = MagicMock()
        mock_client.tiktok.search_videos.return_value = (
            mock_tiktok_search_videos_response(2)
        )
        mock_client_cls.return_value = mock_client

        tool = ScavioTikTokSearchVideosTool(
            api_key=MOCK_API_KEY, sort_type="0", publish_time="0"
        )
        tool._run(
            keyword="python",
            cursor="20",
            count=30,
            sort_type="1",
            publish_time="7",
        )

        _, kwargs = mock_client.tiktok.search_videos.call_args
        assert kwargs["cursor"] == "20"
        assert kwargs["count"] == 30
        assert kwargs["sort_type"] == "1"
        assert kwargs["publish_time"] == "7"

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_search_users_and_hashtag_videos_page(
        self, mock_async, mock_client_cls
    ):
        """Test that user search and hashtag videos forward cursor and count."""
        mock_client = MagicMock()
        mock_client.tiktok.search_users.return_value = mock_tiktok_users_response(2)
        mock_client.tiktok.hashtag_videos.return_value = (
            mock_tiktok_video_list_response(2)
        )
        mock_client_cls.return_value = mock_client

        ScavioTikTokSearchUsersTool(api_key=MOCK_API_KEY)._run(
            keyword="chef", cursor="20", count=30
        )
        _, kwargs = mock_client.tiktok.search_users.call_args
        assert kwargs["cursor"] == "20"
        assert kwargs["count"] == 30

        ScavioTikTokHashtagVideosTool(api_key=MOCK_API_KEY)._run(
            hashtag_id="123456", cursor="20", count=30
        )
        _, kwargs = mock_client.tiktok.hashtag_videos.call_args
        assert kwargs["cursor"] == "20"
        assert kwargs["count"] == 30

    @patch("crewai_scavio._base.ScavioClient")
    @patch("crewai_scavio._base.AsyncScavioClient")
    @patch("crewai_scavio._base.SCAVIO_AVAILABLE", True)
    def test_follow_lists_page_with_token_and_min_time(
        self, mock_async, mock_client_cls
    ):
        """Test that follow lists page with page_token plus min_time."""
        mock_client = MagicMock()
        mock_client.tiktok.user_followers.return_value = (
            mock_tiktok_followers_response(2, "followers")
        )
        mock_client.tiktok.user_followings.return_value = (
            mock_tiktok_followers_response(2, "followings")
        )
        mock_client_cls.return_value = mock_client

        ScavioTikTokUserFollowersTool(api_key=MOCK_API_KEY)._run(
            sec_user_id="MS4wLjAB", count=20, page_token="tok", min_time=1720000000
        )
        _, kwargs = mock_client.tiktok.user_followers.call_args
        assert kwargs["count"] == 20
        assert kwargs["page_token"] == "tok"
        assert kwargs["min_time"] == 1720000000

        ScavioTikTokUserFollowingsTool(api_key=MOCK_API_KEY)._run(
            sec_user_id="MS4wLjAB", count=20, page_token="tok", min_time=1720000000
        )
        _, kwargs = mock_client.tiktok.user_followings.call_args
        assert kwargs["page_token"] == "tok"
        assert kwargs["min_time"] == 1720000000
