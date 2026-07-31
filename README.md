# crewai-scavio

CrewAI integration for the [Scavio Search API](https://scavio.dev?utm_source=crewai_integration), a [search API for AI agents](https://scavio.dev/search-api-for-ai-agents). Provides 46 search tools across Google, Amazon, Walmart, YouTube, Reddit, TikTok, TikTok Shop, and Instagram for use with CrewAI agents.

## Installation

```bash
pip install crewai-scavio
```

## Setup

Get a free API key at [dashboard.scavio.dev](https://dashboard.scavio.dev?utm_source=crewai_integration) and set it as an environment variable:

```bash
export SCAVIO_API_KEY="sk_live_..."
```

## Quick Start

```python
from crewai import Agent, Crew, Task
from crewai_scavio import ScavioSearchTool

search_tool = ScavioSearchTool()

researcher = Agent(
    role="Research Analyst",
    goal="Find the latest information on any topic",
    backstory="An expert researcher who finds accurate, up-to-date information.",
    tools=[search_tool],
    verbose=True,
)

research_task = Task(
    description="Research the top 3 trends in AI agents for 2026.",
    expected_output="A summary of the top 3 AI agent trends with sources.",
    agent=researcher,
)

crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True,
)

result = crew.kickoff()
print(result)
```

## Available Tools

| Provider | Tool Class | Description |
|----------|-----------|-------------|
| Google | `ScavioSearchTool` | Web search with knowledge graphs and related questions |
| Amazon | `ScavioAmazonSearchTool` | Product search across 22 marketplaces |
| Amazon | `ScavioAmazonProductTool` | Product details by ASIN |
| Amazon | `ScavioAmazonOffersTool` | Every seller offer for an ASIN, including the buy-box winner |
| YouTube | `ScavioYouTubeSearchTool` | Video search with filters |
| YouTube | `ScavioYouTubeMetadataTool` | Video metadata by ID or watch URL |
| YouTube | `ScavioYouTubeCommentsTool` | Video comments by ID |
| YouTube | `ScavioYouTubeTranscriptTool` | Video transcript / captions by ID |
| YouTube | `ScavioYouTubeChannelTool` | Channel details by ID, @handle, or URL |
| YouTube | `ScavioYouTubeChannelVideosTool` | Videos uploaded by a channel |
| YouTube | `ScavioYouTubeStreamsTool` | Playable / downloadable stream formats |
| Walmart | `ScavioWalmartSearchTool` | Product search with price/fulfillment filters |
| Walmart | `ScavioWalmartProductTool` | Product details by ID |
| Reddit | `ScavioRedditSearchTool` | Post and comment search |
| Reddit | `ScavioRedditPostTool` | Post metadata and comments by URL |
| TikTok | `ScavioTikTokProfileTool` | User profile lookup |
| TikTok | `ScavioTikTokUserPostsTool` | User's posted videos |
| TikTok | `ScavioTikTokVideoTool` | Video details |
| TikTok | `ScavioTikTokVideoCommentsTool` | Video comments |
| TikTok | `ScavioTikTokCommentRepliesTool` | Comment replies |
| TikTok | `ScavioTikTokSearchVideosTool` | Video search by keyword |
| TikTok | `ScavioTikTokSearchUsersTool` | User search by keyword |
| TikTok | `ScavioTikTokHashtagTool` | Hashtag info |
| TikTok | `ScavioTikTokHashtagVideosTool` | Videos by hashtag |
| TikTok | `ScavioTikTokUserFollowersTool` | User's followers |
| TikTok | `ScavioTikTokUserFollowingsTool` | User's followings |
| TikTok Shop | `ScavioTikTokShopSearchTool` | Product search by keyword (US), with exact prices |
| TikTok Shop | `ScavioTikTokShopSearchSuggestionsTool` | Keyword autocomplete across 8 regions |
| TikTok Shop | `ScavioTikTokShopProductTool` | Full product detail (no price -- upstream masks it) |
| TikTok Shop | `ScavioTikTokShopProductReviewsTool` | Paginated reviews, up to 200 per call |
| TikTok Shop | `ScavioTikTokShopCategoriesTool` | Global category tree (240 nodes, 2 levels) |
| TikTok Shop | `ScavioTikTokShopCategoryProductsTool` | Products under a category, with exact prices |
| TikTok Shop | `ScavioTikTokShopShopProductsTool` | A seller's catalog, with exact prices |
| TikTok Shop | `ScavioTikTokShopResolveTool` | Resolve a Shop URL or share link to an id |
| Instagram | `ScavioInstagramProfileTool` | User profile lookup |
| Instagram | `ScavioInstagramUserPostsTool` | User's posts |
| Instagram | `ScavioInstagramUserReelsTool` | User's reels |
| Instagram | `ScavioInstagramTaggedPostsTool` | Posts user is tagged in |
| Instagram | `ScavioInstagramStoriesTool` | User's active stories |
| Instagram | `ScavioInstagramPostTool` | Post details |
| Instagram | `ScavioInstagramPostCommentsTool` | Post comments |
| Instagram | `ScavioInstagramCommentRepliesTool` | Comment replies |
| Instagram | `ScavioInstagramSearchUsersTool` | User search by keyword |
| Instagram | `ScavioInstagramSearchHashtagsTool` | Hashtag search by keyword |
| Instagram | `ScavioInstagramUserFollowersTool` | User's followers |
| Instagram | `ScavioInstagramUserFollowingsTool` | User's followings |

## Usage Examples

### Amazon Product Search

```python
from crewai_scavio import ScavioAmazonSearchTool, ScavioAmazonOffersTool

amazon_tool = ScavioAmazonSearchTool(country="us", max_results=5)
result = amazon_tool.run("wireless noise cancelling headphones")

offers_tool = ScavioAmazonOffersTool()
offers = offers_tool.run(asin="B08N5WRWNW")
```

> **Amazon changed in 0.4.0 (breaking).** The upstream provider moved. `domain`
> is replaced by `country`, a two-letter marketplace code (`us`, `gb` -- the UK
> is `gb`, not `uk` -- `de`, `jp`, ...). `sort_by`, `pages`, `category_id`,
> `merchant_id`, `language`, `currency`, `device`, `zip_code` and
> `autoselect_variant` are gone: the marketplace ignores all of them, and
> `sort_by` was verified to return the identical unordered set for every value,
> so they are removed rather than kept as silent no-ops. Product responses are
> normalized now -- `price` is a number with a sibling `currency`, not an
> object, and `buybox` is gone (use `ScavioAmazonOffersTool`).

### YouTube Video Search

```python
from crewai_scavio import ScavioYouTubeSearchTool

youtube_tool = ScavioYouTubeSearchTool(max_results=5, sort_by="relevance")
result = youtube_tool.run("CrewAI tutorial")
```

### Reddit Search

```python
from crewai_scavio import ScavioRedditSearchTool

reddit_tool = ScavioRedditSearchTool(max_results=10, sort="hot")
result = reddit_tool.run("AI agents")
```

### TikTok Shop

Two things to know before wiring these together:

1. **`ScavioTikTokShopProductTool` resolves only about 44% of the product ids
   that `ScavioTikTokShopSearchTool` returns.** Upstream has no detail data for
   the rest, so a not-found result is a normal outcome rather than an error --
   skip the product instead of retrying. Search is a listing source, not the
   first leg of a reliable search-then-detail pipeline.
2. **`ScavioTikTokShopProductTool` does not return a price.** Upstream masks the
   digits on the product page, so `price.current` and `price.original` come back
   null. Exact prices are on `ScavioTikTokShopSearchTool`,
   `ScavioTikTokShopShopProductsTool` and `ScavioTikTokShopCategoryProductsTool`.

```python
import json

from crewai_scavio import (
    ScavioTikTokShopSearchTool,
    ScavioTikTokShopProductTool,
    ScavioTikTokShopProductReviewsTool,
)

# Listing data, including the exact price
search_tool = ScavioTikTokShopSearchTool(max_results=10)
page = json.loads(search_tool.run(search="phone case"))
for product in page["data"]["products"]:
    print(product["title"], product["price"]["current"])

# Detail: rich, but priceless and only ~44% resolvable
detail_tool = ScavioTikTokShopProductTool()
detail = json.loads(detail_tool.run(product_id="1732293553906094315"))
if detail.get("not_found"):
    pass                                  # normal outcome: skip, do not retry

# Reviews: page with has_more, never with total_reviews (it drifts)
reviews_tool = ScavioTikTokShopProductReviewsTool(max_results=20)
reviews = json.loads(
    reviews_tool.run(product_id="1732293553906094315", page_size=100)
)
```

## Configuration

All tools accept `api_key` as a parameter, or read from the `SCAVIO_API_KEY` environment variable:

```python
tool = ScavioSearchTool(api_key="sk_live_...", max_results=10)
```


## About Scavio

[Scavio](https://scavio.dev) is a unified [search API](https://scavio.dev/docs/search-api) built for AI agents — one API key, structured JSON, no scraping or proxies. A real-time [Tavily alternative](https://scavio.dev/alternatives/tavily) and [SerpAPI alternative](https://scavio.dev/alternatives/serpapi) with data from:

- [Google Search API](https://scavio.dev/google-search-api) — SERP results, news, images, maps, and knowledge graph
- [Amazon Product API](https://scavio.dev/amazon-product-api) and [Walmart Product API](https://scavio.dev/walmart-product-api) — product search and details
- [YouTube API](https://scavio.dev/youtube-transcript-api), [TikTok API](https://scavio.dev/tiktok-api), and [Instagram API](https://scavio.dev/instagram-api) — video and social media data
- [Reddit API](https://scavio.dev/reddit-api) — posts and threaded comments

Get a free [API key](https://dashboard.scavio.dev) and explore the [documentation](https://scavio.dev/docs/introduction). You can also [compare Scavio vs alternatives](https://scavio.dev/compare) on coverage and pricing.
