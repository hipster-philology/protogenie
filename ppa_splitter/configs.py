from yaml import load, dump
import math
import random

from .splitters import sentence_line_splitter_maker, empty_line_splitter, TokenWindowSplitter
from ppa_splitter.cli_utils import check_files


class Configuration:

    SPLITTERS = {
        "empty": empty_line_splitter,
        "sentence_marker": sentence_line_splitter_maker,
        "token_window": TokenWindowSplitter
    }

    DISPATCH_BUILDER = {
        "empty": "_full_random_dispatch",
        "sentence_marker": "_full_random_dispatch",
        "token_window": "_full_random_dispatch"
    }

    UNIT_NAMES = {
        "empty": "sentences",
        "sentence_marker": "sentences",
        "token_window": "token-windows"
    }

    DEFAULT_COLUMN_MARKER = "TAB"
    COLUMN_SPECIAL_MARKERS = {
        "TAB": "\t"
    }
    REVERSE_COLUMN_SPECIAL_MARKERS = {
        character: name
        for name, character in COLUMN_SPECIAL_MARKERS.items()
    }

    def __init__(self,
                 splitter="sentence_marker", sentence_markers=";.", each_n_words=20,
                 column_marker=DEFAULT_COLUMN_MARKER):
        """ Initiate a configuration which will allow file-basis dispatching

        :param splitter: The splitter to use (Default : empty)
        :param sentence_markers:
        :param each_n_words:
        :param column_marker: Marker for columns in files
        """
        self.splitter_name = splitter
        self.sentence_markers = sentence_markers
        self.each_n_words = each_n_words

        # Some characters are awful to replicate in YAML, that's why
        #  we have a dictionary of simplified names
        self.column_marker = self.COLUMN_SPECIAL_MARKERS.get(column_marker, column_marker)

        # We set up the splitter
        self.splitter = self.SPLITTERS.get(self.splitter_name, None)
        if self.splitter is None:
            raise ValueError("Splitter '{}' is not in the acceptable list: {}".format(
                self.splitter_name, ", ".join(list(self.SPLITTERS.keys()))
            ))
        # Some splitters need to be reconfigured after
        if self.splitter_name == "sentence_line_splitter_maker":
            # This splitter is a function generator, we need to pass it a value
            self.splitter = self.splitter(
                col_marker=self.column_marker,
                sentence_splitter=self.sentence_markers
            )
        elif self.splitter_name == "token_window":
            self.splitter = self.splitter(each_n_words=self.each_n_words)

        self.list_builder = getattr(self, self.DISPATCH_BUILDER[self.splitter_name])

    @property
    def unit_name(self):
        return self.UNIT_NAMES[self.splitter_name]

    @staticmethod
    def _full_random_dispatch(units_count, test_ratio=0.2, dev_ratio=0.0001):
        """ Get the ratios and builds a list of targets completely randomly and shuffled

        :param units_count: Number of units to dispatch (either sentence or dispatch depending on self.splitter)
        :param test_ratio: Ratio of data to be put in test
        :param dev_ratio: Ratio of data to be put in dev
        :return: List of dataset to dispatch to
        """

        train_number = units_count
        dev_number = 0
        if dev_ratio > 0.01:
            dev_number = int(math.ceil(dev_ratio * units_count))
            train_number = train_number - dev_number
        test_number = int(math.ceil(test_ratio * units_count))
        train_number = train_number - test_number

        print(test_number, train_number, dev_number)
        target_dataset = ["test"] * test_number + ["train"] * (train_number + 1) + ["dev"] * dev_number
        random.shuffle(target_dataset)
        return target_dataset

    def build_dataset_dispatch_list(self, units_count, test_ratio=0.2, dev_ratio=0.0001):
        """ Build a list of dataset target that will be used by the dispatching loop


        :param units_count: Number of units to dispatch (either sentence or dispatch depending on self.splitter)
        :param test_ratio: Ratio of data to be put in test
        :param dev_ratio: Ratio of data to be put in dev
        :return:
        """
        return self.list_builder(units_count, test_ratio=test_ratio, dev_ratio=dev_ratio)

    @classmethod
    def from_yaml(cls, yaml_file):
        """ Read a YAML PPA-Splitter configuration file

        :param yaml_file: Path to the YAML file to read
        :return: {File: Configuration} dict
        :rtype: {str: Configuration}
        """
        with open(yaml_file) as f:
            data = load(f)
            return {
                filename: cls(
                    splitter=obj["splitter"],
                    sentence_markers=obj["sentence_markers"],
                    each_n_words=obj["each_n_words"]
                )
                for filename, obj in data.items()
            }

    @classmethod
    def generate_blank(cls, target_files, yaml_file="empty.yaml", input_file=None):
        files = check_files(target_files)
        config = {
            file: {
                "splitter": ",".join(sorted(list(Configuration.SPLITTERS))),
                "sentence_markers": ";,",
                "each_n_words": 20,
                "column_marker": cls.DEFAULT_COLUMN_MARKER
            }
            for file in files
        }
        if input_file:
            with open(input_file) as input_file_io:
                config.update(load(input_file_io))

        with open(yaml_file, "w") as f:
            dump(config, f, default_flow_style=False)
