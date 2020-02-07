from .helpers import _TestHelper
from tempfile import mkstemp, TemporaryDirectory
from typing import Tuple
import os.path as p
import random
import glob
import filecmp

TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="protogeneia/schema.rng" schematypens="http://relaxng.org/ns/structure/1.0"?>
<config>
    <memory path="{memory}.csv" />
    <default-header>
        <header type="order">
            <key map-to="form">2</key>
            <key map-to="lemma">0</key>
            <key map-to="POS">1</key>
        </header>
    </default-header>
    <corpora>{corpora}</corpora>
</config>"""

DEFAULT_CORPUS = """
    <corpus path="../tests/test_data/roman_numbers.tsv" column_marker="TAB">
        <splitter name="empty_line"/>
        <header type="default" />
    </corpus>
"""


class TestMemory(_TestHelper):

    def create_config(self, memory: str, corpora: str, cur_dir: str) -> Tuple[str, str]:
        """ Create a temporary config files and return its filepath and the expected config file"""
        _, filepath = mkstemp(dir=cur_dir, suffix=".xml")
        memory_file = p.join(cur_dir, "memory"+memory)
        with open(filepath, "w") as file:
            file.write(TEMPLATE.format(
                memory=memory_file,
                corpora=corpora
            ))
        return filepath, memory_file

    def test_memory_created(self):
        """ Checks that the name is used for the memory file"""
        with TemporaryDirectory(dir="./") as cur_dir:
            """ Test some memory name"""
            filepath, memory_file = self.create_config(memory="", corpora=DEFAULT_CORPUS, cur_dir=cur_dir)
            self._dispatch(
                train=0.8,
                test=0.1,
                dev=0.1,
                config=filepath,
                output_dir=p.join(cur_dir, "output")
            )
            self.assertTrue(p.isfile(memory_file+".csv"), "A new file should have been created")

    def test_memory_name_form_file(self):
        """ Checks that $file$ is replaced during process """
        with TemporaryDirectory(dir="./") as cur_dir:
            """ Test some memory name"""
            filepath, memory_file = self.create_config(memory="$file$", corpora=DEFAULT_CORPUS, cur_dir=cur_dir)
            self._dispatch(
                train=0.8,
                test=0.1,
                dev=0.1,
                config=filepath,
                output_dir=p.join(cur_dir, "output")
            )

            name = p.splitext(p.basename(filepath))[0]  # [0] form splitext is everything but .xml
            self.assertTrue(p.isfile(memory_file.replace("$file$", name)+".csv"),
                            "A new file should have been created using the config file name")

    # ToDo: Check $date$ but honnestly parsing it is not like my ultimate goal... Wonder how to do that...

    def test_memory_content(self):
        """ This checks up that given a memory file, it is possible to recreate the same content """

        with TemporaryDirectory(dir="./") as cur_dir:
            """ Test some memory name"""
            random.seed(1111)
            config1, memory_file = self.create_config(memory="$file$", corpora=DEFAULT_CORPUS, cur_dir=cur_dir)
            output_dir_1 = p.join(cur_dir, "output")
            self._dispatch(
                train=0.8,
                test=0.1,
                dev=0.1,
                config=config1,
                output_dir=output_dir_1
            )
            name = p.splitext(p.basename(config1))[0]  # [0] form splitext is everything but .xml
            memory_file = memory_file.replace("$file$", name)+".csv"

            # At this point, we have a memory file at `memory`
            # What we need now is a new config, which will reuse the same file but with memory
            # JUST TO BE SURE, we reset the random seed
            random.seed(5555)
            with TemporaryDirectory(dir="./") as second_dir:
                """ Test some memory name"""
                config2, _ = self.create_config(memory="$file$", corpora=DEFAULT_CORPUS, cur_dir=second_dir)
                output_dir_2 = p.join(second_dir, "output")
                self._from_memory(memory_file=memory_file, config=config2, output_dir=output_dir_2)

                seen = 0
                for dataset_type in ["train", "dev", "test"]:
                    for original_file in glob.glob(p.join(output_dir_1, dataset_type, "*.*")):
                        base = p.basename(original_file)
                        created_from_memory = p.join(output_dir_2, dataset_type, base)
                        self.assertTrue(filecmp.cmp(original_file, created_from_memory),
                                        "File %s should be the same" % original_file)
                        seen += 1

                self.assertEqual(seen, 3, "With the current config, there should be three files produced")
