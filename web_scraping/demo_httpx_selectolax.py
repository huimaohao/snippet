"""

``` Shell
pip install httpx
pip install selectolax
```

"""

import asyncio
import httpx

from selectolax.lexbor import LexborHTMLParser


async def demo_1():
    async with httpx.AsyncClient() as client:
        base_url = "https://www.news.cn/"
        response = await client.get(base_url)  # header and content is read here
        assert hasattr(response, "_content")
        html_text = response.text

    html_tree = LexborHTMLParser(html_text)
    node_list = html_tree.css("a[href]")
    href_list = [node.attrs["href"] for node in node_list]

    with open("news_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


async def demo_2():
    async with httpx.AsyncClient() as client:
        base_url = "https://www.gmw.cn/"
        async with client.stream("GET", base_url) as response:  # header is read here
            assert not hasattr(response, "_content")
            await response.aread()  # content is read here
            assert hasattr(response, "_content")
            html_text = response.text

    html_tree = LexborHTMLParser(html_text)
    node_list = html_tree.css("a[href]")
    href_list = [node.attrs["href"] for node in node_list]

    with open("gmw_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


async def main():
    await demo_1()
    await demo_2()


if __name__ == "__main__":
    asyncio.run(main())
