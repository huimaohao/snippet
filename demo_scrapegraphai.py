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


def demo_1():
    # Define the configuration for the scraping pipeline
    graph_config = {
        "llm": {
            "model": "ollama/llama3.2",
            "temperature": 0,
            "model_tokens": 8192,
            "format": "json",
        },
        "verbose": True,
        "headless": False,
    }

    # Create the SmartScraperGraph instance
    smart_scraper_graph = SmartScraperGraph(
        prompt="Find information about the founders and what the company does",
        source="https://scrapegraphai.com/",
        config=graph_config,
    )

    # Run the pipeline
    result = smart_scraper_graph.run()
    print(json.dumps(result, indent=4))

    # Get detailed execution information
    graph_exec_info = smart_scraper_graph.get_execution_info()
    print(prettify_exec_info(graph_exec_info))


def demo_2():
    # Define the output schema
    class Project(BaseModel):
        title: str = Field(description="The title of the project")
        description: str = Field(description="The description of the project")

    class Projects(BaseModel):
        projects: List[Project]

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
        prompt="List all the projects with their descriptions",
        source="https://perinim.github.io/projects/",
        schema=Projects,  # Add schema here
        config=graph_config,
    )

    result = smart_scraper_graph.run()
    print(json.dumps(result, indent=4))

    # Get detailed execution information
    graph_exec_info = smart_scraper_graph.get_execution_info()
    print(prettify_exec_info(graph_exec_info))


if __name__ == "__main__":
    demo_1()
    demo_2()
