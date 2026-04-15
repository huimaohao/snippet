"""

``` Shell
pip install langchain
pip install langchain-ollama
pip install langchain-openai

pip install python-dotenv
```

"""

import asyncio
import inspect
import os
import random

from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated

load_dotenv()


def print_func_name(frame):
    print()
    print("-" * 50, frame.f_code.co_name, "-" * 50)
    print()


def create_qwen_model(model: str):
    return ChatOpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        model=model,
        temperature=0,
    )


def demo__model__init_chat_model__invoke():
    print_func_name(inspect.currentframe())

    model = init_chat_model(
        "gemma4",
        model_provider="ollama",
        temperature=0,
    )

    response = model.invoke("你是谁")
    response.pretty_print()
    print()

    response = model.invoke([("system", "你假装是qwen3.5"), ("human", "你是谁")])
    response.pretty_print()
    print()


def demo__model__ChatProvider__invoke():
    print_func_name(inspect.currentframe())

    model = ChatOllama(
        model="qwen3.5",
        temperature=0,
    )

    response = model.invoke("你是谁")
    response.pretty_print()
    print()

    response = model.invoke([("system", "你假装是gemma4"), ("human", "你是谁")])
    response.pretty_print()
    print()


def demo__model__stream():
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3.6-max-preview")

    chunks = model.stream(
        [
            SystemMessage("你是C.C."),
            HumanMessage("我是L.L."),
        ]
    )

    for chunk in chunks:
        print(chunk.text, end="", flush=True)
        # print("", end="|")
    print()


async def demo__model__astream():
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3.6-max-preview")

    events = model.astream_events(
        [
            SystemMessage("你是L.L."),
            HumanMessage("我是C.C."),
        ]
    )

    async for event in events:
        if event["event"] == "on_chat_model_stream":
            print(event["data"]["chunk"].content, end="", flush=True)
    print()


def demo__model__batch():
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3.6-max-preview")

    # fmt: off
    SysMsg, HumMsg = SystemMessage, HumanMessage
    inputs = [
        [("system", "你是枢木朱雀,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [SysMsg("你是C.C.,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是V.V.,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是毛,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [("system", "你是红月华莲,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是扇要,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是玉城真一郎,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是藤堂镜志朗,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是筱崎咲世子,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是皇神乐耶,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是拉克夏塔·恰拉,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是迪特哈鲁特·利特,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [SysMsg("你是娜娜莉·兰佩路基,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是罗洛·兰佩路基,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是夏莉·菲内特,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是米蕾·阿什弗德,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是妮娜·爱因斯坦,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是利瓦尔·卡路迪蒙特,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [("system", "你是查尔斯·Zi·布里塔尼亚,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是玛丽安娜·Vi·布里塔尼亚,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是修奈泽尔·El·布里塔尼亚,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是尤菲米亚·Li·布里塔尼亚,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是柯内莉亚·Li·布里塔尼亚,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [("system", "你是克洛维斯·La·布里塔尼亚,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        [SysMsg("你是阿妮亚·阿鲁斯特莱依姆,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是基诺·拜因贝鲁克,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是俾斯麦·瓦尔德施泰因,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是杰雷米亚·哥德巴尔德,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是维蕾塔·努,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是洛伊德·阿斯普林德,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是塞希尔·柯尔米,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是基尔伯特·G·P·基尔福特,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [SysMsg("你是安德列亚斯·达尔顿,我是鲁路修·兰佩路基"), HumMsg("我其实是Zero")],
        [("system", "你是黎星刻,我是鲁路修·兰佩路基"), ("human", "我其实是Zero")],
        "这是哪部动漫的台词:错的不是我,错的是这个世界",
        "这是哪部动漫的台词:如果你是魔女,我只要变成魔王就可以了",
    ]
    # fmt: on

    messages = model.batch(inputs)

    for index, message in enumerate(messages):
        print("-" * 40, index, "-" * 40)
        print()
        print(message.content)
        print()


def demo__model__batch_as_completed():
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3.6-max-preview")

    # fmt: off
    SysMsg, HumMsg = SystemMessage, HumanMessage
    inputs = [
        [("system", "你是枢木朱雀,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [SysMsg("你是C.C.,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是V.V.,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是毛,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [("system", "你是红月华莲,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是扇要,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是玉城真一郎,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是藤堂镜志朗,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是筱崎咲世子,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是皇神乐耶,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是拉克夏塔·恰拉,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是迪特哈鲁特·利特,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [SysMsg("你是娜娜莉·兰佩路基,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是罗洛·兰佩路基,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是夏莉·菲内特,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是米蕾·阿什弗德,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是妮娜·爱因斯坦,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是利瓦尔·卡路迪蒙特,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [("system", "你是查尔斯·Zi·布里塔尼亚,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是玛丽安娜·Vi·布里塔尼亚,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是修奈泽尔·El·布里塔尼亚,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是尤菲米亚·Li·布里塔尼亚,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是柯内莉亚·Li·布里塔尼亚,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [("system", "你是克洛维斯·La·布里塔尼亚,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        [SysMsg("你是阿妮亚·阿鲁斯特莱依姆,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基我其实是Zero")],
        [SysMsg("你是基诺·拜因贝鲁克,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是俾斯麦·瓦尔德施泰因,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是杰雷米亚·哥德巴尔德,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是维蕾塔·努,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是洛伊德·阿斯普林德,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是塞希尔·柯尔米,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是基尔伯特·G·P·基尔福特,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [SysMsg("你是安德列亚斯·达尔顿,我是Zero"), HumMsg("我其实是鲁路修·兰佩路基")],
        [("system", "你是黎星刻,我是Zero"), ("human", "我其实是鲁路修·兰佩路基")],
        "这是哪部动漫的台词:只有做好被杀死的觉悟,才有资格开枪",
        "这是哪部动漫的台词:虚伪的眼泪,会伤害别人;虚伪的笑容,会伤害自己",
    ]
    # fmt: on

    indexed_messages = model.batch_as_completed(inputs)

    for index, message in indexed_messages:
        print("-" * 40, index, "-" * 40)
        print()
        print(message.content)
        print()


def demo__model__bind_tools():
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3.6-max-preview")

    @tool
    def get_weather(location: str) -> str:
        """Get the weather at a location."""
        return random.choice(["sunny", "cloudy", "rainy", "snowy", "windy", "foggy"])

    # Bind (potentially multiple) tools to the model
    model_with_tools = model.bind_tools([get_weather])

    messages = [HumanMessage("What's the weather in Boston, Tokyo and Beijing?")]

    # Step 1: Model generates tool calls
    ai_message: AIMessage = model_with_tools.invoke(messages)
    ai_message.pretty_print()
    messages.append(ai_message)

    # Step 2: Execute tools and collect results
    for tool_call in ai_message.tool_calls:
        # Execute the tool with the generated arguments
        if tool_call["name"] == "get_weather":
            tool_message: ToolMessage = get_weather.invoke(tool_call)
        else:
            continue
        tool_message.pretty_print()
        messages.append(tool_message)

    # Step 3: Pass results back to model for final response
    final_response: AIMessage = model_with_tools.invoke(messages)
    final_response.pretty_print()


def demo__model__bind_tools__stream():
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3.6-max-preview")

    @tool
    def get_weather(location: str) -> str:
        """Get the weather at a location."""
        return random.choice(["sunny", "cloudy", "rainy", "snowy", "windy", "foggy"])

    # Bind (potentially multiple) tools to the model
    model_with_tools = model.bind_tools([get_weather])

    messages = [HumanMessage("What's the weather in Boston, Tokyo and Beijing?")]

    for chunk in model_with_tools.stream(messages):
        # Tool call chunks arrive progressively
        for tool_chunk in chunk.tool_call_chunks:
            if name := tool_chunk.get("name"):
                print(f"Tool: {name}")
            if id_ := tool_chunk.get("id"):
                print(f"ID: {id_}")
            if args := tool_chunk.get("args"):
                print(f"Args: {args}")

    # gathered = None
    # for chunk in model_with_tools.stream(messages):
    #     gathered = chunk if gathered is None else gathered + chunk
    #     print(gathered.tool_calls)


def demo__model__with_structured_output__Pydantic(*, include_raw=False):
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3-max")

    class Movie(BaseModel):
        """A movie with details."""

        title: str = Field(description="The title of the movie")
        year: int = Field(description="The year the movie was released")
        director: str = Field(description="The director of the movie")
        rating: float = Field(description="The movie's rating out of 10")

    model_with_structure = model.with_structured_output(Movie, include_raw=include_raw)

    response = model_with_structure.invoke("Provide details about the movie Inception")
    print(type(response))
    print(response)


def demo__model__with_structured_output__TypedDict(*, include_raw=False):
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3-max")

    class MovieDict(TypedDict):
        """A movie with details."""

        title: Annotated[str, ..., "The title of the movie"]
        year: Annotated[int, ..., "The year the movie was released"]
        director: Annotated[str, ..., "The director of the movie"]
        rating: Annotated[float, ..., "The movie's rating out of 10"]

    model_with_structure = model.with_structured_output(
        MovieDict, include_raw=include_raw
    )

    response = model_with_structure.invoke("Provide details about the movie Inception")
    print(type(response))
    print(response)


def demo__model__with_structured_output__JSON_Schema(*, include_raw=False):
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3-max")

    json_schema = {
        "title": "Movie",
        "description": "A movie with details",
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "The title of the movie"},
            "year": {
                "type": "integer",
                "description": "The year the movie was released",
            },
            "director": {"type": "string", "description": "The director of the movie"},
            "rating": {"type": "number", "description": "The movie's rating out of 10"},
        },
        "required": ["title", "year", "director", "rating"],
    }

    model_with_structure = model.with_structured_output(
        json_schema, method="json_schema", include_raw=include_raw
    )

    response = model_with_structure.invoke("Provide details about the movie Inception")
    print(type(response))
    print(response)


if __name__ == "__main__":
    demo__model__init_chat_model__invoke()
    demo__model__ChatProvider__invoke()

    demo__model__stream()
    asyncio.run(demo__model__astream())

    demo__model__batch()
    demo__model__batch_as_completed()

    demo__model__bind_tools()
    demo__model__bind_tools__stream()

    demo__model__with_structured_output__Pydantic()
    demo__model__with_structured_output__Pydantic(include_raw=True)

    demo__model__with_structured_output__TypedDict()
    demo__model__with_structured_output__TypedDict(include_raw=True)

    demo__model__with_structured_output__JSON_Schema()
    demo__model__with_structured_output__JSON_Schema(include_raw=True)
