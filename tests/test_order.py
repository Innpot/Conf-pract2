"""Проверки порядка загрузки."""

import unittest

from src.fixture import read_fixture
from src.graph import build_graph


class OrderTests(unittest.TestCase):
    def test_dependencies_precede_parents(self):
        index = read_fixture(["A: B C", "B: D", "C: D", "D:"])
        graph = build_graph(index, "A")
        self.assertEqual(graph.postorder, ["D", "B", "C", "A"])

    def test_cycle_has_finite_postorder(self):
        index = read_fixture(["A: B", "B: A"])
        graph = build_graph(index, "A")
        self.assertEqual(graph.back_edges, [("B", "A")])
        self.assertEqual(graph.postorder, ["B", "A"])

    def test_excluded_subtree_never_enters_order(self):
        index = read_fixture(["A: B C", "B: D", "C:", "D:"])
        self.assertEqual(build_graph(index, "A", "B").postorder, ["C", "A"])
