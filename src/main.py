"""Точка входа в CLI."""

import argparse
import configparser
import lzma
import sys

from .apt_index import fetch_index
from .config import load_config
from .fixture import load_fixture
from .graph import build_graph
from .visualize import ascii_tree, plantuml

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


def report_order(graph):
    """Вывести зависимости раньше пакетов, которые их требуют."""
    if graph.back_edges:
        print("Строгий порядок невозможен; показан постпорядок DFS.",
              file=sys.stderr)
    print("\n".join(graph.postorder))


def main(argv=None):
    """Вывести PlantUML, ASCII-дерево или порядок обхода."""
    parser = argparse.ArgumentParser(description="Ubuntu dependency graph")
    parser.add_argument("--config", default="examples/ubuntu.ini")
    parser.add_argument("--order", action="store_true",
                        help="show dependency-first DFS postorder")
    parser.add_argument("--plantuml-only", action="store_true",
                        help="emit PlantUML without the optional ASCII tree")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        graph = get_graph(config)
        report_warnings(graph)
        if args.order:
            report_order(graph)
        else:
            print(plantuml(graph))
            if config.ascii_tree and not args.plantuml_only:
                print("\n" + ascii_tree(graph))
    except ERRORS as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
