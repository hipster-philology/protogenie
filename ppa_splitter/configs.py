from typing import Dict, Optional, Any, Type
from yaml import load, dump
import os.path
import xml.etree.ElementTree as ET
from copy import deepcopy

from .splitters import PunctuationSplitter, LineSplitter, TokenWindowSplitter, FileSplitter, _SplitterPrototype
from .cli_utils import check_files
from .defaults import DEFAULT_CONFIG_VALUES
from .reader import Reader
from .postprocessing import Disambiguation

Splitter = Type[_SplitterPrototype]

class CorpusConfiguration:
    SPLITTERS = {
        "empty_line": LineSplitter,
        "punctuation": PunctuationSplitter,
        "token_window": TokenWindowSplitter,
        "file_split": FileSplitter
    }

    UNIT_NAMES = {
        "empty_line": "sentences",
        "punctuation": "sentences",
        "token_window": "token-windows",
        "file_split": "tokens"
    }

    COLUMN_SPECIAL_MARKERS = {
        "TAB": "\t"
    }
    REVERSE_COLUMN_SPECIAL_MARKERS = {
        character: name
        for name, character in COLUMN_SPECIAL_MARKERS.items()
    }

    def __init__(self,
                 reader: Reader,
                 splitter: str = "sentence_marker", **spliter_options):
        """ Initiate a configuration which will allow file-basis dispatching

        :param splitter: The splitter to use (Default : sentence_marker)
        :param sentence_markers: Characters to use for separating on sentence marker
        :param each_n_words:
        :param column_marker: Marker for columns in files
        """
        self.reader: Reader = reader
        self.splitter_name: str = splitter

        _spliter_options: Dict[str, Any] = deepcopy(DEFAULT_CONFIG_VALUES)
        _spliter_options.update(spliter_options)

        # Some characters are awful to replicate in YAML, that's why
        #  we have a dictionary of simplified names
        _spliter_options["column_marker"] = self.COLUMN_SPECIAL_MARKERS.get(
            _spliter_options["column_marker"],
            _spliter_options["column_marker"]
        )

        self.column_marker: str = _spliter_options["column_marker"]

        # We set up the splitter
        splitter_class: Optional[Type] = self.SPLITTERS.get(self.splitter_name, None)
        if splitter_class is None:
            raise ValueError("Splitter '{}' is not in the acceptable list: {}".format(
                self.splitter_name, ", ".join(list(self.SPLITTERS.keys()))
            ))
        # Initialize the splitter
        self.splitter: Splitter = splitter_class(**_spliter_options)

    def __repr__(self):
        return "<corpus column_marker='{column}'>{splitter}</corpus>".format(
            column=self.column_marker.replace("\t", "TAB"),
            splitter=self.splitter
        )

    @property
    def unit_name(self):
        return self.UNIT_NAMES[self.splitter_name]

    def splitter_reset(self):
        """ This function can be useful to reset a splitter in between passes
        """
        self.splitter.reset()

    def build_dataset_dispatch_list(self, units_count, test_ratio=0.2, dev_ratio=0.0001):
        """ Build a list of dataset target that will be used by the dispatching loop


        :param units_count: Number of units to dispatch (either sentence or dispatch depending on self.splitter)
        :param test_ratio: Ratio of data to be put in test
        :param dev_ratio: Ratio of data to be put in dev
        :return: List of dataset name targets (list of "train", "test" and "dev")
        """
        return self.splitter.dispatch(units_count, test_ratio=test_ratio, dev_ratio=dev_ratio)

    @classmethod
    def generate_blank(cls, target_files, yaml_file="empty.yaml", input_file=None):
        """ Generate a blank configuration with all necessary fields

        :param target_files: Which file should be configured by the yaml file
        :param yaml_file: Where to save the configuration
        :param input_file: Previously existing configuration that we want to reuse
        """
        files = check_files(target_files)
        config = {}

        if input_file:
            with open(input_file) as input_file_io:
                config.update(load(input_file_io))

        _default = deepcopy(DEFAULT_CONFIG_VALUES)
        _default["splitter"] = ",".join(sorted(list(CorpusConfiguration.SPLITTERS)))

        config = {
            file: deepcopy(_default)
            for file in files
            if file not in config
        }

        with open(yaml_file, "w") as f:
            dump(config, f, default_flow_style=False)


class PPAConfiguration:
    def __init__(self,
                 path: str,
                 corpora: Dict[str, CorpusConfiguration],
                 postprocessing=None,
                 memory: Optional[str] = None,
                 disambiguation: Optional[Disambiguation] = None,
                 **kwargs
                 ):
        self.path: str = path
        self.dir: str = os.path.abspath(os.path.dirname(path))

        self.memory: Optional[str] = memory
        self.corpora: Dict[str, CorpusConfiguration] = corpora
        self.disambiguation: Optional[Disambiguation] = disambiguation
        self.postprocessing = postprocessing

    @classmethod
    def from_xml(cls, filepath: str) -> "PPAConfiguration":
        with open(filepath) as f:
            xml = ET.parse(f)
        kwargs = {}

        # Get readers
        default_reader = Reader.from_xml(xml.find("./default-header/header"), default=None)

        # Parse corpora configurations
        corpora = {}
        for corpus in xml.findall("./corpora/corpus"):
            corpora[corpus.get("path")] = CorpusConfiguration(**{
                "column_marker": corpus.get("column_marker"),
                "splitter": corpus.find("splitter").get("name"),
                "reader": default_reader,
                **{key: value for key, value in corpus.find("splitter").attrib.items() if key != "name"}
            })

        # Check options
        if len(xml.findall("./memory")):
            kwargs["memory"] = xml.find("./memory").get("path")

        if len(xml.findall("./postprocessing/disambiguation")):
            kwargs["disambiguation"] = Disambiguation.from_xml(xml.find("./postprocessing/disambiguation"))

        return cls(path=filepath, corpora=corpora, **kwargs)
