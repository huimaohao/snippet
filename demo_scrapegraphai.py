"""

``` Shell
pip install scrapegraphai

# required by scrapegraphai
playwright install
```

"""

import os
import json

from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()


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


if __name__ == "__main__":
    demo_SmartScraperGraph()
    demo_SmartScraperGraph_with_schema()
