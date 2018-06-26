""" This module contains scripts that are supposed to be used to know
when the CSV reader enters a new sentence.

"""


def empty_line_splitter(line):
    """ Returns true if the line is a sentence splitter by being empty

    :param line: Line to categorize
    """
    return line == "\n"


def sentence_line_splitter_maker(col_marker, sentence_splitter):
    """ Returns true if the line is a sentence splitter by being empty

    :param col_marker: Marker that splits column in the CSV/TSV
    :param sentence_splitter: Marker that shows the end of a sentence
    """
    def in_line(line):
        return bool(len([
            1
            for token in line.split(col_marker)
            if token in sentence_splitter
        ]))
    return in_line


class BatchLineSplitter:
    def __init__(self, each_n_words):
        """ Class for applying a split every N words

        :param each_n_words: Split as a sentence each N words
        """
        self.each_n_words = each_n_words
        self.words = 0

    def split(self, line):
        # No body cares about line in here
        self.words += 1
        if self.words == self.each_n_words:
            self.words = 0
            return True
        return False
