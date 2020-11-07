Source directory for the shear layer data compilation
=====================================================

This directory contains the scripts that create the database file itself.


## Compilation instructions

To create the database, type

    make


## Files

- `sheardata.py` is the Python module with many low-level commands to interact
  with the data in the database.

- `create_tables.py` creates an empty database.

- Python scripts that use a study identifier as their filename process the data
  from the `data` directory for that study and insert it into the database.


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
