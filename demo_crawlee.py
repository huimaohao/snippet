"""

``` Shell
pip install crawlee
pip install crawlee[playwright]

# required by playwright
playwright install
```

"""

import asyncio

from crawlee import ConcurrencySettings
from crawlee.crawlers import (
    PlaywrightCrawler,
    PlaywrightCrawlingContext,
    PlaywrightPreNavCrawlingContext,
)


async def main() -> None:
    crawler = PlaywrightCrawler(
        headless=False,
        max_crawl_depth=1,
        concurrency_settings=ConcurrencySettings(
            min_concurrency=1,
            max_concurrency=8,
            max_tasks_per_minute=60,
            desired_concurrency=8,
        ),
    )

    @crawler.pre_navigation_hook
    async def navigation_hook(context: PlaywrightPreNavCrawlingContext) -> None:
        await context.block_requests(
            extra_url_patterns=[".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"]
        )

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f"Processing {context.request.url}")

        data = {"url": context.request.url, "depth": context.request.crawl_depth}
        await context.push_data(data)

        await context.enqueue_links(strategy="same-domain")

    await crawler.run(["https://www.news.cn/"])


if __name__ == "__main__":
    asyncio.run(main())
