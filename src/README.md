Source directory for the shear layer data compilation
=====================================================

This directory contains the scripts that create the database and documentation
files.


## Compilation instructions

To create the database, type

    make

Requirements to make the database:

- SQLite

- Python 3

- Numpy Python module

- SQLite 3 Python module

- Uncertainties Python module

To create the documentation, type

    make sheardata.pdf

Additional requirements to make the documentation:

- Matplotlib Python module

- LaTeX distribution

    - `pdflatex`

    - `biber`

    - `hyperref` LaTeX package

    - `siunitx` LaTeX package

    - TikZ LaTeX package

- Graphviz (for classification tree diagram)


## Files

- `sheardata.py` is the Python module with many low-level commands to interact
  with the data in the database.

- `create_tables.py` creates an empty database.

- Python scripts that start with `pre` preprocess the data to insert it to the
  database itself.  They also perform some additional calculations needed to
  calculate additional data from stored data.

- Python scripts that start with `post` postprocess the data.  These scripts
  are needed for the documentation and figures.  They do not run when making
  only the database.


-------------------------------------------------------------------------------

Copyright © 2020-2021 Andrew Trettel

SPDX-License-Identifier: MIT
