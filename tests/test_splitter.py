from unittest import TestCase
import os
import random
import glob
import csv
import contextlib, io
from typing import List, Tuple, Optional
from .helpers import _TestHelper
from protogeneia.cli import dispatch

random.seed(78000)


class TestConfigs(_TestHelper):
    def test_windows(self):
        output = self._dispatch(
            output_dir="./tests/tests_output/",

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
        self._dispatch(
            output_dir="./tests/tests_output/",

            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/sentence.xml"
        )

        def test_header(content):
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")

        chunk_length, train, test, dev = self.parse_files("sentence.tsv", file_test=test_header)

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

    def test_implicit_header(self):
        """Test that implicit header mapping is correct"""
        output = self._dispatch(
            output_dir="./tests/tests_output/",

            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/implicit.xml"
        )

        self.assertIn("16 tokens in test dataset", output, "Empty lines should not be counted as tokens, "
                                                          "so it should be 16*1 because 10%")
        self.assertIn("16 tokens in dev dataset", output, "Empty lines should not be counted as tokens, "
                                                          "so it should be 16*1 because 10%")
        self.assertIn("128 tokens in train dataset", output, "Empty lines should not be counted as tokens, "
                                                             "so it should be 16*8 because 80%")

        def test_header(content):
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")

        chunk_length, train, test, dev = self.parse_files("implicit.tsv", file_test=test_header)

        self.assertEqual(
            chunk_length, [16*8, 16, 16],
            "Chunks should always be the same size, and we have 160 tokens"
        )
        self.assertEqual(
            sum(train) / sum(test), 8,
            "10% of test for 80% of train, which makes 8 sequence of train for 1 of tests"
        )
        self.assertEqual(
            sum(train) / sum(dev), 8,
            "10% of test for 80% of dev, which makes 8 sequence of train for 1 of dev"
        )
