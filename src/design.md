The design of the shear layer database and classes
==================================================


Goals
-----

- Use SQLite as the database backend.  The goal here is to ensure that it is
  possible to use SQL commands to select and find data.

    - The identifiers are intentionally simple and systematic so that it is
      possible to extract information about profiles from the points (and in
      other combinations).  For example, consider the following SQL command:
      `SELECT value FROM point_values WHERE identifier LIKE 'D9999002%';`.
      This selects all values for the points that have a particular profile
      identifier.

- Use the `uncertainties` package to handle uncertainties.  The uncertainties
  will be standard uncertainties (standard deviations of the distribution of
  "reasonable" values from the measurements).

- Store the data as generic records.  This means that each data point in a flow
  is merely a record in a particular table depending on its type.  This design
  is flexible; it can store different data for the same variable easily,
  including data for different averaging systems and measurement techniques.

    - Group data into 4 main categories:

        1. study data (data that applies to an entire study)

        2. series data (data that applies to a series of profiles, like drag
        coefficients, etc.)

        3. station data (data that applies to a single profile, like the
        momentum thickness)

        4. point data (data that applies to a single point in a flow, like the
        local unweighted averaged velocity)

    - Eliminate redundancy in the tables.  Each data point MUST have one and
      only one location.

    - Remember that at least some of the "structure" here really is "data".
      Prefer data over structure, since data is mutable (or at least more
      easily mutable).

    - Specifying the measurement techniques allows for all assumptions
      underlying that data to be specified as well for each record in the
      database.  Calculated parameters can be noted as either exact or
      approximate, for example, and the method of calculation can be specified.

- Use assertions and other checks on the data.

- Consider using a dependency graph to automatically calculate all possible
  variables.

- Include additional fields for commentary (likely editorial commentary).  Also
  include additional fields for the people involved, the facilities involved,
  the organizations involved, locations of any experiments, and any contract
  numbers.

- Note that for duct flows that are fully-developed, it could be possible to
  note this by specifying that both the previous and next stations are the
  current station.  That signifies that the flow is not developing.  Then
  derivatives in the streamwise direction will always be zero automatically.


Tables
------

- `studies`

    - study identifier

    - flow class

    - year

    - study number

    - study type (experimental or numerical)

    - description

    - provenance (chain of custody for data)

        - A description of how the data ended up in the collection.  Was the
          data extracted graphically and from what references?  Was the data
          published in tabulated form?  Was the data sent through private
          correspondence?  Has the transmission of the data altered it in any
          way?

        - <https://en.wikipedia.org/wiki/Provenance#Data_provenance>

        - <https://en.wikipedia.org/wiki/Data_lineage>

    - primary reference

    - additional references

        - These references (and the primary reference) should all be
          primary sources.

    - notes

- `series`

    - series identifier

    - series number

    - number of dimensions (2 or 3)

    - coordinate system

    - working fluid

    - geometry

    - number of sides

    - description

    - notes

- `profiles`

    - profile identifier

    - profile number

    - originator's identifier

    - regime

        - Laminar, transitional, turbulent.  This might involve a "judgment
          call", but it is necessary to sort through data.

    - previous streamwise station

    - next streamwise station

    - previous spanwise station

    - next spanwise station

    - outlier

    - description

    - notes

- `points`

    - point identifier

    - point number

    - label

    - outlier

    - notes


-------------------------------------------------------------------------------

Copyright © 2020-2021 Andrew Trettel

SPDX-License-Identifier: MIT
