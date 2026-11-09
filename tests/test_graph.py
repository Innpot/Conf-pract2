"""Обход, слияние путей, фильтр и ошибки тестовых графов."""

import unittest

from src.fixture import read_fixture
from src.graph import build_graph


class GraphTests(unittest.TestCase):
    def test_diamond_and_cycle(self):
        index = read_fixture(["A: B C", "B: D", "C: D", "D: A"])
        graph = build_graph(index, "A")
        self.assertEqual(list(graph.edges), ["A", "B", "D", "C"])
        self.assertEqual(graph.edges["C"], ("D",))
        self.assertEqual(graph.back_edges, [("D", "A")])

    def test_filter_cuts_subtree(self):
        index = read_fixture(["A: BB C", "BB: D", "C:", "D:"])
        graph = build_graph(index, "A", exclude="B")
        self.assertEqual(graph.edges, {"A": ("C",), "C": ()})

    def test_missing_index_entry(self):
        graph = build_graph({"hello": ("libc6",)}, "hello")
        self.assertEqual(graph.missing, ["libc6"])
        self.assertEqual(graph.edges["libc6"], ())
        with self.assertRaisesRegex(ValueError, "missing"):
            build_graph({}, "missing")

    def test_deep_iterative_walk(self):
        names = [str(number) for number in range(2500)]
        index = {a: (b,) for a, b in zip(names, names[1:])}
        index[names[-1]] = ()
        self.assertEqual(len(build_graph(index, names[0]).edges), len(names))

    def test_invalid_fixtures(self):
        for lines in ([], ["A: b"], ["A: B"], ["A:", "A:"]):
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                read_fixture(lines)
