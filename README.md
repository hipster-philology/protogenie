Protogenie
====================

[![Coverage Status](https://coveralls.io/repos/github/hipster-philology/protogenie/badge.svg?branch=master)](https://coveralls.io/github/hipster-philology/protogenie?branch=master)
[![Build Status](https://travis-ci.org/hipster-philology/protogenie.svg?branch=master)](https://travis-ci.org/hipster-philology/protogenie)
[![PyPI](https://img.shields.io/pypi/v/protogenie)](https://pypi.org/project/protogenie)

## How to cite

```bibtex
@software{thibault_clerice_2020_3883586,
  author       = {Thibault Clérice},
  title        = {Protogenie, post-processing for NLP dataset},
  month        = jun,
  year         = 2020,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.3883585},
  url          = {https://doi.org/10.5281/zenodo.3883585}
}
```

## Install from release

```bash
pip install protogenie
```

## Install unstable

```bash
pip install --upgrade https://github.com/hipster-philology/protogenie/archive/master.zip
```

## Install from source

Start by cloning the repository, and moving inside the created folder

```bash
git clone https://github.com/hipster-philology/protogenie.git
cd protogenie/
```

Create a virtual environment, source it and run

```bash
pip install -r requirements.txt
```

## Configuration file

To configurate, you can have a look at the examples in [./tests/test_config](./tests/test_config) but more generally
you can and should use the schema: [./ppa_splitter/schema.rng](./ppa_splitter/schema.rng)

## Workflow

![What's the workflow ?](flow.png)
