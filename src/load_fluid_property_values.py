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

scales = {
    "HilsenrathJ+1955+eng+BOOK": {
        ( sd.F_AIR, sd.Q_MASS_DENSITY         ): 1293.04,
        ( sd.F_AIR, sd.Q_SPEED_OF_SOUND       ): 331.45,
        ( sd.F_AIR, sd.Q_DYNAMIC_VISCOSITY    ): 1.716e-5,
        ( sd.F_AIR, sd.Q_THERMAL_CONDUCTIVITY ): 2.414e-2,
        ( sd.F_AIR, sd.Q_PRANDTL_NUMBER       ): 1.0,
    },
    "WilsonW+1959+eng+RPRT": {
        ( sd.F_LIQUID_WATER, sd.Q_SPEED_OF_SOUND ): 1.0,
    }
}

for citation_key in scales:
    fluid_property_filename = "../data/fluid_property_values/{:s}.csv".format( citation_key )
    with open( fluid_property_filename, "r" ) as fluid_property_file:
        fluid_property_reader = csv.reader( fluid_property_file, delimiter=",", quotechar='"', skipinitialspace=True )

        # Determine pressure and temperature scales
        fluid_property_row = fluid_property_reader.__next__()
        pressure_label    = str(fluid_property_row[0])
        temperature_label = str(fluid_property_row[1])

        pressure_scale    = 0.0
        if ( pressure_label == "Pressure [Pa]" ):
            pressure_scale = 1.0
        elif ( pressure_label == "Pressure [atm]" ):
            pressure_scale = sd.STANDARD_ATMOSPHERIC_PRESSURE
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
            pressure    = float(fluid_property_row[0]) *    pressure_scale +    pressure_baseline
            temperature = float(fluid_property_row[1]) * temperature_scale + temperature_baseline
            fluid_id    =   str(fluid_property_row[2])
            quantity_id =   str(fluid_property_row[3])
            value       = float(fluid_property_row[4]) * scales[citation_key][fluid_id,quantity_id]

            print( ( pressure, temperature, fluid_id, quantity_id, value ) )

            cursor.execute(
            """
            INSERT INTO fluid_property_values( pressure, temperature, fluid_id,
                                               citation_key, quantity_id,
                                               fluid_property_value,
                                               fluid_property_uncertainty,
                                               outlier )
            VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
            """,
            (
                pressure,
                temperature,
                fluid_id,
                citation_key,
                quantity_id,
                value,
                sd.UNKNOWN_UNCERTAINTY,
                False,
            )
            )

########################################
conn.commit()
conn.close()
