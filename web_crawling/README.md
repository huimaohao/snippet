# Web Crawling

### [Crawl4AI](https://github.com/unclecode/crawl4ai)

- 无法从 `playwright` 或 `patchright` 的报错中恢复，导致爬虫程序终止
- `BestFirstCrawlingStrategy` 只根据 `url` 字符串来打分，从而确定爬取页面的顺序
- `AdaptiveCrawler` 仍处在开发阶段，存在太多 `bug`，且文档不够详细

### [Crawlee](https://github.com/apify/crawlee-python)

- 没有记录被过滤掉的 `url`
- 无法把数据追加到单一文件
- 没有输出 `playwright` 所访问资源的 `url`
- `block_requests()` 的参数 `url_patterns` 是区分大小写的
- 封装地太好了，不好修改功能

### [Scrapy](https://github.com/scrapy/scrapy)

- `settings = {"DEPTH_LIMIT": 1}` 会多爬取一层地址，无法只爬取起始地址
- 无法基于流式 `http` 来即时地处理 `Response`，从而浪费带宽且降低效率
- 使用 `HEAD request method` 并根据 `Content-Type` 来过滤爬取内容，从而节省带宽
- 使用不同的方式或文件，来记录被不同规则过滤的 `url`，以防漏处理部分 `url`
- `scrapy-playwright` 设置为 `"PLAYWRIGHT_MAX_CONTEXTS": 1`，仍打开两个浏览器
- `scrapy-playwright` 会导致 `asyncio` 报错 `assert f is self._write_fut`
- `await page.wait_for_timeout(1000)` 好像除了这样，没有办法减慢打开网页的速度
