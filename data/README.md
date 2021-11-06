Data files for the shear layer data compilation
===============================================


## Directory structure

The data directory has a flat directory structure.

- `data/elements.csv`

- `data/LICENSE.txt`

    - `CC-BY-4.0` license for data files.

- `data/README.md`

- `data/references.bib`

    - This file should contain all BibTeX references for the entire project.

- `data/*.tex`

    - LaTeX files for documentation.

- `data/$(case_identifier)`

    - `README.md`

        - This file serves as the initial documentation for the case.

    - CSV files with tabulated data from the originator or other source.

        - All CSV files MUST contain only data.  Any documentation or
          commentary on the data MUST be in separate files like the directory's
          `README.md` file or additional LaTeX files.
        
        - The first row MUST be a left-aligned header line labeling the
          columns.
        
        - All CSV files SHOULD be as human readable as possible.


## Structure of identifiers

- (REQUIRED) Flow class (1 letter)

- (REQUIRED) Year of first publication (4 digits)

- (REQUIRED) Study number (3 digits)

- (OPTIONAL) Series number (3 digits)

- (OPTIONAL) Station number (3 digits)

- (OPTIONAL) Point number (4 digits)

The required portions are sufficient to identify a study.  The optional
portions can identify a series of profiles/stations, an individual station, or
even a single point in the flow if necessary.  For readability, dashes are
acceptable in any location but removed in the database itself.

Examples:

- Study identifier (accession number)

    - Compact form: `B1944001` (8 characters)

    - Readable form: `B-1944-001` (10 characters)

- Series identifier

    - Compact form: `B1944001001` (11 characters)

    - Readable form: `B-1944-001-001` (14 characters)

- Station identifier

    - Compact form: `B1944001001001` (14 characters)

    - Readable form: `B-1944-001-001-001` (18 characters)

- Point identifier

    - Compact form `B19440010010010001` (18 characters)

    - Readable form: `B-1944-001-001-001-0001` (23 characters)

Longer identifiers specify the data to a greater extent.  For example, the
study identifier specifies what flow class the data falls under, the series
identifier specifies what flow field is being considered (for all points), the
station identifier specifies which station with known streamwise and spanwise
coordinates, and the point identifier specifies which point with known
streamwise, transverse, and spanwise coordinates.


-------------------------------------------------------------------------------

Copyright © 2020-2021 Andrew Trettel

SPDX-License-Identifier: CC-BY-4.0
