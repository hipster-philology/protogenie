from argparse import ArgumentParser
import os
import shutil

from .configs import PPAConfiguration
from .dispatch import split_files, files_from_memory
from .cli_utils import check_ratio

import click

@click.group()
def main():
    """Protogeneia is a tool to preprocess and harmonize datasets in NLP tasks. Might be useful for other stuff too
    as long as you have TSV/CSV ;)"""
    pass


@main.command("get-scheme")
@click.argument("dest", type=click.Path(file_okay=True, dir_okay=True), default="./scheme.rng")
def cli_scheme(dest):
    """Copy the schema file to [WHERE]"""
    import os
    import shutil
    here = os.path.abspath(os.path.dirname(__file__))
    schema = os.path.join(here, "schema.rng")
    shutil.copy(schema, dest)
    click.echo("Copied to {}".format(os.path.abspath(dest)))


@main.command("dispatch")
@click.argument("file", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option("--output", default="./output", type=str, help="Directory where the output should be built")
@click.option("-c", "--clear", default=False, is_flag=True, help="Clear the output directory")
@click.option("-t", "--train", "train", default=0.8, type=float, help="Percentage of data to use for training")
@click.option("-d", "--dev", "dev", default=0., type=float, help="Percentage of data to use for dev set")
@click.option("-e", "--test", "test", default=0.2, type=float, help="Percentage of data to use for test set")
def cli_dispatch(file, output, clear=False, train=0.8, dev=.0, test=0.2):
    """ Uses [FILE] to split and pre-process a training corpus for NLP Tasks. File should follow the schema, see
    protogeneia get-scheme"""

    if clear:
        confirm_message = "Are you sure you want to remove data in {} ? [y/n]\t>\t".format(output)

        if click.confirm(confirm_message):
            click.echo("\tRemoving data in {}".format(output))
            shutil.rmtree(output, ignore_errors=True)
        else:
            print("\tData were not removed")
    dispatch(
        config=file,
        train=train,
        test=test,
        dev=dev,
        output_dir=output
    )


def dispatch(
        train: float, test: float, dev: float, config: str, output_dir: str,
        verbose=True, concat: bool = False) -> PPAConfiguration:
    """

    :param train:
    :param test:
    :param dev:
    :param config:
    :param output_dir:
    :param verbose:
    :param concat:
    :return: PPAConfiguration for test purposes
    """

    train, test, dev = check_ratio(train, test, dev)
    config = PPAConfiguration.from_xml(config)

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

    return config


def from_memory(memory_file: str, config: str, output_dir: str) -> PPAConfiguration:
    config = PPAConfiguration.from_xml(config)

    os.makedirs(output_dir, exist_ok=True)
    for subset in ["dev", "test", "train"]:
        os.makedirs(os.path.join(output_dir, subset), exist_ok=True)

    for file, ratios in files_from_memory(config=config, memory_file=memory_file, output_folder=output_dir):
        print("{} has been transformed".format(file))
        for key, value in ratios.items():
            if value:
                print("\t{} tokens in {} dataset".format(value, key))

    return config