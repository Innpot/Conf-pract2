"""Точка входа в CLI."""

import argparse
import configparser
import lzma
import sys

from .apt_index import fetch_index
from .config import load_config
from .fixture import load_fixture
from .graph import build_graph

ERRORS = (OSError, ValueError, configparser.Error, lzma.LZMAError, EOFError)


def get_graph(config):
    """Получить граф из локального файла или индекса Ubuntu."""
    loader = load_fixture if config.test_mode else fetch_index
    return build_graph(loader(config.repository), config.package,
                       config.exclude)


def report_warnings(graph):
    """Отправить диагностику в stderr, оставляя stdout для результата."""
    for start, end in graph.back_edges:
        print(f"Обратное ребро (цикл): {start} -> {end}", file=sys.stderr)
    if graph.missing:
        print("Нет в индексе: " + ", ".join(graph.missing), file=sys.stderr)


def main(argv=None):
    """Построить граф и напечатать список его рёбер."""
    parser = argparse.ArgumentParser(description="Ubuntu dependency graph")
    parser.add_argument("--config", default="examples/ubuntu.ini")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        graph = get_graph(config)
        report_warnings(graph)
        for package, names in graph.edges.items():
            print(f"{package}: {', '.join(names)}")
    except ERRORS as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
