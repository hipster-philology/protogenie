""" This module contains scripts that are supposed to be used to know
when the CSV reader enters a new sentence.

"""

import re
import math
import random

from .defaults import DEFAULT_SENTENCE_MARKERS


SPACE_ONLY = re.compile("^\s+$")


class _SplitterPrototype:
    """ This will contain any needed function accross splitters
    """
    def reset(self):
        """ Reset the splitter values for the second pass if necessary
        """


class _DispatcherRandom:
    @staticmethod
    def dispatch(units_count, test_ratio=0.2, dev_ratio=0.0001):
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

        target_dataset = ["test"] * test_number + ["train"] * (train_number + 1) + ["dev"] * dev_number
        random.shuffle(target_dataset)
        return target_dataset


class _DispatcherSequential:
    @staticmethod
    def dispatch(units_count, test_ratio=0.2, dev_ratio=0.0001):
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

        target_dataset = ["train"] * (train_number + 1) + ["test"] * test_number + ["dev"] * dev_number
        return target_dataset


class PunctuationSplitter(_SplitterPrototype, _DispatcherRandom):
    def __init__(self, column_marker="\t", sentence_splitter=DEFAULT_SENTENCE_MARKERS, **kwargs):
        """ Returns true if the line is a sentence splitter by being empty

        :param column_marker: Marker that splits column in the CSV/TSV
        :param sentence_splitter: Marker that shows the end of a sentence
        """
        self.column_marker = column_marker
        self.sentence_splitter = sentence_splitter

    def __call__(self, line):
        return bool(len([
            1
            for token in line.split(self.column_marker)
            if token in self.sentence_splitter
        ]))


class LineSplitter(_SplitterPrototype, _DispatcherRandom):
    def __init__(self, **kwargs):
        """ Class for applying a split on new lines (some data are formatted such as sentence are separated
        with empty lines
        """
        # We set it to True so that starting empty lines are
        #  not counting as separators
        self.last_line_was_empty = True

    def __call__(self, line):
        if line == "\n":
            if self.last_line_was_empty:
                return False
            self.last_line_was_empty = True
            return True
        self.last_line_was_empty = False
        return False

    def reset(self):
        """ Reset the last line to True in case the file starts with empty lines
        """
        self.last_line_was_empty = True


class TokenWindowSplitter(_SplitterPrototype, _DispatcherRandom):
    def __init__(self, window=20, **kwargs):
        """ Class for applying a split every N words

        :param window: Split as a sentence each N words
        """
        self.window = window
        self.words = 0

    def __call__(self, line):
        if line == "\n":
            return False
        # No body cares about line in here
        self.words += 1
        if self.words == self.window:
            self.words = 0
            return True
        return False


class FileSplitter(_SplitterPrototype, _DispatcherSequential):
    def __init__(self, **kwargs):
        """ Splitter that affects the file globally. Not expecting random shuffle.
        The real main piece of this splitter is actually the line_counting function
        """

    def __call__(self, line):
        if line == "\n":
            return False
        return True
