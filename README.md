Pandora Data Spliter
====================


## Install

Start by cloning the repository, and moving inside the created folder

```bash
git clone https://github.com/hipster-philology/ppa-splitter.git
cd ppa-splitter/
```

Create a virtual environment, source it and run

```bash
pip install -r requirements.txt
```

## Usage

### Without configuration

**Note that if you want more options, using a configuration file is recommended**

To use the splitter without configuration, you can simply do

```bash
python dispatch.py path/to/file.tsv --train 0.8 --test 0.2
```

Tokens will be splitted by sentence (everytime a character in `;.:` is found.

This will saves the result in three subfolders of `./output` folder (train, test, dev if required)

You have obviously more options. Do

```bash
python dispatch.py --help
```

Optional arguments:

- `--help`: show this help message and exit
- `--train`: Ratio of data to use for training
- `--test`: Ratio of data to use for testing
- `--dev`: Ratio of data to use for dev
- `--col`: Column that contains the form token (Default is TAB)
- `--output`: Directory in which to save files
- `--sentence`: Directory in which to save files
- `--config`: Yaml configuration file for advanced config
- `--clear`: Remove data in output directory (you'll need to confirm)

### With a configuration

You can use a configuration to get more fine-grained options :

```yaml
# For this file, the tokens will be splitted in window of 20 words.
# Sequence are randomly put in sets according to ratios.
datasets/chrestien.tsv:
  column_marker: TAB
  splitter: token_window
  window: 20

# For this file, every time a punctuation character from `sentence_markers`
#   is found in one column (marked by column_marker),
#   it will mark the end of a sequence.
# Sequence are randomly put in sets according to ratios.
datasets/dotmarkers.tsv:
  column_marker: TAB
  sentence_markers: ';.:'
  splitter: punctuation

# For this file, any sequence are separated by one or more empty lines
# Sequence are randomly put in sets according to ratios.
datasets/empty_line.tsv:
  column_marker: TAB
  splitter: empty_line


# The file has not specific markers and windows do not please you ?
#   This function split the following file exactly at the ratio given
#   by the command-line
datasets/flow.tsv:
  column_marker: TAB
  splitter: file_split
```

To use this configuration, you simply need to given the configuration file's path
and your ratios :

```bash
python dispatch.py datasets/*.tsv --config config.yaml --dev 0.1 --test 0.2
```

#### Pre-Generate a configuration
You can generate a blank configuration file with

```bash
# Wildcard
python config-maker.py path/to/multiples/*.tsv
# Single
python config-maker.py datasets/chrestien.tsv
```

Options are :
    - `--output` to express where to save the file and its name
    - `--input` if you have a previous configuration, updates it
    with any new file found