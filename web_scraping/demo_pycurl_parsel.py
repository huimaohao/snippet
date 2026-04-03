"""

``` Shell
pip install pycurl
pip install parsel

# type stubs for pycurl
pip install types-pycurl
```

"""

import pycurl
import parsel

from io import BytesIO


def demo__css_selector():
    content = BytesIO()
    headers = []

    def header_function(header_line: bytes):
        headers.append(header_line.decode("iso-8859-1").strip())

    curl = pycurl.Curl()
    curl.setopt(curl.URL, "https://www.news.cn/")
    curl.setopt(curl.HEADERFUNCTION, header_function)
    curl.setopt(curl.WRITEDATA, content)
    curl.perform()
    curl.close()

    assert "Content-Type: text/html; charset=utf-8" in headers
    html_data = content.getvalue()
    html_text = html_data.decode("utf-8")

    selector = parsel.Selector(html_text)
    href_list = selector.css("a[href]::attr(href)").getall()

    with open("news_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


def demo__xpath_selector():
    content = BytesIO()
    headers = []

    def header_function(header_line: bytes):
        headers.append(header_line.decode("iso-8859-1").strip())

    curl = pycurl.Curl()
    curl.setopt(curl.URL, "https://www.gmw.cn/")
    curl.setopt(curl.HEADERFUNCTION, header_function)
    curl.setopt(curl.WRITEFUNCTION, content.write)
    curl.perform()
    curl.close()

    assert "Content-Type: text/html" in headers
    html_data = content.getvalue()
    html_text = html_data.decode("iso-8859-1")

    selector = parsel.Selector(html_text)
    href_list = selector.xpath("//a[@href]/@href").getall()

    with open("gmw_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


if __name__ == "__main__":
    demo__css_selector()
    demo__xpath_selector()
