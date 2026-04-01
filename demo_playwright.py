"""

``` Shell
pip install playwright

# required by playwright
playwright install
```

"""

import asyncio
import os

from playwright.async_api import async_playwright, Request, Route


async def main():
    request_file_name = "request_url_list.txt"
    if os.path.exists(request_file_name):
        os.remove(request_file_name)

    route_file_name = "route_url_list.txt"
    if os.path.exists(route_file_name):
        os.remove(route_file_name)

    async with async_playwright() as playwright:
        async with await playwright.chromium.launch(headless=False) as browser:
            async with await browser.new_context() as context:
                async with await context.new_page() as page:
                    with (
                        open(request_file_name, "a") as request_file,
                        open(route_file_name, "a") as route_file,
                    ):

                        def request_handler(request: Request):
                            request_file.write(request.url + "\n")

                        page.on("request", request_handler)

                        def route_handler(route: Route):
                            route_file.write(route.request.url + "\n")
                            return route.continue_()

                        await page.route("**", route_handler)

                        await page.goto("https://www.news.cn/")

                        href_list = await page.evaluate(
                            "[...document.links].map(element=>element.href)"
                        )
                        with open("document_href_list.txt", "w") as file:
                            file.write(f"{len(href_list)}\n")
                            for href in href_list:
                                file.write(href + "\n")

                        # await page.pause()


if __name__ == "__main__":
    asyncio.run(main())
