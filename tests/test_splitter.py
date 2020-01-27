from unittest import TestCase
from os import remove
import random
import glob
import csv

from ppa_splitter.cli import dispatch

random.seed(78000)


class TestConfigs(TestCase):
    def setUp(self):
        files = glob.glob("./tests/tests_output/**/*.*")
        for file in files:
            remove(file)

    def get_chunk_size(self, f):
        chunk_length = []
        start = False
        for line_no, line in enumerate(f):
            if line_no != 0:
                if line.strip():
                    if start is False:
                        start = line_no
                else:
                    chunk_length.append(line_no-start)
                    start = False
        if start is not False:
            chunk_length.append(line_no - start)
        return chunk_length

    def open(self, directory, file: str):
        return open("./tests/tests_output/"+directory+"/"+file)

    def test_windows(self):
        dispatch(
            output_dir="./tests/tests_output/",
            clear=False,
            train=0.8,
            dev=0,
            test=0.2,
            config="./tests/test_config/window.xml"
        )
        chunk_length = []
        # Normally, we can expect with the random seed that nothing changed.
        with self.open("train", "window.tsv") as f:
            content = f.read()
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")
            f.seek(0)
            train = self.get_chunk_size(f)
            chunk_length.extend(train)

        with self.open("test", "window.tsv") as f:
            content = f.read()
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")
            f.seek(0)
            test = self.get_chunk_size(f)
            chunk_length.extend(test)

        self.assertEqual(
            sorted(chunk_length), sorted([20, 20, 20, 20, 20, 20, 20, 20, 20, 20]),
            "Chunks should always be the same size, and we have 200 tokens"
        )
        self.assertEqual(
            len(train) / len(test), 4,
            "20% of test for 80% of train, which makes 4 sequences of train for 1 of tests"
        )

    def test_windows_with_dev(self):
        dispatch(
            output_dir="./tests/tests_output/",
            clear=False,
            train=0.8,
            dev=0.1,
            test=0.1,
            config="./tests/test_config/window.xml"
        )
        chunk_length = []
        # Normally, we can expect with the random seed that nothing changed.
        with self.open("train", "window.tsv") as f:
            content = f.read()
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")
            f.seek(0)
            train = self.get_chunk_size(f)
            chunk_length.extend(train)

        with self.open("test", "window.tsv") as f:
            content = f.read()
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")
            f.seek(0)
            test = self.get_chunk_size(f)
            chunk_length.extend(test)

        with self.open("dev", "window.tsv") as f:
            content = f.read()
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")
            f.seek(0)
            dev = self.get_chunk_size(f)
            chunk_length.extend(test)

        self.assertEqual(
            sorted(chunk_length), sorted([20, 20, 20, 20, 20, 20, 20, 20, 20, 20]),
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
            sorted(chunk_length), sorted([19]*10),
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


