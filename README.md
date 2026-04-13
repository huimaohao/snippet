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

### [asyncio](https://docs.python.org/3/library/asyncio.html)

- [A Conceptual Overview of asyncio](https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html)
- [asyncio queues: Queue, PriorityQueue, LifoQueue](https://docs.python.org/3/library/asyncio-queue.html)

### [DashScope](https://github.com/dashscope/dashscope-sdk-python)

- 文档组织混乱，示例代码不友好，不知道哪些接口支持哪些模型，哪些模型支持哪些参数
- 有些模型根本无法使用 `DashScope` 来调用，只能使用兼容 `OpenAI` 的接口来调用
- 参数 `incremental_output` 的名字含义和文档说明，与实际使用效果相反
- 参数 `temperature = 0` 对部分模型无效，而且对其它模型也不是总有效，无法每次得到一致结果
- 参数 `result_format` 不是对所有的模型都有效，例如 `qwen3-max` 只支持 `message` 格式
