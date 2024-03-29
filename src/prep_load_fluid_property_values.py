#!/usr/bin/env python3

# Copyright (C) 2022 Andrew Trettel
#
# SPDX-License-Identifier: MIT

import csv
import math
import sqlite3
import sheardata as sd
import sys

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

conn.commit()
conn.close()
exit()

scales = {
    "HilsenrathJ+1955+eng+BOOK": {
        ( sd.F_GASEOUS_AIR, sd.Q_MASS_DENSITY         ): 1293.04,
        ( sd.F_GASEOUS_AIR, sd.Q_SPEED_OF_SOUND       ): 331.45,
        ( sd.F_GASEOUS_AIR, sd.Q_DYNAMIC_VISCOSITY    ): 1.716e-5,
        ( sd.F_GASEOUS_AIR, sd.Q_THERMAL_CONDUCTIVITY ): 2.414e-2,
        ( sd.F_GASEOUS_AIR, sd.Q_PRANDTL_NUMBER       ): 1.0,
    },
    "HaarL+1984+eng+BOOK": {
        ( sd.F_LIQUID_WATER, sd.Q_SPEED_OF_SOUND    ): 1.0,
        ( sd.F_LIQUID_WATER, sd.Q_DYNAMIC_VISCOSITY ): 1.0e-6,
        ( sd.F_LIQUID_WATER, sd.Q_MASS_DENSITY      ): 1.0,

    },
    "ParryWT+2000+eng+BOOK": {
        ( sd.F_LIQUID_WATER, sd.Q_SPECIFIC_VOLUME      ): 1.0,
        ( sd.F_LIQUID_WATER, sd.Q_SPEED_OF_SOUND       ): 1.0,
        ( sd.F_LIQUID_WATER, sd.Q_DYNAMIC_VISCOSITY    ): 1.0e-6,
        ( sd.F_LIQUID_WATER, sd.Q_THERMAL_CONDUCTIVITY ): 1.0e-3,
    },
    "TouloukianYS+1970+eng+BOOK+V3": {
        ( sd.F_GASEOUS_AIR,  sd.Q_THERMAL_CONDUCTIVITY ): 1.0e-1,
        ( sd.F_LIQUID_WATER, sd.Q_THERMAL_CONDUCTIVITY ): 1.0e-1,
    },
    "TouloukianYS+1975+eng+BOOK+V11": {
        ( sd.F_GASEOUS_AIR,  sd.Q_DYNAMIC_VISCOSITY ): 1.0e-6,
        ( sd.F_LIQUID_WATER, sd.Q_DYNAMIC_VISCOSITY ): 1.0e-3,
    },
}

for citation_key in scales:
    fluid_property_filename = "../data/fluid_property_values/{:s}.csv".format( citation_key )
    with open( fluid_property_filename, "r" ) as fluid_property_file:
        fluid_property_reader = csv.reader( fluid_property_file, delimiter=",", quotechar='"', skipinitialspace=True )

        # Determine pressure and temperature scales
        fluid_property_row = fluid_property_reader.__next__()
        pressure_label    = str(fluid_property_row[0])
        temperature_label = str(fluid_property_row[1])
        uncertainty_label = str(fluid_property_row[5])

        pressure_scale    = 0.0
        if ( pressure_label == "Pressure [Pa]" ):
            pressure_scale = 1.0
        if ( pressure_label == "Pressure [MPa]" ):
            pressure_scale = 1.0e6
        elif ( pressure_label == "Pressure [atm]" ):
            pressure_scale = sd.STANDARD_ATMOSPHERIC_PRESSURE
        elif ( pressure_label == "Pressure [bar]" ):
            pressure_scale = sd.PASCALS_PER_BAR
        elif ( pressure_label == "Pressure [psia]" or pressure_label == "Pressure [psig]" ):
            pressure_scale = sd.PASCALS_PER_PSI

        pressure_baseline = 0.0
        if ( pressure_label == "Pressure [psig]" ):
            pressure_baseline = sd.STANDARD_ATMOSPHERIC_PRESSURE

        temperature_scale = 0.0
        if ( temperature_label == "Temperature [K]" or temperature_label == "Temperature [°C]" ):
            temperature_scale = 1.0

        temperature_baseline = 0.0
        if ( temperature_label == "Temperature [°C]" ):
            temperature_baseline = sd.ABSOLUTE_ZERO

        assert( pressure_scale    != 0.0 )
        assert( temperature_scale != 0.0 )

        # Load values.
        for fluid_property_row in fluid_property_reader:
            pressure            = float(fluid_property_row[0]) *    pressure_scale +    pressure_baseline
            temperature         = float(fluid_property_row[1]) * temperature_scale + temperature_baseline
            fluid_id            =   str(fluid_property_row[2])
            quantity_id         =   str(fluid_property_row[3])
            value               = float(fluid_property_row[4]) * scales[citation_key][fluid_id,quantity_id]
            uncertainty_element =       fluid_property_row[5]
            preferred           =   int(fluid_property_row[6])

            assert( quantity_id not in [
                sd.Q_KINEMATIC_VISCOSITY,
                sd.Q_PRANDTL_NUMBER,
                sd.Q_THERMAL_DIFFUSIVITY,
            ] )

            combined_value = sd.sdfloat(value)
            if ( uncertainty_label == "Uncertainty percent" and uncertainty_element != "" ):
                combined_value = sd.uniform_distribution_sdfloat_percent( value, float(uncertainty_element) )

            final_value       = combined_value
            final_quantity_id = quantity_id
            if ( quantity_id == sd.Q_SPECIFIC_VOLUME ):
                final_value       = 1.0 / combined_value
                final_quantity_id = sd.Q_MASS_DENSITY

            cursor.execute(
            """
            INSERT INTO fluid_property_values( pressure, temperature, fluid_id,
                                               citation_key, quantity_id,
                                               fluid_property_value,
                                               fluid_property_uncertainty,
                                               preferred )
            VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
            """,
            (
                pressure,
                temperature,
                fluid_id,
                citation_key,
                final_quantity_id,
                sd.sdfloat_value(final_value),
                sd.sdfloat_uncertainty(final_value),
                preferred,
            )
            )

########################################
conn.commit()
conn.close()
