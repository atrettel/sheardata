Source directory for the shear layer data compilation
=====================================================

This directory contains the scripts that create the database and documentation
files.


## Compilation instructions

To create an empty database, run

    make sheardata.tmp

To create the database with the flow data in it, run

    make

Requirements to make the database:

- SQLite with built-in mathematical SQL functions

    - <https://www.sqlite.org/lang_mathfunc.html>

    - This requirement may need a custom-compiled version of SQLite.

- Python 3

- Numpy Python module

- SQLite 3 Python module

- Uncertainties Python module

To create the documentation, run

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

- Python scripts

    - `prep` - pre-processing steps to create an empty database.

    - `proc` - processing steps to load flow data into the database.

    - `post` - post-processing steps to use database to generate documentation
      and figures.


-------------------------------------------------------------------------------

Copyright © 2020-2022 Andrew Trettel

SPDX-License-Identifier: MIT
