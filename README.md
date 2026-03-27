# Snippet

``` Shell
python -m venv .venv

.\.venv\Scripts\Activate.ps1 # PowerShell
source .venv/Scripts/activate # Git Bash

deactivate
```

``` Shell
pip list

pip freeze > requirements.txt

pip uninstall -r requirements.txt -y
```

### [asyncio](https://docs.python.org/3/library/asyncio.html)

- [A Conceptual Overview of asyncio](https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html)
- [asyncio queues: Queue, PriorityQueue, LifoQueue](https://docs.python.org/3/library/asyncio-queue.html)

### [Scrapy](https://github.com/scrapy/scrapy)

- `settings = {"DEPTH_LIMIT": 1}` 会多爬取一层地址，无法只爬取起始地址
- 无法基于流式 `http` 来即时地处理 `Response`，从而浪费带宽且降低效率
- 使用 `HEAD request method` 并根据 `Content-Type` 来过滤爬取内容，从而节省带宽
- 使用不同的方式或文件，来记录被不同规则过滤的 `url`，以防漏处理部分 `url`
- `scrapy-playwright` 设置为 `"PLAYWRIGHT_MAX_CONTEXTS": 1`，仍打开两个浏览器
- `scrapy-playwright` 会导致 `asyncio` 报错 `assert f is self._write_fut`
- `await page.wait_for_timeout(1000)` 好像除了这样，没有办法减慢打开网页的速度
