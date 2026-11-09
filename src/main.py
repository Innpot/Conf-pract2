"""Точка входа в CLI."""

import argparse
import configparser
import lzma
import sys

from .apt_index import direct_dependencies, fetch_index
from .config import load_config

ERRORS = (OSError, ValueError, configparser.Error, lzma.LZMAError, EOFError)


def main(argv=None):
    """Вывести прямые зависимости пакета из индекса Ubuntu."""
    parser = argparse.ArgumentParser(description="Ubuntu dependency graph")
    parser.add_argument("--config", default="examples/ubuntu.ini")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if config.test_mode:
            raise ValueError("Режим тестового графа появится на этапе 3")
        names = direct_dependencies(
            fetch_index(config.repository), config.package
        )
        print("\n".join(names) if names else "(нет прямых зависимостей)")
    except ERRORS as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
