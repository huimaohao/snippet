"""

``` Shell
pip install langgraph

pip install langchain
pip install langchain-openai

pip install python-dotenv
```

"""

import inspect
import operator
import os
import pprint

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from langgraph.types import interrupt, Command, RetryPolicy, Send

from langchain_core.messages import BaseMessage

from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.messages import ToolCall
from langchain.tools import tool

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Annotated, List, Literal, TypedDict

load_dotenv()


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


def demo__hello_world():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    def mock_llm(state: MessagesState):
        return {"messages": [{"role": "ai", "content": "hello world"}]}

    graph = StateGraph(MessagesState)
    graph.add_node(mock_llm)
    graph.add_edge(START, "mock_llm")
    graph.add_edge("mock_llm", END)

    graph = graph.compile()
    write_graph(graph, func_name)

    result = graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})
    for message in result["messages"]:
        message.pretty_print()


def demo__agent__calculator__graph_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    # Step 1: Define tools and model

    model = init_chat_model(
        model="qwen3.6-max-preview",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Define tools
    @tool
    def multiply(a: int, b: int) -> int:
        """Multiply `a` and `b`.
        Args:
            a: First int
            b: Second int
        """
        return a * b

    @tool
    def add(a: int, b: int) -> int:
        """Adds `a` and `b`.
        Args:
            a: First int
            b: Second int
        """
        return a + b

    @tool
    def divide(a: int, b: int) -> float:
        """Divide `a` and `b`.
        Args:
            a: First int
            b: Second int
        """
        return a / b

    # Augment the LLM with tools
    tools = [add, multiply, divide]
    tools_by_name = {tool.name: tool for tool in tools}
    model_with_tools = model.bind_tools(tools)

    # Step 2: Define state

    class MessagesState(TypedDict):
        messages: Annotated[list[AnyMessage], operator.add]
        llm_calls: int

    # Step 3: Define model node

    def llm_call(state: dict):
        """LLM decides whether to call a tool or not"""
        return {
            "messages": [
                model_with_tools.invoke(
                    [
                        SystemMessage(
                            content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                        )
                    ]
                    + state["messages"]
                )
            ],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    # Step 4: Define tool node

    def tool_node(state: dict):
        """Performs the tool call"""
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(
                ToolMessage(content=observation, tool_call_id=tool_call["id"])
            )
        return {"messages": result}

    # Step 5: Define logic to determine whether to end

    # Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
    def should_continue(state: MessagesState) -> Literal["tool_node", END]:
        """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
        messages = state["messages"]
        last_message = messages[-1]

        # If the LLM makes a tool call, then perform an action
        if last_message.tool_calls:
            return "tool_node"

        # Otherwise, we stop (reply to the user)
        return END

    # Step 6: Build agent

    # Build workflow
    agent_builder = StateGraph(MessagesState)

    # Add nodes
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)

    # Add edges to connect nodes
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    agent_builder.add_edge("tool_node", "llm_call")

    # Compile the agent
    agent = agent_builder.compile()
    write_graph(agent, func_name)

    # Invoke
    print_title("agent.invoke()", 100, bgn="\n", end="\n")
    messages = [HumanMessage(content="Add 3 and 4.")]
    result = agent.invoke({"messages": messages})
    for message in result["messages"]:
        message.pretty_print()

    # Invoke
    print_title("agent.stream()", 100, bgn="\n", end="\n")
    messages = [HumanMessage(content="Add 3 and 4.")]
    for chunk in agent.stream({"messages": messages}, stream_mode="updates"):
        for key, val in chunk.items():
            print_title(key, 80)
            for message in val["messages"]:
                message.pretty_print()


def demo__agent__calculator__functional_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    # Step 1: Define tools and model

    model = init_chat_model(
        model="qwen3.6-max-preview",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Define tools
    @tool
    def multiply(a: int, b: int) -> int:
        """Multiply `a` and `b`.
        Args:
            a: First int
            b: Second int
        """
        return a * b

    @tool
    def add(a: int, b: int) -> int:
        """Adds `a` and `b`.
        Args:
            a: First int
            b: Second int
        """
        return a + b

    @tool
    def divide(a: int, b: int) -> float:
        """Divide `a` and `b`.
        Args:
            a: First int
            b: Second int
        """
        return a / b

    # Augment the LLM with tools
    tools = [add, multiply, divide]
    tools_by_name = {tool.name: tool for tool in tools}
    model_with_tools = model.bind_tools(tools)

    # Step 2: Define model node

    @task
    def call_llm(messages: list[BaseMessage]):
        """LLM decides whether to call a tool or not"""
        return model_with_tools.invoke(
            [
                SystemMessage(
                    content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                )
            ]
            + messages
        )

    # Step 3: Define tool node

    @task
    def call_tool(tool_call: ToolCall):
        """Performs the tool call"""
        tool = tools_by_name[tool_call["name"]]
        return tool.invoke(tool_call)

    # Step 4: Define agent

    @entrypoint()
    def agent(messages: list[BaseMessage]):
        model_response = call_llm(messages).result()

        while True:
            if not model_response.tool_calls:
                break

            # Execute tools
            tool_result_futures = [
                call_tool(tool_call) for tool_call in model_response.tool_calls
            ]
            tool_results = [fut.result() for fut in tool_result_futures]
            messages = add_messages(messages, [model_response, *tool_results])
            model_response = call_llm(messages).result()

        messages = add_messages(messages, model_response)
        return messages

    # Invoke
    print_title("agent.invoke()", 100, bgn="\n", end="\n")
    messages = [HumanMessage(content="Add 3 and 4.")]
    messages = agent.invoke(messages)
    for message in messages:
        message.pretty_print()

    # Invoke
    print_title("agent.stream()", 100, bgn="\n", end="\n")
    messages = [HumanMessage(content="Add 3 and 4.")]
    for chunk in agent.stream(messages, stream_mode="updates"):
        for key, val in chunk.items():
            if isinstance(val, BaseMessage):
                print_title(key, 80)
                val.pretty_print()
            elif isinstance(val, list):
                for idx, msg in enumerate(val):
                    print_title(f"{key}[{idx}]", 80)
                    msg.pretty_print()
            else:
                assert False


def demo__workflow__customer_support_email():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    # Define the structure for email classification
    class EmailClassification(TypedDict):
        intent: Literal["question", "bug", "billing", "feature", "complex"]
        urgency: Literal["low", "medium", "high", "critical"]
        topic: str
        summary: str

    class EmailAgentState(TypedDict):
        # Raw email data
        email_content: str
        sender_email: str
        email_id: str

        # Classification result
        classification: EmailClassification | None

        # Raw search/API results
        search_results: list[str] | None  # List of raw document chunks
        customer_history: dict | None  # Raw customer data from CRM

        # Generated content
        draft_response: str | None
        messages: list[str] | None

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    def read_email(state: EmailAgentState) -> dict:
        """Extract and parse email content"""
        # In production, this would connect to your email service
        return {
            "messages": [
                HumanMessage(content=f"Processing email: {state['email_content']}")
            ]
        }

    def classify_intent(
        state: EmailAgentState,
    ) -> Command[
        Literal[
            "search_documentation", "human_review", "draft_response", "bug_tracking"
        ]
    ]:
        """Use LLM to classify email intent and urgency, then route accordingly"""

        # Create structured LLM that returns EmailClassification dict
        structured_llm = llm.with_structured_output(EmailClassification)

        # Format the prompt on-demand, not stored in state
        classification_prompt = f"""
        Analyze this customer email and classify it:

        Email: {state['email_content']}
        From: {state['sender_email']}

        Provide classification including intent, urgency, topic, and summary.
        """

        # Get structured response directly as dict
        classification = structured_llm.invoke(classification_prompt)

        # Determine next node based on classification
        if (
            classification["intent"] == "billing"
            or classification["urgency"] == "critical"
        ):
            goto = "human_review"
        elif classification["intent"] in ["question", "feature"]:
            goto = "search_documentation"
        elif classification["intent"] == "bug":
            goto = "bug_tracking"
        else:
            goto = "draft_response"

        # Store classification as a single dict in state
        return Command(update={"classification": classification}, goto=goto)

    def search_documentation(
        state: EmailAgentState,
    ) -> Command[Literal["draft_response"]]:
        """Search knowledge base for relevant information"""

        # Build search query from classification
        # classification = state.get("classification", {})
        # query = f"{classification.get('intent', '')} {classification.get('topic', '')}"

        try:
            # Implement your search logic here
            # Store raw search results, not formatted text
            search_results = [
                "Reset password via Settings > Security > Change Password",
                "Password must be at least 12 characters",
                "Include uppercase, lowercase, numbers, and symbols",
            ]
        except Exception as e:
            # For recoverable search errors, store error and continue
            search_results = [f"Search temporarily unavailable: {str(e)}"]

        return Command(
            update={"search_results": search_results},  # Store raw results or error
            goto="draft_response",
        )

    def bug_tracking(state: EmailAgentState) -> Command[Literal["draft_response"]]:
        """Create or update bug tracking ticket"""

        # Create ticket in your bug tracking system
        ticket_id = "BUG-12345"  # Would be created via API

        return Command(
            update={
                "search_results": [f"Bug ticket {ticket_id} created"],
                "current_step": "bug_tracked",
            },
            goto="draft_response",
        )

    def draft_response(
        state: EmailAgentState,
    ) -> Command[Literal["human_review", "send_reply"]]:
        """Generate response using context and route based on quality"""

        classification = state.get("classification", {})

        # Format context from raw state data on-demand
        context_sections = []

        if state.get("search_results"):
            # Format search results for the prompt
            formatted_docs = "\n".join([f"- {doc}" for doc in state["search_results"]])
            context_sections.append(f"Relevant documentation:\n{formatted_docs}")

        if state.get("customer_history"):
            # Format customer data for the prompt
            context_sections.append(
                f"Customer tier: {state['customer_history'].get('tier', 'standard')}"
            )

        # Build the prompt with formatted context
        draft_prompt = f"""
        Draft a response to this customer email:
        {state['email_content']}

        Email intent: {classification.get('intent', 'unknown')}
        Urgency level: {classification.get('urgency', 'medium')}

        {chr(10).join(context_sections)}

        Guidelines:
        - Be professional and helpful
        - Address their specific concern
        - Use the provided documentation when relevant
        """

        response = llm.invoke(draft_prompt)

        # Determine if human review needed based on urgency and intent
        needs_review = (
            classification.get("urgency") in ["high", "critical"]
            or classification.get("intent") == "complex"
        )

        # Route to appropriate next node
        goto = "human_review" if needs_review else "send_reply"

        return Command(
            update={"draft_response": response.content},  # Store only the raw response
            goto=goto,
        )

    def human_review(state: EmailAgentState) -> Command[Literal["send_reply", END]]:
        """Pause for human review using interrupt and route based on decision"""

        classification = state.get("classification", {})

        # interrupt() must come first - any code before it will re-run on resume
        human_decision = interrupt(
            {
                "email_id": state.get("email_id", ""),
                "original_email": state.get("email_content", ""),
                "draft_response": state.get("draft_response", ""),
                "urgency": classification.get("urgency"),
                "intent": classification.get("intent"),
                "action": "Please review and approve/edit this response",
            }
        )

        # Now process the human's decision
        if human_decision.get("approved"):
            return Command(
                update={
                    "draft_response": human_decision.get(
                        "edited_response", state.get("draft_response", "")
                    )
                },
                goto="send_reply",
            )
        else:
            # Rejection means human will handle directly
            return Command(update={}, goto=END)

    def send_reply(state: EmailAgentState) -> dict:
        """Send the email response"""
        # Integrate with email service
        print(f"Sending reply: {state['draft_response'][:100]}...")
        return {}

    # Create the graph
    workflow = StateGraph(EmailAgentState)

    # Add nodes with appropriate error handling
    # Add retry policy for nodes that might have transient failures
    workflow.add_node("read_email", read_email)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node(
        "search_documentation",
        search_documentation,
        retry_policy=RetryPolicy(max_attempts=3),
    )
    workflow.add_node("bug_tracking", bug_tracking)
    workflow.add_node("draft_response", draft_response)
    workflow.add_node("human_review", human_review)
    workflow.add_node("send_reply", send_reply)

    # Add only the essential edges
    workflow.add_edge(START, "read_email")
    workflow.add_edge("read_email", "classify_intent")
    workflow.add_edge("send_reply", END)

    # Compile with checkpointer for persistence, in case run graph with Local_Server --> Please compile without checkpointer
    memory = InMemorySaver()
    agent = workflow.compile(checkpointer=memory)
    write_graph(agent, func_name)

    def agent_stream(content, emailer):
        print_title(content, 100, bgn="\n", end="\n")
        for chunk in agent.stream(
            {"email_content": content, "sender_email": f"{emailer}@example.com"},
            {"configurable": {"thread_id": emailer}},
            stream_mode="updates",
        ):
            for key, val in chunk.items():
                print_title(key, 80, bgn="\n")
                print(val)
                print_title(key, 80, end="\n")

    agent_stream("How do I reset my password?", "user_1")
    agent_stream("The export feature crashes when I select PDF format", "user_2")
    agent_stream("I was charged twice for my subscription!", "user_3")
    agent_stream("Can you add dark mode to the mobile app?", "user_4")
    agent_stream("Our API integration fails intermittently with 504 errors", "user_5")


def demo__workflow__customer_support_email__short():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    class EmailState(TypedDict):
        email_content: str
        response_text: str | None

    def human_review_node(state: EmailState):
        interrupt(
            {
                "approved": False,
                "edited_response": state.get("response_text") or "",
            }
        )
        return {"response_text": "placeholder"}

    app = (
        StateGraph(EmailState)
        .add_node("human_review", human_review_node)
        .add_edge(START, "human_review")
        .add_edge("human_review", END)
        .compile(checkpointer=InMemorySaver())
    )
    write_graph(app, func_name)

    # Run with a thread_id for persistence
    config = {"configurable": {"thread_id": "customer_123"}}

    initial_state = {
        "email_content": "I was charged twice for my subscription! This is urgent!",
        "response_text": "Draft response",
    }
    result = app.invoke(initial_state, config, version="v2")
    print(result)
    # The graph will pause at human_review

    # Resume execution
    human_response = Command(
        resume={
            "approved": True,
            "edited_response": "We sincerely apologize for the double charge. I've initiated an immediate refund...",
        }
    )
    final_result = app.invoke(human_response, config, version="v2")
    print(final_result)
    # Email sent successfully!


def demo__llms_and_augmentations():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Schema for structured output
    class SearchQuery(BaseModel):
        search_query: str = Field(
            None, description="Query that is optimized web search."
        )
        justification: str = Field(
            None, description="Why this query is relevant to the user's request."
        )

    # Augment the LLM with schema for structured output
    structured_llm = llm.with_structured_output(SearchQuery)

    # Invoke the augmented LLM
    output = structured_llm.invoke(
        "How does Calcium CT score relate to high cholesterol?"
    )

    print_title("llm.with_structured_output()", 100, bgn="\n", end="\n")
    print(output.model_dump_json(indent=4))

    # Define a tool
    def multiply(a: int, b: int) -> int:
        return a * b

    # Augment the LLM with tools
    llm_with_tools = llm.bind_tools([multiply])

    # Invoke the LLM with input that triggers the tool call
    message = llm_with_tools.invoke("What is 2 times 3?")

    print_title("llm.bind_tools()", 100, bgn="\n", end="\n")
    message.pretty_print()


def demo__workflow__prompt_chaining__graph_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Graph state
    class State(TypedDict):
        topic: str
        joke: str
        improved_joke: str
        final_joke: str

    # Nodes
    def generate_joke(state: State):
        """First LLM call to generate initial joke"""
        msg = llm.invoke(f"Write a short joke about {state['topic']}")
        return {"joke": msg.content}

    def check_punchline(state: State):
        """Gate function to check if the joke has a punchline"""
        # Simple check - does the joke contain "?" or "!"
        if "?" in state["joke"] or "!" in state["joke"]:
            return "Pass"
        return "Fail"

    def improve_joke(state: State):
        """Second LLM call to improve the joke"""
        msg = llm.invoke(f"Make this joke funnier by adding wordplay: {state['joke']}")
        return {"improved_joke": msg.content}

    def polish_joke(state: State):
        """Third LLM call for final polish"""
        msg = llm.invoke(
            f"Add a surprising twist to this joke: {state['improved_joke']}"
        )
        return {"final_joke": msg.content}

    # Build workflow
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("generate_joke", generate_joke)
    workflow.add_node("improve_joke", improve_joke)
    workflow.add_node("polish_joke", polish_joke)

    # Add edges to connect nodes
    workflow.add_edge(START, "generate_joke")
    workflow.add_conditional_edges(
        "generate_joke", check_punchline, {"Fail": "improve_joke", "Pass": END}
    )
    workflow.add_edge("improve_joke", "polish_joke")
    workflow.add_edge("polish_joke", END)

    # Compile
    chain = workflow.compile()
    write_graph(chain, func_name)

    # Invoke
    state = chain.invoke({"topic": "cats"})
    print("Initial joke:")
    print(state["joke"])
    print("\n--- --- ---\n")
    if "improved_joke" in state:
        print("Improved joke:")
        print(state["improved_joke"])
        print("\n--- --- ---\n")

        print("Final joke:")
        print(state["final_joke"])
    else:
        print("Final joke:")
        print(state["joke"])


def demo__workflow__prompt_chaining__functional_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Tasks
    @task
    def generate_joke(topic: str):
        """First LLM call to generate initial joke"""
        msg = llm.invoke(f"Write a short joke about {topic}")
        return msg.content

    def check_punchline(joke: str):
        """Gate function to check if the joke has a punchline"""
        # Simple check - does the joke contain "?" or "!"
        if "?" in joke or "!" in joke:
            return "Fail"
        return "Pass"

    @task
    def improve_joke(joke: str):
        """Second LLM call to improve the joke"""
        msg = llm.invoke(f"Make this joke funnier by adding wordplay: {joke}")
        return msg.content

    @task
    def polish_joke(joke: str):
        """Third LLM call for final polish"""
        msg = llm.invoke(f"Add a surprising twist to this joke: {joke}")
        return msg.content

    @entrypoint()
    def prompt_chaining_workflow(topic: str):
        original_joke = generate_joke(topic).result()
        if check_punchline(original_joke) == "Pass":
            return original_joke
        improved_joke = improve_joke(original_joke).result()
        return polish_joke(improved_joke).result()

    # Invoke
    for step in prompt_chaining_workflow.stream("cats", stream_mode="updates"):
        print(step)
        print("\n")


def demo__workflow__parallelization__graph_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Graph state
    class State(TypedDict):
        topic: str
        joke: str
        story: str
        poem: str
        combined_output: str

    # Nodes
    def call_llm_1(state: State):
        """First LLM call to generate initial joke"""
        msg = llm.invoke(f"Write a short joke about {state['topic']}")
        return {"joke": msg.content}

    def call_llm_2(state: State):
        """Second LLM call to generate story"""
        msg = llm.invoke(f"Write a short story about {state['topic']}")
        return {"story": msg.content}

    def call_llm_3(state: State):
        """Third LLM call to generate poem"""
        msg = llm.invoke(f"Write a short poem about {state['topic']}")
        return {"poem": msg.content}

    def aggregator(state: State):
        """Combine the joke, story and poem into a single output"""
        combined = f"Here's a story, joke, and poem about {state['topic']}!\n\n"
        combined += f"STORY:\n{state['story']}\n\n"
        combined += f"JOKE:\n{state['joke']}\n\n"
        combined += f"POEM:\n{state['poem']}"
        return {"combined_output": combined}

    # Build workflow
    parallel_builder = StateGraph(State)

    # Add nodes
    parallel_builder.add_node("call_llm_1", call_llm_1)
    parallel_builder.add_node("call_llm_2", call_llm_2)
    parallel_builder.add_node("call_llm_3", call_llm_3)
    parallel_builder.add_node("aggregator", aggregator)

    # Add edges to connect nodes
    parallel_builder.add_edge(START, "call_llm_1")
    parallel_builder.add_edge(START, "call_llm_2")
    parallel_builder.add_edge(START, "call_llm_3")
    parallel_builder.add_edge("call_llm_1", "aggregator")
    parallel_builder.add_edge("call_llm_2", "aggregator")
    parallel_builder.add_edge("call_llm_3", "aggregator")
    parallel_builder.add_edge("aggregator", END)

    parallel_workflow = parallel_builder.compile()
    write_graph(parallel_workflow, func_name)

    # Invoke
    print_title("parallel_workflow.invoke()", 100, bgn="\n", end="\n")
    state = parallel_workflow.invoke({"topic": "cats"})
    print(state["combined_output"])

    # Invoke
    print_title("parallel_workflow.stream()", 100, bgn="\n", end="\n")
    for chunk in parallel_workflow.stream({"topic": "cats"}, stream_mode="updates"):
        for key, val in chunk.items():
            print_title(key, 80, bgn="\n", end="\n")
            print(val)


def demo__workflow__parallelization__functional_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    @task
    def call_llm_1(topic: str):
        """First LLM call to generate initial joke"""
        msg = llm.invoke(f"Write a short joke about {topic}")
        return msg.content

    @task
    def call_llm_2(topic: str):
        """Second LLM call to generate story"""
        msg = llm.invoke(f"Write a short story about {topic}")
        return msg.content

    @task
    def call_llm_3(topic):
        """Third LLM call to generate poem"""
        msg = llm.invoke(f"Write a short poem about {topic}")
        return msg.content

    @task
    def aggregator(topic, joke, story, poem):
        """Combine the joke and story into a single output"""
        combined = f"Here's a story, joke, and poem about {topic}!\n\n"
        combined += f"STORY:\n{story}\n\n"
        combined += f"JOKE:\n{joke}\n\n"
        combined += f"POEM:\n{poem}"
        return combined

    # Build workflow
    @entrypoint()
    def parallel_workflow(topic: str):
        joke_fut = call_llm_1(topic)
        story_fut = call_llm_2(topic)
        poem_fut = call_llm_3(topic)
        return aggregator(
            topic, joke_fut.result(), story_fut.result(), poem_fut.result()
        ).result()

    # Invoke
    for step in parallel_workflow.stream("cats", stream_mode="updates"):
        print(step)
        print("\n")


def demo__workflow__routing__graph_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Schema for structured output to use as routing logic
    class Route(BaseModel):
        step: Literal["poem", "story", "joke"] = Field(
            None, description="The next step in the routing process"
        )

    # Augment the LLM with schema for structured output
    router = llm.with_structured_output(Route)

    # State
    class State(TypedDict):
        input: str
        decision: str
        output: str

    # Nodes
    def llm_call_1(state: State):
        """Write a story"""
        result = llm.invoke(state["input"])
        return {"output": result.content}

    def llm_call_2(state: State):
        """Write a joke"""
        result = llm.invoke(state["input"])
        return {"output": result.content}

    def llm_call_3(state: State):
        """Write a poem"""
        result = llm.invoke(state["input"])
        return {"output": result.content}

    def llm_call_router(state: State):
        """Route the input to the appropriate node"""
        # Run the augmented LLM with structured output to serve as routing logic
        decision = router.invoke(
            [
                SystemMessage(
                    content="Route the input to story, joke, or poem based on the user's request."
                ),
                HumanMessage(content=state["input"]),
            ]
        )
        return {"decision": decision.step}

    # Conditional edge function to route to the appropriate node
    def route_decision(state: State):
        # Return the node name you want to visit next
        if state["decision"] == "story":
            return "llm_call_1"
        elif state["decision"] == "joke":
            return "llm_call_2"
        elif state["decision"] == "poem":
            return "llm_call_3"

    # Build workflow
    router_builder = StateGraph(State)

    # Add nodes
    router_builder.add_node("llm_call_1", llm_call_1)
    router_builder.add_node("llm_call_2", llm_call_2)
    router_builder.add_node("llm_call_3", llm_call_3)
    router_builder.add_node("llm_call_router", llm_call_router)

    # Add edges to connect nodes
    router_builder.add_edge(START, "llm_call_router")
    router_builder.add_conditional_edges(
        "llm_call_router",
        route_decision,
        {  # Name returned by route_decision : Name of next node to visit
            "llm_call_1": "llm_call_1",
            "llm_call_2": "llm_call_2",
            "llm_call_3": "llm_call_3",
        },
    )
    router_builder.add_edge("llm_call_1", END)
    router_builder.add_edge("llm_call_2", END)
    router_builder.add_edge("llm_call_3", END)

    # Compile workflow
    router_workflow = router_builder.compile()
    write_graph(router_workflow, func_name)

    # Invoke
    state = router_workflow.invoke({"input": "Write me a joke about cats"})
    print(state["output"])


def demo__workflow__routing__functional_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Schema for structured output to use as routing logic
    class Route(BaseModel):
        step: Literal["poem", "story", "joke"] = Field(
            None, description="The next step in the routing process"
        )

    # Augment the LLM with schema for structured output
    router = llm.with_structured_output(Route)

    @task
    def llm_call_1(input_: str):
        """Write a story"""
        result = llm.invoke(input_)
        return result.content

    @task
    def llm_call_2(input_: str):
        """Write a joke"""
        result = llm.invoke(input_)
        return result.content

    @task
    def llm_call_3(input_: str):
        """Write a poem"""
        result = llm.invoke(input_)
        return result.content

    def llm_call_router(input_: str):
        """Route the input to the appropriate node"""
        # Run the augmented LLM with structured output to serve as routing logic
        decision = router.invoke(
            [
                SystemMessage(
                    content="Route the input to story, joke, or poem based on the user's request."
                ),
                HumanMessage(content=input_),
            ]
        )
        return decision.step

    # Create workflow
    @entrypoint()
    def router_workflow(input_: str):
        next_step = llm_call_router(input_)
        if next_step == "story":
            llm_call = llm_call_1
        elif next_step == "joke":
            llm_call = llm_call_2
        elif next_step == "poem":
            llm_call = llm_call_3
        return llm_call(input_).result()

    # Invoke
    for step in router_workflow.stream(
        "Write me a joke about cats", stream_mode="updates"
    ):
        print(step)
        print("\n")


def demo__workflow__orchestrator_worker__graph_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Schema for structured output to use in planning
    class Section(BaseModel):
        name: str = Field(
            description="Name for this section of the report.",
        )
        description: str = Field(
            description="Brief overview of the main topics and concepts to be covered in this section.",
        )

    class Sections(BaseModel):
        sections: List[Section] = Field(
            description="Sections of the report.",
        )

    # Augment the LLM with schema for structured output
    planner = llm.with_structured_output(Sections)

    # Graph state
    class State(TypedDict):
        topic: str  # Report topic
        sections: list[Section]  # List of report sections
        completed_sections: Annotated[
            list, operator.add
        ]  # All workers write to this key in parallel
        final_report: str  # Final report

    # Worker state
    class WorkerState(TypedDict):
        section: Section
        completed_sections: Annotated[list, operator.add]

    # Nodes
    def orchestrator(state: State):
        """Orchestrator that generates a plan for the report"""
        # Generate queries
        report_sections = planner.invoke(
            [
                SystemMessage(content="Generate a plan for the report."),
                HumanMessage(content=f"Here is the report topic: {state['topic']}"),
            ]
        )
        return {"sections": report_sections.sections}

    def llm_call(state: WorkerState):
        """Worker writes a section of the report"""
        # Generate section
        section = llm.invoke(
            [
                SystemMessage(
                    content="Write a report section following the provided name and description. Include no preamble for each section. Use markdown formatting."
                ),
                HumanMessage(
                    content=f"Here is the section name: {state['section'].name} and description: {state['section'].description}"
                ),
            ]
        )
        # Write the updated section to completed sections
        return {"completed_sections": [section.content]}

    def synthesizer(state: State):
        """Synthesize full report from sections"""
        # List of completed sections
        completed_sections = state["completed_sections"]
        # Format completed section to str to use as context for final sections
        completed_report_sections = "\n\n---\n\n".join(completed_sections)
        return {"final_report": completed_report_sections}

    # Conditional edge function to create llm_call workers that each write a section of the report
    def assign_workers(state: State):
        """Assign a worker to each section in the plan"""
        # Kick off section writing in parallel via Send() API
        return [Send("llm_call", {"section": s}) for s in state["sections"]]

    # Build workflow
    orchestrator_worker_builder = StateGraph(State)

    # Add the nodes
    orchestrator_worker_builder.add_node("orchestrator", orchestrator)
    orchestrator_worker_builder.add_node("llm_call", llm_call)
    orchestrator_worker_builder.add_node("synthesizer", synthesizer)

    # Add edges to connect nodes
    orchestrator_worker_builder.add_edge(START, "orchestrator")
    orchestrator_worker_builder.add_conditional_edges(
        "orchestrator", assign_workers, ["llm_call"]
    )
    orchestrator_worker_builder.add_edge("llm_call", "synthesizer")
    orchestrator_worker_builder.add_edge("synthesizer", END)

    # Compile the workflow
    orchestrator_worker = orchestrator_worker_builder.compile()
    write_graph(orchestrator_worker, func_name)

    # Invoke
    state = orchestrator_worker.invoke({"topic": "Create a report on LLM scaling laws"})
    pprint.pprint(state, indent=4, sort_dicts=False)


def demo__workflow__orchestrator_worker__functional_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Schema for structured output to use in planning
    class Section(BaseModel):
        name: str = Field(
            description="Name for this section of the report.",
        )
        description: str = Field(
            description="Brief overview of the main topics and concepts to be covered in this section.",
        )

    class Sections(BaseModel):
        sections: List[Section] = Field(
            description="Sections of the report.",
        )

    # Augment the LLM with schema for structured output
    planner = llm.with_structured_output(Sections)

    @task
    def orchestrator(topic: str):
        """Orchestrator that generates a plan for the report"""
        # Generate queries
        report_sections = planner.invoke(
            [
                SystemMessage(content="Generate a plan for the report."),
                HumanMessage(content=f"Here is the report topic: {topic}"),
            ]
        )
        return report_sections.sections

    @task
    def llm_call(section: Section):
        """Worker writes a section of the report"""
        # Generate section
        result = llm.invoke(
            [
                SystemMessage(content="Write a report section."),
                HumanMessage(
                    content=f"Here is the section name: {section.name} and description: {section.description}"
                ),
            ]
        )
        # Write the updated section to completed sections
        return result.content

    @task
    def synthesizer(completed_sections: list[str]):
        """Synthesize full report from sections"""
        final_report = "\n\n---\n\n".join(completed_sections)
        return final_report

    @entrypoint()
    def orchestrator_worker(topic: str):
        sections = orchestrator(topic).result()
        section_futures = [llm_call(section) for section in sections]
        final_report = synthesizer(
            [section_fut.result() for section_fut in section_futures]
        ).result()
        return final_report

    # Invoke
    report = orchestrator_worker.invoke("Create a report on LLM scaling laws")
    print(report)


def demo__workflow__evaluator_optimizer__graph_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Graph state
    class State(TypedDict):
        joke: str
        topic: str
        feedback: str
        funny_or_not: str

    # Schema for structured output to use in evaluation
    class Feedback(BaseModel):
        grade: Literal["funny", "not funny"] = Field(
            description="Decide if the joke is funny or not.",
        )
        feedback: str = Field(
            description="If the joke is not funny, provide feedback on how to improve it.",
        )

    # Augment the LLM with schema for structured output
    evaluator = llm.with_structured_output(Feedback)

    # Nodes
    def llm_call_generator(state: State):
        """LLM generates a joke"""
        if state.get("feedback"):
            msg = llm.invoke(
                f"Write a joke about {state['topic']} but take into account the feedback: {state['feedback']}"
            )
        else:
            msg = llm.invoke(f"Write a joke about {state['topic']}")
        return {"joke": msg.content}

    def llm_call_evaluator(state: State):
        """LLM evaluates the joke"""
        grade = evaluator.invoke(f"Grade the joke {state['joke']}")
        return {"funny_or_not": grade.grade, "feedback": grade.feedback}

    # Conditional edge function to route back to joke generator or end based upon feedback from the evaluator
    def route_joke(state: State):
        """Route back to joke generator or end based upon feedback from the evaluator"""
        if state["funny_or_not"] == "funny":
            return "Accepted"
        elif state["funny_or_not"] == "not funny":
            return "Rejected + Feedback"

    # Build workflow
    optimizer_builder = StateGraph(State)

    # Add the nodes
    optimizer_builder.add_node("llm_call_generator", llm_call_generator)
    optimizer_builder.add_node("llm_call_evaluator", llm_call_evaluator)

    # Add edges to connect nodes
    optimizer_builder.add_edge(START, "llm_call_generator")
    optimizer_builder.add_edge("llm_call_generator", "llm_call_evaluator")
    optimizer_builder.add_conditional_edges(
        "llm_call_evaluator",
        route_joke,
        {  # Name returned by route_joke : Name of next node to visit
            "Accepted": END,
            "Rejected + Feedback": "llm_call_generator",
        },
    )

    # Compile the workflow
    optimizer_workflow = optimizer_builder.compile()
    write_graph(optimizer_workflow, func_name)

    # Invoke
    print_title("optimizer_workflow.invoke()", 100, bgn="\n", end="\n")
    state = optimizer_workflow.invoke({"topic": "Cats"})
    pprint.pprint(state, indent=4, sort_dicts=False)

    # Invoke
    print_title("optimizer_workflow.stream()", 100, bgn="\n", end="\n")
    for chunk in optimizer_workflow.stream({"topic": "Cats"}, stream_mode="updates"):
        for key, val in chunk.items():
            print_title(key, 80, bgn="\n", end="\n")
            pprint.pprint(val, indent=4, sort_dicts=False)


def demo__workflow__evaluator_optimizer__functional_api():
    func_name = inspect.currentframe().f_code.co_name
    print_title(func_name, bgn="\n", end="\n")

    llm = init_chat_model(
        model="qwen3-max",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        temperature=0,
    )

    # Schema for structured output to use in evaluation
    class Feedback(BaseModel):
        grade: Literal["funny", "not funny"] = Field(
            description="Decide if the joke is funny or not.",
        )
        feedback: str = Field(
            description="If the joke is not funny, provide feedback on how to improve it.",
        )

    # Augment the LLM with schema for structured output
    evaluator = llm.with_structured_output(Feedback)

    # Nodes
    @task
    def llm_call_generator(topic: str, feedback: Feedback):
        """LLM generates a joke"""
        if feedback:
            msg = llm.invoke(
                f"Write a joke about {topic} but take into account the feedback: {feedback}"
            )
        else:
            msg = llm.invoke(f"Write a joke about {topic}")
        return msg.content

    @task
    def llm_call_evaluator(joke: str):
        """LLM evaluates the joke"""
        feedback = evaluator.invoke(f"Grade the joke {joke}")
        return feedback

    @entrypoint()
    def optimizer_workflow(topic: str):
        feedback = None
        while True:
            joke = llm_call_generator(topic, feedback).result()
            feedback = llm_call_evaluator(joke).result()
            if feedback.grade == "funny":
                break
        return joke

    # Invoke
    for step in optimizer_workflow.stream("Cats", stream_mode="updates"):
        print(step)
        print("\n")


if __name__ == "__main__":
    demo__hello_world()

    demo__agent__calculator__graph_api()
    demo__agent__calculator__functional_api()

    demo__workflow__customer_support_email()
    demo__workflow__customer_support_email__short()

    #################################################################

    demo__llms_and_augmentations()

    demo__workflow__prompt_chaining__graph_api()
    demo__workflow__prompt_chaining__functional_api()

    demo__workflow__parallelization__graph_api()
    demo__workflow__parallelization__functional_api()

    demo__workflow__routing__graph_api()
    demo__workflow__routing__functional_api()

    demo__workflow__orchestrator_worker__graph_api()
    demo__workflow__orchestrator_worker__functional_api()

    demo__workflow__evaluator_optimizer__graph_api()
    demo__workflow__evaluator_optimizer__functional_api()
