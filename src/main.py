"""Точка входа в CLI."""

import argparse
import configparser
import sys
from dataclasses import asdict

from .config import load_config


def main(argv=None):
    """Проверить конфигурацию и напечатать её."""
    parser = argparse.ArgumentParser(description="Ubuntu dependency graph")
    parser.add_argument("--config", default="examples/ubuntu.ini")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        for key, value in asdict(config).items():
            print(f"{key}={value}")
    except (OSError, ValueError, configparser.Error) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
