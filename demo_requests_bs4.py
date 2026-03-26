"""

``` Shell
pip install requests
pip install beautifulsoup4

# required by beautifulsoup4
pip install lxml
pip install html5lib

# type stubs for requests
pip install types-requests
```

"""

import requests
import bs4


def demo__get__html_parser():
    base_url = "https://www.news.cn/"
    response = requests.get(base_url)  # header and content is read here
    assert response._content is not False
    html_text = response.text

    soup = bs4.BeautifulSoup(html_text, "html.parser")  # Python's html.parser
    tag_set = soup.find_all("a", href=True)
    href_list = [tag["href"] for tag in tag_set]

    with open("news_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


def demo__with_session_get__lxml_html_parser():
    with requests.Session() as session:
        base_url = "https://www.gmw.cn/"
        response = session.get(base_url)  # header and content is read here
        assert response._content is not False
        html_text = response.text

    soup = bs4.BeautifulSoup(html_text, "lxml")  # lxml's HTML parser
    tag_set = soup.select("a[href]")
    href_list = [tag["href"] for tag in tag_set]

    with open("gmw_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


def demo__with_session_with_get__lxml_xml_parser():
    with requests.Session() as session:
        base_url = "https://www.cnr.cn/"
        with session.get(base_url) as response:  # header and content is read here
            assert response._content is not False
            html_text = response.text

    soup = bs4.BeautifulSoup(html_text, "xml")  # lxml's XML parser
    tag_set = soup.find_all("a", href=True)
    href_list = [tag["href"] for tag in tag_set]

    with open("cnr_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


def demo__with_session_with_get_stream__html5lib():
    with requests.Session() as session:
        base_url = "https://www.huanqiu.com/"
        with session.get(base_url, stream=True) as response:  # header is read here
            assert response._content is False
            html_text = response.text  # content is read here
            assert response._content is not False

    soup = bs4.BeautifulSoup(html_text, "html5lib")  # html5lib
    tag_set = soup.select("a[href]")
    href_list = [tag["href"] for tag in tag_set]

    with open("huanqiu_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


if __name__ == "__main__":
    demo__get__html_parser()
    demo__with_session_get__lxml_html_parser()
    demo__with_session_with_get__lxml_xml_parser()
    demo__with_session_with_get_stream__html5lib()
