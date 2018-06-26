from argparse import ArgumentParser
from glob import glob
import os
import sys
import random
import math

def add_sentence(output_folder, dataset, filename, sentence):
    with open(os.path.join(output_folder, dataset, filename), "wa") as f:
        f.write("\n".join(sentence))


def run(files, output_folder, dev_ratio, test_ratio, col_marker, sentence_splitter, verbose=False):
    def in_line(line):
        return bool(len([
            1
            for token in line.split(col_marker)
            if token in sentence_splitter
        ]))

    for file in files:
        sentence_count = 0
        lines = 0
        with open(file) as f:
            for line in f:
                sentence_count += int(in_line(line))
                lines += 1

        # If the sentence count is 0, we switch to random batch of X words
        if sentence_count:
            def in_line()

        if verbose:
            print("{} sentences in {}".format(file, sentence_count))

        train_number = sentence_count
        dev_number = 0
        if dev_ratio > 0.01:
            dev_number = int(math.ceil(dev_ratio * sentence_count))
            train_number = train_number - dev_number
        test_number = int(math.ceil(test_ratio * sentence_count))
        train_number = train_number - test_number

        target = ["test"] * test_number + ["train"] * train_number + ["dev"] * dev_number
        training_tokens = {"test": 0, "dev": 0, "train": 0}
        random.shuffle(target)

        with open(file) as f:
            sentence = []
            for line in f:
                sentence.append(line)
                if in_line(line):
                    dataset = target.pop()
                    add_sentence(
                        output_folder=output_folder,
                        dataset=dataset,
                        filename=file,
                        sentence=sentence
                    )
                    training_tokens[dataset] += len(sentence)
                    sentence = []

        yield file, training_tokens


def check_files(path):
    """ Check that there is files

    :param path: Path for a single or multiple files
    :return: List of files to process
    """
    if os.path.isfile(path):
        data = [path]
    else:
        data = list(glob(path))
    if len(data):
        return data
    raise ValueError("No files were found at {}".format(path))


def check_ratio(train, test, dev):
    """ Check and adapt ratios from user input in case the sum is over 1.
    Current behavior is to scale done train.

    :param train: Training dataset ratio
    :param test: Testing dataset ratio
    :param dev: Dev dataset ratio
    :return: Train, test, dev
    """
    if train + test + dev > 1.0:
        train = 1.0 - test - dev
        print("Ratios are over 1, scaling down train ratio to {}".format(train))
    return train, test, dev


if __name__ == "__main__":
    cli = ArgumentParser(
        description="""This tool helps you to split PPA-formated output to training, testing and dev set
This tool expects your data to not have header."""
    )
    cli.add_argument("path", help="A unix wildcard or single file path, eg. 'pandora.tsv' or 'data/*.csv'")
    cli.add_argument("--train", default=0.8, type=float, help="Ratio of data to use for training")
    cli.add_argument("--test", default=0.2, type=float, help="Ratio of data to use for testing")
    cli.add_argument("--dev", default=0, type=float, help="Ratio of data to use for dev")
    cli.add_argument("--col", dest="col_marker",
                     default="\t", help="Column that contains the form token (Default is TAB)")
    cli.add_argument("--output", default="./output", help="Directory in which to save files")
    cli.add_argument("--sentence", dest="sentence_marker", default=".;", help="Directory in which to save files")

    # Issue when

    arguments = cli.parse_args()

    train, test, dev = check_ratio(arguments.train, arguments.test, arguments.dev)

    try:
        files = check_files(arguments.path)
    except ValueError:
        print("There is no such files")
        sys.exit(0)

    os.makedirs(arguments.output, exist_ok=True)
    for subset in ["dev", "test", "train"]:
        os.makedirs(os.path.join(arguments.output, subset), exist_ok=True)

    for file, ratios in run(
            files,
            output_folder=arguments.output, verbose=True,
            col_marker=arguments.col_marker, sentence_splitter=arguments.sentence_marker):
        print("{} has been transformed".format(file))
        for key, value in ratios:
            if value:
                print("\t{} tokens in {} dataset".format(value, key))
