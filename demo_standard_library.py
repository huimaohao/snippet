import http.client
import urllib.request

from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href_list = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.href_list.append(value)


def demo__http_client__html_parser():
    connection = http.client.HTTPSConnection("www.news.cn")
    connection.request("GET", "/")
    response = connection.getresponse()
    assert response.getheader("Content-Type") == "text/html; charset=utf-8"
    html_data = response.read()

    html_text = html_data.decode("utf-8")
    parser = MyHTMLParser()
    parser.feed(html_text)
    href_list = parser.href_list

    with open("news_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


def demo__urllib_request__html_parser():
    with urllib.request.urlopen("https://www.gmw.cn/") as response:
        assert response.getheader("Content-Type") == "text/html"
        html_data = response.read()

    html_text = html_data.decode("iso-8859-1")
    parser = MyHTMLParser()
    parser.feed(html_text)
    href_list = parser.href_list

    with open("gmw_href_list.txt", "w") as file:
        file.write(f"{len(href_list)}\n")
        for href in href_list:
            file.write(href + "\n")


if __name__ == "__main__":
    demo__http_client__html_parser()
    demo__urllib_request__html_parser()
