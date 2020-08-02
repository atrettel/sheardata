The design of the shear layer database and classes
==================================================


Goals
-----

- Use SQLite as the database backend.  The goal here is to ensure that it is
  possible to use SQL commands to select and find data.

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

    - There are two majors unknowns here.  First, I do not know precisely what
      nondimensionalization works best for each class, but what matters more is
      consistency.  Any methods should return any arbitrary variable anyhow, so
      the precise representation of the data in the database itself does not
      matter.  The second issue relates to the previous point about how much
      data the database should contain.  The simplest choice is to only keep a
      single nondimensionalization in the database and to calculate other
      nondimensionalizations when needed.  The tradeoff is same as before: it
      is more computationally expensive.

    - The nondimensionalization should be unambiguous.  This goal is more
      difficult that it appears.  For example, internal flows have well-defined
      length scales (based on bulk properties and geometry), but external flows
      and free-shear flows do not have any well-defined length scales.  Notions
      like boundary layer thickness are somewhat vague, so I would prefer to
      pick a nondimensionalization that is consistent above all else.

- Keep variable names in both the database and classes human-readable.  Prefer
  `skin_friction_coefficient` to `c_f`.

- Keep track of assumptions for each case.

- Keep track of which parameters are "input" parameters and which are
  calculated.

- Use a dependency graph to automatically calculate all possible variables.

- Use assertions and other checks on the data.


Design details
--------------

- Tables

    - `globals_d` - discrete globals

        - These are global variables that do not have any uncertainty.

        - Note that Fernholz 1977 refers to what I call "globals" as
          "kopfdaten" (header data).  That is another good term for this
          concept.

    - `globals_n` - real values of globals

        - It would be simpler to just note various profile locations with
          labels (wall, edge, etc.) rather than have a large number of
          additional global variables.  However, no single point in the profile
          might represent these states (but in many cases it will).

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


Table fields
------------

Some of these only apply to certain flow classes (the most general flow class
being listed).

- Globals (discrete)

    - Profile identifier (`S`)

    - Series identifier (`S`)

    - Case identifier (`S`)

    - Flow class (`S`)

    - Year (`S`)

    - Case number (`S`)

    - Series number (`S`)

    - Profile number (`S`)

    - Data type (`S`)

        - `E` for experimental, `N` for numerical.

    - Originator's identifier (`S`)

    - Working fluid (`S`)

    - Working fluid phase (`S`)

    - Number of dimensions (`S`)

        - 2 or 3.  Setting this to 2 should enforce certain values for certain
          profiles.

    - Coordinate system (`S`)

        - `XYZ`, `XRT`, etc.

    - Geometry (`I`)

        - `E` for ellipse, `P` for polygon

    - Number of sides (`I`)

        - 3 for triangular duct, 4 for rectangular ducts, ...

    - Streamwise previous station (`S`)

    - Streamwise next station (`S`)

    - Spanwise previous station (`S`)

    - Spanwise next station (`S`)

- Globals (real)

    - Profile identifier (`S`)

    - Origin, streamwise coordinate (`S`)

    - Origin, transverse coordinate (`S`)

    - Origin, spanwise coordinate (`S`)

    - Streamwise wall curvature (`C`)

    - Spanwise wall curvature (`C`)

        - Fernholz 1977, p. 13 defines this as positive for external flows and
          negative for internal flows.

    - Roughness height (`C`)

    - Friction Reynolds number (`C`)

    - Semi-local friction Reynolds number (`C`)

    - Incompressible displacement thickness (`C`)

    - Incompressible momentum thickness (`C`)

    - Compressible displacement thickness (`C`)

    - Compressible momentum thickness (`C`)

    - Equilibrium parameter (`E`)

    - Aspect ratio (`I`)

    - Hydraulic diameter (`I`)

    - Freestream turbulence intensity (`C`)

    - Edge Mach number (`C`) 

    - Friction Mach number (`C`)

- Profiles (real)

    - Point identifier (`S`)

    - Profile identifier (`S`)

    - Point number (`S`)

    - Label (`S`)

        - Center-line, edge, maximum, wall, etc.

    - Transverse coordinate (`S`)

        - It might be better to refer to this as the distance from the local
          origin.  For wall-bounded flows, this could interpreted as the
          wall-normal distance from the wall.

    - Mean bulk viscosity (`S`)

    - Mean density (`S`)

    - Mean dynamic viscosity (`S`)

    - Mean heat capacity ratio (`S`)

    - Mean isobaric heat capacity (`S`)

    - Mean isochoric heat capacity (`S`)

    - Mean kinematic viscosity (`S`)

    - Mean Mach number (`S`)

    - Mean Momentum density (`S`)

    - Mean Prandtl number (`S`)

    - Mean pressure (`S`)

    - Mean shear stress (`S`)

    - Mean spanwise velocity (`S`)

    - Mean spanwise vorticity (`S`)

    - Mean specific enthalpy (`S`)

    - Mean specific entropy (`S`)

    - Mean specific internal energy (`S`)

    - Mean specific total enthalpy (`S`)

    - Mean specific total internal energy (`S`)

    - Mean specific volume (`S`)

    - Mean speed (`S`)

    - Mean speed of sound (`S`)

    - Mean stagnation pressure (`S`)

    - Mean stagnation temperature (`S`)

    - Mean streamwise velocity (`S`)

    - Mean streamwise vorticity (`S`)

    - Mean temperature (`S`)

    - Mean thermal conductivity (`S`)

    - Mean thermal diffusivity (`S`)

    - Mean transverse velocity (`S`)

    - Mean transverse vorticity (`S`)

    - Mean turbulent kinetic energy (`S`)

    - Mean turbulent stress UU (`S`)

    - Mean turbulent stress UV (`S`)

    - Mean turbulent stress UW (`S`)

    - Mean turbulent stress VV (`S`)

    - Mean turbulent stress VW (`S`)

    - Mean turbulent stress WW (`S`)

-------------------------------------------------------------------------------

Copyright © 2020 Andrew Trettel

This file is licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.  You may
obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
