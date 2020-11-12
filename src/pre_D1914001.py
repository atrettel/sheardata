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

import csv
import math
import sqlite3
import sheardata as sd
import sys
from uncertainties import ufloat
from uncertainties import unumpy as unp

conn = sqlite3.connect( sys.argv[1] )
cursor =  conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

flow_class    = sd.DUCT_FLOW_CLASS
year          = 1914
study_number  = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "StantonTE+1914+eng+JOUR", 1 )

class Pipe:
    diameter = None
    length   = None
    material = None

    def __init__( self, diameter, length, material ):
        self.diameter = float(diameter)
        if ( length == 0.0 ):
            self.length = None
        else:
            self.length   = float(length)
        self.material = str(material)

pipes = {}
pipes_filename = "../data/{:s}/pipes.csv".format( study_identifier )
with open( pipes_filename, "r" ) as pipes_file:
    pipes_reader = csv.reader(
        pipes_file,
        delimiter=",",
        quotechar='"', \
        skipinitialspace=True,
    )
    next(pipes_reader)
    for pipes_row in pipes_reader:
        pipes[str(pipes_row[0])] = Pipe(
            float(pipes_row[1]) * 1.0e-2,
            float(pipes_row[2]) * 1.0e-2,
            str(pipes_row[3]),
        )

series_number = 0
ratio_filename = "../data/{:s}/bulk_and_maximum_velocities.csv".format( study_identifier )
with open( ratio_filename, "r" ) as ratio_file:
    ratio_reader = csv.reader(
        ratio_file,
        delimiter=",",
        quotechar='"', \
        skipinitialspace=True,
    )
    next(ratio_reader)
    for ratio_row in ratio_reader:
        series_number += 1

        bulk_velocity    = float(ratio_row[0]) * 1.0e-2
        maximum_velocity = float(ratio_row[1]) * 1.0e-2
        working_fluid    =   str(ratio_row[2])
        pipe             =   str(ratio_row[3])

        diameter = pipes[pipe].diameter
        length   = pipes[pipe].length

        # The velocity ratio experiments do not give the test conditions like
        # the temperature.  Graphical extraction from figure 1 reveals that the
        # kinematic viscosity used there is consistent with the value around
        # 15°C.
        #
        # These values were extracted graphically from figure 1 and averaged to
        # a single value.
        kinematic_viscosity = 0.0
        if ( working_fluid == "Water" ):
            kinematic_viscosity = 9.186e-7
        elif ( working_fluid == "Air" ):
            kinematic_viscosity = 1.468e-5
        temperature = 15.0 + 273.15

        Re_bulk = bulk_velocity * diameter / kinematic_viscosity

        volumetric_flow_rate = 0.25 * math.pi * diameter**2.0 * bulk_velocity

        series_identifier = sd.add_series(
            cursor,
            flow_class=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            number_of_dimensions=2,
            coordinate_system=sd.CYLINDRICAL_COORDINATE_SYSTEM,
        )

        if ( working_fluid == "Air" ):
            sd.add_air_components( cursor, series_identifier )
        elif ( working_fluid == "Water" ):
            sd.add_working_fluid_component(
                cursor,
                series_identifier,
                sd.WATER_LIQUID,
            )

        sd.update_series_geometry(
            cursor,
            series_identifier,
            sd.ELLIPTICAL_GEOMETRY
        )

        station_number = 1
        station_identifier = sd.add_station(
            cursor,
            flow_class=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            station_number=station_number,
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.HYDRAULIC_DIAMETER_QUANTITY,
            diameter,
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.ASPECT_RATIO_QUANTITY,
            1.0,
        )

        n_points = 2
        for point_number in [1, n_points]:
            point_label = None
            if ( point_number == 1 ):
                point_label = sd.WALL_POINT_LABEL
            elif ( point_number == n_points ):
                point_label = sd.CENTER_LINE_POINT_LABEL

            point_identifier = sd.add_point(
                cursor,
                flow_class=flow_class,
                year=year,
                study_number=study_number,
                series_number=series_number,
                station_number=station_number,
                point_number=point_number,
                point_label=point_label,
            )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.BULK_VELOCITY_QUANTITY,
            bulk_velocity,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            measurement_technique=sd.IMPACT_TUBE_MEASUREMENT_TECHNIQUE,
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.BULK_TO_CENTER_LINE_VELOCITY_RATIO_QUANTITY,
            bulk_velocity / maximum_velocity,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            measurement_technique=sd.IMPACT_TUBE_MEASUREMENT_TECHNIQUE,
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.BULK_REYNOLDS_NUMBER_QUANTITY,
            Re_bulk,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            measurement_technique=sd.CALCULATION_MEASUREMENT_TECHNIQUE
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.VOLUMETRIC_FLOW_RATE_QUANTITY,
            volumetric_flow_rate,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            measurement_technique=sd.CALCULATION_MEASUREMENT_TECHNIQUE
        )

        for label in [ sd.WALL_POINT_LABEL, sd.CENTER_LINE_POINT_LABEL ]:
            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.KINEMATIC_VISCOSITY_QUANTITY,
                label,
                kinematic_viscosity,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
                measurement_technique=sd.ASSUMPTION_MEASUREMENT_TECHNIQUE
            )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.TEMPERATURE_QUANTITY,
                label,
                temperature,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
                measurement_technique=sd.ASSUMPTION_MEASUREMENT_TECHNIQUE
            )

        for quantity in [ sd.ROUGHNESS_HEIGHT_QUANTITY,
                          sd.INNER_LAYER_ROUGHNESS_HEIGHT_QUANTITY,
                          sd.OUTER_LAYER_ROUGHNESS_HEIGHT_QUANTITY, ]:
            sd.set_labeled_value(
                cursor,
                station_identifier,
                quantity,
                sd.WALL_POINT_LABEL,
                0.0,
                measurement_technique=sd.ASSUMPTION_MEASUREMENT_TECHNIQUE,
            )

        sd.set_labeled_value(
            cursor,
            station_identifier,
            sd.STREAMWISE_VELOCITY_QUANTITY,
            sd.WALL_POINT_LABEL,
            ufloat( 0.0, 0.0 ),
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
        )

        sd.set_labeled_value(
            cursor,
            station_identifier,
            sd.STREAMWISE_VELOCITY_QUANTITY,
            sd.CENTER_LINE_POINT_LABEL,
            maximum_velocity,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            measurement_technique=sd.IMPACT_TUBE_MEASUREMENT_TECHNIQUE,
        )

conn.commit()
conn.close()


# p. 202
#
# \begin{quote}
# For very accurate comparison the surfaces of the tubes should have been
# precisely geometrically similar, as regards roughness, but as this condition
# could not be fulfilled, the experiments were all made on commercially
# smooth-drawn brass pipes.
# \end{quote}
#
# However, this only appears to be the case for most of the experiments.  Some
# were conducted using steel pipes.  One experiment using air and all of the
# experiments with thick oil are using steel pipes.
#
# p. 209
#
# \begin{quote}
# As a matter of interest the results of a series of observations of the
# surface fraction of this oil, when flowing through a steel pipe 10.1 cm.
# diameter at speeds varying from 5 to 60 cm. per second, are given in Table
# IV. and are also plotted in fig. 3.
# \end{quote}
#
# Pipe 12A on p. 224 is not in the table on p. 207.  It is possible that this
# pipe is a brass pipe, but unfortunately the test length is not specified.

# p. 203
#
# \begin{quote}
# To measure the velocity of the current, one of two methods was used according
# to convenience.  By one method the total quantity of fluid passing through
# the pipe in a given time was either weighed directly, or passed through a
# water-meter or a gas-holder, which had been designed for the purpose of the
# experiments and carefully calibrated.  By the other method the velocity at
# the axis of the pipe was estimated by measuring the difference of pressure
# between that in a small Pitot tube facing the current and placed in the axis
# of the pipe and that in a small hole in the wall of the pipe.
# \end{quote}
velocity_measurement_technique = sd.IMPACT_TUBE_MEASUREMENT_TECHNIQUE

# p. 203
#
# \begin{quote}
# To determine the amount of the surface friction two small holes were made
# in the walls of the experimental portion of the pipe, one at each extremity,
# at a known distance apart, and connected to a tilting manometer.  \ldots  In
# this way the fall of pressure along a given length of the pipe was
# determined, and from the known diameter of the pipe the surface friction per
# unit area was calculated.
# \end{quote}
wall_shear_stress_measurement_technique = "PD"

# p. 203
#
# \begin{quote}
# The form of the tilting manometer used for the estimation of both the surface
# friction and the axial velocity, is that devised by Dr. A. P. Chattock and
# has been previously described.†  For the purpose of the present paper it is
# sufficient to state that in this manometer a pressure difference of the order
# of 0.003 mm. of water can be detected, which is well within the limits of
# sensitivity required in these experiments.  As the fall of pressure in these
# pipes varied from 0.5 to 150,000 mm. of water, other manometers were required
# for the higher pressures, and for this purpose water or mercury U-tubes were
# used for the intermediate pressures, and the Bourdon pressure gauges for the
# highest pressures.
# \end{quote}
#
# The footnote lists two papers that should contain more information about the
# manometers used.

# p. 207
#
# This contains a table of global parameters listing the measurement techniques
# for different series of measurements.
#
# However, even knowing how the flow rate was measured does not provide enough
# information to quantify the uncertainty on that measurement, since the paper
# does not appear to give any information on that subject.

# p. 209
#
# \begin{quote}
# The particular oil on which these observations were made had a value of the
# kinematical viscosity at 15.5° C. of 36.2, or 3230 times that of water at the
# same temperature.  By heating this to 50° C. the kinematical viscosity could
# be reduced to 2.1, but even at this temperature the critical velocity in the
# 10 cm. pipe used for the experiments would have been 525 cm. per second.
# \end{quote}

