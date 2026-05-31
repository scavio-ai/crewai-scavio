"""Shared fixtures and mock response builders for Scavio AutoGen tests."""

from __future__ import annotations


def mock_search_response(num_results: int = 10) -> dict:
    return {
        "query": "test query",
        "page": 1,
        "credits_used": 1,
        "credits_remaining": 999,
        "results": [
            {
                "title": f"Result {i}",
                "url": f"https://example.com/{i}",
                "description": f"Description {i}",
                "position": i,
            }
            for i in range(1, num_results + 1)
        ],
        "knowledge_graph": {"title": "Test", "subtitle": "A test entity"},
        "questions": [{"question": "What is test?", "answer": "A test."}],
    }


def mock_amazon_search_response(num_products: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "products": [
                {
                    "asin": f"B00{i}",
                    "title": f"Product {i}",
                    "price": {"value": 29.99 + i, "currency": "USD"},
                    "rating": 4.5,
                }
                for i in range(1, num_products + 1)
            ],
        },
    }


def mock_amazon_product_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "asin": "B001",
            "title": "Test Product",
            "price": {"value": 29.99, "currency": "USD"},
        },
    }


def mock_youtube_search_response(num_results: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "results": [
                {
                    "video_id": f"vid_{i}",
                    "title": f"Video {i}",
                    "channel": f"Channel {i}",
                    "view_count": 1000 * i,
                }
                for i in range(1, num_results + 1)
            ],
        },
    }


def mock_youtube_metadata_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "video_id": "vid_1",
            "title": "Test Video",
            "channel": "Test Channel",
            "view_count": 10000,
        },
    }


def mock_walmart_search_response(num_products: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "products": [
                {
                    "product_id": f"WM{i}",
                    "title": f"Product {i}",
                    "price": 19.99 + i,
                }
                for i in range(1, num_products + 1)
            ],
        },
    }


def mock_walmart_product_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "product_id": "WM1",
            "title": "Test Product",
            "price": 19.99,
        },
    }


def mock_reddit_search_response(num_posts: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "posts": [
                {
                    "id": f"post_{i}",
                    "title": f"Post {i}",
                    "subreddit": "test",
                    "author": f"user_{i}",
                }
                for i in range(1, num_posts + 1)
            ],
        },
    }


def mock_reddit_post_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "post": {
                "id": "post_1",
                "title": "Test Post",
                "body": "Test body",
            },
            "comments": [
                {"id": "c1", "body": "Comment 1"},
            ],
        },
    }


def mock_tiktok_profile_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "user": {
                "username": "testuser",
                "followers": 1000,
                "following": 500,
            },
        },
    }


def mock_tiktok_video_list_response(
    num_items: int = 10, key: str = "aweme_list"
) -> dict:
    return {
        "credits_used": 1,
        "data": {
            key: [
                {
                    "aweme_id": f"vid_{i}",
                    "desc": f"Video {i}",
                    "statistics": {"play_count": 1000 * i},
                }
                for i in range(1, num_items + 1)
            ],
            "has_more": 1,
        },
    }


def mock_tiktok_comments_response(num_comments: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "comments": [
                {
                    "cid": f"c_{i}",
                    "text": f"Comment {i}",
                    "digg_count": i * 10,
                }
                for i in range(1, num_comments + 1)
            ],
            "has_more": 1,
        },
    }


def mock_tiktok_search_videos_response(num_items: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "search_item_list": [
                {
                    "aweme_id": f"vid_{i}",
                    "desc": f"Search result {i}",
                }
                for i in range(1, num_items + 1)
            ],
        },
    }


def mock_tiktok_users_response(num_users: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "user_list": [
                {
                    "username": f"user_{i}",
                    "followers": 100 * i,
                }
                for i in range(1, num_users + 1)
            ],
        },
    }


def mock_tiktok_hashtag_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "challengeInfo": {
                "challenge": {"title": "test", "video_count": 1000},
            },
        },
    }


def mock_tiktok_followers_response(
    num_items: int = 10, key: str = "followers"
) -> dict:
    return {
        "credits_used": 1,
        "data": {
            key: [
                {"username": f"follower_{i}", "followers": 50 * i}
                for i in range(1, num_items + 1)
            ],
            "has_more": True,
        },
    }
