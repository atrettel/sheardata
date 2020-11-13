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
# - Stations that have the quantity of interest

for quantity in [ sd.BULK_TO_CENTER_LINE_VELOCITY_RATIO_QUANTITY,
                             sd.FANNING_FRICTION_FACTOR_QUANTITY ]:
    if ( quantity == sd.BULK_TO_CENTER_LINE_VELOCITY_RATIO_QUANTITY ):
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
            quantity,
        )
        )
    elif ( quantity == sd.FANNING_FRICTION_FACTOR_QUANTITY ):
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
        FROM points
        WHERE identifier IN (
            SELECT point
            FROM point_values
            WHERE quantity=? AND outlier=0
        )
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
            quantity,
        )
        )

    stations = []
    for result in cursor.fetchall():
        stations.append( str(result[0]) )

    bulk_reynolds_number_array = []
    quantity_values_array      = []
    for station in stations:
        bulk_reynolds_number_array.append( sd.get_station_value(
            cursor,
            station,
            sd.BULK_REYNOLDS_NUMBER_QUANTITY,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
        ) )

        if ( quantity == sd.BULK_TO_CENTER_LINE_VELOCITY_RATIO_QUANTITY ):
            quantity_values_array.append( sd.get_station_value(
                cursor,
                station,
                quantity,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            ) )
        elif ( quantity == sd.FANNING_FRICTION_FACTOR_QUANTITY ):
            quantity_values_array.append( sd.get_labeled_value(
                cursor,
                station,
                quantity,
                sd.WALL_POINT_LABEL,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            ) )

    fig = plt.figure()
    ax  = fig.add_subplot( 1, 1, 1 )

    bulk_reynolds_number = np.array( bulk_reynolds_number_array )
    quantity_values      = np.array(      quantity_values_array )

    bulk_reynolds_number_bounds = None
    quantity_values_bounds      = None
    y_label        = None
    filename_label = None
    quantity_label = None
    if ( quantity == sd.BULK_TO_CENTER_LINE_VELOCITY_RATIO_QUANTITY ):
        bulk_reynolds_number_bounds = ( 1.00e+3, 1.00e+5, )
        quantity_values_bounds      = ( 0.50e+0, 0.85e+0, )

        y_label        = r"$\frac{U_b}{U_c}$"
        filename_label = "velocity-ratios"
        quantity_label = "Bulk-to-center-line velocity ratio"

        ax.semilogx(
            unp.nominal_values( bulk_reynolds_number  ),
            unp.nominal_values( quantity_values ),
            marker="o",
            linestyle="",
            clip_on=False,
            zorder=1,
        )
    elif ( quantity == sd.FANNING_FRICTION_FACTOR_QUANTITY ):
        bulk_reynolds_number_bounds = ( 1.00e+1, 1.00e+6, )
        quantity_values_bounds      = ( 1.00e-3, 1.00e-1, )

        y_label        = r"$f = \frac{2 \tau_w}{\rho U_b^2}$"
        filename_label = "fanning-friction-factor"
        quantity_label = "Fanning friction factor"

        ax.loglog(
            unp.nominal_values( bulk_reynolds_number  ),
            unp.nominal_values( quantity_values ),
            marker="o",
            linestyle="",
            clip_on=True,
            zorder=2,
        )

        laminar_bulk_reynolds_number = np.linspace(
            bulk_reynolds_number_bounds[0],
            2.0e+3,
            gfx.page_size.max_elements(),
        )
        laminar_fanning_friction_factor = 16.0 / laminar_bulk_reynolds_number

        ax.loglog(
            laminar_bulk_reynolds_number,
            laminar_fanning_friction_factor,
            clip_on=True,
            zorder=1,
        )

    ax.set_xlim( bulk_reynolds_number_bounds )
    ax.set_ylim(      quantity_values_bounds )

    gfx.label_axes(
        ax,
        r"$\mathrm{Re}_b = U_b D_H / \nu$",
        y_label
    )

    fig.savefig( "figure-pipe-flow-{:s}.pgf".format( filename_label ) )
    fig.clear()
    plt.close( fig )

    with open( "caption-pipe-flow-{:s}.tex.tmp".format( filename_label ), "w" ) as f:
        short_caption = "{:s} for fully-developed, incompressible pipe flow \
                         as a function of the bulk Reynolds number.".format(
            quantity_label,
        )

        f.write( r"\caption[" )
        f.write( short_caption )
        f.write( r"]{" )
        f.write( short_caption+"  " )

        f.write( "{:d} stations in total: ".format(
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
            f.write( ", {:d} stations".format(
                studies[study],
            ) )
            i_study += 1
            if ( i_study != len(studies) ):
                f.write( "; " )

        f.write( r".}" )

conn.commit()
conn.close()
