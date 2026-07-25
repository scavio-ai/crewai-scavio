# crewai-scavio

CrewAI integration for the [Scavio Search API](https://scavio.dev?utm_source=crewai_integration), a [search API for AI agents](https://scavio.dev/search-api-for-ai-agents). Provides 37 search tools across Google, Amazon, Walmart, YouTube, Reddit, TikTok, and Instagram for use with CrewAI agents.

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
| Amazon | `ScavioAmazonSearchTool` | Product search across 20+ marketplaces |
| Amazon | `ScavioAmazonProductTool` | Product details by ASIN |
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
from crewai_scavio import ScavioAmazonSearchTool

amazon_tool = ScavioAmazonSearchTool(domain="com", max_results=5)
result = amazon_tool.run("wireless noise cancelling headphones")
```

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
