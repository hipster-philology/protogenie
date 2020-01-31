from .io_utils import add_sentence, get_name
from .configs import CorpusConfiguration, PPAConfiguration
from .defaults import DEFAULT_SENTENCE_MARKERS, DEFAULT_SPLITTER
from .splitters import LineSplitter
import glob
import os
import csv


def split_files(
        config: PPAConfiguration, output_folder: str, dev_ratio: float, test_ratio: float,
        verbose: bool =True):
    """ Dispatch sentence for each file in files

    :param output_folder: Folder where the data should be saved
    :param dev_ratio: Ratio of data to put in dev
    :param test_ratio: Ratio of data to put in test
    :param verbose: Verbosity (Adds some print during process)

    :yield: File, Dispatch stats about file
    """

    memory, memory_file = None, None
    if config.memory:
        memory_file = open(config.memory, "w")
        memory = csv.writer(memory_file)

    # For each file
    for unix_path, current_config in config.corpora.items():
        unix_path = os.path.join(config.dir, unix_path)
        for file in glob.glob(unix_path):
            # We do two passes here
            #  1. The first one is used to collect informations about the file. In order to not keep data in memory,
            #     we iterate over it and count the number of real lines + the number of sentences.
            #     Sentences are counted on the base of the Configuration.split function
            #  2. We read the file again and dispatch according to the ratio and the data we got before
            #      Note : We use .pop(0) to move from start to end. If we have one day a performance issue
            #      we might want to move to a yield system
            #
            # This method is slower but allows for memory efficiency.

            # We count things in the file
            unit_counts = 0
            lines = 0
            with open(file) as f:
                for line_no, line in enumerate(f):
                    if line_no == 0 and current_config.reader.has_header:
                        continue  # Skip the first line in count if we have a header
                    unit_counts += int(current_config.splitter(line))
                    lines += int(line == "\n")  # Count only lines if they are empty

            if verbose:
                print("{unit_count} {unit_name} to dispatch in {filename} ({lines})".format(
                    filename=file, unit_name=current_config.unit_name, unit_count=unit_counts,
                    lines=lines
                ))

            # We set up numbers based on the ratio
            # In order to do that, we get to use
            target_dataset = current_config.build_dataset_dispatch_list(
                units_count=unit_counts,
                test_ratio=test_ratio,
                dev_ratio=dev_ratio
            )

            # We set up a dictionary of token count to print nice
            #  information later
            training_tokens = {"test": 0, "dev": 0, "train": 0}

            # ToDo: When file splitter, the number of lines should be passed here probably ? Or is reset the issue ? ...

            current_config.splitter.reset()
            current_config.splitter.set_targets(target_dataset)

            header_line = []
            with open(file) as f:
                sentence = []
                blanks = 0
                for line_no, line in enumerate(f):
                    if line_no == 0:
                        if current_config.reader.has_header:
                            header_line = [current_config.reader.map_to[key]
                                           for key in line.strip().split(current_config.column_marker)]
                            continue
                        else:
                            header_line = current_config.reader.header
                    elif not line.strip() and not isinstance(current_config.splitter, LineSplitter):
                        # Only count is we already have written or the sentence writing has started
                        if len(sentence) > 0:
                            blanks += 1
                        continue

                    sentence.append(line)
                    if current_config.splitter(line):
                        dataset = target_dataset.pop(0)

                        if memory:
                            memory.writerow([file, "{}-{}".format(line_no-len(sentence)+1-blanks, line_no), dataset])
                            blanks = 0
                        sentence = [x for x in sentence if x.strip()]
                        add_sentence(
                            output_folder=output_folder,
                            dataset=dataset,
                            filename=file,
                            sentence=sentence
                        )
                        training_tokens[dataset] += len(sentence)
                        sentence = []

                # Finally, if there is something remaining
                if len(sentence):
                    try:
                        dataset = target_dataset.pop(0)
                        print("last dataset ?")
                    except Exception:
                        dataset = "train"

                    if memory:
                        memory.writerow([file, "{}-{}".format(line_no-len(sentence)+1-blanks, line_no), dataset])

                    add_sentence(
                        output_folder=output_folder,
                        dataset=dataset,
                        filename=file,
                        sentence=sentence
                    )
                    training_tokens[dataset] += len(sentence)
            # Add the header to the files
            for dataset, tokens in training_tokens.items():
                if tokens:
                    trg = get_name(output_folder, dataset, file)
                    with open(trg) as f:
                        content = f.read()
                    with open(trg, "w") as f:
                        f.write(current_config.column_marker.join(header_line)+"\n"+content)
            yield file, training_tokens
    if memory:
        memory_file.close()
