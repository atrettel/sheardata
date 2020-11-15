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
year         = 1928
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "DaviesSJ+1928+eng+JOUR", 1 )
sd.add_source( cursor, study_identifier, "DeanRB+1974+eng+RPRT",   2 )
sd.add_source( cursor, study_identifier, "JonesOC+1976+eng+JOUR",  2 )
sd.add_source( cursor, study_identifier, "DeanRB+1978+eng+JOUR",   2 )

# p. 93
#
# \begin{quote}
# The water under pressure was taken from the mains, with suitable arrangements
# to ensure sufficient constancy of flow.  The water flowing in a definite time
# was weighted.  Pressure differences were measured by a simple manometer,
# employing either mercury or water as a fluid according to the range of
# pressure.
# \end{quote}
flow_rate_measurement_technique         = sd.MT_WEIGHING_METHOD
wall_shear_stress_measurement_technique = sd.MT_MOMENTUM_BALANCE

n   = 0
SSE = 0.0
series_filename = "../data/{:s}/series.csv".format( study_identifier, )
with open( series_filename, "r" ) as series_file:
    series_reader = csv.reader(
        series_file,
        delimiter=",",
        quotechar='"', \
        skipinitialspace=True,
    )
    next(series_reader)
    for series_row in series_reader:
        measured_depth   = float(series_row[1]) * 1.0e-2
        calculated_depth = float(series_row[2]) * 1.0e-2
        number_of_tests  =   int(series_row[3])

        for i in range(number_of_tests):
            n   += 1
            SSE += ( measured_depth - calculated_depth )**2.0

height_uncertainty = ( SSE / ( n - 1 ) )**0.5

series_number = 0
globals_filename = "../data/{:s}/globals.csv".format( study_identifier, )
with open( globals_filename, "r" ) as globals_file:
    globals_reader = csv.reader(
        globals_file,
        delimiter=",",
        quotechar='"', \
        skipinitialspace=True,
    )
    next(globals_reader)
    for globals_row in globals_reader:
        series_number += 1

        # p. 107
        #
        # \begin{quote}
        # Throughout the calculations the density has been taken as 1 gm./c.c.
        # \end{quote}
        mass_density = 1000.0

        # p. 107
        width                          = 2.540e-2
        development_length             = 0.100e-2
        distance_between_pressure_taps = 0.780e-2

        # p. 107
        #
        # Page 107 gives the height of the duct as approximately 0.025 cm, but
        # later gives a corrected value of the height to 0.0238 cm.  Using this
        # corrected height moves friction factor onto the laminar curve.
        # Without the correction, the values are too high, likely due to the
        # development length being very short.
        #
        # Rather than accept the correction, instead calculate the uncertainty
        # of the depth measurements using the table on p. 95.
        height = ufloat( 0.025e-2, height_uncertainty )

        aspect_ratio         = width / height
        cross_sectional_area = width * height
        wetted_perimeter     = 2.0 * ( width + height )
        hydraulic_diameter   = 4.0 * cross_sectional_area / wetted_perimeter

        test_number = int(globals_row[0])
        originators_identifier = "Series 11, test {:d}".format(
            test_number,
        )

        temperature_value         = float(globals_row[2]) + 273.15
        kinematic_viscosity_value = float(globals_row[3]) * 1.0e-4
        mass_flow_rate_value      = float(globals_row[4]) * 1.0e-3
        pressure_difference_value = float(globals_row[5]) * 1.0e-2 * 1000.0 * 9.81

        # p. 94
        #
        # \begin{quote}
        # With regard to the accuracy of measurement, the errors of water
        # quantities may be taken as less than 0.2 per cent.  It is difficult
        # to assess the magnitude of the possible errors of temperature
        # measurement.  The thermometer was read to 0.1 °C., but the
        # temperature of the water in the test pipe might have been different.
        # It seems unlikely that the error would exceed 0.5 °C., which would
        # correspond to a possible, but unlikely, error of 1.5 per cent. in the
        # value of the viscosity.  The manometer readings for the most part
        # should not involved errors exceeding 0.2 per cent.
        # \end{quote}
        #
        # However, later on the same page:
        #
        # \begin{quote}
        # In any particular series of observations it was found that a test could be
        # repeated with 0.3 per cent. of the previous value.
        # \end{quote}
        #
        # Assume a uniform distribution.  Use this larger uncertainty for
        # everything but the temperature and kinematic viscosity.
        temperature_uncertainty         = 0.5 / 3.0**0.5
        kinematic_viscosity_uncertainty = kinematic_viscosity_value * 0.015 / 3.0**0.5
        mass_flow_rate_uncertainty      = mass_flow_rate_value * 0.03 / 3.0**0.5
        pressure_difference_uncertainty = pressure_difference_value * 0.03 / 3.0**0.5

        temperature = ufloat(
            temperature_value,
            temperature_uncertainty,
        )
        kinematic_viscosity = ufloat(
            kinematic_viscosity_value,
            kinematic_viscosity_uncertainty,
        )
        mass_flow_rate = ufloat(
            mass_flow_rate_value,
            mass_flow_rate_uncertainty,
        )
        pressure_difference = ufloat(
            pressure_difference_value,
            pressure_difference_uncertainty,
        )

        dynamic_viscosity       = mass_density * kinematic_viscosity
        volumetric_flow_rate    = mass_flow_rate / mass_density
        bulk_velocity           = volumetric_flow_rate / cross_sectional_area
        wall_shear_stress       = ( cross_sectional_area / wetted_perimeter ) * ( pressure_difference / distance_between_pressure_taps )
        fanning_friction_factor = 2.0 * wall_shear_stress / ( mass_density * bulk_velocity**2.0 )
        bulk_reynolds_number    = bulk_velocity * hydraulic_diameter / kinematic_viscosity

        # TODO: Correct this approximation later.
        speed_of_sound = ( 1481.0 - 1447.0 ) * ( temperature - 263.15 ) / 10.0 + 1447.0
        bulk_mach_number = bulk_velocity / speed_of_sound

        series_identifier = sd.add_series(
            cursor,
            flow_class=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            number_of_dimensions=2,
            coordinate_system=sd.RECTANGULAR_COORDINATE_SYSTEM,
        )

        sd.add_working_fluid_component(
            cursor,
            series_identifier,
            sd.WATER_LIQUID,
        )

        sd.update_series_geometry(
            cursor,
            series_identifier,
            sd.RECTANGULAR_GEOMETRY
        )

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
            aspect_ratio,
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.Q_MASS_FLOW_RATE,
            mass_flow_rate,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            measurement_technique=flow_rate_measurement_technique,
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.Q_VOLUMETRIC_FLOW_RATE,
            volumetric_flow_rate,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            measurement_technique=flow_rate_measurement_technique,
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.Q_BULK_VELOCITY,
            bulk_velocity,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            measurement_technique=flow_rate_measurement_technique,
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.Q_BULK_REYNOLDS_NUMBER,
            bulk_reynolds_number,
            averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,
            measurement_technique=sd.MT_CALCULATION
        )

        sd.set_station_value(
            cursor,
            station_identifier,
            sd.Q_BULK_MACH_NUMBER,
            bulk_mach_number,
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

        # In general, the surface is not well-described in this study at all.
        # The data is consistent with a smooth surface, though.
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
            measurement_technique=sd.MT_ASSUMPTION,
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
