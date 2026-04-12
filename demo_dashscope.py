"""

``` Shell
pip install dashscope

pip install python-dotenv
```

"""

import asyncio
import dashscope
import inspect
import json
import os

from dotenv import load_dotenv

load_dotenv()

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


def print_func_name(frame):
    print()
    print("-" * 50, frame.f_code.co_name, "-" * 50)
    print()


def demo_Generation_text():
    print_func_name(inspect.currentframe())

    messages = [
        {"role": "system", "content": "我是三体人,你是叶文洁"},
        {"role": "user", "content": "世界属于三体"},
    ]

    response = dashscope.Generation.call(
        messages=messages,
        # result_format="text",  # it's default to qwen-plus
        model="qwen-max",
        temperature=0.0,
    )

    # print(json.dumps(response, indent=4, ensure_ascii=False))
    print(response.output.text)


def demo_Generation_text_stream():
    print_func_name(inspect.currentframe())

    messages = [
        {"role": "system", "content": "我是三体人,你是王淼"},
        {"role": "user", "content": "世界属于三体"},
    ]

    responses = dashscope.Generation.call(
        messages=messages,
        # result_format="text",  # it's default to qwen-plus
        stream=True,
        incremental_output=True,
        model="qwen-max",
        temperature=0.0,
    )

    for response in responses:
        # print(json.dumps(response, indent=4, ensure_ascii=False))
        print(response.output.text, end="", flush=True)
    print()


async def demo_AioGeneration_text():
    print_func_name(inspect.currentframe())

    messages = [
        {"role": "system", "content": "我是三体人,你是罗辑"},
        {"role": "user", "content": "世界属于三体"},
    ]

    response = await dashscope.AioGeneration.call(
        messages=messages,
        # result_format="text",  # it's default to qwen-plus
        model="qwen-max",
        temperature=0.0,
    )

    # print(json.dumps(response, indent=4, ensure_ascii=False))
    print(response.output.text)


def demo_Generation_message():
    print_func_name(inspect.currentframe())

    messages = [
        {"role": "system", "content": "我是三体人,你是章北海"},
        {"role": "user", "content": "世界属于三体"},
    ]

    response = dashscope.Generation.call(
        messages=messages,
        result_format="message",
        model="qwen-max",
        temperature=0.0,
    )

    # print(json.dumps(response, indent=4, ensure_ascii=False))
    print(response.output.choices[0].message.content)


def demo_Generation_message_stream():
    print_func_name(inspect.currentframe())

    messages = [
        {"role": "system", "content": "我是三体人,你是云天明"},
        {"role": "user", "content": "世界属于三体"},
    ]

    responses = dashscope.Generation.call(
        messages=messages,
        result_format="message",
        stream=True,
        incremental_output=True,
        model="qwen-max",
        temperature=0.0,
    )

    for response in responses:
        # print(json.dumps(response, indent=4, ensure_ascii=False))
        print(response.output.choices[0].message.content, end="", flush=True)
    print()


async def demo_AioGeneration_message():
    print_func_name(inspect.currentframe())

    messages = [
        {"role": "system", "content": "我是三体人,你是程心"},
        {"role": "user", "content": "世界属于三体"},
    ]

    response = await dashscope.AioGeneration.call(
        messages=messages,
        result_format="message",
        model="qwen-max",
        temperature=0.0,
    )

    # print(json.dumps(response, indent=4, ensure_ascii=False))
    print(response.output.choices[0].message.content)


def demo_Generation_tools():
    print_func_name(inspect.currentframe())

    messages = [{"role": "user", "content": "杭州天气怎么样"}]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "当你想知道现在的时间时非常有用。",
                "parameters": {},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "当你想查询指定城市的天气时非常有用。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                        }
                    },
                },
                "required": ["location"],
            },
        },
    ]

    response = dashscope.Generation.call(
        messages=messages,
        # result_format="message",  # not work with function calling
        tools=tools,
        model="qwen-plus",
    )

    # print(json.dumps(response, indent=4, ensure_ascii=False))
    print(
        json.dumps(
            response.output.choices[0].message.tool_calls,
            indent=4,
            ensure_ascii=False,
        )
    )


def demo_MultiModalConversation_image():
    print_func_name(inspect.currentframe())

    messages = [
        {
            "role": "user",
            "content": [
                {"image": "https://jpeg.org/images/jpeg-home.jpg"},
                {"image": "https://jpeg.org/images/jpeg2000-home.jpg"},
                {"image": "https://jpeg.org/images/jpegai-home.jpg"},
                {"text": "描述图片内容"},
            ],
        },
    ]

    response = dashscope.MultiModalConversation.call(
        messages=messages,
        model="qwen3.5-omni-plus",
    )

    # print(json.dumps(response, indent=4, ensure_ascii=False))
    print(response.output.choices[0].message.content[0]["text"])


def demo_MultiModalConversation_image_stream():
    print_func_name(inspect.currentframe())

    messages = [
        {
            "role": "user",
            "content": [
                {"image": "https://jpeg.org/images/jpeg-home.jpg"},
                {"image": "https://jpeg.org/images/jpeg2000-home.jpg"},
                {"image": "https://jpeg.org/images/jpegai-home.jpg"},
                {"text": "描述图片内容"},
            ],
        },
    ]

    responses = dashscope.MultiModalConversation.call(
        messages=messages,
        stream=True,
        incremental_output=True,
        model="qwen3.5-omni-plus",
    )

    for response in responses:
        # print(json.dumps(response, indent=4, ensure_ascii=False))
        content = response.output.choices[0].message.content
        if content:
            print(content[0]["text"], end="", flush=True)
    print()


def demo_MultiModalConversation_video():
    print_func_name(inspect.currentframe())

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "video": [
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/xzsgiz/football1.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/tdescd/football2.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/zefdja/football3.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/aedbqh/football4.jpg",
                    ],
                    "fps": 2,
                },
                {"text": "描述视频内容"},
            ],
        }
    ]

    response = dashscope.MultiModalConversation.call(
        messages=messages,
        model="qwen3.5-omni-plus",
    )

    # print(json.dumps(response, indent=4, ensure_ascii=False))
    print(response["output"]["choices"][0]["message"].content[0]["text"])


def demo_MultiModalConversation_video_stream():
    print_func_name(inspect.currentframe())

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "video": [
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/xzsgiz/football1.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/tdescd/football2.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/zefdja/football3.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/aedbqh/football4.jpg",
                    ],
                    "fps": 2,
                },
                {"text": "描述视频内容"},
            ],
        }
    ]

    responses = dashscope.MultiModalConversation.call(
        messages=messages,
        stream=True,
        incremental_output=True,
        model="qwen3.5-omni-plus",
    )

    for response in responses:
        # print(json.dumps(response, indent=4, ensure_ascii=False))
        content = response.output.choices[0].message.content
        if content:
            print(content[0]["text"], end="", flush=True)
    print()


if __name__ == "__main__":
    demo_Generation_text()
    demo_Generation_text_stream()
    asyncio.run(demo_AioGeneration_text())

    demo_Generation_message()
    demo_Generation_message_stream()
    asyncio.run(demo_AioGeneration_message())

    demo_Generation_tools()

    demo_MultiModalConversation_image()
    demo_MultiModalConversation_image_stream()

    demo_MultiModalConversation_video()
    demo_MultiModalConversation_video_stream()
