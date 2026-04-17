"""

``` Shell
pip install langchain
pip install langchain-openai

pip install python-dotenv
```

"""

import inspect
import os

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model, after_model
from langchain.agents.middleware import SummarizationMiddleware
from langchain.messages import RemoveMessage
from langchain.tools import tool, ToolRuntime

from langchain_core.runnables import RunnableConfig

from langchain_openai import ChatOpenAI

from dataclasses import dataclass
from dotenv import load_dotenv

from typing import Any

load_dotenv()


def print_func_name(frame):
    print()
    print("-" * 50, frame.f_code.co_name, "-" * 50)
    print()


def print_horizontal_divider():
    print()
    print("-" * 100)
    print()


def print_result_messages(result, *, divider: bool = False):
    for message in result["messages"]:
        message.pretty_print()

    if divider:
        print_horizontal_divider()


def create_qwen_model(model: str):
    return ChatOpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        model=model,
        temperature=0,
    )


def demo__agent__tool__access_context():
    print_func_name(inspect.currentframe())

    USER_DATABASE = {
        "user123": {
            "name": "Alice Johnson",
            "account_type": "Premium",
            "balance": 5000,
            "email": "alice@example.com",
        },
        "user456": {
            "name": "Bob Smith",
            "account_type": "Standard",
            "balance": 1200,
            "email": "bob@example.com",
        },
    }

    @dataclass
    class UserContext:
        user_id: str

    @tool
    def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
        """Get the current user's account information."""
        user_id = runtime.context.user_id

        if user_id in USER_DATABASE:
            user = USER_DATABASE[user_id]
            return f"Account holder: {user['name']}\nType: {user['account_type']}\nBalance: ${user['balance']}"
        return "User not found"

    model = create_qwen_model("qwen3.6-max-preview")

    agent = create_agent(
        model,
        tools=[get_account_info],
        context_schema=UserContext,
        system_prompt="You are a financial assistant.",
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What's my current balance?"}]},
        context=UserContext(user_id="user123"),
    )
    print_result_messages(result)


def demo__agent__tool__access_store():
    print_func_name(inspect.currentframe())

    # Access memory
    @tool
    def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
        """Look up user info."""
        store = runtime.store
        user_info = store.get(("users",), user_id)
        return str(user_info.value) if user_info else "Unknown user"

    # Update memory
    @tool
    def save_user_info(
        user_id: str, user_info: dict[str, Any], runtime: ToolRuntime
    ) -> str:
        """Save user info."""
        store = runtime.store
        store.put(("users",), user_id, user_info)
        return "Successfully saved user info."

    model = create_qwen_model("qwen3.6-max-preview")

    store = InMemoryStore()
    agent = create_agent(model, tools=[get_user_info, save_user_info], store=store)

    # First session: save user info
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Save the following user: userid: abc123, name: Foo, age: 25, email: foo@langchain.dev",
                }
            ]
        }
    )
    print_result_messages(result, divider=True)

    # Second session: get user info
    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "Get user info for user with id 'abc123'"}
            ]
        }
    )
    print_result_messages(result)


def demo__agent__memory__trim_messages():
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3.6-max-preview")

    @before_model
    def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """Keep only the last few messages to fit context window."""
        messages = state["messages"]

        if len(messages) <= 3:
            return None  # No changes needed

        first_msg = messages[0]
        recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
        new_messages = [first_msg] + recent_messages

        return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *new_messages]}

    agent = create_agent(
        model,
        middleware=[trim_messages],
        checkpointer=InMemorySaver(),
    )

    config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    result = agent.invoke({"messages": "hi, my name is bob"}, config)
    print_result_messages(result, divider=True)

    result = agent.invoke({"messages": "write a short poem about cats"}, config)
    print_result_messages(result, divider=True)

    result = agent.invoke({"messages": "now do the same but for dogs"}, config)
    print_result_messages(result, divider=True)

    result = agent.invoke({"messages": "what's my name?"}, config)
    print_result_messages(result)


def demo__agent__memory__delete_messages():
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3.6-max-preview")

    @after_model
    def delete_old_messages(state: AgentState, runtime: Runtime) -> dict | None:
        """Remove old messages to keep conversation manageable."""
        messages = state["messages"]
        if len(messages) > 2:
            # remove the earliest two messages
            return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
        return None

    agent = create_agent(
        model,
        system_prompt="Please be concise and to the point.",
        middleware=[delete_old_messages],
        checkpointer=InMemorySaver(),
    )

    config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    for event in agent.stream(
        {"messages": [{"role": "user", "content": "hi! I'm bob"}]},
        config,
        stream_mode="values",
    ):
        print([(message.type, message.content) for message in event["messages"]])

    print_horizontal_divider()

    for event in agent.stream(
        {"messages": [{"role": "user", "content": "what's my name?"}]},
        config,
        stream_mode="values",
    ):
        print([(message.type, message.content) for message in event["messages"]])


def demo__agent__memory__summarize_messages():
    print_func_name(inspect.currentframe())

    model = create_qwen_model("qwen3.6-max-preview")

    agent = create_agent(
        model,
        middleware=[
            SummarizationMiddleware(
                model=model,
                trigger=("tokens", 4000),
                keep=("messages", 6),
            )
        ],
        checkpointer=InMemorySaver(),
    )

    config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    result = agent.invoke({"messages": "hi, my name is bob"}, config)
    print_result_messages(result, divider=True)

    result = agent.invoke({"messages": "write a long poem about cats"}, config)
    print_result_messages(result, divider=True)

    result = agent.invoke({"messages": "now do the same but for dogs"}, config)
    print_result_messages(result, divider=True)

    result = agent.invoke({"messages": "now do the same but for cows"}, config)
    print_result_messages(result, divider=True)

    result = agent.invoke({"messages": "now do the same but for pigs"}, config)
    print_result_messages(result, divider=True)

    result = agent.invoke({"messages": "what's my name?"}, config)
    print_result_messages(result)


if __name__ == "__main__":
    demo__agent__tool__access_context()
    demo__agent__tool__access_store()

    demo__agent__memory__trim_messages()
    demo__agent__memory__delete_messages()
    demo__agent__memory__summarize_messages()
