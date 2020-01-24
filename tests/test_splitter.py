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
            chunk_length.extend(self.get_chunk_size(f))

        with self.open("test", "window.tsv") as f:
            content = f.read()
            self.assertFalse(content.startswith("lem\t"), "The header should not have been kept")
            self.assertTrue(content.startswith("lemma\tPOS\ttoken"), "Header should have been mapped")
            f.seek(0)
            chunk_length.extend(self.get_chunk_size(f))

        self.assertEqual(
            sorted(chunk_length), sorted([20, 20, 20, 20, 20, 20, 20, 20, 20, 20]),
            "Chunks should always be the same size, and we have 200 tokens"
        )
