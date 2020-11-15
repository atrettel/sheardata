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
  database itself.  They also perform some additional calculations.

- Python scripts that start with `post` postprocess the data.  These scripts
  are needed for the documentation and do not run when making only the
  database.


-------------------------------------------------------------------------------

Copyright © 2020 Andrew Trettel

This file is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This file is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this file.  If not, see <https://www.gnu.org/licenses/>.
