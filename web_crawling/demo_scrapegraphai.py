"""

``` Shell
pip install scrapegraphai

# required by scrapegraphai
playwright install
pip install qdrant-client
pip install fastembed
```

"""

import os
import json

from dotenv import load_dotenv
from scrapegraphai.graphs import DepthSearchGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()


def demo_DepthSearchGraph():
    graph_config = {
        "llm": {
            "model": "deepseek/deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        },
        "depth": 2,
        "verbose": True,
        "headless": False,
        "only_inside_links": True,
    }

    # Create the DepthSearchGraph instance
    search_graph = DepthSearchGraph(
        prompt="列出所有新闻或文章的标题和摘要",
        source="https://www.dili360.com",
        config=graph_config,
    )

    # Run the graph
    result = search_graph.run()
    print(json.dumps(result, indent=4, ensure_ascii=False))

    # Get detailed execution information
    graph_exec_info = search_graph.get_execution_info()
    print(prettify_exec_info(graph_exec_info))


if __name__ == "__main__":
    demo_DepthSearchGraph()
