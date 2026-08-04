"""Shared fixtures and mock response builders for Scavio CrewAI tests."""

from __future__ import annotations


def mock_search_response(num_results: int = 10) -> dict:
    return {
        "query": "test query",
        "credits_used": 1,
        "credits_remaining": 999,
        "organic_results": [
            {
                "title": f"Result {i}",
                "link": f"https://example.com/{i}",
                "snippet": f"Snippet {i}",
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
                    "price": 29.99 + i,
                    "currency": "USD",
                    "rating": 4.5,
                    "reviews_count": 100 + i,
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
            "price": 29.99,
            "list_price": 39.99,
            "currency": "USD",
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


def mock_youtube_video_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "video_id": "vid_1",
            "title": "Test Video",
            "channel": "Test Channel",
            "view_count": 10000,
        },
    }


def mock_youtube_comments_response(num_comments: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "comments": [
                {
                    "comment_id": f"c_{i}",
                    "text": f"Comment {i}",
                    "like_count": 10 * i,
                    "reply_count": i,
                }
                for i in range(1, num_comments + 1)
            ],
            "has_more": True,
        },
    }


def mock_youtube_transcript_response() -> dict:
    return {
        "credits_used": 8,
        "data": {
            "video_id": "vid_1",
            "language_code": "en",
            "language_name": "English",
            "format": "text",
            "content": "hello and welcome to this video",
        },
    }


def mock_youtube_channel_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "channel_id": "chan_1",
            "title": "Test Channel",
            "subscriber_count": 509000000,
            "video_count": 993,
            "view_count": 134561410625,
        },
    }


def mock_youtube_channel_videos_response(num_results: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "channel_id": "chan_1",
            "results": [
                {
                    "video_id": f"vid_{i}",
                    "title": f"Video {i}",
                    "view_count": 1000 * i,
                }
                for i in range(1, num_results + 1)
            ],
            "has_more": True,
        },
    }


def mock_youtube_streams_response() -> dict:
    return {
        "credits_used": 3,
        "data": {
            "video_id": "vid_1",
            "title": "Test Video",
            "length_seconds": 212,
            "view_count": 10000,
            "is_live": False,
            "formats": [
                {"itag": 22, "url": "https://example.com/v", "quality_label": "720p"},
            ],
            "available_qualities": ["720p", "360p"],
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
            "results": [
                {
                    "post_id": f"t3_post_{i}",
                    "title": f"Post {i}",
                    "subreddit": "test",
                    "author": f"user_{i}",
                }
                for i in range(1, num_posts + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
        },
    }


def mock_reddit_post_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "post_id": "t3_post_1",
            "title": "Test Post",
            "text": "Test body",
            "subreddit": "test",
            "author": "user_1",
            "score": 42,
            "num_comments": 7,
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


# -- TikTok Shop ------------------------------------------------------------
#
# These are the NORMALIZED shapes the backend emits, taken from running
# backend/src/lib/tikhub/tiktok-shop-normalize.ts over the recorded fixtures in
# backend/tests/fixtures/tiktok-shop/. The key names here are the key names the
# tools must read.


def mock_tiktok_shop_card(i: int = 1) -> dict:
    return {
        "product_id": f"17324831328036832{i:02d}",
        "title": f"Pink Cherry Blossom Phone Case {i}",
        "url": f"https://shop.tiktok.com/us/pdp/17324831328036832{i:02d}",
        "image": "https://p19-oec-general.ttcdn-us.com/image.webp",
        "price": {
            "current": 4.88,
            "original": None,
            "currency": "USD",
            "discount_percent": None,
            "savings": None,
            "min": 4.88,
            "max": 7.88,
        },
        "rating": {"score": 4.7, "review_count": 15},
        "sold_count": 103,
        "variant_count": 25,
        "brand": None,
        "shop": {
            "shop_id": "7494676034572093351",
            "shop_name": "AmiShell",
            "shop_logo": "https://p16-oec-general.ttcdn-us.com/logo.png",
        },
        "labels": ["Free shipping"],
    }


def mock_tiktok_shop_review(i: int = 1) -> dict:
    return {
        "review_id": f"763255059759346663{i}",
        "rating": 5,
        "text": f"Review body {i}",
        "created_at": "2026-04-25T04:34:57.611Z",
        "reviewer_name": "C**",
        "reviewer_avatar": "https://p16-common-sign.tiktokcdn-us.com/a.jpg",
        "images": ["https://p16-oec-general-useast5.ttcdn-us.com/r.webp"],
        "is_verified_purchase": True,
        "is_incentivized": False,
        "variant": "Default",
        "country": "US",
    }


def mock_tiktok_shop_search_response(num_products: int = 30) -> dict:
    return {
        "credits_used": 1,
        "credits_remaining": 999,
        "response_time": 1.42,
        "data": {
            "query": "phone case",
            "products": [mock_tiktok_shop_card(i) for i in range(1, num_products + 1)],
            "shops": [
                {
                    "shop_id": "7494676034572093351",
                    "shop_name": "MAGIC JOHN",
                    "shop_logo": "https://p16-oec-general.ttcdn-us.com/logo.png",
                }
            ],
            "next_cursor": "eyJrIjoic2VhcmNoIiwibyI6MzB9",
            "has_more": True,
            "degraded": False,
        },
    }


def mock_tiktok_shop_suggestions_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "query": "wireless",
            "region": "US",
            "suggestions": [
                "wireless charger",
                "wireless apple carplay",
                "wireless headphones",
            ],
        },
    }


def mock_tiktok_shop_product_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "product_id": "1732293553906094315",
            "title": "[medicube] NAD+ EGF Firming Serum",
            "description": "Plain text description.",
            "url": "https://shop.tiktok.com/us/pdp/1732293553906094315",
            "images": ["https://p19-oec-general.ttcdn-us.com/img.webp"],
            # Upstream masks every price on the product page: current and
            # original are always null here.
            "price": {
                "currency": "USD",
                "current": None,
                "original": None,
                "discount_percent": 31,
                "savings": None,
            },
            "rating": {
                "score": 4.7,
                "review_count": 12561,
                "distribution": {
                    "1": 431, "2": 221, "3": 571, "4": 1175, "5": 10163,
                },
            },
            "sold_count": 231615,
            "variants": [
                {
                    "sku_id": "1732293560756310251",
                    "name": "PMEUS43022R00",
                    "in_stock": True,
                    "available_quantity": 64657,
                    "properties": [
                        {"name": "Specifications", "value": "Default"}
                    ],
                    "weight_kg": 0.1,
                    "dimensions_cm": {"length": 7.0, "width": 3.0, "height": 3.0},
                }
            ],
            "shipping": {
                "fee": 4.22,
                "currency": "USD",
                "delivery_min_days": 6,
                "delivery_max_days": 9,
                "delivery_min_business_days": 4,
                "delivery_max_business_days": 7,
                "cod_available": False,
                "fulfillable": True,
            },
            "shop": {
                "shop_id": "7495514739648989419",
                "shop_name": "medicube US Store",
                "shop_logo": "https://p16-oec-general.ttcdn-us.com/logo.png",
                "shop_url": "https://shop.tiktok.com/us/store/7495514739648989419",
                "rating": 4.6,
                "review_count": 455798,
                "sold_count": 7938115,
                "followers_count": 588860,
                "product_count": 153,
                "video_count": 1006,
                "region": "US",
                "is_official": True,
            },
            "categories": [
                {
                    "category_id": "601450",
                    "name": "Beauty & Personal Care",
                    "slug": "beauty-personal-care",
                }
            ],
            "breadcrumbs": [
                {
                    "name": "Skincare",
                    "url": "https://shop.tiktok.com/us/c/skincare/848776",
                }
            ],
            "top_reviews": [mock_tiktok_shop_review(1)],
            "seller": {
                "business_name": "APR US INC",
                "business_address": "41 GREENFIELD, Irvine, California, US",
            },
        },
    }


def mock_tiktok_shop_reviews_response(num_reviews: int = 20) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "product_id": "1732293553906094315",
            "page": 1,
            "page_size": 20,
            "filters_applied": {
                "sort": "relevant",
                "rating": None,
                "has_media": False,
                "verified_only": False,
            },
            "total_reviews": 12561,
            "rating": {
                "score": 4.6,
                "review_count": 12561,
                "distribution": {
                    "1": 431, "2": 221, "3": 571, "4": 1175, "5": 10163,
                },
            },
            "reviews": [
                mock_tiktok_shop_review(i) for i in range(1, num_reviews + 1)
            ],
            "has_more": True,
        },
    }


def mock_tiktok_shop_categories_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "categories": [
                {
                    "category_id": "601450",
                    "name": "Beauty & Personal Care",
                    "slug": "beauty-personal-care",
                    "level": 1,
                    "parent_id": None,
                    "image": "https://lf16-tiktok-common.tiktokcdn-us.com/b.png",
                    "children": [
                        {
                            "category_id": "849032",
                            "name": "Hand & Foot Care",
                            "slug": "hand-foot-care",
                            "level": 2,
                            "parent_id": "601450",
                            "image": "https://lf16-tiktok-common.tiktokcdn-us.com/h.png",
                            "children": [],
                        }
                    ],
                }
            ],
            "total_categories": 240,
        },
    }


def mock_tiktok_shop_category_products_response(num_products: int = 15) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "category_id": "601450",
            "products": [mock_tiktok_shop_card(i) for i in range(1, num_products + 1)],
            "next_cursor": "eyJrIjoiY2F0ZWdvcnkiLCJvIjoyMH0",
            "has_more": True,
        },
    }


def mock_tiktok_shop_shop_products_response(num_products: int = 30) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "shop_id": "7495514739648989419",
            "shop": {
                "shop_id": "7495514739648989419",
                "shop_name": "medicube US Store",
                "shop_logo": "https://p16-oec-general.ttcdn-us.com/logo.png",
            },
            "products": [mock_tiktok_shop_card(i) for i in range(1, num_products + 1)],
            "next_cursor": "eyJrIjoic2hvcCIsInMiOiIzMF9XemN5In0",
            "has_more": True,
        },
    }


def mock_tiktok_shop_resolve_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "type": "product",
            "product_id": "8651224669119091502",
            "shop_id": None,
            "url": "https://shop.tiktok.com/us/pdp/8651224669119091502",
            "resolved_by": "share_link",
        },
    }


class MockNotFoundError(Exception):
    """Stands in for the SDK's NotFoundError, which carries status_code 404."""

    status_code = 404


# -- Reddit (the ten endpoints beyond search / post) ------------------------
#
# Reddit envelopes are {data, response_time, credits_used, credits_remaining}.
# The list key differs per endpoint: search -> results, the subreddit / user /
# popular feeds -> posts, comments -> comments, replies -> replies.


def mock_reddit_suggestions_response(num_suggestions: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "suggestions": [f"python {i}" for i in range(1, num_suggestions + 1)],
            "total_count": num_suggestions,
        },
    }


def mock_reddit_comments_response(num_comments: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "comments": [
                {
                    "comment_id": f"t1_c_{i}",
                    "text": f"Comment {i}",
                    "author": f"user_{i}",
                    "score": i * 3,
                    "depth": 0,
                    "reply_cursor": f"reply_cursor_{i}",
                }
                for i in range(1, num_comments + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
        },
    }


def mock_reddit_replies_response(num_replies: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "replies": [
                {
                    "comment_id": f"t1_r_{i}",
                    "text": f"Reply {i}",
                    "author": f"user_{i}",
                    "score": i,
                    "depth": 1,
                    "reply_cursor": None,
                }
                for i in range(1, num_replies + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
        },
    }


def mock_reddit_subreddit_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "id": "t5_2qh1i",
            "name": "AskReddit",
            "prefixed_name": "r/AskReddit",
            "title": "Ask Reddit",
            "public_description": "Ask away.",
            "subscribers": 45000000,
            "active_count": 12000,
            "is_nsfw": False,
        },
    }


def mock_reddit_posts_feed_response(num_posts: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "posts": [
                {
                    "post_id": f"t3_post_{i}",
                    "title": f"Post {i}",
                    "subreddit": "test",
                    "author": f"user_{i}",
                    "score": 10 * i,
                    "num_comments": i,
                }
                for i in range(1, num_posts + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
        },
    }


def mock_reddit_user_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "id": "t2_1w72",
            "name": "spez",
            "is_employee": True,
            "is_verified": True,
            "karma": 900000,
            "post_karma": 200000,
            "comment_karma": 700000,
        },
    }


def mock_reddit_user_comments_response(num_comments: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "comments": [
                {
                    "comment_id": f"t1_uc_{i}",
                    "text": f"User comment {i}",
                    "author": "spez",
                    "post": {"id": f"t3_post_{i}", "title": f"Post {i}"},
                    "score": i * 2,
                }
                for i in range(1, num_comments + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
        },
    }


def mock_reddit_trending_response(num_trends: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "trending": [
                {"query": f"trend {i}", "raw_query": f"trend+{i}"}
                for i in range(1, num_trends + 1)
            ],
            "total_count": num_trends,
        },
    }


# -- YouTube (the eight endpoints beyond the original seven) ----------------


def mock_youtube_shorts_response(num_results: int = 10) -> dict:
    return {
        "credits_used": 2,
        "data": {
            "results": [
                {
                    "video_id": f"short_{i}",
                    "title": f"Short {i}",
                    "url": f"https://www.youtube.com/shorts/short_{i}",
                }
                for i in range(1, num_results + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
        },
    }


def mock_youtube_suggestions_response(num_suggestions: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "suggestions": [
                f"python tutorial {i}" for i in range(1, num_suggestions + 1)
            ],
            "total_count": num_suggestions,
        },
    }


def mock_youtube_comment_replies_response(num_replies: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "replies": [
                {
                    "comment_id": f"r_{i}",
                    "text": f"Reply {i}",
                    "like_count": i,
                }
                for i in range(1, num_replies + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
        },
    }


def mock_youtube_related_response(num_results: int = 10) -> dict:
    # No next_cursor / has_more here -- /related returns total_count only.
    return {
        "credits_used": 1,
        "data": {
            "results": [
                {"video_id": f"rel_{i}", "title": f"Related {i}"}
                for i in range(1, num_results + 1)
            ],
            "total_count": num_results,
        },
    }


def mock_youtube_channel_search_response(num_results: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "results": [
                {
                    "channel_id": f"chan_{i}",
                    "name": f"Channel {i}",
                    "handle": f"@channel{i}",
                    "subscriber_count": 1000 * i,
                    "verified": True,
                }
                for i in range(1, num_results + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
            "total_count": num_results,
        },
    }


def mock_youtube_channel_shorts_response(num_results: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "channel_id": "chan_1",
            "results": [
                {
                    "video_id": f"short_{i}",
                    "title": f"Short {i}",
                    "url": f"https://www.youtube.com/shorts/short_{i}",
                    "thumbnail": "https://example.com/t.jpg",
                }
                for i in range(1, num_results + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
            "total_count": num_results,
        },
    }


def mock_youtube_channel_community_response(num_posts: int = 10) -> dict:
    return {
        "credits_used": 1,
        "data": {
            "channel_id": "chan_1",
            "posts": [
                {
                    "post_id": f"cp_{i}",
                    "text": f"Community post {i}",
                    "vote_count": 10 * i,
                    "comment_count": i,
                }
                for i in range(1, num_posts + 1)
            ],
            "next_cursor": "cursor_2",
            "has_more": True,
        },
    }


def mock_youtube_channel_resolve_response() -> dict:
    return {
        "credits_used": 1,
        "data": {
            "channel_id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
            "channel_url": "https://www.youtube.com/@MrBeast",
        },
    }


# -- Google v2 --------------------------------------------------------------
#
# Every Google response is FLAT: the payload sits at the top level next to
# response_time / credits_used / credits_remaining / cached. There is no
# `data` wrapper anywhere in this family.


def mock_google_ai_mode_response(num_references: int = 10) -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "text_blocks": [{"type": "paragraph", "snippet": "An answer."}],
        "references": [
            {"title": f"Reference {i}", "link": f"https://example.com/{i}"}
            for i in range(1, num_references + 1)
        ],
    }


def mock_google_maps_search_response(num_results: int = 10) -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "local_results": [
            {
                "position": i,
                "title": f"Business {i}",
                "place_id": f"ChIJ_{i}",
                "data_id": f"0x89c2596{i}:0xe230af1b18e542a7",
                "rating": 4.5,
            }
            for i in range(1, num_results + 1)
        ],
    }


def mock_google_maps_place_response() -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "place_results": {
            "title": "Business 1",
            "place_id": "ChIJ_1",
            "rating": 4.5,
            "reviews": 1200,
        },
    }


def mock_google_maps_reviews_response(num_reviews: int = 10) -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "place_info": {"title": "Business 1"},
        "reviews": [
            {"user": f"Reviewer {i}", "rating": 5, "snippet": f"Review {i}"}
            for i in range(1, num_reviews + 1)
        ],
        "pagination": {"next_page_token": "token_2"},
    }


def mock_google_shopping_response(num_results: int = 10) -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "shopping_results": [
            {
                "position": i,
                "title": f"Product {i}",
                "price": f"${i}.99",
                "catalog_id": f"catalog_{i}",
            }
            for i in range(1, num_results + 1)
        ],
    }


def mock_google_shopping_product_response() -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "product_results": {
            "title": "Product 1",
            "stores": [
                {"name": "Store 1", "total_price": "$19.99"},
            ],
        },
    }


def mock_google_shopping_stores_response() -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "product_results": {
            "stores": [
                {"name": f"Store {i}", "total_price": f"${i}.99"}
                for i in range(1, 4)
            ],
        },
    }


def mock_google_flights_response(num_flights: int = 10) -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "best_flights": [
            {"price": 200 + i, "total_duration": 300 + i}
            for i in range(1, num_flights + 1)
        ],
        "other_flights": [
            {"price": 400 + i, "total_duration": 500 + i}
            for i in range(1, num_flights + 1)
        ],
    }


def mock_google_hotels_response(num_properties: int = 10) -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "properties": [
            {
                "name": f"Hotel {i}",
                "detail_token": f"detail_token_{i}",
                "rate_per_night": {"lowest": f"${100 + i}"},
            }
            for i in range(1, num_properties + 1)
        ],
    }


def mock_google_hotels_detail_response() -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "property": {
            "name": "Hotel 1",
            "booking_sources": [{"name": "Booking.com", "rate": "$120"}],
        },
    }


def mock_google_news_response(num_results: int = 10) -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "news_results": [
            {
                "position": i,
                "title": f"Story {i}",
                "link": f"https://news.example.com/{i}",
                "source": {"name": f"Publisher {i}"},
            }
            for i in range(1, num_results + 1)
        ],
    }


def mock_google_trends_response(num_regions: int = 10) -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "interest_over_time": {
            "timeline_data": [{"date": "Jul 2026", "values": [{"value": "80"}]}],
        },
        "interest_by_region": [
            {"location": f"Region {i}", "value": 100 - i}
            for i in range(1, num_regions + 1)
        ],
    }


def mock_google_trending_response(num_trends: int = 10) -> dict:
    return {
        "credits_used": 1,
        "cached": False,
        "trends": [
            {"query": f"trend {i}", "search_volume": 1000 * i}
            for i in range(1, num_trends + 1)
        ],
    }
