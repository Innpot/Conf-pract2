"""Проверки всех параметров CLI."""

import tempfile
import unittest
from pathlib import Path

from src.config import load_config

VALID = {
    "package": "hello",
    "repository": "https://example.org/Packages.xz",
    "test_mode": "false",
    "ascii_tree": "false",
    "exclude": "",
}


class ConfigTests(unittest.TestCase):
    def read(self, **overrides):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.ini"
            values = VALID | overrides
            lines = [f"{key} = {value}" for key, value in values.items()]
            path.write_text("[graph]\n" + "\n".join(lines), encoding="utf-8")
            (path.parent / "graph.txt").write_text("A:\n", encoding="utf-8")
            return load_config(path)

    def test_valid_ini(self):
        self.assertEqual(self.read().package, "hello")
        config = self.read(package="A", repository="graph.txt",
                           test_mode="true", ascii_tree="true")
        self.assertEqual(Path(config.repository).name, "graph.txt")
        self.assertTrue(config.ascii_tree)

    def test_invalid_settings(self):
        for key, value in {
            "package": "BAD", "repository": "file:///Packages",
            "test_mode": "maybe", "ascii_tree": "maybe", "exclude": "??",
        }.items():
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, key):
                self.read(**{key: value})

    def test_filter_cannot_remove_root(self):
        with self.assertRaisesRegex(ValueError, "exclude"):
            self.read(exclude="ell")

    def test_missing_fixture(self):
        with self.assertRaisesRegex(ValueError, "repository"):
            self.read(package="A", test_mode="true", repository="missing")
