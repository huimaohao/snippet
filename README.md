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
