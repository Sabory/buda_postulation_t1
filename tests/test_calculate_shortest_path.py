import unittest
import networkx as nx
from rich.console import Console

import calculate_shortest_path as csp

console = Console()


class TestCalculateShortestPath(unittest.TestCase):
    def setUp(self):
        self.json_graph = "./tests/test_network_graph.json"
        self.graph = csp.read_json_file(file_path=self.json_graph)

    def test_change_distances_to_n_for_non_elegible_nodes(self):
        test_elegible_nodes = ["A", "B", "F"]
        new_graph = csp.change_distances_to_n_for_non_elegible_nodes(
            graph=self.graph, elegible_nodes=test_elegible_nodes, n=0
        )
        self.assertEqual(new_graph["A"]["costs"][0], ("B", 1))
        self.assertEqual(new_graph["B"]["costs"][1], ("C", 0))
        self.assertEqual(new_graph["C"]["costs"][1], ("D", 0))
        self.assertEqual(new_graph["E"]["costs"][1], ("F", 1))

    def test_filter_graph_according_to_color(self):
        new_graph = csp.filter_graph_according_to_color(graph=self.graph, color="red")
        _keys = new_graph.keys()
        self.assertNotIn("G", _keys)
        self.assertIn("H", _keys)
        self.assertIn("F", _keys)

    def test_convert_graph_dict_into_networkx_graph(self):
        G = csp.convert_graph_dict_into_networkx_graph(graph=self.graph)
        for key in self.graph.keys():
            self.assertIn(key, G.nodes)

        for edge in list(G.edges.data()):
            self.assertEqual(edge[2]["weight"], 1)

    def test_get_shortest_path(self):
        # Test no color
        test = csp.get_shortest_path(
            graph_json_path=self.json_graph, root="A", goal="F", color=None
        )
        self.assertEqual(test, ["A", "B", "C", "D", "E", "F"])

        # Test next station
        test = csp.get_shortest_path(
            graph_json_path=self.json_graph, root="A", goal="B", color=None
        )
        self.assertEqual(test, ["A", "B"])

        # test color 1
        test = csp.get_shortest_path(
            graph_json_path=self.json_graph, root="A", goal="F", color="red"
        )
        self.assertEqual(test, ["A", "B", "C", "H", "F"])

        # test color 2
        test = csp.get_shortest_path(
            graph_json_path=self.json_graph, root="A", goal="F", color="green"
        )
        self.assertEqual(test, ["A", "B", "C", "D", "E", "F"])

        test = csp.get_shortest_path(
            graph_json_path=self.json_graph,
            root="A",
            goal="F",
            color="non_existing_color",
        )
        self.assertEqual(test, ["A", "B", "C", "F"])


if __name__ == "__main__":
    unittest.main()
