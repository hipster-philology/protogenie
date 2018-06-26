from glob import glob
import os
import random
import math

from .splitters import sentence_line_splitter_maker, empty_line_splitter, BatchLineSplitter
from .io_utils import add_sentence


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


def run(files, output_folder, dev_ratio, test_ratio, col_marker, sentence_splitter, verbose=False):

    for file in files:
        in_line = sentence_line_splitter_maker(col_marker, sentence_splitter)
        in_line = empty_line_splitter
        in_line = (BatchLineSplitter(each_n_words=20)).split
        sentence_count = 0
        lines = 0
        with open(file) as f:
            for line in f:
                sentence_count += int(in_line(line))
                lines += 1

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
