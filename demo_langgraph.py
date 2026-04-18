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

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from langgraph.types import interrupt, Command, RetryPolicy

from langchain_core.messages import BaseMessage

from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.messages import ToolCall
from langchain.tools import tool

from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict

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


def demo__calculator_agent__graph_api():
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


def demo__calculator_agent__functional_api():
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

    write_graph(agent, func_name)

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


def demo__customer_support_email():
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


def demo__customer_support_email__short():
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


if __name__ == "__main__":
    demo__hello_world()

    demo__calculator_agent__graph_api()
    demo__calculator_agent__functional_api()

    demo__customer_support_email()
    demo__customer_support_email__short()
