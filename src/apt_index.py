"""Чтение индекса Ubuntu Packages без APT и сторонних библиотек."""

import gzip
import lzma
import re
from io import BytesIO, TextIOWrapper
from urllib.request import urlopen

from .config import PACKAGE

HTTP_TIMEOUT = 30
RELATION = re.compile(
    rf"({PACKAGE.pattern})(?::[a-z0-9-]+)?(?:\s+\([^()]+\))?"
)
RELATION_FIELDS = ("Pre-Depends", "Depends")


def paragraphs(lines):
    """Читать абзацы формата deb822 с продолжениями полей."""
    fields = {}
    key = None
    for raw in lines:
        line = raw.rstrip("\r\n")
        if not line.strip():
            if fields:
                yield fields
                fields = {}
                key = None
        elif line[0].isspace() and key is not None:
            fields[key] += " " + line.strip()
        else:
            key, colon, value = line.partition(":")
            if not colon or not key or any(c.isspace() for c in key):
                raise ValueError("Некорректное поле в индексе Packages")
            fields[key] = value.strip()
    if fields:
        yield fields


def relation_names(expression):
    """Вернуть имена всех альтернатив без версии и архитектуры."""
    for term in re.split(r"[,|]", expression):
        match = RELATION.fullmatch(term.strip())
        if not match:
            raise ValueError(f"Некорректная зависимость: {term.strip()}")
        yield match[1]


def dependencies(fields):
    """Объединить Pre-Depends и Depends, удалив дубликаты."""
    names = (
        name
        for field in RELATION_FIELDS if fields.get(field)
        for name in relation_names(fields[field])
    )
    return tuple(dict.fromkeys(names))


def parse_index(lines):
    """Создать отображение пакет → прямые зависимости."""
    index = {}
    for fields in paragraphs(lines):
        package = fields.get("Package", "")
        if not PACKAGE.fullmatch(package):
            raise ValueError("Некорректное имя Package в индексе")
        if package in index:
            raise ValueError(f"В индексе повторяется пакет {package}")
        index[package] = dependencies(fields)
    if not index:
        raise ValueError("Индекс Packages пуст")
    return index


def decode_index(payload):
    """Распаковать XZ/GZIP по сигнатуре или прочитать обычный UTF-8."""
    if payload.startswith(b"\xfd7zXZ\x00"):
        stream = lzma.LZMAFile(BytesIO(payload))
    elif payload.startswith(b"\x1f\x8b"):
        stream = gzip.GzipFile(fileobj=BytesIO(payload))
    else:
        stream = BytesIO(payload)
    with TextIOWrapper(stream, encoding="utf-8") as source:
        return parse_index(source)


def fetch_index(url):
    """Загрузить и разобрать конкретный индекс Packages по HTTP(S)."""
    with urlopen(url, timeout=HTTP_TIMEOUT) as response:
        return decode_index(response.read())


def direct_dependencies(index, package):
    """Найти пакет, не смешивая его отсутствие с пустым списком."""
    if package not in index:
        raise ValueError(f"Пакет {package} не найден в индексе")
    return index[package]
