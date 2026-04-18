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

---

### [asyncio](https://docs.python.org/3/library/asyncio.html)

- [A Conceptual Overview of asyncio](https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html)
- [asyncio queues: Queue, PriorityQueue, LifoQueue](https://docs.python.org/3/library/asyncio-queue.html)

### [LangChain](https://github.com/langchain-ai/langchain)

- 应用了大量的抽象层，导致学习曲线陡峭，且调试困难
- 除了 `LangChain` 本身，还需要了解 `LangGraph` 和 `LangSmith`

---

- [langgraph](https://github.com/langchain-ai/langgraph)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
