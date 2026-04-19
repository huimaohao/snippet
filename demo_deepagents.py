"""

``` Shell
pip install deepagents

pip install langchain-openai
pip install tavily-python
pip install python-dotenv
```

"""

import inspect
import os
import pprint

from deepagents import create_deep_agent, DeepAgentState

from langchain_core.utils.uuid import uuid7

from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from dataclasses import dataclass
from dotenv import load_dotenv
from tavily import TavilyClient
from typing import Literal

load_dotenv()

model = init_chat_model(
    model="qwen3.7-max",
    model_provider="openai",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    temperature=0,
)


def print_title(title, width=120, bgn="", end=""):
    print(bgn, end="")
    sub = width - len(title)
    sub_div_2 = sub // 2
    sub_mod_2 = sub % 2
    print("-" * (sub_div_2 - 1), title, "-" * (sub_div_2 + sub_mod_2 - 1))
    print(end, end="")


def write_graph(graph, fname):
    with open(f"{fname}.png", "wb") as f:
        f.write(graph.get_graph(xray=True).draw_mermaid_png())


def demo__overview():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    def get_weather(city: str) -> str:
        """Get weather for a given city."""
        return f"It's always sunny in {city}!"

    agent = create_deep_agent(
        model=model,
        tools=[get_weather],
        system_prompt="You are a helpful assistant",
    )
    write_graph(agent, func_name)

    # Run the agent
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
    )
    for message in result["messages"]:
        message.pretty_print()


def demo__quickstart():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
    ):
        """Run a web search"""
        return tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )

    # System prompt to steer the agent to be an expert researcher
    research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

    You have access to an internet search tool as your primary means of gathering information.

    ## `internet_search`

    Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
    """

    agent = create_deep_agent(
        model=model,
        tools=[internet_search],
        system_prompt=research_instructions,
    )
    write_graph(agent, func_name)

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What is langgraph?"}]}
    )
    for message in result["messages"]:
        message.pretty_print()


def demo__context_schema():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    @dataclass
    class Context:
        user_id: str
        api_key: str

    @tool
    def fetch_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
        """Fetch data for the current user."""
        user_id = runtime.context.user_id
        return f"Data for user {user_id}: {query}"

    agent = create_deep_agent(
        model=model,
        tools=[fetch_user_data],
        context_schema=Context,
    )
    write_graph(agent, func_name)

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Get my recent activity"}]},
        context=Context(user_id="user-123", api_key="sk-..."),
    )
    for message in result["messages"]:
        message.pretty_print()


def demo__state_schema():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    class ResearchState(DeepAgentState):
        page_url: str
        file_urls: list[str]

    @tool
    def cite_page(runtime: ToolRuntime) -> str:
        """Return the current page URL."""
        return runtime.state["page_url"]

    agent = create_deep_agent(
        model=model,
        tools=[cite_page],
        state_schema=ResearchState,
    )
    write_graph(agent, func_name)

    result = agent.invoke(
        {
            "messages": [{"role": "user", "content": "Cite the current page"}],
            "page_url": "https://example.com/report",
            "file_urls": [],
        }
    )
    for message in result["messages"]:
        message.pretty_print()


def demo__subagent():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
    ):
        """Run a web search"""
        return tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )

    research_subagent = {
        "name": "research-agent",
        "description": "Used to research more in depth questions",
        "system_prompt": "You are a great researcher",
        "tools": [internet_search],
        "model": model,  # Optional override, defaults to main agent model
    }
    subagents = [research_subagent]

    agent = create_deep_agent(
        model=model,
        subagents=subagents,
    )
    write_graph(agent, func_name)

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What is langgraph?"}]}
    )
    for message in result["messages"]:
        message.pretty_print()


def demo__human_in_the_loop():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    @tool
    def remove_file(path: str) -> str:
        """Delete a file from the filesystem."""
        return f"Deleted {path}"

    @tool
    def fetch_file(path: str) -> str:
        """Read a file from the filesystem."""
        return f"Contents of {path}"

    @tool
    def notify_email(to: str, subject: str, body: str) -> str:
        """Send an email."""
        return f"Sent email to {to}"

    # Checkpointer is REQUIRED for human-in-the-loop
    checkpointer = MemorySaver()

    agent = create_deep_agent(
        model=model,
        tools=[remove_file, fetch_file, notify_email],
        interrupt_on={
            "remove_file": True,  # Default: approve, edit, reject, respond
            "fetch_file": False,  # No interrupts needed
            "notify_email": {"allowed_decisions": ["approve", "reject", "edit"]},
        },
        checkpointer=checkpointer,  # Required!
    )
    write_graph(agent, func_name)

    # Create config with thread_id for state persistence
    config = {"configurable": {"thread_id": str(uuid7())}}

    last_messages_length = 0

    # Invoke the agent
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Create a file named temp.txt"}]},
        config=config,
        version="v2",
    )
    for message in result.value["messages"][last_messages_length:]:
        message.pretty_print()
    last_messages_length = len(result.value["messages"])
    for interrupt in result.interrupts:
        pprint.pprint(interrupt)

    print("-" * 100)

    # Invoke the agent
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Delete the file temp.txt"}]},
        config=config,
        version="v2",
    )
    for message in result.value["messages"][last_messages_length:]:
        message.pretty_print()
    last_messages_length = len(result.value["messages"])
    for interrupt in result.interrupts:
        pprint.pprint(interrupt)

    print("-" * 100)

    # Get user decisions (one per action_request, in order)
    decisions = [
        {
            "type": "reject",
            "message": "User rejected deleting temp.txt. Do not retry deletion.",
        }
    ]
    # Resume execution with decisions
    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,  # Must use the same config!
        version="v2",
    )
    for message in result.value["messages"][last_messages_length:]:
        message.pretty_print()
    last_messages_length = len(result.value["messages"])
    for interrupt in result.interrupts:
        pprint.pprint(interrupt)

    # Invoke the agent
    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "Notify admin@example.com anything"}
            ]
        },
        config=config,
        version="v2",
    )
    for message in result.value["messages"][last_messages_length:]:
        message.pretty_print()
    last_messages_length = len(result.value["messages"])
    for interrupt in result.interrupts:
        pprint.pprint(interrupt)

    # Get user decisions (one per action_request, in order)
    assert result.interrupts[0].value["action_requests"][0]["name"] == "notify_email"
    decisions = [
        {
            "type": "edit",
            "edited_action": {
                "name": "notify_email",  # Must include the tool name
                "args": {"to": "team@company.com", "subject": "...", "body": "..."},
            },
        }
    ]
    # Resume execution with decisions
    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,  # Must use the same config!
        version="v2",
    )
    for message in result.value["messages"][last_messages_length:]:
        message.pretty_print()
    last_messages_length = len(result.value["messages"])
    for interrupt in result.interrupts:
        pprint.pprint(interrupt)


if __name__ == "__main__":
    demo__overview()
    demo__quickstart()

    demo__context_schema()
    demo__state_schema()

    demo__subagent()

    demo__human_in_the_loop()
