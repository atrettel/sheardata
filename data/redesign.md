Redesign of the shear layer database
====================================


## Data categories

The data categories serve as the main subjects of the database.  Different
quantities are classified under different data categories depending on the
nature of the quantity in question.

| Data category       | Description                                       |
| ------------------- | ------------------------------------------------- |
| Fluids              | Physical media for flow                           |
| Facilities          | Experimental facilities or numerical codes        |
| Facility components | Parts of facilities                               |
| Instruments         | Measurement probes and calculation techniques     |
| Models              | Objects around which or through which fluid flows |
| Model sections      | Slices of models, composed of vertices            |
| Model vertices      | 3D points of a model                              |
| Studies             | Collections of series                             |
| Series              | Individual realizations of flow                   |
| Stations            | Lines or profiles in a flow                       |
| Flow sections       | Cross sections of flow                            |
| Points              | Locations in a flow                               |
| Times               | Instances of time                                 |


## Tables

TODO: Create a list of tables.  Classify them as data tables, linking tables,
subset tables, or validation tables (lookup tables).  There should be no views
listed here.


## Quantities

This table is a work in progress.  Unlike the previous table, some calculated
quantities are listed here as views.  Some data tables need to be calculated
manually, but I have not noted this yet.

Labeled points count as another type of data category in this table.  There are
four label categories:

- center-line

- edge

- far-field

- wall

Point quantities should have corresponding views for each of these label
categories for ease of use.

| Quantity                                     | Definition or symbol                          | Data categories                 | Type       |
| -------------------------------------------- | --------------------------------------------- | ---------------------------     | ---------- |
| Angle of attack                              | `alpha`                                       | Series                          | Data table |
| Drag coefficient                             | `C_D = D / ( q_inf * A_r )`                   | Series, model, far-field points | View       |
| Drag force                                   | `D`                                           | Series                          | Data table |
| Reference area                               | `A_r`                                         | Model                           | Data table |
| Projected frontal area                       | `A_p`                                         | Model                           | Data table |
| Body volume                                  | `V`                                           | Model                           | Data table |
| Body mass                                    | `m`                                           | Model                           | Data table |
| Body surface area                            | `S`                                           | Model                           | Data table |
| Body planform area                           | `A_w`                                         | Model                           | Data table |
| Body span                                    | `s`                                           | Model                           | Data table |
| Body planform aspect ratio                   | `AR = s^2 / A_w`                              | Model                           | View       |
| Body standard mean chord                     | `SMC = A_w / s`                               | Model                           | View       |
| Freestream Mach number                       | `Ma_inf = V_inf / a_inf`                      | Far-field points                | View       |
| Lift coefficient                             | `C_L = L / ( q_inf * A_p )`                   | Series, model, far-field points | View       |
| Lift force                                   | `L`                                           | Series                          | Data table |
| Lift-to-drag ratio                           | `L/D`                                         | Series                          | View       |
| Body length                                  | `l_b`                                         | Model                           | Data table |
| Body width                                   | `w_b`                                         | Model                           | Data table |
| Body height                                  | `h_b`                                         | Model                           | Data table |
| Body length Reynolds number                  | `Re_l = V_inf * l_b / nu_inf`                 | Series, model                   | View       |
| Body width  Reynolds number                  | `Re_w = V_inf * w_b / nu_inf`                 | Series, model                   | View       |
| Body height Reynolds number                  | `Re_h = V_inf * h_b / nu_inf`                 | Series, model                   | View       |
| Mass flow rate                               | `mdot`                                        | Flow section                    | Data table |
| Bulk mass density                            | `rho_b = mdot / Q`                            | Flow section                    | View       |
| Volumetric flow rate                         | `Q`                                           | Flow section                    | Data table |
| Cross-sectional dynamic viscosity            | `mu_cs`                                       | Flow section                    | Data table |
| Cross-sectional speed                        | `V_cs = Q / A_cs`                             | Flow section, model section     | View       |
| Cross-sectional area                         | `A_cs`                                        | Model section                   | Data table |
| Cross-sectional kinematic viscosity          | `nu_cs = mu_cs / rho_cs`                      | Flow section                    | View       |
| Cross-sectional Mach number                  | `Ma_cs = V_cs / a_cs`                         | Flow section                    | View       |
| Cross-sectional speed of sound               | `a_cs`                                        | Flow section                    | Data table |
| Hydraulic diameter                           | `D_H = 4 * A_cs / P_cs`                       | Model section                   | View       |
| Hydraulic radius                             | `R_H = 0.25 * D_H`                            | Model section                   | View       |
| Cross-sectional perimeter (wetted perimeter) | `P_cs`                                        | Model section                   | Data table |
| Hydraulic diameter Reynolds number           | `Re_D = V_cs * D_H / nu_cs`                   | Flow section, model section     | View       |
| Hydraulic radius Reynolds number             | `Re_D = V_cs * R_H / nu_cs`                   | Flow section, model section     | View       |
| Clauser thickness                            | `Delta`                                       | Station                         | Data table |
| Cross-sectional height                       | `h_cs`                                        | Model section                   | Data table |
| Cross-sectional width                        | `w_cs`                                        | Model section                   | Data table |
| Cross-sectional half-height                  | `b_cs = 0.5 * h_cs`                           | Model section                   | View       |
| Cross-sectional aspect ratio                 | `AR_cs = w_cs / h_cs`                         | Model section                   | View       |
| Development length                           | `l_d`                                         | Station                         | Data table |
| Displacement thickness                       | `delta_1`                                     | Station                         | Data table |
| Displacement thickness Reynolds number       | `Re_delta_1 = u_e * delta_1 / nu_e`           | Station, edge points            | View       |
| Momentum thickness                           | `delta_2`                                     | Station                         | Data table |
| Momentum thickness Reynolds number           | `Re_delta_2 = u_e * delta_2 / nu_e`           | Station, edge points            | View       |
| Modified momentum thickness Reynolds number  | `Re_delta_2 = rho_e * u_e * delta_2 / mu_w`   | Station, edge points            | View       |
| Energy thickness                             | `delta_3`                                     | Station                         | Data table |
| Shape factor 1-to-2                          | `H_12 = delta_1 / delta_2`                    | Station                         | View       |
| Shape factor 3-to-2                          | `H_32 = delta_3 / delta_2`                    | Station                         | View       |
| Equilibrium parameter                        | `beta = delta_1 * dP/dx_w / tau_xy_w`         | Station, wall points            | View       |
| Inner diameter                               | `D_i`                                         | Model section                   | Data table |
| Outer diameter                               | `D_o`                                         | Model section                   | Data table |
| Momentum integral left-hand side             | `phi_l`                                       | ?                               | Data table |
| Momentum integral right-hand side            | `phi_r`                                       | ?                               | Data table |
| Outer-layer length scale                     | `l_o`                                         | ?                               | Data table |
| Outer-layer development length               | `l_d / l_o`                                   | Station, ?                      | View       |
| Temperature recovery factor                  | `r = ( T_aw - T_e ) / ( T_0_e - T_e )`        | Wall and edge points            | View       |
| Fanning friction factor                      | `f_f = 0.5 * tau_xy_w / ( rho_cs * V_cs )`    | Flow section, wall points       | View       |
| Darcy friction factor                        | `f_D = 4.0 * f_f`                             | Flow section, wall points       | View       |

TODO: Add these quantities below, which the current list depends on.

- Pressure gradient (all 3 components)

- Shear stress (all 6 components)

- Dynamic pressure

TODO: Also add

- Number of points (in all 3 directions) as a series quantity.  Unlike the
  other quantities, the value field number be an integer.

- Average skin friction coefficient

Notes on some quantities:

- The reference area in the drag and lift coefficients largely depends on the
  type of body, so drag coefficients between different types of bodies may not
  be directly comparable.

- The outer-layer length scale requires a `UNION`, since it varies based on the
  flow class.  For boundary layers, it is one of the many boundary layer
  thicknesses.  For internal flows, it depends on the flow type.  For pipe
  flows it is the pipe radius and for channel flows it is the channel
  half-height.

- The temperature recovery factor should only be defined for adiabatic walls.


## Fields for quantities

- Given flow quantities

    - Identifier, either `study_id`, `series_id`, `station_id`, or `point_id`

    - Time, `time_id`

    - Fluid, `fluid_id`

    - Value type, `value_type_id`

    - Instrument, `instrument_id`

        - This only allows for one measurement per instrument, though, so
          repeated measurements with the same instrument cannot be represented
          here.  That may be an adequate design choice since I am concerned
          about how variations in the instrumentation affect the results.  Any
          variation with the same instrument is better represented through
          uncertainty quantification.

    - Mean value, `value`

    - Standard uncertainty, `uncertainty`

        - The mean value and standard uncertainty allow for standard
          uncertainty propagation.

    - Minimum value, `minimum`

    - Maximum value, `maximum`

        - The minimum and maximum values allow for uncertainty propagation
          using interval arithmetic.  They also provide an additional check on
          other values.  Note that for uniform distributions, the mean value is
          the average of the minimum and maximum values, but using two separate
          values, rather than merely some kind of "uncertainty" centered around
          the mean, allows for more information about the probability
          distribution to be represented in a simple manner.

    - Correction status, `corrected`

        - TODO: Is this needed?  This may be an instrument property rather than
          a property of the value itself.  In that sense, corrected values are
          values with a different instrument, in a sense.

    - Outlier status, `outlier`

- Calculated flow quantities

    - These may have additional quantities and may be more complicated.  For
      example, there may be more than one instrument given and more than one
      type of data category identifier.


-------------------------------------------------------------------------------

Copyright © 2022-2023 Andrew Trettel

SPDX-License-Identifier: CC-BY-4.0

