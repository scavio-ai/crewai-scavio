"""SDK endpoints this package deliberately does not wrap yet.

The spec-derived guards (test_fanout, test_registry) read ``scavio._spec``, so
raising the SDK floor (to 0.23.0, for the map/crawl/batch tools) also pulls in
every endpoint the SDK gained since 0.15.0. These are named here, explicitly,
instead of silently shrinking the guard: wrapping one means deleting it from
this set, and the guards then demand the tool.
"""

from __future__ import annotations

# Added to the SDK between 0.16.0 and 0.23.0, not wrapped here yet.
NOT_YET_WRAPPED = frozenset(
    {
        "costco_autocomplete",
        "costco_availability",
        "costco_categories",
        "costco_category",
        "costco_clearance",
        "costco_coupons",
        "costco_deals",
        "costco_gas",
        "costco_prices",
        "costco_product",
        "costco_reviews",
        "costco_search",
        "costco_warehouses",
        "mercadolibre_best_sellers",
        "mercadolibre_product",
        "mercadolibre_questions",
        "mercadolibre_reviews",
        "mercadolibre_search",
        "realtor_agent",
        "realtor_agents",
        "realtor_locations",
        "realtor_market",
        "realtor_property",
        "realtor_search",
        "reddit_search_comments",
        "reddit_search_subreddits",
        "rightmove_agent",
        "rightmove_agents",
        "rightmove_locations",
        "rightmove_property",
        "rightmove_search",
        "rightmove_sold",
        "rightmove_sold_property",
        "tiktok_music",
        "tiktok_music_chart",
        "tiktok_music_videos",
        "tiktok_playlist_videos",
        "tiktok_search_music",
        "tiktok_search_suggestions",
        "tiktok_trending_searches",
        "tiktok_trending_videos",
        "tiktok_user_live",
        "tiktok_user_playlists",
        "tiktok_user_region",
        "tiktok_user_similar",
        "tiktok_video_transcript",
        "trustpilot_business",
        "trustpilot_categories",
        "trustpilot_category",
        "trustpilot_review",
        "trustpilot_reviews",
        "trustpilot_search",
        "walmart_stores",
        "x_community",
        "x_community_tweets",
        "x_search_communities",
        "youtube_community_post",
        "youtube_community_post_comments",
        # Added to the SDK between 0.24.0 and 0.27.0, not wrapped here yet.
        "chatgpt_prompt",
        "gemini_prompt",
        "google_custom_search",
    }
)

# Parameters the SDK accepts that these tools do not expose yet (Walmart store
# targeting returned to the API after the tools were written).
NOT_YET_EXPOSED_PARAMS = {
    "walmart_search": frozenset({"store_id", "delivery_zip"}),
    "walmart_product": frozenset({"store_id", "delivery_zip", "domain"}),
}

# The multi-page Extract operations. Their tools add a bounded wait
# (wait_seconds, limit) on top of the wire body and have their own contract
# tests in test_extract_web.py, so the generic one-call-per-endpoint fanout
# checks skip them.
EXTRACT_WEB = frozenset({"extract_map", "extract_crawl", "extract_batch"})
