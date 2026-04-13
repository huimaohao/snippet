"""

``` Shell
pip install ollama

# required by ollama
ollama list
ollama pull gemma4:26b
ollama pull embeddinggemma
```

"""

import ollama
import asyncio
import inspect


def print_func_name(frame):
    print()
    print("-" * 50, frame.f_code.co_name, "-" * 50)
    print()


def demo_chat():
    print_func_name(inspect.currentframe())

    response: ollama.ChatResponse = ollama.chat(
        model="gemma4:26b",
        messages=[
            {"role": "system", "content": "中文对话,我是冈部伦太郎,你是牧濑红莉栖"},
            {"role": "user", "content": "EL PSY KONGROO"},
        ],
        options={"temperature": 0},
    )

    print(response.message.content)


def demo_chat_stream():
    print_func_name(inspect.currentframe())

    stream = ollama.chat(
        model="gemma4:26b",
        messages=[
            {"role": "system", "content": "中文对话,我是冈部伦太郎,你是椎名真由理"},
            {"role": "user", "content": "EL PSY KONGROO"},
        ],
        options={"temperature": 0},
        stream=True,
    )

    chunk: ollama.ChatResponse
    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)
    print()


def demo_Client_chat():
    print_func_name(inspect.currentframe())

    response: ollama.ChatResponse = ollama.Client().chat(
        model="gemma4:26b",
        messages=[
            {"role": "system", "content": "中文对话,我是冈部伦太郎,你是阿万音铃羽"},
            {"role": "user", "content": "EL PSY KONGROO"},
        ],
        options={"temperature": 0},
    )

    print(response.message.content)


def demo_Client_chat_stream():
    print_func_name(inspect.currentframe())

    stream = ollama.Client().chat(
        model="gemma4:26b",
        messages=[
            {"role": "system", "content": "中文对话,我是冈部伦太郎,你是漆原琉华"},
            {"role": "user", "content": "EL PSY KONGROO"},
        ],
        options={"temperature": 0},
        stream=True,
    )

    chunk: ollama.ChatResponse
    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)
    print()


async def demo_AsyncClient_chat():
    print_func_name(inspect.currentframe())

    response: ollama.ChatResponse = await ollama.AsyncClient().chat(
        model="gemma4:26b",
        messages=[
            {"role": "system", "content": "中文对话,我是冈部伦太郎,你是菲利斯·喵喵"},
            {"role": "user", "content": "EL PSY KONGROO"},
        ],
        options={"temperature": 0},
    )

    print(response.message.content)


async def demo_AsyncClient_chat_stream():
    print_func_name(inspect.currentframe())

    stream = ollama.AsyncClient().chat(
        model="gemma4:26b",
        messages=[
            {"role": "system", "content": "中文对话,我是冈部伦太郎,你是桥田至"},
            {"role": "user", "content": "EL PSY KONGROO"},
        ],
        options={"temperature": 0},
        stream=True,
    )

    chunk: ollama.ChatResponse
    async for chunk in await stream:
        print(chunk["message"]["content"], end="", flush=True)
    print()


def demo_generate():
    print_func_name(inspect.currentframe())

    response: ollama.GenerateResponse = ollama.generate(
        model="gemma4:26b",
        system="中文对话,我是冈部伦太郎,你是桐生萌郁",
        prompt="EL PSY KONGROO",
        options={"temperature": 0},
    )

    print(response.response)


def demo_generate_stream():
    print_func_name(inspect.currentframe())

    stream = ollama.generate(
        model="gemma4:26b",
        system="中文对话,我是冈部伦太郎,你是比屋定真帆",
        prompt="EL PSY KONGROO",
        options={"temperature": 0},
        stream=True,
    )

    chunk: ollama.GenerateResponse
    for chunk in stream:
        print(chunk["response"], end="", flush=True)
    print()


def demo_embed():
    print_func_name(inspect.currentframe())

    response: ollama.EmbedResponse = ollama.embed(
        model="embeddinggemma",
        input="我是冈部伦太郎",
    )

    embedding = response.embeddings[0]
    # print(embedding)
    print(len(embedding), embedding[:5] + ["..."])


def demo_embed_batch():
    print_func_name(inspect.currentframe())

    response: ollama.EmbedResponse = ollama.embed(
        model="embeddinggemma",
        input=[
            "我是冈部伦太郎",
            "我是凤凰院凶真",
        ],
    )

    embeddings = response["embeddings"]
    # print(embeddings)
    for embedding in embeddings:
        # print(embedding)
        print(len(embedding), embedding[:5] + ["..."])


def demo_embeddings():
    print_func_name(inspect.currentframe())

    response: ollama.EmbeddingsResponse = ollama.embeddings(
        model="embeddinggemma",
        prompt="我是凤凰院凶真",
    )

    embedding = response.embedding
    # print(embedding)
    print(len(embedding), embedding[:5] + ["..."])


if __name__ == "__main__":
    demo_chat()
    demo_chat_stream()

    demo_Client_chat()
    demo_Client_chat_stream()

    asyncio.run(demo_AsyncClient_chat())
    asyncio.run(demo_AsyncClient_chat_stream())

    demo_generate()
    demo_generate_stream()

    ##################################################

    demo_embed()
    demo_embed_batch()

    demo_embeddings()
