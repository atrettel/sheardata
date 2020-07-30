Data files for the shear layer data compilation
===============================================


## Directory structure

The data directory has a flat directory structure.

- `data/README.md`

- `data/references.bib`

    - This file should contain all references for the entire project.

- `data/taxonomy.md`

    - A draft taxonomy of flows.  This taxonomy is used as the first letter of
      the case identifiers.

- `data/$(case_identifier)`

    - `README.md`

        - This file should serve as the initial documentation for the case,
          though I am considering migrating to LaTeX files instead.

    - CSV files with tabulated data from the originator or other source.

        - All CSV files MUST contain only data.  Any documentation or
          commentary on the data MUST be in separate files like the directory's
          `README.md` file.
        
        - The first row MUST be a left-aligned header line labeling the
          columns.
        
        - All CSV files SHOULD be as human readable as possible.


## Structure of identifiers

- (REQUIRED) Flow class (1 letter)

    - See `data/taxonomy.md` for more information.

- (REQUIRED) Year of first publication (4 digits)

- (REQUIRED) Case number (3 digits)

- (OPTIONAL) Series number (3 digits)

- (OPTIONAL) Profile or station number (3 digits)

- (OPTIONAL) Point number (4 digits)

The required portions are sufficient to identify a case.  The optional portions
can identify a series of profiles, an individual profile, or even a single
point in the flow if necessary.  For readability, dashes are acceptable in any
location but removed in the database itself.

Examples:

- Case identifier (accession number)

    - Compact form: `B1944001` (8 characters)

    - Readable form: `B-1944-001` (10 characters)

- Series identifier

    - Compact form: `B1944001001` (11 characters)

    - Readable form: `B-1944-001-001` (14 characters)

- Profile identifier

    - Compact form: `B1944001001001` (14 characters)

    - Readable form: `B-1944-001-001-001` (18 characters)

- Point identifier

    - Compact form `B19440010010010001` (18 characters)

    - Readable form: `B-1944-001-001-001-0001` (23 characters)


-------------------------------------------------------------------------------

Copyright © 2020 Andrew Trettel

This file is licensed under the Creative Commons Attribution 4.0 International
license (`CC-BY-4.0`).  For more information, please visit the Creative Commons
website at <https://creativecommons.org/licenses/by/4.0/>.
