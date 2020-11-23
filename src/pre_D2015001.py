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

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

flow_class   = sd.DUCT_FLOW_CLASS
year         = 2015
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.DIRECT_NUMERICAL_SIMULATION_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "TrettelA+2015+eng+THES", 1 )
sd.add_source( cursor, study_identifier, "TrettelA+2016+eng+JOUR", 1 )


dynamic_viscosity_note = None
with open( "../data/{:s}/note_dynamic_viscosity.tex".format( study_identifier ), "r" ) as f:
    dynamic_viscosity_note = f.read()

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

        originators_identifier              = str(globals_row[0])
        bulk_mach_number                    = sd.sdfloat(globals_row[1])
        bulk_reynolds_number                = sd.sdfloat(globals_row[2])
        prandtl_number                      = sd.sdfloat(globals_row[3],0.0)
        heat_capacity_ratio                 = sd.sdfloat(globals_row[4],0.0)
        specific_gas_constant               = sd.sdfloat(globals_row[5],0.0)
        omega                               = sd.sdfloat(globals_row[6],0.0)
        nx                                  = int(globals_row[7])
        ny                                  = int(globals_row[8])
        nz                                  = int(globals_row[9])
        wall_temperature                    = sd.sdfloat(globals_row[10],0.0)
        wall_mass_density                   = sd.sdfloat(globals_row[11])
        wall_dynamic_viscosity              = sd.sdfloat(globals_row[12])
        wall_shear_stress                   = sd.sdfloat(globals_row[13])
        center_line_velocity                = sd.sdfloat(globals_row[14])
        center_line_temperature             = sd.sdfloat(globals_row[15])
        center_line_mass_density            = sd.sdfloat(globals_row[16])
        center_line_dynamic_viscosity       = sd.sdfloat(globals_row[17])
        friction_velocity                   = sd.sdfloat(globals_row[18])
        viscous_length_scale                = sd.sdfloat(globals_row[19])
        friction_temperature                = sd.sdfloat(globals_row[20])
        B_q                                 = sd.sdfloat(globals_row[21])
        wall_heat_flux                      = sd.sdfloat(globals_row[22])
        friction_reynolds_number            = sd.sdfloat(globals_row[23])
        semi_local_friction_reynolds_number = sd.sdfloat(globals_row[24])
        friction_mach_number                = sd.sdfloat(globals_row[25])

        # In Hybrid simulations, the number of points in the y-direction
        # exclude the center-line and the wall, so these are added back in the
        # previous post-processing.
        number_of_points = ny // 2 + 2

        bulk_velocity      = sd.sdfloat(   1.0, 0.0 )
        height             = sd.sdfloat(   2.0, 0.0 )
        aspect_ratio       = sd.sdfloat( "inf", 0.0 )
        development_length = sd.sdfloat( "inf", 0.0 )

        half_height                    = 0.5 * height
        hydraulic_diameter             = 2.0 * height
        outer_layer_development_length = development_length / hydraulic_diameter

        specific_isochoric_heat_capacity = specific_gas_constant / ( heat_capacity_ratio - 1.0 )
        specific_isobaric_heat_capacity  = heat_capacity_ratio * specific_isochoric_heat_capacity

        bulk_to_center_line_velocity_ratio    = bulk_velocity / center_line_velocity
        center_line_to_wall_temperature_ratio = center_line_temperature / wall_temperature

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

        station_number = 1
        station_identifier = sd.add_station(
            cursor,
            flow_class=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            station_number=station_number,
        )

        sd.mark_station_as_periodic( cursor, station_identifier )

        sd.set_station_value( cursor, station_identifier, sd.Q_HYDRAULIC_DIAMETER,                 hydraulic_diameter,             )
        sd.set_station_value( cursor, station_identifier, sd.Q_DEVELOPMENT_LENGTH,                 development_length,             )
        sd.set_station_value( cursor, station_identifier, sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH,     outer_layer_development_length, )
        sd.set_station_value( cursor, station_identifier, sd.Q_ASPECT_RATIO,                       aspect_ratio,                   )
        sd.set_station_value( cursor, station_identifier, sd.Q_HEIGHT,                             height,                         )
        sd.set_station_value( cursor, station_identifier, sd.Q_HALF_HEIGHT,                        half_height,                    )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_VELOCITY,                      bulk_velocity,                      averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_TO_CENTER_LINE_VELOCITY_RATIO, bulk_to_center_line_velocity_ratio, averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_REYNOLDS_NUMBER,               bulk_reynolds_number,               averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_MACH_NUMBER,                   bulk_mach_number,                   averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )

        point_number = 0
        series_filename = "../data/{:s}/{:s}_profiles.csv".format(
            study_identifier,
            originators_identifier,
        )
        with open( series_filename, "r" ) as series_file:
            series_reader = csv.reader(
                series_file,
                delimiter=",",
                quotechar='"', \
                skipinitialspace=True,
            )
            next(series_reader)
            for series_row in series_reader:
                point_number += 1

                point_label = None
                if ( point_number == 1 ):
                    point_label = sd.WALL_POINT_LABEL
                elif ( point_number == number_of_points ):
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

                distance_from_wall     = sd.sdfloat(series_row[0])
                inner_layer_coordinate = sd.sdfloat(series_row[1])
                streamwise_velocity_uw = sd.sdfloat(series_row[5])
                streamwise_velocity_dw = sd.sdfloat(series_row[6])
                mass_density           = sd.sdfloat(series_row[11])
                pressure               = sd.sdfloat(series_row[12])
                temperature_uw         = sd.sdfloat(series_row[13])
                temperature_dw         = sd.sdfloat(series_row[14])
                dynamic_viscosity      = sd.sdfloat(series_row[15])

                outer_layer_coordinate =  distance_from_wall / half_height
                kinematic_viscosity    =   dynamic_viscosity / mass_density
                thermal_diffusivity    = kinematic_viscosity / prandtl_number
                thermal_conductivity   = thermal_diffusivity * mass_density * specific_isobaric_heat_capacity

                sd.set_point_value( cursor, point_identifier, sd.Q_DISTANCE_FROM_WALL,               distance_from_wall,                                                                                                                                         )
                sd.set_point_value( cursor, point_identifier, sd.Q_INNER_LAYER_COORDINATE,           inner_layer_coordinate,           averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                                               )
                sd.set_point_value( cursor, point_identifier, sd.Q_OUTER_LAYER_COORDINATE,           outer_layer_coordinate,                                                                                                                                     )
                sd.set_point_value( cursor, point_identifier, sd.Q_STREAMWISE_VELOCITY,              streamwise_velocity_uw,           averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,                                                                          )
                sd.set_point_value( cursor, point_identifier, sd.Q_STREAMWISE_VELOCITY,              streamwise_velocity_dw,           averaging_system=sd.DENSITY_WEIGHTED_AVERAGING_SYSTEM,                                                                    )
                sd.set_point_value( cursor, point_identifier, sd.Q_MASS_DENSITY,                     mass_density,                     averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,                                                                          )
                sd.set_point_value( cursor, point_identifier, sd.Q_PRESSURE,                         pressure,                         averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,                                                                          )
                sd.set_point_value( cursor, point_identifier, sd.Q_TEMPERATURE,                      temperature_uw,                   averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,                                                                          )
                sd.set_point_value( cursor, point_identifier, sd.Q_TEMPERATURE,                      temperature_dw,                   averaging_system=sd.DENSITY_WEIGHTED_AVERAGING_SYSTEM,                                                                    )
                sd.set_point_value( cursor, point_identifier, sd.Q_DYNAMIC_VISCOSITY,                dynamic_viscosity,                averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, measurement_technique=sd.MT_APPROXIMATION, notes=dynamic_viscosity_note, )
                sd.set_point_value( cursor, point_identifier, sd.Q_KINEMATIC_VISCOSITY,              kinematic_viscosity,              averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, measurement_technique=sd.MT_APPROXIMATION,                               )
                sd.set_point_value( cursor, point_identifier, sd.Q_PRANDTL_NUMBER,                   prandtl_number,                   averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                                               )
                sd.set_point_value( cursor, point_identifier, sd.Q_HEAT_CAPACITY_RATIO,              heat_capacity_ratio,              averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                                               )
                sd.set_point_value( cursor, point_identifier, sd.Q_SPECIFIC_GAS_CONSTANT,            specific_gas_constant,            averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                                               )
                sd.set_point_value( cursor, point_identifier, sd.Q_SPECIFIC_ISOBARIC_HEAT_CAPACITY,  specific_isobaric_heat_capacity,  averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                                               )
                sd.set_point_value( cursor, point_identifier, sd.Q_SPECIFIC_ISOCHORIC_HEAT_CAPACITY, specific_isochoric_heat_capacity, averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                                               )
                sd.set_point_value( cursor, point_identifier, sd.Q_THERMAL_CONDUCTIVITY,             thermal_conductivity,             averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, measurement_technique=sd.MT_APPROXIMATION,                               )
                sd.set_point_value( cursor, point_identifier, sd.Q_THERMAL_DIFFUSIVITY,              thermal_diffusivity,              averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM,                                                                          )

        for quantity in [ sd.Q_ROUGHNESS_HEIGHT,
                          sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,
                          sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT, ]:
            sd.set_labeled_value(
                cursor,
                station_identifier,
                quantity,
                sd.WALL_POINT_LABEL,
                0.0,
            )

        sd.set_labeled_value( cursor, station_identifier, sd.Q_SHEAR_STRESS,                          sd.WALL_POINT_LABEL, wall_shear_stress,                     averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_VELOCITY,                     sd.WALL_POINT_LABEL, friction_velocity,                     averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_VISCOUS_LENGTH_SCALE,                  sd.WALL_POINT_LABEL, viscous_length_scale,                  averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_TEMPERATURE,                  sd.WALL_POINT_LABEL, friction_temperature,                  averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_INNER_LAYER_HEAT_FLUX,                 sd.WALL_POINT_LABEL, B_q,                                   averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_HEAT_FLUX,                             sd.WALL_POINT_LABEL, wall_heat_flux,                        averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_REYNOLDS_NUMBER,              sd.WALL_POINT_LABEL, friction_reynolds_number,              averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER,   sd.WALL_POINT_LABEL, semi_local_friction_reynolds_number,   averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_MACH_NUMBER,                  sd.WALL_POINT_LABEL, friction_mach_number,                  averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_CENTER_LINE_TO_WALL_TEMPERATURE_RATIO, sd.WALL_POINT_LABEL, center_line_to_wall_temperature_ratio, averaging_system=sd.UNWEIGHTED_AVERAGING_SYSTEM, )

conn.commit()
conn.close()
