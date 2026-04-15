"""

``` Shell
pip install openai
pip install openai[aiohttp]

pip install python-dotenv
```

"""

import asyncio
import base64
import inspect
import os
import urllib

from openai import OpenAI, AsyncOpenAI, DefaultAioHttpClient
from openai.types.responses.response import Response
from openai.types.chat.chat_completion import ChatCompletion

from dotenv import load_dotenv

load_dotenv()

base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = os.environ.get("DASHSCOPE_API_KEY")
model = "qwen3.6-plus"
image_url = "https://jpeg.org/images/jpeg-home.jpg"


def print_func_name(frame):
    print()
    print("-" * 50, frame.f_code.co_name, "-" * 50)
    print()


def demo_OpenAI_responses():
    print_func_name(inspect.currentframe())

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    response: Response = client.responses.create(
        model=model,
        instructions="我是佐藤和真,你是阿克娅",
        input="头好痛!这是哪?我是谁?你又是谁?",
    )

    print(response.output_text)


def demo_OpenAI_responses_stream():
    print_func_name(inspect.currentframe())

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    stream = client.responses.create(
        model=model,
        instructions="我是佐藤和真,你是惠惠",
        input="头好痛!这是哪?我是谁?你又是谁?",
        stream=True,
    )

    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    print()


async def demo_AsyncOpenAI_responses():
    print_func_name(inspect.currentframe())

    async with AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
    ) as client:
        response: Response = await client.responses.create(
            model=model,
            instructions="我是佐藤和真,你是达克妮斯",
            input="头好痛!这是哪?我是谁?你又是谁?",
        )

        print(response.output_text)


async def demo_AsyncOpenAI_responses_stream():
    print_func_name(inspect.currentframe())

    async with AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
    ) as client:
        stream = await client.responses.create(
            model=model,
            instructions="我是佐藤和真,你是悠悠",
            input="头好痛!这是哪?我是谁?你又是谁?",
            stream=True,
        )

        async for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
        print()


async def demo_AsyncOpenAI_responses_aiohttp():
    print_func_name(inspect.currentframe())

    async with AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
        http_client=DefaultAioHttpClient(),
    ) as client:
        response: Response = await client.responses.create(
            model=model,
            instructions="我是佐藤和真,你是克里斯",
            input="头好痛!这是哪?我是谁?你又是谁?",
        )

        print(response.output_text)


def demo_OpenAI_chat_completions():
    print_func_name(inspect.currentframe())

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    completion: ChatCompletion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "我是齐木楠雄,你是燃堂力",
            },
            {
                "role": "user",
                "content": "头好痛!这是哪?我是谁?你又是谁?",
            },
        ],
    )

    print(completion.choices[0].message.content)


def demo_OpenAI_chat_completions_stream():
    print_func_name(inspect.currentframe())

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "我是齐木楠雄,你是海藤瞬",
            },
            {
                "role": "user",
                "content": "头好痛!这是哪?我是谁?你又是谁?",
            },
        ],
        stream=True,
    )

    for chunk in stream:
        if len(chunk.choices) and chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
    print()


async def demo_AsyncOpenAI_chat_completion():
    print_func_name(inspect.currentframe())

    async with AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
    ) as client:
        completion: ChatCompletion = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "我是齐木楠雄,你是灰吕杵志",
                },
                {
                    "role": "user",
                    "content": "头好痛!这是哪?我是谁?你又是谁?",
                },
            ],
        )

        print(completion.choices[0].message.content)


async def demo_AsyncOpenAI_chat_completion_stream():
    print_func_name(inspect.currentframe())

    async with AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
    ) as client:
        stream = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "我是齐木楠雄,你是鸟束零太",
                },
                {
                    "role": "user",
                    "content": "头好痛!这是哪?我是谁?你又是谁?",
                },
            ],
            stream=True,
        )

        async for chunk in stream:
            if len(chunk.choices) and chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        print()


async def demo_AsyncOpenAI_chat_completion_aiohttp():
    print_func_name(inspect.currentframe())

    async with AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
        http_client=DefaultAioHttpClient(),
    ) as client:
        completion: ChatCompletion = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "我是齐木楠雄,你是照桥心美",
                },
                {
                    "role": "user",
                    "content": "头好痛!这是哪?我是谁?你又是谁?",
                },
            ],
        )

        print(completion.choices[0].message.content)


def demo_OpenAI_responses_image_url():
    print_func_name(inspect.currentframe())

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    response: Response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "图中有什么",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"{image_url}",
                    },
                ],
            },  # type: ignore
        ],
    )

    print(response.output_text)


def demo_OpenAI_responses_image_data():
    print_func_name(inspect.currentframe())

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    with urllib.request.urlopen(image_url) as res:
        b64_image = base64.b64encode(res.read()).decode("utf-8")

    response: Response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "图中有什么",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{b64_image}",
                    },
                ],
            },  # type: ignore
        ],
    )

    print(response.output_text)


if __name__ == "__main__":
    demo_OpenAI_responses()
    demo_OpenAI_responses_stream()
    asyncio.run(demo_AsyncOpenAI_responses())
    asyncio.run(demo_AsyncOpenAI_responses_stream())
    asyncio.run(demo_AsyncOpenAI_responses_aiohttp())

    demo_OpenAI_chat_completions()
    demo_OpenAI_chat_completions_stream()
    asyncio.run(demo_AsyncOpenAI_chat_completion())
    asyncio.run(demo_AsyncOpenAI_chat_completion_stream())
    asyncio.run(demo_AsyncOpenAI_chat_completion_aiohttp())

    demo_OpenAI_responses_image_url()
    demo_OpenAI_responses_image_data()
