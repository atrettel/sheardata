The design of the shear layer database and classes
==================================================


Goals
-----

- Use SQLite as the database backend.  The goal here is to ensure that it is
  possible to use SQL commands to select and find data.

- Use the `uncertainties` package to handle uncertainties.  The uncertainties
  will be standard uncertainties (standard deviations of the distribution of
  "reasonable" values from the measurements).

- Use SI for all units.  Prefer dimensionless variables if possible.

- Develop a series of classes based on the flow taxonomy.  These classes act as
  interfaces to the database.  Their methods access the data and perform
  calculations based on it.

    - Keep the amount of data in memory (in the objects themselves) to a
      minimum.  Load what is needed from the database but not more.  The
      objects are interfaces to the database and do not store the data
      themselves.  The tradeoff is that unless the data were pre-calculated,
      this choice uses more computational resources.  All data must be accessed
      through methods as well.

    - Another tradeoff is that almost all actions are "side effects" in a
      sense.

- Keep variable names in both the database and classes human-readable.  Prefer
  `skin_friction_coefficient` to `c_f`.

- Keep track of assumptions for each case.

- Use a dependency graph to automatically calculate all possible variables.

- Use assertions and other checks on the data.


Design details
--------------

- Tables

    - `globals_d` - discrete globals

        - These are global variables that do not have any uncertainty.

    - `globals_n` - real values of globals

    - `globals_s` - real uncertainties of globals

    - `uw_profiles_n` - real values for unweighted mean profiles

    - `uw_profiles_s` - real uncertainties for unweighted mean profiles

    - `dw_profiles_n` - real values for density-weighted mean profiles

    - `dw_profiles_s` - real uncertainties for density-weighted mean profiles

- Have corresponding tables for values and uncertainties.  The field names
  should be identical.  `n` is for the values and `s` is for uncertainties.
  This convention follows the Python `uncertainties` package.

- Include tables for global parameters, unweighted mean profiles, and
  density-weighted mean profiles.


-------------------------------------------------------------------------------

Copyright © 2020 Andrew Trettel

This file is licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.  You may
obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
