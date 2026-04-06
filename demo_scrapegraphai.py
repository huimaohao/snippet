"""

``` Shell
pip install scrapegraphai

# required by scrapegraphai
playwright install
```

"""

import os
import json

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Type, List, Optional
from langchain_openai import ChatOpenAI

from scrapegraphai.nodes import FetchNode, ParseNode, GenerateAnswerNode
from scrapegraphai.graphs import (
    BaseGraph,
    AbstractGraph,
    SmartScraperGraph,
    SearchGraph,
)
from scrapegraphai.utils import prettify_exec_info

load_dotenv()


def demo_BaseGraph():
    llm_model = ChatOpenAI(
        base_url="https://api.deepseek.com",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-chat",
    )

    # Create nodes
    fetch_node = FetchNode(
        input="url | local_dir",
        output=["doc"],
        node_config={"llm_model": llm_model},
    )

    parse_node = ParseNode(
        input="doc",
        output=["parsed_doc"],
        node_config={"llm_model": llm_model, "chunk_size": 8192},
    )

    generate_answer_node = GenerateAnswerNode(
        input="user_prompt & parsed_doc",
        output=["answer"],
        node_config={"llm_model": llm_model},
    )

    # Create graph
    graph = BaseGraph(
        nodes=[fetch_node, parse_node, generate_answer_node],
        edges=[(fetch_node, parse_node), (parse_node, generate_answer_node)],
        entry_point=fetch_node,
        graph_name="MyCustomGraph",
    )

    # Execute graph
    initial_state = {
        "user_prompt": "列出所有新闻或文章的标题和摘要",
        "url": "https://www.nature.com",
    }
    final_state, execution_info = graph.execute(initial_state)
    print(json.dumps(final_state["answer"], indent=4, ensure_ascii=False))
    print(prettify_exec_info(execution_info))


def demo_AbstractGraph():
    class MyCustomGraph(AbstractGraph):
        """Custom graph for specialized scraping tasks"""

        def __init__(
            self,
            prompt: str,
            source: str,
            config: dict,
            schema: Optional[Type[BaseModel]] = None,
        ):
            super().__init__(prompt, config, source, schema)
            self.input_key = "url" if source.startswith("http") else "local_dir"

        def _create_graph(self) -> BaseGraph:
            """Define the node structure and edges"""

            # Create nodes
            fetch_node = FetchNode(
                input="url | local_dir",
                output=["doc"],
                node_config={"llm_model": self.llm_model},
            )

            parse_node = ParseNode(
                input="doc",
                output=["parsed_doc"],
                node_config={
                    "llm_model": self.llm_model,
                    "chunk_size": self.model_token,
                },
            )

            generate_node = GenerateAnswerNode(
                input="user_prompt & parsed_doc",
                output=["answer"],
                node_config={"llm_model": self.llm_model, "schema": self.schema},
            )

            # Build and return graph
            return BaseGraph(
                nodes=[fetch_node, parse_node, generate_node],
                edges=[(fetch_node, parse_node), (parse_node, generate_node)],
                entry_point=fetch_node,
                graph_name=self.__class__.__name__,
            )

        def run(self) -> str:
            """Execute the graph and return results"""
            inputs = {"user_prompt": self.prompt, self.input_key: self.source}
            self.final_state, self.execution_info = self.graph.execute(inputs)
            return self.final_state.get("answer", "No answer found.")

    # Use the custom graph
    graph_config = {
        "llm": {
            "model": "deepseek/deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        },
        "verbose": True,
        "headless": True,
    }

    custom_graph = MyCustomGraph(
        prompt="列出所有新闻或文章的标题和摘要",
        source="https://www.nature.com",
        config=graph_config,
    )

    result = custom_graph.run()
    print(json.dumps(result, indent=4, ensure_ascii=False))

    graph_exec_info = custom_graph.get_execution_info()
    print(prettify_exec_info(graph_exec_info))


def demo_SmartScraperGraph():
    # Define the configuration for the scraping pipeline
    graph_config = {
        "llm": {
            "model": "deepseek/deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        },
        "verbose": True,
        "headless": False,
    }

    # Create the SmartScraperGraph instance
    smart_scraper_graph = SmartScraperGraph(
        prompt="列出所有新闻或文章的标题和摘要",
        source="https://www.nature.com",
        config=graph_config,
    )

    # Run the pipeline
    result = smart_scraper_graph.run()
    print(json.dumps(result, indent=4, ensure_ascii=False))

    # Get detailed execution information
    graph_exec_info = smart_scraper_graph.get_execution_info()
    print(prettify_exec_info(graph_exec_info))


def demo_SmartScraperGraph_with_schema():
    # Define the output schema
    class Article(BaseModel):
        title: str = Field(description="The title")
        abstract: str = Field(description="The abstract")

    class Articles(BaseModel):
        articles: List[Article]

    # Configure the scraper with schema
    graph_config = {
        "llm": {
            "model": "deepseek/deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        },
        "verbose": True,
        "headless": False,
    }

    # Create scraper with schema
    smart_scraper_graph = SmartScraperGraph(
        prompt="列出所有新闻或文章的标题和摘要",
        source="https://www.nature.com",
        schema=Articles,  # Add schema here
        config=graph_config,
    )

    # Run the pipeline
    result = smart_scraper_graph.run()
    print(json.dumps(result, indent=4, ensure_ascii=False))

    # Get detailed execution information
    graph_exec_info = smart_scraper_graph.get_execution_info()
    print(prettify_exec_info(graph_exec_info))


def demo_SearchGraph():
    graph_config = {
        "llm": {
            "model": "deepseek/deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        },
        "search_engine": "duckduckgo",  # only duckduckgo work
        "max_results": 2,  # not work
        "verbose": True,
        "headless": False,
    }

    # Create the SearchGraph instance
    search_graph = SearchGraph(
        prompt="List best cities to visit in China and give the reason",
        config=graph_config,
    )

    # Run the graph
    result = search_graph.run()
    print(json.dumps(result, indent=4, ensure_ascii=False))

    # Get the URLs that were considered
    urls = search_graph.get_considered_urls()
    print("Scraped URLs:", urls)


def demo_SearchGraph_with_schema():
    class City(BaseModel):
        name: str = Field(description="City name")
        reason: str = Field(description="Reason to visit")

    class Cities(BaseModel):
        cities: List[City]  # = Field(description="List of cities")

    graph_config = {
        "llm": {
            "model": "deepseek/deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        },
        "search_engine": "duckduckgo",  # only duckduckgo work
        "max_results": 2,  # not work
        "verbose": True,
        "headless": False,
    }

    search_graph = SearchGraph(
        prompt="List best cities to visit in China and give the reason",
        config=graph_config,
        schema=Cities,
    )

    # Run the graph
    result = search_graph.run()
    print(json.dumps(result, indent=4, ensure_ascii=False))

    # Get the URLs that were considered
    urls = search_graph.get_considered_urls()
    print("Scraped URLs:", urls)


if __name__ == "__main__":
    demo_BaseGraph()
    demo_AbstractGraph()
    demo_SmartScraperGraph()
    demo_SmartScraperGraph_with_schema()
    demo_SearchGraph()
    # demo_SearchGraph_with_schema()  # DeepSeek: response format is unavailable
