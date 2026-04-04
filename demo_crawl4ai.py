"""

``` Shell
pip install crawl4ai

# required by crawl4ai
crawl4ai-setup
crawl4ai-doctor
```

"""

import os
import asyncio

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy


async def main():
    data_path = "data"
    os.makedirs(data_path, exist_ok=True)

    crawler_run_config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=1,
        ),
        stream=True,
    )

    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun(
            "https://www.news.cn",
            config=crawler_run_config,
        ):
            title = result.metadata.get("title")
            depth = result.metadata.get("depth")
            score = result.metadata.get("score")

            print(f"URL: {result.url}")
            print(f"Title: {title}")
            print(f"Depth: {depth} | Score: {score}")

            file_name = title.replace("|", "_")
            file_path = f"{data_path}/{file_name}.md"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.markdown)


if __name__ == "__main__":
    asyncio.run(main())
