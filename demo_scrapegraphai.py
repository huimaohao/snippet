"""

``` Shell
pip install scrapegraphai

# required by scrapegraphai
playwright install
```

"""

from scrapegraphai.graphs import SmartScraperGraph
import json


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


if __name__ == "__main__":
    demo_1()
