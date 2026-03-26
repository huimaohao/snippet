"""

``` Shell
pip install urllib3
pip install html5lib

# type stubs for html5lib
pip install types-html5lib
```

"""

import urllib3
import html5lib


def demo__preload_content__namespace_element__iter():
    with urllib3.PoolManager() as http:
        base_url = "https://www.news.cn/"
        response = http.request("GET", base_url)  # header and content is read here
        assert response.headers.get("Content-Type") == "text/html; charset=utf-8"
        assert response._body is not None
        html_data = response.data

    html_text = html_data.decode("utf-8")
    html_elem = html5lib.parse(html_text)
    elem_list = filter(
        lambda e: e.tag == "{http://www.w3.org/1999/xhtml}a" and "href" in e.attrib,
        html_elem.iter(),
    )
    href_list = [elem.attrib["href"] for elem in elem_list]

    with open("news_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


def demo__not_preload_content__namespace_element__findall():
    with urllib3.PoolManager() as http:
        base_url = "https://www.gmw.cn/"
        response = http.request(
            "GET", base_url, preload_content=False
        )  # header is read here
        try:
            assert response.headers.get("Content-Type") == "text/html"
            assert response._body is None
            html_data = response.data  # content is read here
            assert response._body is not None
        finally:
            response.release_conn()

    html_text = html_data.decode("iso-8859-1")
    html_elem = html5lib.parse(html_text)
    elem_list = html_elem.findall(
        ".//html:a[@href]", namespaces={"html": "http://www.w3.org/1999/xhtml"}
    )
    href_list = [elem.attrib["href"] for elem in elem_list]

    with open("gmw_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


def demo__preload_content__no_namespace_element__iter():
    with urllib3.PoolManager() as http:
        base_url = "https://www.cnr.cn/"
        response = http.request("GET", base_url)  # header and content is read here
        assert response.headers.get("Content-Type") == "text/html"
        assert response._body is not None
        html_data = response.data

    html_text = html_data.decode("iso-8859-1")
    html_elem = html5lib.parse(html_text, namespaceHTMLElements=False)
    elem_list = [e for e in html_elem.iter() if e.tag == "a" and "href" in e.attrib]
    href_list = [elem.attrib["href"] for elem in elem_list]

    with open("cnr_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


def demo__not_preload_content__no_namespace_element__findall():
    with urllib3.PoolManager() as http:
        base_url = "https://www.huanqiu.com/"
        response = http.request(
            "GET", base_url, preload_content=False
        )  # header is read here
        try:
            assert response.headers.get("Content-Type") == "text/html; charset=UTF-8"
            assert response._body is None
            html_data = response.data  # content is read here
            assert response._body is not None
        finally:
            response.release_conn()

    html_text = html_data.decode("utf-8")
    html_elem = html5lib.parse(html_text, namespaceHTMLElements=False)
    elem_list = html_elem.findall(".//a[@href]")
    href_list = [elem.attrib["href"] for elem in elem_list]

    with open("huanqiu_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


if __name__ == "__main__":
    demo__preload_content__namespace_element__iter()
    demo__not_preload_content__namespace_element__findall()
    demo__preload_content__no_namespace_element__iter()
    demo__not_preload_content__no_namespace_element__findall()
