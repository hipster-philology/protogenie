from yaml import load, dump
from .splitters import sentence_line_splitter_maker, empty_line_splitter, BatchLineSplitter
from .dispatch import check_files


class Configuration:

    SPLITTERS = {
        "empty": empty_line_splitter,
        "sentence_marker": sentence_line_splitter_maker,
        "batch": BatchLineSplitter
    }

    def __init__(self, splitter="empty", markers="", each_n_words=20):
        """

        :param splitter: The splitter to use (Default : empty)
        :param markers:
        :param each_n_words:
        """

    @classmethod
    def from_yaml(cls, yaml_file):
        with open(yaml_file) as f:
            data = load(f)
            return {

            }

    @staticmethod
    def generate_blank(target_files, yaml_file="empty.yaml", input_file=None):
        files = check_files(target_files)
        config = {
            file: {
                "splitter": ",".join(sorted(list(Configuration.SPLITTERS))),
                "markers": ";,",
                "each_n_words": 20
            }
            for file in files
        }
        if input_file:
            with open(input_file) as input_file_io:
                config.update(load(input_file_io))

        with open(yaml_file, "w") as f:
            dump(config, f, default_flow_style=False)

