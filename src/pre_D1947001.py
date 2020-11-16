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

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

flow_class   = sd.DUCT_FLOW_CLASS
year         = 1947
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "HuebscherRG+1947+eng+JOUR", 1 )

# Duct dimensions
#
# p. 128
#
# \begin{quote}
# The first part of the paper gives the results of an experimental
# investigation using three ducts of different forms but each of 8 in.
# equivalent diameter.  The duct sizes were 8 in. ID round, 8 in. square and
# 4.5 in. by 36 in. rectangular (8:1 aspect ratio).  Air velocities used ranged
# from 300 to 9310 fpm.
# \end{quote}

class Duct:
    aspect_ratio = None
    length       = None

    def __init__( self, aspect_ratio, length ):
        self.aspect_ratio = float(aspect_ratio)
        self.length       = float(length)

ducts = {}
globals_filename = "../data/{:s}/globals.csv".format( study_identifier )
with open( globals_filename, "r" ) as globals_file:
    globals_reader = csv.reader(
        globals_file,
        delimiter=",",
        quotechar='"', \
        skipinitialspace=True,
    )
    next(globals_reader)
    for globals_row in globals_reader:
        ducts[str(globals_row[0])] = Duct(
            float(globals_row[1]),
            float(globals_row[2]) * sd.METERS_PER_FOOT
        )

mass_density_note = \
"""
The air density of test 17 of the square duct results appears to have a
typographic error.  The number given is 6.0697; the database uses 0.0697.
"""

series_number = 0
for duct in ducts:
    duct_globals_filename = "../data/{:s}/{:s}_duct_globals.csv".format(
        study_identifier,
        duct.lower(),
    )
    with open( duct_globals_filename, "r" ) as duct_globals_file:
        duct_globals_reader = csv.reader(
            duct_globals_file,
            delimiter=",",
            quotechar='"', \
            skipinitialspace=True,
        )
        next(duct_globals_reader)
        for duct_globals_row in duct_globals_reader:
            series_number += 1

            test_number = int(duct_globals_row[0])
            originators_identifier = "{:s} duct {:d}".format(
                duct,
                test_number
            )
            temperature        = sd.fahrenheit_to_kelvin( float(duct_globals_row[2]) )
            mass_density       = float(duct_globals_row[4]) * sd.KILOGRAM_PER_POUND_MASS / sd.METERS_PER_FOOT**3.0
            bulk_velocity      = float(duct_globals_row[5]) * sd.METERS_PER_FOOT / sd.SECONDS_PER_MINUTE
            hydraulic_diameter = float(duct_globals_row[6]) * sd.METERS_PER_INCH
            pressure_gradient  = float(duct_globals_row[7]) * sd.PASCALS_PER_INCH_OF_WATER / sd.METERS_PER_FOOT
            Re_bulk_value      = float(duct_globals_row[10])

            # Uncertainty of wall shear stress measurements
            #
            # p. 128
            #
            # \begin{quote}
            # The estimated error in any flow measurement due to all sources,
            # including the assumption of constant nozzle coefficient, did not
            # exceed $\pm 2$ percent.
            # \end{quote}
            #
            # p. 129
            #
            # \begin{quote}
            # The maximum sensitivity of the five gages was $\pm 0.02$ in. of
            # water, with an accuracy within this value over the entire range.
            # \end{quote}
            #
            # The first number about the flow rate measurements appears
            # reasonable, but the second number about the pressure drop
            # measurements creates extremely large uncertainties for the lower
            # bulk Reynolds number cases.  It appears that this "maximum" is
            # perhaps far too high.
            wall_shear_stress = 0.25 * hydraulic_diameter * pressure_gradient

            fanning_friction_factor = 2.0 * wall_shear_stress / ( mass_density * bulk_velocity**2.0 )

            kinematic_viscosity = bulk_velocity * hydraulic_diameter / Re_bulk_value
            dynamic_viscosity   = mass_density * kinematic_viscosity
            Re_bulk             = bulk_velocity * hydraulic_diameter / kinematic_viscosity

            speed_of_sound = sd.ideal_gas_speed_of_sound( temperature )
            Ma_bulk        = bulk_velocity / speed_of_sound

            series_identifier = None
            if ( duct == "Round" ):
                series_identifier = sd.add_series(
                    cursor,
                    flow_class=flow_class,
                    year=year,
                    study_number=study_number,
                    series_number=series_number,
                    number_of_dimensions=2,
                    coordinate_system=sd.CYLINDRICAL_COORDINATE_SYSTEM,
                )

                sd.update_series_geometry(
                    cursor,
                    series_identifier,
                    sd.ELLIPTICAL_GEOMETRY
                )
            else:
                series_identifier = sd.add_series(
                    cursor,
                    flow_class=flow_class,
                    year=year,
                    study_number=study_number,
                    series_number=series_number,
                    number_of_dimensions=2,
                    coordinate_system=sd.RECTANGULAR_COORDINATE_SYSTEM,
                )

                sd.update_series_geometry(
                    cursor,
                    series_identifier,
                    sd.RECTANGULAR_GEOMETRY
                )

            sd.add_air_components( cursor, series_identifier )

            station_number = 1
            station_identifier = sd.add_station(
                cursor,
                flow_class=flow_class,
                year=year,
                study_number=study_number,
                series_number=series_number,
                station_number=station_number,
                originators_identifier=originators_identifier,
            )

            sd.mark_station_as_periodic( cursor, station_identifier )

            sd.set_station_value(
                cursor,
                station_identifier,
                sd.Q_HYDRAULIC_DIAMETER,
                hydraulic_diameter,
            )

            sd.set_station_value(
                cursor,
                station_identifier,
                sd.Q_ASPECT_RATIO,
                ducts[duct].aspect_ratio,
            )

            # p. 128
            #
            # \begin{quote}
            # The mean air velocity was determined from the measurement of the
            # air quantity and the duct area.  \ldots  Air quantity was
            # measured by the use of five cast aluminum nozzles made
            # approximately to ASME log-radius, low-ratio proportions and
            # equiped with throat static taps.  \ldots  The nozzles were
            # calibrated in place by impact tube traverses at the throat over
            # the full flow range.
            # \end{quote}
            sd.set_station_value(
                cursor,
                station_identifier,
                sd.Q_BULK_VELOCITY,
                bulk_velocity,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
                measurement_technique=sd.MT_IMPACT_TUBE,
            )

            sd.set_station_value(
                cursor,
                station_identifier,
                sd.Q_BULK_REYNOLDS_NUMBER,
                Re_bulk,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
                measurement_technique=sd.MT_CALCULATION
            )

            sd.set_station_value(
                cursor,
                station_identifier,
                sd.Q_BULK_MACH_NUMBER,
                Ma_bulk,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
                measurement_technique=sd.MT_CALCULATION
            )

            # This set of data only considers wall quantities.
            point_number = 1
            point_identifier = sd.add_point(
                cursor,
                flow_class=flow_class,
                year=year,
                study_number=study_number,
                series_number=series_number,
                station_number=station_number,
                point_number=point_number,
                point_label=sd.WALL_POINT_LABEL,
            )

            # TODO: Correct this assumption later.
            #
            # Duct material
            #
            # p. 128
            #
            # \begin{quote}
            # The three ducts were fabricated from 16 gage galvanized sheet
            # metal to provide the necessary rigidity against deflection.
            # \end{quote}
            #
            # p. 129
            #
            # \begin{quote}
            # The internal roughness of all three ducts was typical of
            # galvanized iron, very little roughness was contributed by the
            # joints.  The hydraulic roughness magnitude cannot be measured
            # geometrically but can be deduced from the test results.
            # \end{quote}
            for quantity in [ sd.Q_ROUGHNESS_HEIGHT,
                              sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,
                              sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT, ]:
                sd.set_labeled_value(
                    cursor,
                    station_identifier,
                    quantity,
                    sd.WALL_POINT_LABEL,
                    0.0,
                    measurement_technique=sd.MT_ASSUMPTION,
                )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_MASS_DENSITY,
                sd.WALL_POINT_LABEL,
                mass_density,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
                notes=( mass_density_note if ( test_number == 17 and duct == "Square" ) else None ),
            )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_KINEMATIC_VISCOSITY,
                sd.WALL_POINT_LABEL,
                kinematic_viscosity,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_DYNAMIC_VISCOSITY,
                sd.WALL_POINT_LABEL,
                dynamic_viscosity,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_TEMPERATURE,
                sd.WALL_POINT_LABEL,
                temperature,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_SPEED_OF_SOUND,
                sd.WALL_POINT_LABEL,
                speed_of_sound,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
                measurement_technique=sd.MT_ASSUMPTION,
            )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_STREAMWISE_VELOCITY,
                sd.WALL_POINT_LABEL,
                ufloat( 0.0, 0.0 ),
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_DISTANCE_FROM_WALL,
                sd.WALL_POINT_LABEL,
                ufloat( 0.0, 0.0 ),
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_OUTER_LAYER_COORDINATE,
                sd.WALL_POINT_LABEL,
                ufloat( 0.0, 0.0 ),
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            )

            # p. 129
            wall_shear_stress_measurement_technique = sd.MT_MOMENTUM_BALANCE

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_SHEAR_STRESS,
                sd.WALL_POINT_LABEL,
                wall_shear_stress,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
                measurement_technique=wall_shear_stress_measurement_technique,
            )

            sd.set_labeled_value(
                cursor,
                station_identifier,
                sd.Q_FANNING_FRICTION_FACTOR,
                sd.WALL_POINT_LABEL,
                fanning_friction_factor,
                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
                measurement_technique=wall_shear_stress_measurement_technique,
            )

conn.commit()
conn.close()

# p. 132
#
# \begin{quote}
# Two traverses at opposite ends of the round duct indicated
# different velocity profiles, the centerline velocity at the
# downstream end was 6.6 percent higher than at the upstream end
# for a mean velocity of 9310 fpm.
# \end{quote}
