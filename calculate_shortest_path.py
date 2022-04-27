import networkx as nx
from rich.console import Console
from rich.markdown import Markdown
import copy
import json
from typing import Optional
import click

console = Console()


@click.command()
@click.option(
    "-j",
    "--graph_json_path",
    default="./network_graph.json",
    help="Path to the graph configuration json file.",
    type=click.Path(exists=True),
)
@click.option(
    "-r",
    "--root",
    help="Root node to start the shortest path calculation.",
    type=str,
)
@click.option(
    "-g",
    "--goal",
    help="goal/target node to start the shortest path calculation.",
    type=str,
)
@click.option(
    "-c",
    "--color",
    default=None,
    help="Color of the train to use for the shortest path calculation.",
    type=str,
)
def main(
    graph_json_path: str, root: str, goal: str, color: Optional[str] = None
) -> list:
    # Main execution. Support click option commands.
    res = get_shortest_path(graph_json_path, root, goal, color)
    return res


def get_shortest_path(
    graph_json_path: str,
    root: str,
    goal: str,
    color: Optional[str] = None,
) -> list:
    """Get shortest path between two nodes in a given dict graph.
    Args:
        graph: A graph represented as a dictionary.
        root: The root node.
        goal: The goal node.
        color: The type of node to search for.
    """
    console.print("Calculating the shortest path. Delivered params:", locals())
    graph = read_json_file(file_path=graph_json_path)

    if root not in graph.keys():
        raise ValueError(f"Root node {root} not found in graph.")
    if goal not in graph.keys():
        raise ValueError(f"Goal node {goal} not found in graph.")

    elegible_nodes = get_elegible_nodes(graph=graph, color=color)
    console.print("Elegible nodes:", elegible_nodes)

    # Change non reachable nodes distances to 0. This way we simulate that
    # the train can't go through these nodes. And wont sum into the shortest path count.
    correct_costs_graph = change_distances_to_n_for_non_elegible_nodes(
        graph=graph, elegible_nodes=elegible_nodes, n=0
    )
    console.print("Correct costs graph:", correct_costs_graph)

    graph_nx = convert_graph_dict_into_networkx_graph(correct_costs_graph)

    # Will use the networkx shortest path function using as strategy the "dijkstra" algorithm.
    # This calculate the sum of all the costs between all the nodes. And then
    # return the shortest path for the desired source and target node.
    shortest_path = nx.shortest_path(
        graph_nx, source=root, target=goal, weight="weight", method="dijkstra"
    )
    final_shortest_path = remove_non_elegible_nodes(
        shortest_path=shortest_path, elegible_nodes=elegible_nodes
    )

    console.print(Markdown("# RESULT"))
    console.print(
        f"Shortest path from [bold]{root}[/bold] to [bold]{goal}[/bold]:",
        final_shortest_path,
    )
    return final_shortest_path


def read_json_file(file_path: str) -> dict:
    with open(file_path, "r") as f:
        graph = json.load(f)

    return graph


def remove_non_elegible_nodes(shortest_path: tuple, elegible_nodes: tuple) -> tuple:
    # Remove all nodes that are not elegible
    filtered_shortest_path = []
    for node in shortest_path:
        if node in elegible_nodes:
            filtered_shortest_path.append(node)

    return filtered_shortest_path


def change_distances_to_n_for_non_elegible_nodes(
    graph: dict, elegible_nodes: tuple, n: int = 0
) -> dict:
    """Change the distances of all nodes that are not reachable by the selected color to n.
    Args:
        graph: A graph represented as a dictionary.
        elegible_nodes: The nodes that the selected color can reach.
        n: The value to change the distances to. Default is 0.
    Returns:
        A graph with all distances to non reachable nodes changed to n.
    """
    new_graph = copy.deepcopy(graph)
    for node, data in new_graph.items():
        new_edges = []
        for edge in data["costs"]:
            if edge[0] in elegible_nodes:
                new_edges.append((edge[0], edge[1]))
            else:
                new_edges.append((edge[0], n))
        new_graph[node]["costs"] = new_edges

    return new_graph


def get_elegible_nodes(graph: dict, color: str) -> tuple:
    """Get all nodes that the selected color can reach.
    Args:
        graph: A graph represented as a dictionary.
        color: The type of node to search for. If None, all nodes are elegible.
    Returns:
        A tuple of all nodes that the selected color can reach.
    """
    filtered_graph = filter_graph_according_to_color(graph=graph, color=color)
    return filtered_graph.keys()


def filter_graph_according_to_color(graph: dict, color: str) -> dict:
    """Filter the graph according to the selected color.
    Args:
        graph: A graph represented as a dictionary.
        color: The type of node to search for. If None, all nodes are elegible.
    Returns:
        modified graph with only the nodes that the selected color can reach.
    """
    elegible_graph = {}
    for node, data in graph.items():
        if color in data["color"] or data["color"] == [] or color is None:
            elegible_graph[node] = data

    return elegible_graph


def convert_graph_dict_into_networkx_graph(graph: dict) -> nx.DiGraph:
    """Create a networkx graph
    Args:
        graph: A graph represented as a dictionary.
    Returns:
        A networkX graph.
    """
    G = nx.DiGraph()

    for node, data in graph.items():
        distances = data["costs"]
        for distance in distances:
            G.add_edge(node, distance[0], weight=distance[1])

    return G


if __name__ == "__main__":
    main()
