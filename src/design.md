The design of the shear layer database and classes
==================================================


Goals
-----

- Use SQLite as the database backend.  The goal here is to ensure that it is
  possible to use SQL commands to select and find data.

    - Limit the number of calls to the database itself (separate use and
      implementation).  This could allow me to change the kind of database
      later.  Write the interfaces in such a way that the user may be unaware
      what kind of database is operating underneath (no need to load `sqlite3`
      package manually...).

- Use the `uncertainties` package to handle uncertainties.  The uncertainties
  will be standard uncertainties (standard deviations of the distribution of
  "reasonable" values from the measurements).

- Develop a series of classes based on the flow taxonomy.  These classes act as
  interfaces to the database.  Their methods access the data and perform
  calculations based on it.

    - Keep the amount of data in memory (in the objects themselves) to a
      minimum.  The objects are interfaces to the database and do not store the
      data themselves.  In a sense, all procedures have side effects.

    - The unknown here is how much data the database *should* contain.  It
      could contain a bare minimum --- say, the minimum amount of data to
      calculate everything else --- and most methods then calculate the data
      when it is needed.  Or it could contain a much larger amount of data that
      could be accessible by other interfaces.  In this case, some data is
      "pre-calculated".  For now I am opting for the minimal amount of data.
      The tradeoff is that most operations are computationally expensive, but
      only the computations that are needed are performed, and the database is
      simpler.

- Prefer dimensionless variables, but use SI for any variables that require
  units.

    - Profiles should be nondimensionalized by a standard set of well-defined
      and unambiguous scales.  Each flow class has a different set of standard
      scales.  The scales should be the most easily-found and common ones for
      each case.

    - There is some conflict between the two requirements.  Some scales are
      often given in datasets, but they are sometimes ill-defined (bulk
      density, etc. for internal flows).  Some scales are often not measured
      too (wall shear stress in external flows), so nondimensionalizing by them
      cannot be done without additional assumptions.  The goal here is to
      minimize the uncertainty in the scalings themselves.

    - Alternatively, I could considering using different profile scalings for
      each case, depending what data emerge from the case.  The tradeoff with
      this is that the database itself becomes less standardized.

- Keep variable names in both the database and classes human-readable.  Prefer
  `skin_friction_coefficient` to `c_f`.

- Keep track of assumptions for each case.

- Keep track of which parameters are "input" parameters and which are
  calculated.

- Use a dependency graph to automatically calculate all possible variables.

- Use assertions and other checks on the data.

- Eliminate redundancy in the tables.  Each data point MUST have one and only
  one location.

- Remember that at least some of the "structure" here really is "data".  Prefer
  data over structure, since data is mutable (or at least more easily mutable).

- Include additional fields for commentary (likely editorial commentary).  Also
  include additional fields for the people involved, the facilities involved,
  the organizations involved, locations of any experiments, and any contract
  numbers.

- Note that for duct flows that are fully-developed, it could be possible to
  note this by specifying that both the previous and next stations are the
  current station.  That signifies that the flow is not developing.  Then
  derivatives in the streamwise direction will always be zero automatically.


Design details
--------------

The identifiers are intentionally simple and systematic so that it is possible
to extract information about profiles from the points (and in other
combinations).  For example, consider the following SQL command

    SELECT value FROM point_values WHERE identifier LIKE 'D9999002%';

This selects all values for the points that have a particular profile
identifier.


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

    - trip present?

        - It might be better to set this as a series variable that notes
          the location of the trip rather than whether it was tripped.

    - geometry (`I`)

        - `E` for ellipse, `P` for polygon

    - number of sides (`I`)

        - 3 for triangular duct, 4 for rectangular ducts, ...

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

    - outlier?

    - description

    - notes

- `points`

    - point identifier

    - point number

    - label

    - outlier?

    - notes

- `study_values`

- `series_values`

- `profile_values`

- `point_values`

    - point identifier

    - quantity identifier

    - value

    - uncertainty

    - averaging system

    - measurement technique

    - outlier?

    - notes


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
