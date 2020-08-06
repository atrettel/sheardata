The design of the shear layer database and classes
==================================================


Goals
-----

- Use SQLite as the database backend.  The goal here is to ensure that it is
  possible to use SQL commands to select and find data.

    - Limit the number of calls to the database itself (separate use and
      implementation).  This could allow me to change the kind of database
      later.

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


Design details
--------------

- Tables

    - `discrete_globals`

        - These are global variables that do not have any uncertainty.

    - `dimensional_globals_n`, `dimensional_globals_s`

        - These are global variables that have some uncertainty but do not
          change in different averaging systems.

        - It would be simpler to just note various profile locations with
          labels (wall, edge, etc.) rather than have a large number of
          additional global variables.  However, no single point in the profile
          might represent these states (but in many cases it will).  Redundancy
          through duplication seems like a worthwhile tradeoff in that case.

    - `uw_dimensional_globals_n`, `uw_dimensional_globals_s`

    - `dw_dimensional_globals_n`, `dw_dimensional_globals_s`

    - `uw_dimensionless_globals_n`, `uw_dimensionless_globals_s`

    - `dw_dimensionless_globals_n`, `dw_dimensionless_globals_s`

    - `uw_dimensionless_profiles_n`, `uw_dimensionless_profiles_s`

    - `dw_dimensionless_profiles_n`, `dw_dimensionless_profiles_s`

- Have corresponding tables for values and uncertainties.  The field names
  should be identical.  `n` is for the values and `s` is for uncertainties.
  This convention follows the Python `uncertainties` package.  Also have
  corresponding tables of unweighted variables (`uw`) and density-weighted
  variables (`dw`).

- Include additional fields for commentary (likely editorial commentary).  Also
  include additional fields for the people involved, the facilities involved,
  the organizations involved, locations of any experiments, and any contract
  numbers.

- Note the type of measurement used (though this will require an additional set
  of codes or a taxonomy of these).


Table fields
------------

Some of these only apply to certain flow classes (the most general flow class
being listed).

- Discrete globals

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

    - Number of points (`S`)

    - Number of dimensions (`S`)

        - 2 or 3.  Setting this to 2 should enforce certain values for certain
          profiles.

    - Originator's identifier (`S`)

    - Working fluid (`S`)

        - Consider using CAS registry numbers for these.  These are
          standardized.  A separate table for fluid properties could then also
          exist.

    - Working fluid phase (`S`)

    - Coordinate system (`S`)

        - `XYZ`, `XRT`, `RTZ`, `RTP`, etc.

    - Geometry (`I`)

        - `E` for ellipse, `P` for polygon

    - Number of sides (`I`)

        - 3 for triangular duct, 4 for rectangular ducts, ...

    - Streamwise previous station (`S`)

        - Pointers like these are much more flexible than assuming that the
          profile numbers are in order by station number.

    - Streamwise next station (`S`)

    - Spanwise previous station (`S`)

        - These should also be null for 2D flows.

    - Spanwise next station (`S`)

    - Regime (`S`)

        - Laminar, transitional, turbulent.  It may be better to consider this
          algorithmically, though.

    - Trip present? (`C`)

- Dimensional globals (real, use SI, averaging-system independent)

    - Profile identifier (`S`)

    - Origin, streamwise coordinate (`S`)

    - Origin, transverse coordinate (`S`)

    - Origin, spanwise coordinate (`S`)

    - Streamwise wall curvature (`C`)

    - Spanwise wall curvature (`C`)

        - Fernholz 1977, p. 13 defines this as positive for external flows and
          negative for internal flows.

    - Roughness height (`C`)

    - Characteristic width (`I`)

    - Characteristic height (`I`)

    - Aspect ratio (`I`)

        - This is actually dimensionless.

    - Cross-sectional area (`I`)

    - Wetted perimeter (`I`)

    - Hydraulic diameter (`I`)

    - Streamwise trip location (`C`)

- Dimensional globals (real, use SI, averaging-system dependent)

    - Profile identifier (`S`)

    - Bulk dynamic viscosity (`I`)

    - Bulk kinematic viscosity (`I`)

    - Bulk mass density (`I`)

    - Bulk pressure (`I`)

    - Bulk specific isobaric heat capacity (`I`)

    - Bulk speed of sound (`I`)

    - Bulk streamwise velocity (`I`)

    - Bulk temperature (`I`)

    - Bulk transverse velocity (`I`)

    - Center-line dynamic viscosity (`I`)

    - Center-line kinematic viscosity (`I`)

    - Center-line mass density (`I`)

    - Center-line pressure (`I`)

    - Center-line specific isobaric heat capacity (`I`)

    - Center-line speed of sound (`I`)

    - Center-line streamwise velocity (`I`)

    - Center-line temperature (`I`)

    - Center-line transverse velocity (`I`)

    - Clauser thickness (`C`)

    - Compressible displacement thickness (`C`)

    - Compressible momentum thickness (`C`)

    - Edge dynamic viscosity (`E` and `F`)

    - Edge kinematic viscosity (`E` and `F`)

    - Edge mass density (`E` and `F`)

    - Edge pressure (`E` and `F`)

    - Edge specific isobaric heat capacity (`E` and `F`)

    - Edge speed of sound (`E` and `F`)

    - Edge streamwise velocity (`E` and `F`)

    - Edge temperature (`E` and `F`)

    - Edge transverse velocity (`E` and `F`)

    - Edge velocity gradient (`E` and `F`)

    - Friction velocity (`C`)

    - Friction temperature (`C`)

    - Incompressible displacement thickness (`C`)

    - Incompressible momentum thickness (`C`)

    - Left-hand side of momentum integral (`E`)

    - Mass flow rate (`I`)

    - Maximum dynamic viscosity (`S`)

    - Maximum kinematic viscosity (`S`)

    - Maximum mass density (`S`)

    - Maximum pressure (`S`)

    - Maximum specific isobaric heat capacity (`S`)

    - Maximum speed of sound (`S`)

    - Maximum streamwise velocity (`S`)

    - Maximum temperature (`S`)

    - Maximum transverse velocity (`S`)

    - Minimum dynamic viscosity (`S`)

    - Minimum kinematic viscosity (`S`)

    - Minimum mass density (`S`)

    - Minimum pressure (`S`)

    - Minimum specific isobaric heat capacity (`S`)

    - Minimum speed of sound (`S`)

    - Minimum streamwise velocity (`S`)

    - Minimum temperature (`S`)

    - Minimum transverse velocity (`S`)

    - Reservoir pressure (`S`)

    - Reservoir speed of sound (`S`)

    - Reservoir temperature (`S`)

    - Right-hand side of momentum integral (`E`)

    - Streamwise pressure gradient (`C`)

    - Viscous length scale (`C`)

    - Wall dynamic viscosity (`C`)

    - Wall kinematic viscosity (`C`)

    - Wall mass density (`C`)

    - Wall pressure (`C`)

    - Wall shear stress (`C`)

    - Wall specific isobaric heat capacity (`S`)

    - Wall speed of sound (`C`)

    - Wall streamwise velocity (`C`)

    - Wall temperature (`C`)

    - Wall transverse velocity (`C`)

    - 99-percent velocity boundary layer thickness

    - 99-percent temperature boundary layer thickness

- Dimensionless globals (real, averaging-system dependent)

    - Profile identifier (`S`)

    - Bulk heat capacity ratio (`I`)

    - Bulk Mach number (`I`)

    - Bulk Prandtl number (`I`)

    - Center-line heat capacity ratio (`I`)

    - Center-line Mach number (`I`)

    - Center-line Prandtl number (`I`)

    - Dimensionless wall heat flux (`B_q`) (`C`)

    - Edge heat capacity ratio (`E`)

    - Edge Mach number (`E`)

    - Edge Prandtl number (`E`)

    - Edge Reynolds number based on displacement thickness (`E`)

    - Edge Reynolds number based on momentum thickness (`E`)

    - Equilibrium parameter (`E`)

    - Freestream turbulence intensity (`S`)

    - Friction factor (`I`)

    - Friction Mach number (`C`)

    - Friction Reynolds number (`C`)

    - Heat transfer coefficient (`E`)

    - Maximum heat capacity ratio  (`S`)

    - Maximum Mach number (`S`)

    - Maximum Prandtl number (`S`)

    - Minimum heat capacity ratio  (`S`)

    - Minimum Mach number (`S`)

    - Minimum Prandtl number (`S`)

    - Recovery factor (`C`)

    - Semi-local friction Reynolds (`C`)

    - Skin friction coefficient (`E`)

    - Wall heat capacity ratio (`C`)

    - Wall Mach number (`C`)

    - Wall Prandtl number (`C`)

- Dimensionless profiles (real, averaging-system dependent)

    - Point identifier (`S`)

    - Profile identifier (`S`)

    - Point number (`S`)

    - Label (`S`)

        - Center-line, edge, maximum, minimum, wall

    - Transverse coordinate (`S`)

        - It might be better to refer to this as the distance from the local
          origin.  For wall-bounded flows, this could interpreted as the
          wall-normal distance from the wall.

    - Distance from wall (`C`)

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
