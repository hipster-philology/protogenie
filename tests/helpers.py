from unittest import TestCase
import os
import glob
import contextlib, io
from typing import List, Tuple, Optional

from ppa_splitter.cli import dispatch


class _TestHelper(TestCase):
    def setUp(self):
        self.verbose = True
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