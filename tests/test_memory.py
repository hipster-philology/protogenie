from .helpers import _TestHelper
from tempfile import mkstemp, TemporaryDirectory
from typing import Tuple
import os.path as p
import random
import glob
import filecmp

from protogenie.dispatch import ConfigError

TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="protogeneia/schema.rng" schematypens="http://relaxng.org/ns/structure/1.0"?>
<config>
    <output column_marker="TAB" />
    {postprocessing}
    <memory path="{memory}.csv" />
    <default-header>
        <header type="explicit">
            <key map-to="form">tok</key>
            <key map-to="lemma">lem</key>
            <key map-to="POS">pos</key>
        </header>
    </default-header>
    <corpora>{corpora}</corpora>
</config>"""

DEFAULT_CORPUS = """
    <corpus path="../tests/test_data/roman_numbers.tsv" column_marker="TAB">
        <splitter name="empty_line"/>
        <header type="order">
            <key map-to="form">2</key>
            <key map-to="lemma">0</key>
            <key map-to="POS">1</key>
        </header>
    </corpus>
"""

DEFAULT_PROCESSING = """<postprocessing>
    <toolbox name="RomanNumeral">
        <applyTo source="form">
            <target>form</target>
            <target>lemma</target>
        </applyTo>
    </toolbox>
</postprocessing>"""


class TestMemory(_TestHelper):

    def create_config(self, memory: str, corpora: str, cur_dir: str, postprocessing: str = "") -> Tuple[str, str]:
        """ Create a temporary config files and return its filepath and the expected config file"""
        _, filepath = mkstemp(dir=cur_dir, suffix=".xml")
        memory_file = p.join(cur_dir, "memory"+memory)
        with open(filepath, "w") as file:
            file.write(TEMPLATE.format(
                memory=memory_file,
                corpora=corpora,
                postprocessing=postprocessing
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

    def test_memory_content_with_post_proc(self):
        """ Checks that postprocessing is carried the same way on memorized file """

        with TemporaryDirectory(dir="./") as cur_dir:
            """ Test some memory name"""
            random.seed(1111)
            config1, memory_file = self.create_config(memory="$file$", corpora=DEFAULT_CORPUS, cur_dir=cur_dir,
                                                      postprocessing=DEFAULT_PROCESSING)
            output_dir_1 = p.join(cur_dir, "output")
            self._dispatch(
                train=0.8,
                test=0.1,
                dev=0.1,
                config=config1,
                output_dir=output_dir_1
            )
            name = p.splitext(p.basename(config1))[0]  # [0] form splitext is everything but .xml
            memory_file = memory_file.replace("$file$", name) + ".csv"

            # At this point, we have a memory file at `memory`
            # What we need now is a new config, which will reuse the same file but with memory
            # JUST TO BE SURE, we reset the random seed
            random.seed(5555)
            with TemporaryDirectory(dir="./") as second_dir:
                """ Test some memory name"""
                config2, _ = self.create_config(memory="$file$", corpora=DEFAULT_CORPUS, cur_dir=second_dir,
                                                      postprocessing=DEFAULT_PROCESSING)
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

            random.seed(9999)
            with TemporaryDirectory(dir="./") as third_dir:
                # On the other end, if we do not have post-processing, things that are not roman number
                #   should be the same, but roman number should differ
                config2, _ = self.create_config(memory="$file$", corpora=DEFAULT_CORPUS, cur_dir=third_dir)
                output_dir_2 = p.join(third_dir, "output")
                self._from_memory(memory_file=memory_file, config=config2, output_dir=output_dir_2)

                seen = 0
                for dataset_type in ["train", "dev", "test"]:
                    for original_file in glob.glob(p.join(output_dir_1, dataset_type, "*.*")):
                        base = p.basename(original_file)
                        created_from_memory = p.join(output_dir_2, dataset_type, base)
                        self.assertFalse(
                            filecmp.cmp(original_file, created_from_memory),
                            "File %s should differ" % original_file)
                        seen += 1
                        lines = 0
                        with open(original_file) as orig:
                            with open(created_from_memory) as copy:
                                for line1, line2 in zip(orig.readlines(), copy.readlines()):
                                    if line1.strip():  # If we do not have an empty line
                                        (_, pos1, _), (_, pos2, _) = line1.split(), line2.split()
                                        if pos1 == "RomNum" and pos2 == "RomNum":
                                            self.assertNotEqual(line1, line2, "Lemma and token should be different")
                                        else:
                                            self.assertEqual(line1, line2, "Lines that do not contain roman numer"
                                                                           "should be the same.")
                                        lines += 1

                self.assertEqual(seen, 3, "With the current config, there should be three files produced")
                self.assertNotEqual(lines, 0, "There should be more than one line")

    def test_memory_content_multiple_files(self):
        """ This checks up that given a memory file, it is possible to recreate the same content on multiple files"""
        newcorpus = DEFAULT_CORPUS + """<corpus path="../tests/test_data/sentence.tsv" column_marker="TAB">""" \
                                        """<splitter name="regexp"><option matchPattern="[\.:?!]"/></splitter> """ \
                                        """<header type="default" /></corpus>"""
        with TemporaryDirectory(dir="./") as cur_dir:
            random.seed(1111)
            config1, memory_file = self.create_config(
                memory="$file$",
                corpora=newcorpus,
                cur_dir=cur_dir,
                postprocessing=DEFAULT_PROCESSING
            )
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
                config2, _ = self.create_config(
                    memory="$file$", corpora=newcorpus, cur_dir=second_dir,
                    postprocessing=DEFAULT_PROCESSING
                )
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

                self.assertEqual(seen, 6, "With the current config, there should be 6 files produced")

    def test_memory_content_multiple_files_plus_new_file(self):
        """ This checks up that given a memory file, new files are otherwise dispatched """

        newcorpus = DEFAULT_CORPUS + """<corpus path="../tests/test_data/sentence.tsv" column_marker="TAB">""" \
                                    """<splitter name="regexp"><option matchPattern="[\.:?!]"/></splitter> """ \
                                        """<header type="default" /></corpus>"""

        secondcorpus = newcorpus + """<corpus path="../tests/test_data/file.tsv" column_marker="TAB">""" \
                                        """<splitter name="file_split"/>""" \
                                        """<header type="default" /></corpus>"""

        with TemporaryDirectory(dir="./") as cur_dir:
            random.seed(1111)
            config1, memory_file = self.create_config(
                memory="$file$",
                corpora=newcorpus,
                cur_dir=cur_dir,
                postprocessing=DEFAULT_PROCESSING
            )
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
                config2, _ = self.create_config(
                    memory="$file$$date$", corpora=secondcorpus, cur_dir=second_dir,
                    postprocessing=DEFAULT_PROCESSING
                )
                output_dir_2 = p.join(second_dir, "output")

                with self.assertRaises(ConfigError):
                    """New files without ratios should crash """
                    self._from_memory(memory_file=memory_file, config=config2, output_dir=output_dir_2)

            with TemporaryDirectory(dir="./") as second_dir:
                """ Test some memory name"""
                config2, _ = self.create_config(
                    memory="$file$$date$", corpora=secondcorpus, cur_dir=second_dir,
                    postprocessing=DEFAULT_PROCESSING
                )
                output_dir_2 = p.join(second_dir, "output")
                self._from_memory(memory_file=memory_file, config=config2, output_dir=output_dir_2,
                                  test_ratio=0.2, dev_ratio=0.1)

                seen = 0
                similar = 0
                for dataset_type in ["train", "dev", "test"]:
                    for created_from_memory in glob.glob(p.join(output_dir_2, dataset_type, "*.*")):
                        base = p.basename(created_from_memory)
                        original_file = p.join(output_dir_1, dataset_type, base)
                        if base != "file.tsv":
                            self.assertTrue(filecmp.cmp(original_file, created_from_memory),
                                            "File %s should be the same" % original_file)
                            similar += 1
                        seen += 1

                self.assertEqual(seen, 9, "9 files should be produced")
                self.assertEqual(similar, 6, "6 of them are mirrored")
