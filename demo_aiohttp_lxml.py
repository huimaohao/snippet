"""

``` Shell
pip install aiohttp
pip install lxml

# required by lxml
pip install cssselect

# type stubs for lxml
pip install types-lxml
```

"""

import asyncio
import aiohttp
import lxml.html


async def demo__xpath():
    async with aiohttp.ClientSession() as session:
        base_url = "https://www.news.cn/"
        async with session.get(base_url) as response:  # header is read here
            assert response._body is None
            html_text = await response.text()  # content is read here
            assert response._body is not None

    html_tree = lxml.html.fromstring(html_text)
    href_list = html_tree.xpath("//a[@href]/@href")

    with open("news_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


async def demo__cssselect():
    async with aiohttp.ClientSession() as session:
        base_url = "https://www.gmw.cn/"
        async with session.get(base_url) as response:  # header is read here
            assert response._body is None
            html_text = await response.text()  # content is read here
            assert response._body is not None

    html_tree = lxml.html.fromstring(html_text)
    node_list = html_tree.cssselect("a[href]")
    href_list = [node.get("href") for node in node_list]

    with open("gmw_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


async def main():
    await demo__xpath()
    await demo__cssselect()


if __name__ == "__main__":
    asyncio.run(main())
