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
import numpy as np
from uncertainties import ufloat
from uncertainties import unumpy as unp

import matplotlib as mpl
mpl.use("pgf")
import matplotlib.pylab as plt
import grfstyl as gfx
mpl.rcParams.update( gfx.rc_custom_preamble() )

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

bulk_reynolds_number_array = []
velocity_ratio_array       = []
for station in stations:
    bulk_reynolds_number_array.append( sd.get_station_value(
        cursor,
        station,
        sd.BULK_REYNOLDS_NUMBER_QUANTITY,
        averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
    ) )
    velocity_ratio_array.append( sd.get_station_value(
        cursor,
        station,
        sd.BULK_TO_CENTER_LINE_VELOCITY_RATIO_QUANTITY,
        averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
    ) )

conn.commit()
conn.close()

fig = plt.figure()
ax  = fig.add_subplot( 1, 1, 1 )

bulk_reynolds_number = np.array( bulk_reynolds_number_array )
velocity_ratio       = np.array( velocity_ratio_array       )

bulk_reynolds_number_bounds = ( 1.00e1, 1.00e6 )
velocity_ratio_bounds       = ( 0.50,   0.85   )

ax.semilogx(
    unp.nominal_values( bulk_reynolds_number  ),
    unp.nominal_values( velocity_ratio ),
    marker="o",
    linestyle="",
    clip_on=False,
)

ax.set_xlim( bulk_reynolds_number_bounds )
ax.set_ylim(       velocity_ratio_bounds )

gfx.label_axes(
    ax,
    r"$\mathrm{Re}_b$",
    r"$\frac{U_b}{U_c}$",
)

fig.savefig( "figure-pipe-flow-velocity-ratios.pgf" )
