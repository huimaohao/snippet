# Snippet

``` Shell
python -m venv .venv

.\.venv\Scripts\Activate.ps1 # PowerShell
source .venv/Scripts/activate # Bash

deactivate
```

``` Shell
pip install sampleproject

pip list

pip freeze > requirements.txt

pip uninstall -r requirements.txt -y
```

### [Beautiful Soup](https://launchpad.net/beautifulsoup)

- 支持的解析器: `html.parser`、`lxml`、`lxml-xml` / `xml`、`html5lib`
- 当使用 `lxml-xml` 来解析损坏的 `XML` 文本时 (例如有些 `HTML` 文本)，`beautifulsoup` 会令其恢复错误而非报错，但 `lxml-xml` 的恢复功能会造成大量文本内容的丢失

### [html5lib](https://github.com/html5lib/html5lib-python)

- 遵循 `WHATWG HTML Standard`
- 不支持 `XPath` 的所有特性。例如，无法使用 `.//a[@href]/@href` 来提取属性值

### [Parsel](https://github.com/scrapy/parsel)

- 使用 `cssselect` 库，将 `CSS` 选择器翻译成 `XPath` 表达式
- 支持扩展的 `CSS` 选择器语法，使其功能更靠近 `XPath`。例如，使用 `a[href]::attr(href)` 中的 `::attr(href)` 来提取属性值

### [Scrapy](https://github.com/scrapy/scrapy)

- `settings = {"DEPTH_LIMIT": 1}` 会多爬取一层地址，无法只爬取起始地址
- 无法基于流式 `http` 来即时地处理 `Response`，从而浪费带宽且降低效率
- 使用 `HEAD request method` 并根据 `Content-Type` 来过滤爬取内容，从而节省带宽
- 使用不同的方式或文件，来记录被不同规则过滤的 `url`，以防漏处理部分 `url`
- `scrapy-playwright` 设置为 `"PLAYWRIGHT_MAX_CONTEXTS": 1`，仍打开两个浏览器
- `scrapy-playwright` 会导致 `asyncio` 报错 `assert f is self._write_fut`
- `await page.wait_for_timeout(1000)` 好像除了这样，没有办法减慢打开网页的速度
