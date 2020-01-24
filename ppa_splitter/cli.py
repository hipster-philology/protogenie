from argparse import ArgumentParser
import os
import sys
import shutil

from .defaults import DEFAULT_SENTENCE_MARKERS
from .configs import CorpusConfiguration, PPAConfiguration
from .dispatch import split_files
from .cli_utils import check_files, check_ratio


def generate_cli():
    cli = ArgumentParser(
        description="""This tool helps you to split PPA-formated output to training, testing and dev set
This tool expects your data to not have header."""
    )
    cli.add_argument("path", nargs="+", help="A unix wildcard or single file path, eg. 'pandora.tsv' or 'data/*.csv'")
    cli.add_argument("--output", default="empty.yaml", help="The Configuration file to write in")
    cli.add_argument("--input", default=None, help="An input file that has already some configurations in it")

    arguments = cli.parse_args()

    CorpusConfiguration.generate_blank(
        target_files=arguments.path,
        yaml_file=arguments.output,
        input_file=arguments.input
    )


def dispatch_cli():
    cli = ArgumentParser(
        description="""This tool helps you to split PPA-formated output to training, testing and dev set
    This tool expects your data to not have header."""
    )
    cli.add_argument("config", help="XML Config file")
    cli.add_argument("--train", default=0.8, type=float, help="Ratio of data to use for training")
    cli.add_argument("--test", default=0.2, type=float, help="Ratio of data to use for testing")
    cli.add_argument("--dev", default=0, type=float, help="Ratio of data to use for dev")
    cli.add_argument("--output", dest="output_dir", default="./output", help="Directory in which to save files")
    cli.add_argument("--clear", dest="clear", default=False, action="store_true",
                     help="Remove data in output directory (you'll need to confirm)")
    cli.add_argument("--concat", dest="concat", default=False, action="store_true",
                     help="Concat output in a single file")

    arguments = cli.parse_args()
    dispatch(**vars(arguments))


def dispatch(
        train: float, test: float, dev: float, config: str, output_dir: str,
        clear=False, verbose=True, concat: bool = False):

    train, test, dev = check_ratio(train, test, dev)
    config = PPAConfiguration.from_xml(config)

    if clear:
        confirm = ""
        confirm_message = "Are you sure you want to remove data in {} ? [y/n]\t>\t".format(output_dir)

        while confirm not in ["y", "n"]:
            confirm = input(confirm_message).lower()
            confirm_message = "Are you sure you want to remove data in {} ? [y/n] (your previous answer was wrong)" \
                              "\t>\t".format(output_dir)

        if confirm == "y":
            print("\tRemoving data in {}".format(output_dir))
            shutil.rmtree(output_dir, ignore_errors=True)
        else:
            print("\tData were not removed")

    os.makedirs(output_dir, exist_ok=True)
    for subset in ["dev", "test", "train"]:
        os.makedirs(os.path.join(output_dir, subset), exist_ok=True)

    print("=============")
    print("Processing...")
    # I run over each files
    for file, ratios in split_files(output_folder=output_dir, verbose=verbose, dev_ratio=dev, test_ratio=test,
                                    config=config):

        print("{} has been transformed".format(file))
        for key, value in ratios.items():
            if value:
                print("\t{} tokens in {} dataset".format(value, key))

    if concat:
        print("==============")
        print("Concatenating")
        for file, rations in group_files(
            files,
            output_folder=arguments.output,
            verbose=True,
                config=arguments.config
        ):
            print(file, rations)