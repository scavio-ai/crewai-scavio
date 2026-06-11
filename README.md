# crewai-scavio

CrewAI integration for the [Scavio Search API](https://scavio.dev?utm_source=crewai_integration). Provides 32 search tools across Google, Amazon, Walmart, YouTube, Reddit, TikTok, and Instagram for use with CrewAI agents.

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
| YouTube | `ScavioYouTubeMetadataTool` | Video metadata by ID |
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
