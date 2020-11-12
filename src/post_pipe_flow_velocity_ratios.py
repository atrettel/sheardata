#!/usr/bin/env python3

# Copyright (C) 2020 Andrew Trettel
#
# This file is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This file is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this file.  If not, see <https://www.gnu.org/licenses/>.

import sheardata as sd
import sqlite3
import sys
from uncertainties import ufloat
from uncertainties import unumpy as unp

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

# Intersection of
# - Stations in duct flow studies
# - Stations in 2D series in cylindrical coordinates with elliptical
#   geometries
# - Stations that have points with smooth walls
# - Stations that have an aspect ratio of 1.0
# - Stations that have the bulk Reynolds number
# - Stations that have the bulk-t-center-line velocity ratio

cursor.execute(
"""
SELECT identifier
FROM stations
WHERE study IN (
    SELECT identifier
    FROM studies
    WHERE flow_class=?
)
INTERSECT
SELECT identifier
FROM stations
WHERE series IN (
    SELECT identifier
    FROM series
    WHERE number_of_dimensions=? AND coordinate_system=? AND geometry=?
)
INTERSECT
SELECT station
FROM points
WHERE identifier IN (
    SELECT point
    FROM point_values
    WHERE quantity=? AND point_value<? AND outlier=0
)
INTERSECT
SELECT station
FROM station_values
WHERE quantity=? AND station_value=? AND outlier=0
INTERSECT
SELECT station
FROM station_values
WHERE quantity=? AND outlier=0
INTERSECT
SELECT station
FROM station_values
WHERE quantity=? AND outlier=0
ORDER BY identifier;
""",
(
    sd.DUCT_FLOW_CLASS,
    int(2),
    sd.CYLINDRICAL_COORDINATE_SYSTEM,
    sd.ELLIPTICAL_GEOMETRY,
    sd.INNER_LAYER_ROUGHNESS_HEIGHT_QUANTITY,
    float(1.0),
    sd.ASPECT_RATIO_QUANTITY,
    float(1.0),
    sd.BULK_REYNOLDS_NUMBER_QUANTITY,
    sd.BULK_TO_CENTER_LINE_VELOCITY_RATIO_QUANTITY,
)
)

stations = []
for result in cursor.fetchall():
    stations.append( result[0] )

for station in stations:
    print( station )

conn.commit()
conn.close()

