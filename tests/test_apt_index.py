"""Проверки чтения индекса deb822."""

import gzip
import lzma
import unittest
from io import BytesIO
from unittest.mock import patch

from src.apt_index import decode_index, direct_dependencies, fetch_index

INDEX = b"""Package: hello
Pre-Depends: libc6 (>= 2.34)
Depends: foo:any | bar, libc6,
 baz (= 1:2.3-4)
Recommends: optional
Description: example
 long description

Package: foo
Version: 2
"""


class IndexTests(unittest.TestCase):
    def test_compression_and_alternatives(self):
        for encode in (bytes, gzip.compress, lzma.compress):
            with self.subTest(encode=encode):
                index = decode_index(encode(INDEX))
                self.assertEqual(
                    index, {"hello": ("libc6", "foo", "bar", "baz"),
                            "foo": ()}
                )

    def test_http_reader(self):
        with patch("src.apt_index.urlopen", return_value=BytesIO(INDEX)):
            index = fetch_index("https://example.org/Packages")
        self.assertEqual(direct_dependencies(index, "foo"), ())
        with self.assertRaisesRegex(ValueError, "absent"):
            direct_dependencies(index, "absent")

    def test_bad_index(self):
        for data in (b"", b"invalid", b"Package: hello\nDepends: ***\n",
                     INDEX + b"\nPackage: hello\n"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                decode_index(data)
