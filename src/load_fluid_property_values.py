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

###########################
# NBS Circular 564 (1955) #
###########################
citation_key = "HilsenrathJ+1955+eng+BOOK"

scales = {
( sd.F_AIR, sd.Q_MASS_DENSITY         ): 1293.04,
( sd.F_AIR, sd.Q_SPEED_OF_SOUND       ): 331.45,
( sd.F_AIR, sd.Q_DYNAMIC_VISCOSITY    ): 1.716e-5,
( sd.F_AIR, sd.Q_THERMAL_CONDUCTIVITY ): 2.414e-2,
( sd.F_AIR, sd.Q_PRANDTL_NUMBER       ): 1.0,
}

fluid_property_filename = "../data/fluid_property_values/{:s}.csv".format( citation_key )
with open( fluid_property_filename, "r" ) as fluid_property_file:
    fluid_property_reader = csv.reader( fluid_property_file, delimiter=",", quotechar='"', skipinitialspace=True )
    next(fluid_property_reader)
    for fluid_property_row in fluid_property_reader:
        pressure    = float(fluid_property_row[0]) * sd.STANDARD_ATMOSPHERIC_PRESSURE
        temperature = float(fluid_property_row[1])
        fluid_id    =   str(fluid_property_row[2])
        quantity_id =   str(fluid_property_row[3])
        value       = scales[fluid_id,quantity_id] * float(fluid_property_row[4])

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

conn.commit()
conn.close()
