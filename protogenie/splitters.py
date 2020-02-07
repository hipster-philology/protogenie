""" This module contains scripts that are supposed to be used to know
when the CSV reader enters a new sentence.

"""

import re
import math
import random
from typing import Dict, Union, List, Tuple, Optional
if not True:
    from .configs import CorpusConfiguration

from .defaults import DEFAULT_SENTENCE_MARKERS


SPACE_ONLY = re.compile("^\s+$")


class _DispatcherSequential:
    @staticmethod
    def dispatch(units_count, test_ratio=0.2, dev_ratio=0.0001) -> List[str]:
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

        target_dataset = ["train"] * train_number + ["test"] * test_number + ["dev"] * dev_number
        return target_dataset


class _DispatcherRandom(object):
    @staticmethod
    def dispatch(units_count, test_ratio=0.2, dev_ratio=0.0001) -> List[str]:
        """ Get the ratios and builds a list of targets completely randomly and shuffled

        :param units_count: Number of units to dispatch (either sentence or dispatch depending on self.splitter)
        :param test_ratio: Ratio of data to be put in test
        :param dev_ratio: Ratio of data to be put in dev
        :return: List of dataset to dispatch to
        """

        target_dataset = _DispatcherSequential.dispatch(units_count, test_ratio, dev_ratio)
        random.shuffle(target_dataset)
        return target_dataset


class _SplitterPrototype(_DispatcherRandom):
    """ This will contain any needed function accross splitters
    """
    def __init__(self, *args, **kwargs):
        pass

    def reset(self) -> None:
        """ Reset the splitter values for the second pass if necessary
        """

    def _repr_options(self) -> str:
        """ Return options of the splitter"""
        return ""

    def __repr__(self) -> str:
        return "<splitter name='{}'{}/>".format(self.__class__.__name__, self._repr_options())

    def read_line(self, line, corpus_configuration: "CorpusConfiguration") -> Dict[str, str]:
        line = line.split(corpus_configuration.column_marker)
        return line

    def __call__(self, *args, **kwargs) -> bool:
        raise NotImplemented

    def set_targets(self, targets: List[str]) -> None:
        pass


class RegExpSplitter(_SplitterPrototype):
    def __init__(self, column_marker="\t", matchPattern="["+DEFAULT_SENTENCE_MARKERS+"]", **kwargs):
        """ Returns true if the line is a sentence splitter by being empty

        :param column_marker: Marker that splits column in the CSV/TSV
        :param sentence_splitter: Marker that shows the end of a sentence
        """
        self.column_marker = column_marker
        self.match_pattern = matchPattern
        self.matcher = re.compile(matchPattern)

    def _repr_options(self):
        return " matchPattern='{}'".format(self.match_pattern)

    def __call__(self, line):
        return True in [
            bool(self.matcher.search(token))
            for token in line.split(self.column_marker)
        ]


class LineSplitter(_SplitterPrototype):
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


class TokenWindowSplitter(_SplitterPrototype):
    def __init__(self, window=20, **kwargs):
        """ Class for applying a split every N words

        :param window: Split as a sentence each N words
        """
        self.window = int(window)
        self.words = 0

    def __call__(self, line):
        if not line.strip():
            return False
        # No body cares about line in here
        self.words += 1
        if self.words == self.window:
            self.words = 0
            return True
        return False

    def _repr_options(self):
        return " window='{}'".format(self.window)

    def reset(self):
        self.words = 0


class FileSplitter(_SplitterPrototype):
    def __init__(self, *args, **kwargs):
        """ Splitter that affects the file globally. Not expecting random shuffle.
        The real main piece of this splitter is actually the line_counting function
        """
        super(FileSplitter, self).__init__(self, *args, **kwargs)
        self.line_count = 0
        self._sets_size: Dict[str, int] = {}
        self._dispatching: bool = False  #
        self._sizes: Optional[List[int]] = None
        
    def __call__(self, line):
        if not line.strip():
            return False

        if not self._dispatching:  # If we are counting lines
            return True

        if self._sizes:
            self._sizes[0] -= 1
            # If we still have something in our size, we reduce the number
            if self._sizes[0]:
                return False
            else:
                self._sizes.pop(0)
                return True
        else:
            raise Exception("Sizes should be set and were not found")

    def reset(self) -> None:
        self.line_count = 0
        self._dispatching = True
        self._sizes = [
            self._sets_size.get("train", 0),
            self._sets_size.get("dev", 0),
            self._sets_size.get("test", 0),
        ]

    def dispatch(self, units_count, test_ratio=0.2, dev_ratio=0.0001) -> List[str]:
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

        target_dataset = ["train"] * train_number + ["test"] * test_number + ["dev"] * dev_number
        self._sets_size = {
            key: target_dataset.count(key)
            for key in filter(lambda x: x in target_dataset, ["train", "dev", "test"])
        }
        return list(filter(lambda x: x in target_dataset, ["train", "dev", "test"]))
