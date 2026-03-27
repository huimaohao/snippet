"""

``` Shell
pip install scrapy
pip install scrapy-playwright

# required by playwright
playwright install
```

"""

import re

from scrapy import Spider
from scrapy.http import Request, Response
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlsplit


class XinhuaSpider(Spider):
    name = "xinhua"
    custom_settings = {"FEEDS": {"xinhua_results.json": {"format": "json"}}}
    start_urls = ["https://www.news.cn/"]

    reo_allowed_url = re.compile(
        r"^https?://.*\.(news\.cn|xinhuanet\.(com|ltd))(/.*)?$"
    )

    def parse(self, response: Response):
        content_type = response.headers.get("Content-Type")
        if content_type is None or b"text/html" not in content_type:
            return

        hrefs = response.css("a::attr(href)").getall()
        for href in hrefs:
            abs_href = response.urljoin(href)

            if self.reo_allowed_url.match(abs_href):
                yield {"url": response.url, "allowed_href": abs_href}
                yield Request(abs_href, self.parse)
            else:
                yield {"url": response.url, "ignored_href": abs_href}


def should_abort_request(request: Request):
    url_path = urlsplit(request.url).path.lower()
    return url_path.endswith((".jpg", ".jpeg", ".png", ".gif", ".css", ".woff2"))


class XinhuaPlaywrightSpider(Spider):
    name = "xinhua_playwright"
    custom_settings = {
        "FEEDS": {"xinhua_playwright_results.json": {"format": "json"}},
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
        "PLAYWRIGHT_MAX_CONTEXTS": 1,
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT": 2,
        "PLAYWRIGHT_ABORT_REQUEST": should_abort_request,
    }
    start_urls = ["https://www.news.cn/"]

    reo_allowed_url = re.compile(
        r"^https?://.*\.(news\.cn|xinhuanet\.(com|ltd))(/.*)?$"
    )

    async def start(self):
        for url in self.start_urls:
            yield Request(
                url,
                self.parse,
                meta={"playwright": True, "playwright_include_page": True},
            )

    async def parse(self, response: Response):
        content_type = response.headers.get("Content-Type")
        if content_type is None or b"text/html" not in content_type:
            return

        page = response.meta["playwright_page"]
        await page.wait_for_timeout(1000)  # Wait for any potential JS to execute
        hrefs = await page.evaluate("()=>[...document.links].map(a=>a.href)")
        await page.close()

        for href in hrefs:
            abs_href = response.urljoin(href)

            url_path = urlsplit(abs_href).path.lower()
            if url_path.endswith(".jpg"):
                continue

            if self.reo_allowed_url.match(abs_href):
                yield {"url": response.url, "allowed_href": abs_href}
                yield Request(
                    abs_href,
                    self.parse,
                    meta={"playwright": True, "playwright_include_page": True},
                )
            else:
                yield {"url": response.url, "ignored_href": abs_href}


if __name__ == "__main__":
    settings = {
        "DEPTH_LIMIT": 1,
        "LOG_LEVEL": "INFO",
    }

    process = CrawlerProcess(settings)
    process.crawl(XinhuaSpider)
    process.crawl(XinhuaPlaywrightSpider)
    process.start()
