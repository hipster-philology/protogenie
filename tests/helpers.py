from unittest import TestCase
import os
import glob
import contextlib
import io
import csv
from typing import List, Tuple, Optional, Generator, Dict

from protogenie.cli import dispatch, from_memory
from protogenie.configs import ProtogenieConfiguration
from os import getenv


class _TestHelper(TestCase):
    output_dir = "./tests/test_config/"
    def setUp(self):
        self.verbose = getenv("VERBOSE_TESTS", "0") == "1"  # Allows for more debugging during tests
        files = glob.glob("./tests/tests_output/**/*.*")
        for file in files:
            os.remove(file)
        try:
            os.remove("memory.csv")
        except:
            pass

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

    def _dispatch(self, *args, **kwargs) -> Tuple[str, ProtogenieConfiguration]:
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            config = dispatch(*args, **kwargs)
        o = f.getvalue()
        if self.verbose:
            print(o)
        return o, config

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

    def read_file(self, directory: str, filename: str, delimiter: str = "\t") -> Generator[Dict[str, str], None, None]:
        with open(self.path(directory, filename)) as f:
            header = []
            for line_no, line in enumerate(csv.reader(f, delimiter=delimiter)):
                if line_no == 0:
                    header = line
                else:
                    yield dict(zip(header, line))

    def _from_memory(self, memory_file: str, config: str, output_dir: str, **kwargs) -> ProtogenieConfiguration:
        return from_memory(memory_file, config, output_dir, **kwargs)
