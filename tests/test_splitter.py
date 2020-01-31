from unittest import TestCase
import os
import random
import glob
import csv
import contextlib, io
from typing import List, Tuple, Optional

from ppa_splitter.cli import dispatch

random.seed(78000)


class TestConfigs(TestCase):
    def setUp(self):
        self.verbose = False
        files = glob.glob("./tests/tests_output/**/*.*")
        for file in files:
            os.remove(file)

    def get_chunk_size(self, f):
        chunk_length = []
        start = False
        for line_no, line in enumerate(f):
            if line_no != 0:
                if line.strip():
                    if start is False:
                        start = line_no
                else:
                    if start is not False:
                        chunk_length.append(line_no-start)
                        start = False
        if start is not False:
            chunk_length.append(line_no - start)
        return chunk_length

    def open(self, directory, file: str) -> str:
        return open(self.path(directory, file))

    def path(self, directory: str, file: str) -> str:
        return "./tests/tests_output/"+directory+"/"+file

    def _dispatch(self, *args, **kwargs) -> str:
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            dispatch(*args, **kwargs)
        o = f.getvalue()
        if self.verbose:
            print(o)
        return o

    def parse_files(self, name: str, file_test: Optional = None) -> Tuple[List[int], List[int], List[int], List[int]]:
        chunk_length = []
        dev = []
        # Normally, we can expect with the random seed that nothing changed.
        with self.open("train", name) as f:
            content = f.read()
            if file_test:
                file_test(content)
            f.seek(0)
            train = self.get_chunk_size(f)
            chunk_length.extend(train)

        with self.open("test", name) as f:
            content = f.read()
            if file_test:
                file_test(content)
            f.seek(0)
            test = self.get_chunk_size(f)
            chunk_length.extend(test)

        if os.path.isfile(self.path("dev", name)):
            with self.open("dev", name) as f:
                content = f.read()
                if file_test:
                    file_test(content)
                f.seek(0)
                dev = self.get_chunk_size(f)
                chunk_length.extend(test)

        return chunk_length, train, test, dev

    def test_windows(self):
        output = self._dispatch(
            output_dir="./tests/tests_output/",
            clear=False,
            train=0.8,
            dev=0,
            test=0.2,
            config="./tests/test_config/window.xml"
        )

        def test_header(content):
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")

        chunk_length, train, test, _ = self.parse_files("window.tsv", file_test=test_header)

        self.assertEqual(
            chunk_length, sorted([20, 20, 20, 20, 20, 20, 20, 20, 20, 20]),
            "Chunks should always be the same size, and we have 200 tokens"
        )
        self.assertEqual(
            len(train) / len(test), 4,
            "20% of test for 80% of train, which makes 4 sequences of train for 1 of tests"
        )

    def test_windows_with_dev(self):
        output = self._dispatch(
            output_dir="./tests/tests_output/",
            clear=False,
            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/window.xml"
        )

        def test_header(content):
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")

        chunk_length, train, test, dev = self.parse_files("window.tsv", file_test=test_header)

        self.assertEqual(
            chunk_length, sorted([20, 20, 20, 20, 20, 20, 20, 20, 20, 20]),
            "Chunks should always be the same size, and we have 200 tokens"
        )
        self.assertEqual(
            len(train) / len(test), 8,
            "10% of test for 80% of train, which makes 8 sequence of train for 1 of tests"
        )
        self.assertEqual(
            len(train) / len(dev), 8,
            "10% of test for 80% of dev, which makes 8 sequence of train for 1 of dev"
        )

    def test_sentence(self):

        dispatch(
            output_dir="./tests/tests_output/",
            clear=False,
            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/sentence.xml"
        )
        chunk_length = []
        # Normally, we can expect with the random seed that nothing changed.
        with self.open("train", "sentence.tsv") as f:
            content = f.read()
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")
            f.seek(0)
            train = self.get_chunk_size(f)
            chunk_length.extend(train)

        with self.open("test", "sentence.tsv") as f:
            content = f.read()
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")
            f.seek(0)
            test = self.get_chunk_size(f)
            chunk_length.extend(test)

        with self.open("dev", "sentence.tsv") as f:
            content = f.read()
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")
            f.seek(0)
            dev = self.get_chunk_size(f)
            chunk_length.extend(test)

        self.assertEqual(
            chunk_length, [19]*10,
            "Chunks should always be the same size, and we have 190 tokens"
        )
        self.assertEqual(
            len(train) / len(test), 8,
            "10% of test for 80% of train, which makes 8 sequence of train for 1 of tests"
        )
        self.assertEqual(
            len(train) / len(dev), 8,
            "10% of test for 80% of dev, which makes 8 sequence of train for 1 of dev"
        )

    def test_empty_line(self):
        output = self._dispatch(
                output_dir="./tests/tests_output/",
                clear=False,
                train=0.8,
                dev=0.1,
                test=0.1,
                config="./tests/test_config/empty_line.xml"
            )

        self.assertIn("18 tokens in test dataset", output, "Empty lines should not be counted as tokens, "
                                                           "so it should be 18")
        self.assertIn("18 tokens in dev dataset", output, "Empty lines should not be counted as tokens, "
                                                          "so it should be 18")
        self.assertIn("144 tokens in train dataset", output, "Empty lines should not be counted as tokens, "
                                                             "so it should be 18")

        def test_header(content):
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")

        chunk_length, train, test, dev = self.parse_files("empty_line.tsv", file_test=test_header)

        self.assertEqual(
            chunk_length, [18]*10,
            "Chunks should always be the same size, and we have 180 tokens"
        )
        self.assertEqual(
            len(train) / len(test), 8,
            "10% of test for 80% of train, which makes 8 sequence of train for 1 of tests"
        )
        self.assertEqual(
            len(train) / len(dev), 8,
            "10% of test for 80% of dev, which makes 8 sequence of train for 1 of dev"
        )

    def test_file(self):
        """Test that splitting file works """
        output = self._dispatch(
            output_dir="./tests/tests_output/",
            clear=False,
            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/file.xml"
        )

        self.assertIn("17 tokens in test dataset", output, "Empty lines should not be counted as tokens, "
                                                          "so it should be 17*1 because 10%")
        self.assertIn("17 tokens in dev dataset", output, "Empty lines should not be counted as tokens, "
                                                          "so it should be 17*1 because 10%")
        self.assertIn("136 tokens in train dataset", output, "Empty lines should not be counted as tokens, "
                                                             "so it should be 17*10 because 80%")

        def test_header(content):
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")

        chunk_length, train, test, dev = self.parse_files("file.tsv", file_test=test_header)

        self.assertEqual(
            chunk_length, [136, 17, 17],
            "Chunks should always be the same size, and we have 170 tokens"
        )
        self.assertEqual(
            sum(train) / sum(test), 8,
            "10% of test for 80% of train, which makes 8 sequence of train for 1 of tests"
        )
        self.assertEqual(
            sum(train) / sum(dev), 8,
            "10% of test for 80% of dev, which makes 8 sequence of train for 1 of dev"
        )
