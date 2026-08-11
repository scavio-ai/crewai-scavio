# crewai-scavio

CrewAI integration for the [Scavio Search API](https://scavio.dev?utm_source=crewai_integration), a [search API for AI agents](https://scavio.dev/search-api-for-ai-agents). Provides 188 search tools -- one per Scavio endpoint -- for use with CrewAI agents:

- **Search and web** -- Google (web, AI Mode, news, maps, shopping, flights, hotels, trends) and `ScavioExtractTool`, which reads any URL as HTML, Markdown or plain text
- **Retail** -- Amazon, Walmart, eBay, Target, Home Depot, TikTok Shop
- **Social and video** -- YouTube, TikTok, Instagram, Reddit, X (Twitter), Threads, Kuaishou
- **Real estate** -- Zillow, Redfin
- **Travel and local** -- Booking.com, Airbnb, Tripadvisor, Yelp
- **Jobs and employers** -- LinkedIn, Indeed, Glassdoor
- **Apps** -- Apple App Store, Google Play
- **Company and filings** -- SEC EDGAR, Companies House (UK)
- **Software reviews** -- G2, Capterra
- **Ad transparency** -- Google Ads Transparency, Meta Ad Library

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
| Walmart | `ScavioWalmartSearchTool` | Product search with price and fulfillment filters |
| Walmart | `ScavioWalmartProductTool` | Product details by item id (US only, no domain) |
| Walmart | `ScavioWalmartReviewsTool` | Customer reviews, 10 per page, with the rating breakdown |
| Walmart | `ScavioWalmartCategoryTool` | Products in a category, same shape as search |
| Walmart | `ScavioWalmartOffersTool` | The buy-box offer only -- not the full seller list |
| Walmart | `ScavioWalmartSellerTool` | Marketplace seller storefront and Pro Seller badge |
| Walmart | `ScavioWalmartSellerProductsTool` | A seller's catalog, first ~40 items, no pagination |
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
| Threads | `ScavioThreadsProfileTool` | Profile by user_id (2 credits) or username (4) |
| Threads | `ScavioThreadsUserPostsTool` | A user's posts, cursor-paginated |
| Threads | `ScavioThreadsUserRepliesTool` | A user's replies, cursor-paginated |
| Threads | `ScavioThreadsPostTool` | A single post by post_id or threads.net URL |
| Threads | `ScavioThreadsPostCommentsTool` | Replies to a post, cursor-paginated |
| Threads | `ScavioThreadsSearchUsersTool` | Profile search -- the only search Threads exposes |
| Kuaishou | `ScavioKuaishouProfileTool` | User profile (10 credits) |
| Kuaishou | `ScavioKuaishouUserPostsTool` | A user's top posts, cursor-paginated |
| Kuaishou | `ScavioKuaishouUserLiveTool` | A user's current live-stream status |
| Kuaishou | `ScavioKuaishouUserResolveTool` | Share link to user id (kuaishou.com only) |
| Kuaishou | `ScavioKuaishouVideoTool` | One video by photo id or URL |
| Kuaishou | `ScavioKuaishouVideoCommentsTool` | Comments on a video, cursor-paginated |
| Kuaishou | `ScavioKuaishouCommentRepliesTool` | Replies under a root comment |
| Kuaishou | `ScavioKuaishouVideosBatchTool` | Up to 20 videos in one call (40 credits) |
| Kuaishou | `ScavioKuaishouSearchTool` | Mixed-result search (10 credits per page) |
| Kuaishou | `ScavioKuaishouSearchVideosTool` | Video search (10 credits per page) |
| Kuaishou | `ScavioKuaishouSearchUsersTool` | User search (10 credits per page) |
| Kuaishou | `ScavioKuaishouSearchLiveTool` | Live-stream search (10 credits per page) |
| Kuaishou | `ScavioKuaishouTagFeedTool` | Posts under a hashtag, cursor-paginated |
| Kuaishou | `ScavioKuaishouTrendingTool` | Hot / live / shopping / brand / music leaderboards |
| eBay | `ScavioEbaySearchTool` | Live or SOLD listings; `seller` works with no keyword |
| eBay | `ScavioEbayProductTool` | One listing in full, by item number or URL |
| eBay | `ScavioEbaySellerTool` | Seller profile card (profile only, not a catalog) |
| Target | `ScavioTargetSearchTool` | Target.com search with prices, ratings and promotions |
| Target | `ScavioTargetCategoryTool` | Products in a category, plus the breadcrumb |
| Target | `ScavioTargetProductTool` | Product details by TCIN |
| Target | `ScavioTargetReviewsTool` | Reviews with per-attribute averages and guest photos |
| Home Depot | `ScavioHomeDepotSearchTool` | Search with per-store pricing and availability |
| Home Depot | `ScavioHomeDepotProductTool` | Full item detail, spec table and documents |
| Home Depot | `ScavioHomeDepotReviewsTool` | Review bodies and the rating distribution |
| Zillow | `ScavioZillowSearchTool` | Listings in a region with Zestimate and coordinates |
| Zillow | `ScavioZillowPropertyTool` | Full listing: price and tax history, RESO facts, schools |
| Zillow | `ScavioZillowAgentReviewsTool` | A Zillow agent's profile and reviews |
| Booking.com | `ScavioBookingSearchTool` | Properties for a destination and stay, with live prices |
| Booking.com | `ScavioBookingHotelTool` | One property: rooms, rate plans, facilities, house rules |
| Booking.com | `ScavioBookingReviewsTool` | Guest reviews with the score breakdown by category |
| Tripadvisor | `ScavioTripadvisorLocationsTool` | Start here: resolve a name to geo_id / location_id |
| Tripadvisor | `ScavioTripadvisorSearchTool` | Restaurants, hotels or attractions in a geo |
| Tripadvisor | `ScavioTripadvisorLocationTool` | One location in full, with page 1 of reviews |
| Tripadvisor | `ScavioTripadvisorReviewsTool` | Reviews past page 1 (de-duplicate on review_id) |
| Indeed | `ScavioIndeedSearchTool` | Job postings with salary range, type and benefits |
| Indeed | `ScavioIndeedJobTool` | One posting in full, description text and HTML |
| Indeed | `ScavioIndeedCompanyTool` | Employer profile with ratings and open roles |
| Indeed | `ScavioIndeedCompanyReviewsTool` | Employee reviews, 20 per page, with per-category ratings |
| Airbnb | `ScavioAirbnbSearchTool` | Stays with stay-total price and the discount ledger |
| Airbnb | `ScavioAirbnbListingTool` | One listing: capacity, amenities, house rules, photos |
| Airbnb | `ScavioAirbnbReviewsTool` | Review bodies with per-review rating and reviewer |
| Glassdoor | `ScavioGlassdoorCompaniesTool` | Start here: resolve a company name to employer_id |
| Glassdoor | `ScavioGlassdoorCompanyTool` | Employer profile, size, revenue and ratings |
| Glassdoor | `ScavioGlassdoorReviewsTool` | Up to three full reviews -- Glassdoor's login wall caps it |
| Glassdoor | `ScavioGlassdoorSalariesTool` | Salaries by job title, 10 titles per page |
| Yelp | `ScavioYelpSearchTool` | Businesses in Yelp's ranked order |
| Yelp | `ScavioYelpBusinessTool` | One business: hours, attributes, photos, highlights |
| Yelp | `ScavioYelpReviewsTool` | Review bodies with author profile and expertise counts |
| App Store | `ScavioAppStoreSearchTool` | Up to 200 fully-shaped app rows |
| App Store | `ScavioAppStoreAppTool` | Full listing: pricing, ratings, screenshots, devices |
| App Store | `ScavioAppStoreReviewsTool` | Reviews with the app version each was written against |
| Google Play | `ScavioGooglePlaySearchTool` | Ranked apps with package name, rating and installs |
| Google Play | `ScavioGooglePlayAppTool` | Full store listing, including the real install count |
| Google Play | `ScavioGooglePlayReviewsTool` | Reviews with thumbs-up count and developer replies |
| SEC EDGAR | `ScavioSECLookupTool` | Start here: resolve a name or ticker to a CIK |
| SEC EDGAR | `ScavioSECCompanyTool` | Filer profile: SIC industry, EIN, LEI, former names |
| SEC EDGAR | `ScavioSECFilingsTool` | A page of filings with direct document links |
| SEC EDGAR | `ScavioSECConceptTool` | Every value reported for one XBRL concept |
| SEC EDGAR | `ScavioSECFactsTool` | The index of every XBRL concept a filer reports |
| SEC EDGAR | `ScavioSECSearchTool` | EDGAR full-text search, coverage from 2001 |
| Redfin | `ScavioRedfinSearchTool` | Listings with price per sqft, lot size and year built |
| Redfin | `ScavioRedfinPropertyTool` | One listing: Redfin Estimate, MLS facts, comparables |
| Redfin | `ScavioRedfinMarketTool` | Housing-market stats for a region |
| Companies House | `ScavioCompaniesHouseSearchTool` | Start here: name to company_number on the UK register |
| Companies House | `ScavioCompaniesHouseCompanyTool` | Full register entry: status, SIC codes, addresses |
| Companies House | `ScavioCompaniesHouseOfficersTool` | Officers, current and resigned, 35 per page |
| Companies House | `ScavioCompaniesHouseFilingHistoryTool` | Filings, most recent first, with type codes |
| G2 | `ScavioG2SearchTool` | B2B software search with rating and review count |
| G2 | `ScavioG2ProductTool` | Full product profile: pros, cons, features, alternatives |
| G2 | `ScavioG2ReviewsTool` | Reviews with likes, dislikes and reviewer job title |
| Capterra | `ScavioCapterraSearchTool` | 20 ranked products with vendor and pricing |
| Capterra | `ScavioCapterraProductTool` | Full profile with the four scored criteria |
| Capterra | `ScavioCapterraReviewsTool` | Reviews with five per-criterion scores |
| Google Ads | `ScavioGoogleAdsAdvertisersTool` | Resolve a brand or domain to an advertiser_id |
| Google Ads | `ScavioGoogleAdsSearchTool` | Every ad Ads Transparency holds for an advertiser |
| Google Ads | `ScavioGoogleAdsCreativeTool` | One creative in full, with its size variations |
| Meta Ads | `ScavioMetaAdsSearchTool` | Ad Library keyword search, 30 ads per page |
| Meta Ads | `ScavioMetaAdsAdvertiserTool` | Every ad a Facebook Page is running |
| Meta Ads | `ScavioMetaAdsAdTool` | One ad by archive id, with run dates and platforms |
| Any URL | `ScavioExtractTool` | Read any URL as HTML, Markdown or plain text |

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

> **Walmart changed in 0.8.0 (breaking).** Walmart moved to a new upstream and
> gained five endpoints. `device`, `delivery_zip` and `store_id` are retired:
> sending them now returns a 200 with a `warnings[]` array explaining why, so
> they are removed here rather than kept as silent no-ops. `start_page` still
> works as a deprecated alias, but `page` is the field to use. `ScavioWalmartProductTool`
> takes no `domain` -- walmart.ca product pages cannot be fetched at all.

`domain` is the price-bearing parameter: `com` and `ca` cost 1 credit,
`com.mx` costs 2. Search and category accept it; the other five do not.

```python
from crewai_scavio import ScavioWalmartSearchTool, ScavioWalmartOffersTool

walmart_tool = ScavioWalmartSearchTool(max_results=10)
result = walmart_tool.run(
    query="air fryer",
    page=2,
    sort_by="price_low",
    min_price=50,
    max_price=200,
    fulfillment_speed="tomorrow",
)

# Offers returns the BUY-BOX seller only -- there is no way to page
# through the other sellers.
offers = ScavioWalmartOffersTool().run(product_id="13544111159")
```

`ScavioWalmartSellerProductsTool` wants the NUMERIC catalog seller id, the
`seller_catalog_id` field on a product, search or offers row. The GUID
`seller_id` 404s.

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

### Reading Any URL

`ScavioExtractTool` is not tied to a platform: give it a URL and it returns the
page as raw HTML, readability Markdown, or that Markdown flattened to plain
text. `mode` is the price-bearing argument -- `normal` (plain fetch) and
`advanced` (full browser render) cost 1 credit, `ultra` costs 2 -- and only a
successful extraction is billed, so a dead link, bot wall or timeout costs
nothing.

```python
from crewai_scavio import ScavioExtractTool

extract_tool = ScavioExtractTool()
page = extract_tool.run(url="https://example.com/pricing", format="markdown")

# Hardest targets only: 2 credits, so do not reach for it first.
stubborn = extract_tool.run(url="https://example.com/gated", mode="ultra")
```

### eBay Sold-Listing Price Research

`sold=True` searches completed listings that actually sold, which is what makes
eBay a price-history source rather than another catalog. eBay publishes no
headline count on that view, so `total_results` comes back null -- page until a
page comes back short instead of trusting a total.

`ScavioEbaySellerTool` is a profile card and cannot enumerate a catalog. To
page a seller's inventory, use search with `seller` set and no keyword.

```python
from crewai_scavio import ScavioEbaySearchTool

ebay_tool = ScavioEbaySearchTool(max_results=20)
sold = ebay_tool.run(query="ps5 slim", sold=True, condition="used", per_page=120)

catalogue = ebay_tool.run(seller="musicmagpie", sort_by="newly_listed")
```

`per_page` accepts only 60, 120 or 240; eBay silently falls back to 60 for
anything else.

### Lookup-First Platforms

Five surfaces are keyed by an id you have to resolve first. Spend the lookup
call rather than guessing the id:

| Platform | Resolve with | Then call |
|----------|--------------|-----------|
| Tripadvisor | `ScavioTripadvisorLocationsTool` | search / location / reviews |
| Glassdoor | `ScavioGlassdoorCompaniesTool` | company / reviews / salaries |
| SEC EDGAR | `ScavioSECLookupTool` | company / filings / concept / facts |
| Companies House | `ScavioCompaniesHouseSearchTool` | company / officers / filing-history |
| Google Ads | `ScavioGoogleAdsAdvertisersTool` | search / creative |

```python
import json

from crewai_scavio import ScavioSECFilingsTool, ScavioSECLookupTool

cik = json.loads(ScavioSECLookupTool().run(query="Apple"))["data"]["results"][0]
filings = ScavioSECFilingsTool(max_results=10).run(cik=cik["cik"], form="10-K")
```

### Body-Priced Endpoints

Four surfaces cost a number that depends on the request body, not on the route.
Budget for the expensive branch:

| Surface | What moves the price |
|---------|----------------------|
| Walmart | `domain`: `com` / `ca` cost 1 credit, `com.mx` costs 2 |
| Threads | `user_id` costs 2 credits, `username` costs 4 -- pass `user_id` when you have it |
| Kuaishou | Priced per endpoint: 1, 2, 10 or 40 credits (`videos_batch` is the 40) |
| Extract | `mode`: `normal` and `advanced` cost 1 credit, `ultra` costs 2 |

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
- X (Twitter), LinkedIn, Threads, and Kuaishou — tweets, profiles, timelines, company pages, and jobs
- eBay, Target, and Home Depot — retail search, product detail, and reviews
- Zillow and Redfin — listings, property detail, and market stats
- Booking.com, Airbnb, Tripadvisor, and Yelp — travel and local business data
- Indeed and Glassdoor — job postings, employer profiles, reviews, and salaries
- Apple App Store and Google Play — app listings and reviews
- SEC EDGAR and Companies House — filings, XBRL facts, officers, and UK register entries
- G2 and Capterra — B2B software ratings and review bodies
- Google Ads Transparency and the Meta Ad Library — competitor ad creatives

Get a free [API key](https://dashboard.scavio.dev) and explore the [documentation](https://scavio.dev/docs/introduction). You can also [compare Scavio vs alternatives](https://scavio.dev/compare) on coverage and pricing.
