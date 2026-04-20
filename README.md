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

### [Deep Agents](https://github.com/langchain-ai/deepagents)

- 多种开箱即用的功能：上下文管理、文件系统后端、子智能代理、人机回环、权限管理、记忆、技能、沙盒、解释器

---

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
