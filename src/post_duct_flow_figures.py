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
# - Stations in duct flow experimental studies
# - Stations in 2D series in cylindrical coordinates with elliptical
#   geometries
# - Stations that are fully-developed (next station is the previous station)
# - Stations that have points with smooth walls
# - Stations that have an aspect ratio of 1.0
# - Stations that have bulk Mach numbers between 0.0 and 0.3
# - Stations that have the bulk Reynolds number
# - Stations that have the bulk-to-center-line velocity ratio

cursor.execute(
"""
SELECT identifier
FROM stations
WHERE study IN (
    SELECT identifier
    FROM studies
    WHERE flow_class=? AND study_type=?
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
SELECT identifier
FROM stations
WHERE previous_streamwise_station=next_streamwise_station
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
WHERE quantity=? AND station_value>=? AND station_value<? AND outlier=0
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
    sd.EXPERIMENTAL_STUDY_TYPE,
    int(2),
    sd.CYLINDRICAL_COORDINATE_SYSTEM,
    sd.ELLIPTICAL_GEOMETRY,
    sd.INNER_LAYER_ROUGHNESS_HEIGHT_QUANTITY,
    float(1.0),
    sd.ASPECT_RATIO_QUANTITY,
    float(1.0),
    sd.BULK_MACH_NUMBER_QUANTITY,
    float(0.0),
    float(0.3),
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

bulk_reynolds_number_bounds = ( 1.00e3, 1.00e5 )
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

with open( "caption-pipe-flow-velocity-ratios.tex.tmp", "w" ) as f:
    short_caption = "Bulk-to-center-line velocity ratios for fully-developed, \
                     incompressible pipe flow as a function of the bulk \
                     Reynolds number."

    f.write( r"\caption[" )
    f.write( short_caption )
    f.write( r"]{" )
    f.write( short_caption+"  " )

    f.write( "{:d} points in total: ".format(
        len(stations),
    ) )

    studies = sd.count_studies( stations )
    i_study = 0
    for study in studies:
        f.write( r"\texttt{" )
        f.write( "{:s}".format(
            sd.make_readable_identifier( study ),
        ) )
        f.write( r"}" )
        f.write( ", {:d} points".format(
            studies[study],
        ) )
        i_study += 1
        if ( i_study != len(studies) ):
            f.write( "; " )

    f.write( r".}" )
