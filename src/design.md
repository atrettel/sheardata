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


Design details
--------------

- Tables

    - `studies`

        - study identifier

        - flow class

        - year

        - study number

        - study type (experimental or numerical)

        - description

        - provenance (chain of custody for data)

            - A description of how the data ended up in the collection.  Was
              the data extracted graphically and from what references?  Was the
              data published in tabulated form?  Was the data sent through
              private correspondence?  Has the transmission of the data altered
              it in any way?

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

        - study identifier

        - number of dimensions (2 or 3)

        - coordinate system

        - working fluid

        - working fluid phase

            - Also consider combining these two into a single field.

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

        - profile identifier

        - label

            - Center-line, edge, wall

            - Note that for some flows, there can be two walls.

        - streamwise coordinate

        - transverse coordinate

        - spanwise coordinate

            - It might be better to put these as a profile quantity.

        - outlier?

        - notes

    - `quantities`

    - `fluids`

    - `measurement_techniques`

    - `study_values`

    - `series_values`

    - `profile_values`

    - `point_values`

        - profile identifier

        - point number

        - quantity identifier

        - value

        - uncertainty

        - averaging system

        - measurement technique

        - outlier?

        - notes


Measurement techniques
----------------------

- Flow measurement technique

- Velocity measurement technique

    - Pitot tube

    - Pitot-static tube

    - Hot-wire anemometer

    - Laser Doppler velocimetry or anemometer

    - Particle image velocimetry

- Wall shear stress measurement technique

    - Pressure gradient (for internal flows only)

    - Direct measurement

    - Viscous sublayer gradient

    - Stanton tube

    - Preston tube

    - Clauser chart


Quantities
----------

- Series quantities

    - Streamwise trip location (`C`)

- Profile quantities

    - Aspect ratio (`I`)

    - Cross-sectional area (`I`)

    - Hydraulic diameter (`I`)

    - Bulk dynamic viscosity (`I`)

    - Bulk kinematic viscosity (`I`)

    - Bulk mass density (`I`)

    - Bulk pressure (`I`)

    - Bulk specific isobaric heat capacity (`I`)

    - Bulk speed of sound (`I`)

    - Bulk streamwise velocity (`I`)

    - Bulk temperature (`I`)

    - Bulk transverse velocity (`I`)

    - Clauser thickness (`C`)

    - Compressible displacement thickness (`C`)

    - Compressible momentum thickness (`C`)

    - Friction velocity (`C`)

    - Friction temperature (`C`)

    - Incompressible displacement thickness (`C`)

    - Incompressible momentum thickness (`C`)

    - Left-hand side of momentum integral (`E`)

    - Mass flow rate (`I`)

    - Volume flow rate (`I`)

    - Reservoir pressure (`S`)

    - Reservoir speed of sound (`S`)

    - Reservoir temperature (`S`)

    - Right-hand side of momentum integral (`E`)

    - Streamwise pressure gradient (`C`)

    - Viscous length scale (`C`)

    - 99-percent velocity boundary layer thickness (`E`)

    - 99-percent temperature boundary layer thickness (`E`)

    - Bulk heat capacity ratio (`I`)

    - Bulk Mach number (`I`)

    - Bulk Prandtl number (`I`)

    - Dimensionless wall heat flux (`B_q`) (`C`)

    - Equilibrium parameter (`E`)

    - Freestream turbulence intensity (`S`)

    - Friction factor (`I`)

        - Which one is up to debate right now.

    - Friction Mach number (`C`)

    - Friction Reynolds number (`C`)

    - Heat transfer coefficient (`E`)

    - Recovery factor (`C`)

    - Semi-local friction Reynolds number (`C`)

    - Local skin friction coefficient (`E`)

    - Streamwise coordinate

    - Spanwise coordinate

        - It might be better to put these under points.

- Wall profile quantities - these can appear twice

    - Streamwise wall curvature (`C`)

    - Spanwise wall curvature (`C`)

        - Fernholz 1977, p. 13 defines this as positive for external flows and
          negative for internal flows.

    - Roughness height (`C`)

- Point quantities

    - Bulk viscosity (`S`)

    - Dynamic viscosity (`S`)

    - Heat capacity ratio (`S`)

    - Specific isobaric heat capacity (`S`)

    - Specific isochoric heat capacity (`S`)

    - Kinematic viscosity (`S`)

    - Mach number (`S`)

    - Mass density (`S`)

    - Momentum density (`S`)

    - Prandtl number (`S`)

    - Pressure (`S`)

    - Shear stress (`S`)

    - Spanwise velocity (`S`)

    - Spanwise vorticity (`S`)

    - Specific enthalpy (`S`)

    - Specific entropy (`S`)

    - Specific internal energy (`S`)

    - Specific total enthalpy (`S`)

    - Specific total internal energy (`S`)

    - Specific volume (`S`)

    - Speed (`S`)

    - Speed of sound (`S`)

    - Stagnation pressure (`S`)

    - Stagnation temperature (`S`)

    - Streamwise velocity (`S`)

    - Streamwise vorticity (`S`)

    - Temperature (`S`)

    - Thermal conductivity (`S`)

    - Thermal diffusivity (`S`)

    - Transverse velocity (`S`)

    - Transverse vorticity (`S`)

    - Turbulent kinetic energy (`S`)

    - Turbulent stress UU (`S`)

    - Turbulent stress UV (`S`)

    - Turbulent stress UW (`S`)

    - Turbulent stress VV (`S`)

    - Turbulent stress VW (`S`)

    - Turbulent stress WW (`S`)

    - Velocity covariance UU (`S`)

    - Velocity covariance UV (`S`)

    - Velocity covariance UW (`S`)

    - Velocity covariance VV (`S`)

    - Velocity covariance VW (`S`)

    - Velocity covariance WW (`S`)


-------------------------------------------------------------------------------

Copyright © 2020 Andrew Trettel

This file is licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.  You may
obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
