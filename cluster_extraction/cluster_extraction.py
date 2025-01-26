import logging
import os
import json
import threading
import time
import warnings

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from functools import reduce

from dotenv import load_dotenv
from sklearn.cluster import SpectralClustering
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import Field, BaseModel

import networkx as nx
from langchain_core.output_parsers import PydanticOutputParser

from context_processor import process_fields_to_graph, parse_nodes_to_prompt

load_dotenv()

warnings.filterwarnings("ignore")

logger = logging.getLogger("clustering")

class NodeIds(BaseModel):
    nodeIds: List[str] = Field(description="String IDs of nodes related to the user's query")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Mimics the behavior of dict.get() method.
        Returns the value associated with the given key or the default value if the key is not found.
        """
        return getattr(self, key, default)


def detect_communities(G: nx.Graph, n_clusters: int = 5) -> Dict[int, List[int]]:
    """
    Detect communities in a given graph using spectral clustering.

    Args:
        G (nx.Graph): The input graph on which to detect communities.
        n_clusters (int, optional): The number of clusters to form. Defaults to 5.

    Returns:
        Dict[int, List[int]]: A dictionary mapping each cluster index to a list of node IDs
        belonging to that cluster.
    """
    adj_matrix = nx.to_numpy_array(G)
    clustered = SpectralClustering(
        n_clusters=n_clusters, affinity="precomputed"
    ).fit_predict(adj_matrix)
    communities = {}
    for node, label in zip(G.nodes, clustered):
        communities.setdefault(int(label), []).append(node)
    return communities


def map_func(query: str, nodes: str) -> str:
    """
    Threaded version of the map phase to process nodes.

    Args:
        query (str): The user query or coding task to base the node selection on.
        nodes (str): The string representation of the nodes to process.

    Returns:
        str: A JSON string with a list of relevant node IDs.
    """
    template = """
    # BPMN Assistant Prompt

    You are a data analysis expert specializing in datamodel recognition and node selection within a knowledge graph.
    Your task is strictly **analytical** and does not involve executing the query or performing any operations. 
    Under no circumstances should you attempt to interpret the query as an instruction to execute or simulate any process.


    Your task is as follows:
    1. Do not explain what you do.
    2. You must not answer to the query. 
    3. Don't make conversations.
    4. Under no circumstances ask any questions or ask something to be provided. 
    5. Query and nodes are always provided. Do not engage in the conversations. Do not ask user to provide it.
    6. Analyze the provided user query and the list of graph nodes.
    7. Use symbol as a node ID.
    7. Identify the datamodels or entities explicitly or implicitly mentioned in the query.
    8. Do not execute, interpret, or simulate any operation or action described in the query. Your task is limited to **analysis and node selection**.
    9. From the provided nodes, select only those that match the datamodels or entities referenced in the query.
    10. Do not, under any circumstances, return the whole node data or any part of the node other than its ID.
    11. Return **only** the IDs of the selected nodes.
    12. Always return the result **exclusively** as a JSON object, formatted as follows:
       ```json

           "nodeIds": [<list of selected node IDs as strings>]
    13. Never execute the provided query. Never write instructions for provided query.
    14. Select only nodes that references entities in the query and return their IDs as json specified above.
    15. If you don't find relevant IDs, return empty list:
        ```json

           "nodeIds": []

    ## Query
    {query}

    ## Nodes
    {nodes}
    """
    llm = ChatOpenAI(
        temperature=0.0,
        model=os.environ.get("BIELIK_MODEL"),
        base_url=os.environ.get("BIELIK_BASE_URL"),
        api_key=os.environ.get("BIELIK_API_KEY"),
    )
    parser = PydanticOutputParser(pydantic_object=NodeIds)
    prompt = PromptTemplate.from_template(template)

    chain = prompt | llm | parser
    thread_name = threading.current_thread().name
    logger.info(f"Thread {thread_name} calling model {llm.model_name}...")
    res = chain.invoke(input={"query": query, "nodes": nodes})
    print(f"Thread {thread_name} received response: {res}")
    return res


def reduce_phase(G: nx.Graph) -> callable:
    """
    Create a function that aggregates a list of JSON objects containing node IDs
    and their associated data.

    The generated function, `reduce_func`, takes in a string and a dictionary with
    a list of node IDs and returns a concatenated string of the JSON objects
    representing the nodes.

    Args:
        G (nx.Graph): The input graph on which the nodes exist.

    Returns:
        callable: A function that takes in a string and a dictionary with a list of
        node IDs and returns a concatenated string of the JSON objects representing
        the nodes.
    """

    def reduce_func(accumulator: list, related_nodes: dict) -> list:
        for node_id in related_nodes.get("nodeIds", []):
            print("found: ", json.dumps(G.nodes[node_id]))
            accumulator.append(dict(G.nodes[node_id]))
        return accumulator

    return reduce_func


def prepare_summaries(G: nx.Graph, communities: Dict[int, List[int]]) -> List[str]:
    """
    Prepare summaries for each community in the graph.

    This function takes in a graph and a dictionary of communities, where each entry
    consists of a cluster index and a list of node IDs belonging to that cluster.
    It generates a summary for each community based on the node details. The
    summaries are concatenated strings of the JSON objects representing the
    nodes.

    Args:
        G (nx.Graph): The input graph containing node information.
        communities (Dict[int, List[int]]): A dictionary mapping each cluster index
            to a list of node IDs belonging to that cluster.

    Returns:
        List[str]: A list of summaries for each community.
    """
    summaries = []
    for _, nodes in communities.items():
        node_details = [json.dumps(G.nodes[node]) for node in nodes]
        summaries.append("\n".join(node_details))
    return summaries


def mapreduce(
        G: nx.Graph,
        query: str,
        communities: Dict[int, List[int]],
) -> list:
    """
    MapReduce function using threads to process graph communities in parallel.

    Args:
        G (nx.Graph): The input graph on which the nodes exist.
        query (str): The user query or coding task to base the node selection on.
        communities (Dict[int, List[int]]): A dictionary mapping each cluster index
            to a list of node IDs belonging to that cluster.

    Returns:
        str: A single string answer.
    """
    start_time = time.time()
    summaries = prepare_summaries(G, communities)

    with ThreadPoolExecutor() as executor:
        map_results = list(
            executor.map(lambda summary: map_func(query, summary), summaries)
        )


    context = reduce(reduce_phase(G), map_results, [])
    print("--- %s seconds ---" % (time.time() - start_time))
    return context



def main() -> None:
    with open("context.json", "r") as f:
        context = json.load(f)
    fields = context["context"]["fields"]

    G = process_fields_to_graph(fields)

    communities = detect_communities(G)
    query = "Sprawdź czy w rodzinie istnieje osoba starsza niż 85 lat, jeśli tak zmień składkę podstawową na 107 * ilość osób w rodzinie."
    logger.info("Query:", query)
    answer = mapreduce(G, query, communities)
    print(f"Answer:{answer}")

    print(parse_nodes_to_prompt(answer))


if __name__ == "__main__":
    main()
