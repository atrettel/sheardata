Tables for shear-layer database
===============================

- TODO: Determine tables for fluid properties.

    - These can just mirror the flow quantity tables.

- TODO: Determine the correspondence between points and model vertices.

    - Models correspond to the walls in internal and external flows.  They do
      not come into play in free-shear flows.  Each station can correspond to
      up to two model vertices, so for uniqueness model vertices should
      correspond directly to points at the wall (each wall point may have a
      single model vertices, in other words).  However, this poses a
      difficulty, since the model data must always contain the relevant points.
      This also introduces the possiblity of some data redundancy, which should
      be avoided as much as possible.

    - Model sections are a bit different.  In internal flows, model sections
      are the cross section of the duct.  In external flows, model sections are
      the cross section of the object.  Model sections correspond to a station
      in an internal flow, but a given section in an external flow many have
      multiple stations.  This distinction is tricky and I need to develop a
      better way to handle this.

        - One way to handle this is to avoid the association between stations
          and sections altogether.  Instead, each model vertex may be part of
          one model section.  Accessing the section data would require a large
          amount of joins, but this prevents any data redundancy and simplifies
          the tables.

- TODO: In some boundary layer studies, the model is the wind tunnel wall
  itself. 
  
    - In that case, each model can correspond to a particular facility
      component, but in general the database must not include full CAD models
      for facility components.


## The data categories

- Data category

    - Fluids

    - Facilities

        - Facility components

    - Instruments

    - Models

        - Model sections

        - Model vertices

    - Studies

        - Series

            - Stations

                - Points


## Quantities

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

        - TODO: Is this needed?

    - Outlier status, `outlier`

- Calculated flow quantities

    - These may have additional quantities and may be more complicated.


### Table of quantities

TOOD: Complete the table.

| Quantity           | Category           | Type       |
| ------------------ | ------------------ | ---------- |
| Angle of attack    | Series             | Given      |
| Coordinate         | Point              | Given      |
| Density            | Point              | Given      |
| Distance from wall | Point              | Calculated |
| Mesh size          | Facility component | Given      |
| Roughness height   | Model              | Given      |
| Specific volume    | Point              | Calculated |


-------------------------------------------------------------------------------

Copyright © 2022 Andrew Trettel

SPDX-License-Identifier: MIT

