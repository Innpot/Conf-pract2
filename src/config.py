"""Чтение и проверка INI."""

import configparser
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

PACKAGE = re.compile(r"[a-z0-9][a-z0-9+.-]+")
TEST_PACKAGE = re.compile(r"[A-Z]+")
FIELDS = {"package", "repository", "test_mode", "ascii_tree", "exclude"}
FILTER = re.compile(r"[A-Za-z0-9+.-]*")


@dataclass(frozen=True)
class Config:
    """Параметры построения графа."""

    package: str
    repository: str
    test_mode: bool
    ascii_tree: bool
    exclude: str


def read_ini(path):
    """Прочитать ровно одну секцию graph с обязательными ключами."""
    parser = configparser.ConfigParser(interpolation=None)
    with path.open(encoding="utf-8-sig") as source:
        parser.read_file(source)
    if parser.sections() != ["graph"] or parser.defaults():
        raise ValueError("INI: ожидается только секция [graph]")
    section = parser["graph"]
    missing, extra = FIELDS - section.keys(), section.keys() - FIELDS
    if missing or extra:
        raise ValueError(
            f"INI: отсутствуют {sorted(missing)}, лишние {sorted(extra)}"
        )
    return section


def read_bool(section, key):
    """Прочитать логический ключ с диагностикой по имени."""
    try:
        return section.getboolean(key)
    except ValueError as error:
        raise ValueError(f"{key}: ожидается true или false") from error


def validate_url(value):
    """Проверить HTTP(S) URL без учётных данных и фрагмента."""
    try:
        url = urlsplit(value)
        url.port
        if (
            url.scheme in {"http", "https"} and url.hostname
            and not url.username and not url.password and not url.fragment
            and not any(char.isspace() for char in value)
        ):
            return
    except ValueError:
        pass
    raise ValueError("repository: ожидается HTTP(S) URL индекса Packages")


def resolve_repository(path, value, test_mode):
    """Проверить источник и раскрыть относительный путь от INI."""
    if not test_mode:
        validate_url(value)
        return value
    if not value:
        raise ValueError("repository: укажите файл тестового графа")
    source = (path.parent / value).resolve()
    if not source.is_file():
        raise ValueError(f"repository: файл не найден: {source}")
    return str(source)


def load_config(filename):
    """Собрать проверенную конфигурацию из файла."""
    path = Path(filename)
    section = read_ini(path)
    test_mode = read_bool(section, "test_mode")
    ascii_tree = read_bool(section, "ascii_tree")
    package = section["package"]
    if not (TEST_PACKAGE if test_mode else PACKAGE).fullmatch(package):
        raise ValueError("package: неверное имя для выбранного режима")
    exclude = section["exclude"]
    if not FILTER.fullmatch(exclude):
        raise ValueError("exclude: используйте латиницу, цифры, +, . или -")
    if exclude and exclude in package:
        raise ValueError("exclude: фильтр исключает корневой пакет")
    repository = resolve_repository(path, section["repository"], test_mode)
    return Config(package, repository, test_mode, ascii_tree, exclude)
