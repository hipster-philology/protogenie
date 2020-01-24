from unittest import TestCase
from os import remove, makedirs
import glob

from ppa_splitter.cli import dispatch


class TestConfigs(TestCase):
    def setUp(self):
        makedirs("./tests/tests_output/train", exist_ok=True)
        makedirs("./tests/tests_output/dev", exist_ok=True)
        makedirs("./tests/tests_output/test", exist_ok=True)
        files = glob.glob("./tests/tests_output/**/*.*")
        for file in files:
            remove(file)

    def test_windows(self):
        dispatch(
            output_dir="./tests/tests_output/",
            clear=False,
            train=0.8,
            dev=0,
            test=0.2,
            config="./tests/test_config/window.xml"
        )
