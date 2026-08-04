# crewai-scavio

CrewAI integration for the [Scavio Search API](https://scavio.dev?utm_source=crewai_integration), a [search API for AI agents](https://scavio.dev/search-api-for-ai-agents). Provides 97 search tools -- one per Scavio endpoint -- across Google, Amazon, Walmart, YouTube, Reddit, TikTok, TikTok Shop, Instagram, X (Twitter), and LinkedIn for use with CrewAI agents.

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
| Google | `ScavioGoogleAiModeTool` | AI Mode conversational answer with references |
| Google | `ScavioGoogleMapsSearchTool` | Local business results (place_id + data_id per hit) |
| Google | `ScavioGoogleMapsPlaceTool` | Place details by place_id or data_cid |
| Google | `ScavioGoogleMapsReviewsTool` | Place reviews, up to 20 per page |
| Google | `ScavioGoogleShoppingTool` | Shopping listings with price and shipping filters |
| Google | `ScavioGoogleShoppingProductTool` | Shopping product detail and seller list |
| Google | `ScavioGoogleShoppingStoresTool` | More sellers for a shopping product |
| Google | `ScavioGoogleFlightsTool` | Flight itineraries between two airports |
| Google | `ScavioGoogleHotelsTool` | Hotel search for a destination and date range |
| Google | `ScavioGoogleHotelsDetailTool` | Property details and booking sources |
| Google | `ScavioGoogleNewsTool` | News by query, topic, story, or publication |
| Google | `ScavioGoogleTrendsTool` | Trends interest over time and by region |
| Google | `ScavioGoogleTrendingTool` | Trending Now searches for a country |
| Amazon | `ScavioAmazonSearchTool` | Product search across 22 marketplaces |
| Amazon | `ScavioAmazonProductTool` | Product details by ASIN |
| Amazon | `ScavioAmazonOffersTool` | Every seller offer for an ASIN, including the buy-box winner |
| YouTube | `ScavioYouTubeSearchTool` | Video search with filters |
| YouTube | `ScavioYouTubeVideoTool` | Video metadata by ID or watch URL |
| YouTube | `ScavioYouTubeCommentsTool` | Video comments by ID |
| YouTube | `ScavioYouTubeTranscriptTool` | Video transcript / captions by ID |
| YouTube | `ScavioYouTubeChannelTool` | Channel details by ID, @handle, or URL |
| YouTube | `ScavioYouTubeChannelVideosTool` | Videos uploaded by a channel |
| YouTube | `ScavioYouTubeStreamsTool` | Playable / downloadable stream formats |
| YouTube | `ScavioYouTubeShortsTool` | Shorts search by keyword |
| YouTube | `ScavioYouTubeSuggestionsTool` | Search autocomplete suggestions |
| YouTube | `ScavioYouTubeCommentRepliesTool` | Replies to a comment, via its reply_cursor |
| YouTube | `ScavioYouTubeRelatedTool` | Videos related to a video |
| YouTube | `ScavioYouTubeChannelSearchTool` | Channel search by keyword |
| YouTube | `ScavioYouTubeChannelShortsTool` | Shorts posted by a channel |
| YouTube | `ScavioYouTubeChannelCommunityTool` | A channel's community posts |
| YouTube | `ScavioYouTubeChannelResolveTool` | Resolve an @handle or URL to a channel ID |
| Walmart | `ScavioWalmartSearchTool` | Product search with price/fulfillment filters |
| Walmart | `ScavioWalmartProductTool` | Product details by ID |
| Reddit | `ScavioRedditSearchTool` | Post search with cursor pagination |
| Reddit | `ScavioRedditSearchSuggestionsTool` | Search query autocomplete |
| Reddit | `ScavioRedditPostTool` | Post details by url or post_id (no comments) |
| Reddit | `ScavioRedditPostCommentsTool` | Top-level comments on a post |
| Reddit | `ScavioRedditCommentRepliesTool` | Replies to a comment, via its reply_cursor |
| Reddit | `ScavioRedditSubredditTool` | Subreddit metadata |
| Reddit | `ScavioRedditSubredditPostsTool` | A subreddit's post feed (accepts RISING) |
| Reddit | `ScavioRedditUserTool` | Redditor profile and karma |
| Reddit | `ScavioRedditUserPostsTool` | A redditor's submitted posts |
| Reddit | `ScavioRedditUserCommentsTool` | A redditor's comments |
| Reddit | `ScavioRedditPopularTool` | Site-wide popular feed |
| Reddit | `ScavioRedditTrendingTool` | Trending Reddit searches |
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
| X | `ScavioXSearchTool` | Tweet / people search (query field is `search`) |
| X | `ScavioXTweetTool` | Tweet details by id |
| X | `ScavioXTweetCommentsTool` | Replies to a tweet |
| X | `ScavioXTweetRetweetersTool` | Users who retweeted a tweet |
| X | `ScavioXUserTool` | Profile by screen name |
| X | `ScavioXUserTweetsTool` | A user's tweets |
| X | `ScavioXUserRepliesTool` | A user's replies |
| X | `ScavioXUserMediaTool` | A user's media tweets |
| X | `ScavioXUserFollowersTool` | A user's followers |
| X | `ScavioXUserFollowingsTool` | A user's followings (response key is `following`) |
| X | `ScavioXTrendingTool` | Trends by country name (e.g. 'UnitedStates') |
| LinkedIn | `ScavioLinkedInPersonTool` | Person profile by username or URL |
| LinkedIn | `ScavioLinkedInPersonAboutTool` | A person's about section |
| LinkedIn | `ScavioLinkedInPersonPostsTool` | A person's posts, comments, or reactions |
| LinkedIn | `ScavioLinkedInCompanyTool` | Company profile with featured employees |
| LinkedIn | `ScavioLinkedInCompanyPostsTool` | A company's posts |
| LinkedIn | `ScavioLinkedInSearchJobsTool` | Job search |
| LinkedIn | `ScavioLinkedInJobTool` | Job details by id |
| LinkedIn | `ScavioLinkedInPostTool` | Post details by id or URL |
| LinkedIn | `ScavioLinkedInPostCommentsTool` | Post comments (paged by integer `page`) |

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

### Google Web Search

Every native v2 param -- `gl`, `hl`, `start`, `google_domain`, `device`,
`location`, `uule`, `lr`, `cr`, `safe`, `filter`, `time_period`, `nfpr`,
`include_html`, `resolve_ai_overview` -- is an argument the agent can set per
call. `start` is a result OFFSET, not a page number: 0 is page 1, 10 is page 2.

```python
from crewai_scavio import ScavioSearchTool

search_tool = ScavioSearchTool(max_results=10)
page_two = search_tool.run(
    query="best running shoes",
    gl="de",
    hl="de",
    start=10,
    time_period="last_week",
)
```

Constructor values are defaults for when the agent omits an argument. The v1
spellings `country_code`, `language` and `page` still work there and seed `gl`,
`hl` and `start`; anything the agent passes wins.

### YouTube Video Search

`sort_by`, `type`, `duration` and `upload_date` moved into the tool's argument
schema in 0.7.0, alongside `cursor` and the feature flags (`hd`, `four_k`,
`subtitles`, `creative_commons`, `live`, `hdr`, `vr180`, `video_360`,
`video_3d`, and the `features` list). Setting them on the constructor still
works as a default.

```python
from crewai_scavio import ScavioYouTubeSearchTool

youtube_tool = ScavioYouTubeSearchTool(max_results=5, sort_by="relevance")

result = youtube_tool.run(
    query="CrewAI tutorial",
    sort_by="view_count",
    duration="long",
    upload_date="this_month",
)

# Page 2: pass back data.next_cursor from the previous response.
more = youtube_tool.run(query="CrewAI tutorial", cursor="<next_cursor>")
```

### TikTok Pagination

TikTok's `cursor` is a STRING -- `"0"` for the first page, then the `cursor`
value the previous response returned. A numeric cursor is a 400. `count` is a
number, capped per endpoint (30 on the video lists, 50 on comments, 20 on the
follow lists).

```python
from crewai_scavio import ScavioTikTokSearchVideosTool, ScavioTikTokUserFollowersTool

videos_tool = ScavioTikTokSearchVideosTool(max_results=20)
page_two = videos_tool.run(
    keyword="cooking recipe", cursor="20", count=30, publish_time="7"
)

# Followers/followings break the pattern: no cursor, page with
# page_token plus min_time instead.
followers_tool = ScavioTikTokUserFollowersTool(max_results=20)
followers = followers_tool.run(
    sec_user_id="<sec_user_id>", page_token="<next_page_token>", min_time=1720000000
)
```

### Walmart Product Search

`start_page` is the only pagination field -- Walmart has no `page`. Price,
fulfillment and store filters are agent-visible arguments.

```python
from crewai_scavio import ScavioWalmartSearchTool

walmart_tool = ScavioWalmartSearchTool(max_results=10)
result = walmart_tool.run(
    query="air fryer",
    start_page=2,
    sort_by="price_low",
    min_price=50,
    max_price=200,
    delivery_zip="10001",
)
```

### Reddit Search

Results come back in relevance order under `data.results`. The endpoint takes
only `query` and `cursor` -- there is no sort or result-type filter. Paginate
by passing back the previous response's `data.next_cursor`.

```python
from crewai_scavio import ScavioRedditSearchTool

reddit_tool = ScavioRedditSearchTool(max_results=10)
result = reddit_tool.run("AI agents")
```

`/reddit/post` returns a flat post object with no comments. Fetch the thread in
a second call, then drill into a comment with its `reply_cursor`:

```python
from crewai_scavio import (
    ScavioRedditCommentRepliesTool,
    ScavioRedditPostCommentsTool,
)

comments_tool = ScavioRedditPostCommentsTool(max_results=20)
comments = comments_tool.run(post_id="t3_1v6ngaf", sort="TOP")

# cursor is REQUIRED here and must be a comment's reply_cursor,
# not the feed's next_cursor.
replies_tool = ScavioRedditCommentRepliesTool()
replies = replies_tool.run(post_id="t3_1v6ngaf", cursor="<reply_cursor>")
```

The subreddit and user feeds return `data.posts`, not `data.results`. Sort
values are uppercase, and `RISING` exists on the subreddit feed only.

### Google Maps

Maps is a two-step lookup: search for the business, then use the `place_id` or
`data_id` it returns. Google responses are flat -- there is no `data` wrapper.

```python
from crewai_scavio import ScavioGoogleMapsReviewsTool, ScavioGoogleMapsSearchTool

maps_tool = ScavioGoogleMapsSearchTool(max_results=5)
places = maps_tool.run(query="coffee in brooklyn", gl="us")

reviews_tool = ScavioGoogleMapsReviewsTool(max_results=20)
reviews = reviews_tool.run(place_id="<place_id>", sort_by="newest")
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

- [Google Search API](https://scavio.dev/google-search-api) — SERP results, AI Mode, news, maps, shopping, flights, hotels, and trends
- [Amazon Product API](https://scavio.dev/amazon-product-api) and [Walmart Product API](https://scavio.dev/walmart-product-api) — product search and details
- [YouTube API](https://scavio.dev/youtube-transcript-api), [TikTok API](https://scavio.dev/tiktok-api), and [Instagram API](https://scavio.dev/instagram-api) — video and social media data
- [Reddit API](https://scavio.dev/reddit-api) — posts, threaded comments, subreddit and user feeds
- X (Twitter) and LinkedIn — tweets, profiles, timelines, company pages, and jobs

Get a free [API key](https://dashboard.scavio.dev) and explore the [documentation](https://scavio.dev/docs/introduction). You can also [compare Scavio vs alternatives](https://scavio.dev/compare) on coverage and pricing.
