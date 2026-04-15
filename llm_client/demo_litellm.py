"""

``` Shell
pip install litellm
```

"""

import asyncio
import inspect
import json
import litellm

from dotenv import load_dotenv

load_dotenv()


def print_func_name(frame):
    print()
    print("-" * 50, frame.f_code.co_name, "-" * 50)
    print()


def demo__get_supported_openai_params():
    print_func_name(inspect.currentframe())

    response = litellm.get_supported_openai_params(
        model="qwen3.6-plus",
        custom_llm_provider="dashscope",
    )
    print("dashscope/qwen3.6-plus")
    print(response)
    print()

    response = litellm.get_supported_openai_params(
        model="qwen3.6:27b",
        custom_llm_provider="ollama",
    )
    print("ollama/qwen3.6:27b")
    print(response)
    print()

    response = litellm.get_supported_openai_params(
        model="qwen3-embedding",
        custom_llm_provider="ollama",
    )
    print("ollama/qwen3-embedding")
    print(response)
    print()


def demo__responses():
    print_func_name(inspect.currentframe())

    response = litellm.responses(
        model="dashscope/qwen3.6-plus",
        instructions="我是黑桐干也,你是两仪式",
        input="...",
    )

    # print(response.model_dump_json(indent=4))
    # print(response.output[0].content[0].text)
    print(response.output_text)


def demo__responses__stream():
    print_func_name(inspect.currentframe())

    response = litellm.responses(
        model="dashscope/qwen3.6-plus",
        instructions="我是黑桐干也,你是两仪织",
        input="...",
        stream=True,
    )

    for event in response:
        # print(event.model_dump_json(indent=4))
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    print()


def demo__completion():
    print_func_name(inspect.currentframe())

    response = litellm.completion(
        model="dashscope/qwen3.6-plus",
        messages=[
            {"role": "system", "content": "我是黑桐干也,你是根源式"},
            {"role": "user", "content": "..."},
        ],
    )

    # print(response.to_json(indent=4))
    print(response.choices[0].message.content)


def demo__text_completion():
    print_func_name(inspect.currentframe())

    response = litellm.text_completion(
        model="ollama/qwen3.6:27b",
        prompt="直死之魔眼",
        timeout=3600,
    )

    # print(response.model_dump_json(indent=4))
    print(response.choices[0].text)


def demo__embedding():
    print_func_name(inspect.currentframe())

    response = litellm.embedding(
        model="ollama/qwen3-embedding",
        input=["两仪式", "两仪织", "根源式"],
    )

    response_json = response.json()
    # print(json.dumps(response_json, indent=4))
    for data in response_json["data"]:
        embedding = data["embedding"]
        print(len(embedding), embedding[:5] + ["..."])


async def demo__aembedding():
    print_func_name(inspect.currentframe())

    response = await litellm.aembedding(
        model="ollama/qwen3-embedding",
        input=["杀人考察（前）", "杀人考察（后）"],
    )

    response_json = response.json()
    # print(json.dumps(response_json, indent=4))
    for data in response_json["data"]:
        embedding = data["embedding"]
        print(len(embedding), embedding[:10] + ["..."])


if __name__ == "__main__":
    demo__get_supported_openai_params()

    demo__responses()
    demo__responses__stream()

    demo__completion()

    demo__text_completion()

    demo__embedding()
    asyncio.run(demo__aembedding())
