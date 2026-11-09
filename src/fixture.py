"""Чтение тестового графа вида A: B C."""

from pathlib import Path

from .config import TEST_PACKAGE


def read_fixture(lines):
    """Проверить синтаксис, уникальность и объявления вершин."""
    index = {}
    for number, raw in enumerate(lines, 1):
        line = raw.partition("#")[0].strip()
        if not line:
            continue
        package, colon, children = line.partition(":")
        package, names = package.strip(), children.split()
        if not colon or not all(
            TEST_PACKAGE.fullmatch(name) for name in (package, *names)
        ):
            raise ValueError(f"Строка {number}: ожидается A: B C")
        if package in index:
            raise ValueError(f"Строка {number}: повтор пакета {package}")
        index[package] = tuple(dict.fromkeys(names))
    if not index:
        raise ValueError("Тестовый граф пуст")
    missing = sorted({name for names in index.values() for name in names}
                     - index.keys())
    if missing:
        raise ValueError("Нет объявления: " + ", ".join(missing))
    return index


def load_fixture(filename):
    """Прочитать локальный тестовый граф в UTF-8."""
    with Path(filename).open(encoding="utf-8-sig") as source:
        return read_fixture(source)
