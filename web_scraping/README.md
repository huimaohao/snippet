# Web Scraping

### [Beautiful Soup](https://launchpad.net/beautifulsoup)

- 支持的解析器: `html.parser`、`lxml`、`lxml-xml` / `xml`、`html5lib`
- 当使用 `lxml-xml` 来解析损坏的 `XML` 文本时 (例如有些 `HTML` 文本)，`beautifulsoup` 会令其恢复错误而非报错，但 `lxml-xml` 的恢复功能会造成大量文本内容的丢失

### [html5lib](https://github.com/html5lib/html5lib-python)

- 遵循 `WHATWG HTML Standard`
- 不支持 `XPath` 的所有特性。例如，无法使用 `.//a[@href]/@href` 来提取属性值

### [Parsel](https://github.com/scrapy/parsel)

- 使用 `cssselect` 库，将 `CSS` 选择器翻译成 `XPath` 表达式
- 支持扩展的 `CSS` 选择器语法，使其功能更靠近 `XPath`。例如，使用 `a[href]::attr(href)` 中的 `::attr(href)` 来提取属性值
