import os


def add_sentence(output_folder, dataset, filename, sentence):
    """ Write a sentence in the given dataset

    :param output_folder:
    :param dataset:
    :param filename:
    :param sentence:
    :return:
    """
    with open(os.path.join(output_folder, dataset, filename), "wa") as f:
        f.write("\n".join(sentence))