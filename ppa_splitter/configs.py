from yaml import load, dump
from copy import deepcopy

from .splitters import PunctuationSplitter, LineSplitter, TokenWindowSplitter, FileSplitter
from .cli_utils import check_files
from .defaults import DEFAULT_CONFIG_VALUES


class Configuration:
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
                 splitter="sentence_marker", **spliter_options):
        """ Initiate a configuration which will allow file-basis dispatching

        :param splitter: The splitter to use (Default : sentence_marker)
        :param sentence_markers: Characters to use for separating on sentence marker
        :param each_n_words:
        :param column_marker: Marker for columns in files
        """
        self.splitter_name = splitter

        _spliter_options = deepcopy(DEFAULT_CONFIG_VALUES)
        _spliter_options.update(spliter_options)

        # Some characters are awful to replicate in YAML, that's why
        #  we have a dictionary of simplified names
        _spliter_options["column_marker"] = self.COLUMN_SPECIAL_MARKERS.get(
            _spliter_options["column_marker"],
            _spliter_options["column_marker"]
        )

        # We set up the splitter
        self.splitter = self.SPLITTERS.get(self.splitter_name, None)
        if self.splitter is None:
            raise ValueError("Splitter '{}' is not in the acceptable list: {}".format(
                self.splitter_name, ", ".join(list(self.SPLITTERS.keys()))
            ))
        # Initialize the splitter
        self.splitter = self.splitter(**_spliter_options)

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
                    **obj
                )
                for filename, obj in data.items()
            }

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
        _default["splitter"] = ",".join(sorted(list(Configuration.SPLITTERS)))

        config = {
            file: deepcopy(_default)
            for file in files
            if file not in config
        }

        with open(yaml_file, "w") as f:
            dump(config, f, default_flow_style=False)
