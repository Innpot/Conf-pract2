"""Проверки выводов на цикле и общей зависимости."""

import unittest

from src.graph import build_graph
from src.visualize import ascii_tree, plantuml


class VisualizeTests(unittest.TestCase):
    def test_aliases_and_cycle_edges(self):
        graph = build_graph({"X": ("Y",), "Y": ("X",)}, "X")
        self.assertEqual(
            plantuml(graph).splitlines(),
            ["@startuml", "left to right direction",
             'component "X" as p0', 'component "Y" as p1',
             "p0 --> p1", "p1 --> p0 : cycle", "@enduml"],
        )
        self.assertTrue(ascii_tree(graph).endswith("X [see above]"))

    def test_shared_vertex_and_missing_vertex(self):
        index = {"A": ("B", "C"), "B": ("D",), "C": ("D",)}
        graph = build_graph(index, "A")
        lines = ascii_tree(graph).splitlines()
        self.assertEqual(lines, [
            "A", "|-- B", "|   `-- D [missing]", "`-- C",
            "    `-- D [see above] [missing]",
        ])
        self.assertIn('component "D (missing)"', plantuml(graph))
