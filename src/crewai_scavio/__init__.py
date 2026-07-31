"""CrewAI integration for Scavio Search API."""

from __future__ import annotations

from crewai_scavio.amazon import (
    ScavioAmazonOffersTool,
    ScavioAmazonProductTool,
    ScavioAmazonSearchTool,
)
from crewai_scavio.google import ScavioSearchTool
from crewai_scavio.instagram import (
    ScavioInstagramCommentRepliesTool,
    ScavioInstagramPostCommentsTool,
    ScavioInstagramPostTool,
    ScavioInstagramProfileTool,
    ScavioInstagramSearchHashtagsTool,
    ScavioInstagramSearchUsersTool,
    ScavioInstagramStoriesTool,
    ScavioInstagramTaggedPostsTool,
    ScavioInstagramUserFollowersTool,
    ScavioInstagramUserFollowingsTool,
    ScavioInstagramUserPostsTool,
    ScavioInstagramUserReelsTool,
)
from crewai_scavio.reddit import ScavioRedditPostTool, ScavioRedditSearchTool
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
    ScavioTikTokVideoTool,
)
from crewai_scavio.tiktok_shop import (
    ScavioTikTokShopCategoriesTool,
    ScavioTikTokShopCategoryProductsTool,
    ScavioTikTokShopProductReviewsTool,
    ScavioTikTokShopProductTool,
    ScavioTikTokShopResolveTool,
    ScavioTikTokShopSearchSuggestionsTool,
    ScavioTikTokShopSearchTool,
    ScavioTikTokShopShopProductsTool,
)
from crewai_scavio.walmart import ScavioWalmartProductTool, ScavioWalmartSearchTool
from crewai_scavio.youtube import (
    ScavioYouTubeChannelTool,
    ScavioYouTubeChannelVideosTool,
    ScavioYouTubeCommentsTool,
    ScavioYouTubeMetadataTool,
    ScavioYouTubeSearchTool,
    ScavioYouTubeStreamsTool,
    ScavioYouTubeTranscriptTool,
)

__version__ = "0.3.0"

__all__ = [
    "ScavioSearchTool",
    "ScavioAmazonSearchTool",
    "ScavioAmazonProductTool",
    "ScavioAmazonOffersTool",
    "ScavioYouTubeSearchTool",
    "ScavioYouTubeMetadataTool",
    "ScavioYouTubeCommentsTool",
    "ScavioYouTubeTranscriptTool",
    "ScavioYouTubeChannelTool",
    "ScavioYouTubeChannelVideosTool",
    "ScavioYouTubeStreamsTool",
    "ScavioWalmartSearchTool",
    "ScavioWalmartProductTool",
    "ScavioRedditSearchTool",
    "ScavioRedditPostTool",
    "ScavioTikTokProfileTool",
    "ScavioTikTokUserPostsTool",
    "ScavioTikTokVideoTool",
    "ScavioTikTokVideoCommentsTool",
    "ScavioTikTokCommentRepliesTool",
    "ScavioTikTokSearchVideosTool",
    "ScavioTikTokSearchUsersTool",
    "ScavioTikTokHashtagTool",
    "ScavioTikTokHashtagVideosTool",
    "ScavioTikTokUserFollowersTool",
    "ScavioTikTokUserFollowingsTool",
    "ScavioTikTokShopSearchTool",
    "ScavioTikTokShopSearchSuggestionsTool",
    "ScavioTikTokShopProductTool",
    "ScavioTikTokShopProductReviewsTool",
    "ScavioTikTokShopCategoriesTool",
    "ScavioTikTokShopCategoryProductsTool",
    "ScavioTikTokShopShopProductsTool",
    "ScavioTikTokShopResolveTool",
    "ScavioInstagramProfileTool",
    "ScavioInstagramUserPostsTool",
    "ScavioInstagramUserReelsTool",
    "ScavioInstagramTaggedPostsTool",
    "ScavioInstagramStoriesTool",
    "ScavioInstagramPostTool",
    "ScavioInstagramPostCommentsTool",
    "ScavioInstagramCommentRepliesTool",
    "ScavioInstagramSearchUsersTool",
    "ScavioInstagramSearchHashtagsTool",
    "ScavioInstagramUserFollowersTool",
    "ScavioInstagramUserFollowingsTool",
]
