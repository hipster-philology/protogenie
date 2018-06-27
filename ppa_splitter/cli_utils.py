import os
from glob import glob


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
        print("Ratios are over 1, scaling down train ratio to {0:.2f}".format(train))
    return train, test, dev
