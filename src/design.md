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
      identifier.  However, I should also include additional columns for each
      higher category for additional clarity.

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
      database.

- Use assertions and other checks on the data.

- Consider using a dependency graph to automatically calculate all possible
  variables.

- Include additional fields for commentary (likely editorial commentary).  Also
  include additional fields for the people involved, the facilities involved,
  the organizations involved, locations of any experiments, and any contract
  numbers.


-------------------------------------------------------------------------------

Copyright © 2020-2021 Andrew Trettel

SPDX-License-Identifier: MIT
