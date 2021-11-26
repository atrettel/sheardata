#!/usr/bin/env python3

# Copyright (C) 2020-2021 Andrew Trettel
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

flow_class   = sd.DUCT_FLOW_CLASS
year         = 1928
study_number = 2

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "CornishRJ+1928+eng+JOUR",   sd.PRIMARY_SOURCE )
sd.add_source( cursor, study_identifier, "JonesOC+1976+eng+JOUR",   sd.SECONDARY_SOURCE )
sd.add_source( cursor, study_identifier, "ObotNT+1988+eng+JOUR",    sd.SECONDARY_SOURCE )

# p. 691
#
# \begin{quote}
# The object of the research was to investigate the flow of water in a pipe of
# rectangular cross-section.
# \end{quote}

# p. 692
#
# \begin{quote}
# The width of the channel ($2 a$) was 1.178 cms., and the depth ($2 b$) was
# 0.404 cm.  The maximum variation from these average figures was less than 0.5
# per cent. in both cases.
# \end{quote}
#
# Assume a uniform distribution.
width_value        = 1.178e-2
height_value       = 0.404e-2
width_uncertainty  = 0.005 * width_value / 3.0**0.5
height_uncertainty = 0.005 * height_value / 3.0**0.5

width  = sd.sdfloat( width_value, width_uncertainty )
height = sd.sdfloat( height_value, height_uncertainty )

half_height          = 0.5 * height
aspect_ratio         = width / height
hydraulic_diameter   = 2.0 * width * height / ( width + height )
cross_sectional_area = width * height
wetted_perimeter     = 2.0 * ( width + height )

# p. 692
#
# \begin{quote}
# The pressure differences were measured in three ways, according to the
# magnitude---
#
# \begin{enumerate}
#
# \item Very small differences, up to about 12 cms. of water, were found by
# observing a differential water gauge with a cathetometer, which could be read
# to 0.001 cm. by a verneier.
#
# \item Up to about 30 inches water a differential water gauge, read directly,
# was used.
#
# \item For all higher pressures two mercury gauges were used.
# \end{enumerate}
#
# A calibrated mercury thermometer was used for temperature, and the quantity
# of water was found by measuring with a stop watch (calibrated every day) the
# time to fill vessels whose volume was known within 0.1 per cent.
# \end{quote}
mt_wall_shear_stress = sd.MT_MOMENTUM_BALANCE
mt_flow_rate         = sd.MT_WEIGHING_METHOD

# p. 692
#
# \begin{quote}
# Fig. 1 shows a cross section through the pipe.  The two main components were
# two brass casting about 120 cms. long.  In the lower casting a channel was
# cut and finished smooth with emery paper.  The upper casting was a plate,
# planed flat and smoothed with emery paper.  Three gauge holes, $\alpha$,
# $\beta$, $\gamma$, each 1/16 inch in diameter, were drilled in it.  The
# distance from the entrance to $\alpha$ was 30.2 cms., from $\alpha$ to
# $\beta$ 30.50 cms., from $\beta$ to $\gamma$ 36.43 cms., and from $\gamma$ to
# the exit 22.8 cms.
# \end{quote}
#
# p. 693
#
# \begin{quote}
# The results have been divided into two series, and are detailed in Appendix
# I.  Series 1 includes readings taken at gauge holes $\alpha$ and $\gamma$ and
# the readings of series 2 were taken at $\beta$ and $\gamma$.
# \end{quote}
#
# Use the term "set" instead of "series" to prevent confusion.  These
# paragraphs provide detailed information about the development length and
# distance between pressure taps.
point_alpha =               sd.sdfloat(30.20e-2)
point_beta  = point_alpha + sd.sdfloat(30.50e-2)
point_gamma = point_beta  + sd.sdfloat(36.43e-2)

development_lengths = {}
development_lengths[1] = point_alpha
development_lengths[2] = point_beta

distances_between_pressure_taps = {}
distances_between_pressure_taps[1] = point_gamma - point_alpha
distances_between_pressure_taps[2] = point_gamma - point_beta

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

        data_set      = int(globals_row[0])
        temperature   = sd.fahrenheit_to_kelvin( sd.sdfloat(globals_row[1]) )
        bulk_velocity = sd.sdfloat(globals_row[2]) * 1.0e-2

        pressure_drop       = None
        pressure_drop_units = str(globals_row[4])
        if ( pressure_drop_units == "cm water" ):
            pressure_drop = sd.sdfloat(globals_row[3]) * 1.0e-2 * sd.PASCALS_PER_METER_OF_WATER
        elif ( pressure_drop_units == "in water" ):
            pressure_drop = sd.sdfloat(globals_row[3]) * sd.PASCALS_PER_INCH_OF_WATER
        elif ( pressure_drop_units == "in mercury" ):
            pressure_drop = sd.sdfloat(globals_row[3]) * sd.PASCALS_PER_INCH_OF_MERCURY

        development_length             = development_lengths[data_set]
        distance_between_pressure_taps = distances_between_pressure_taps[data_set]
        outer_layer_development_length = development_length / hydraulic_diameter

        pressure_gradient = (-1.0) * pressure_drop / distance_between_pressure_taps

        wall_shear_stress = (-1.0) * ( cross_sectional_area / wetted_perimeter ) * pressure_gradient

        mass_density        =      sd.liquid_water_mass_density( temperature )
        dynamic_viscosity   = sd.liquid_water_dynamic_viscosity( temperature )
        speed_of_sound      =    sd.liquid_water_speed_of_sound( temperature )
        kinematic_viscosity = dynamic_viscosity / mass_density

        bulk_reynolds_number = bulk_velocity * hydraulic_diameter / kinematic_viscosity
        bulk_mach_number     = bulk_velocity / speed_of_sound

        fanning_friction_factor = 2.0 * wall_shear_stress / ( mass_density * bulk_velocity**2.0 )

        friction_velocity        = ( wall_shear_stress / mass_density )**0.5
        viscous_length_scale     = kinematic_viscosity / friction_velocity
        friction_reynolds_number = half_height / viscous_length_scale
        friction_mach_number     = friction_velocity / speed_of_sound

        volumetric_flow_rate = bulk_velocity * cross_sectional_area
        mass_flow_rate       = mass_density * volumetric_flow_rate

        series_identifier = sd.add_series(
            cursor,
            flow_class=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            number_of_dimensions=2,
            coordinate_system=sd.RECTANGULAR_COORDINATE_SYSTEM,
        )

        # TODO: set liquid water as the working fluid.

        sd.update_series_geometry(
            cursor,
            series_identifier,
            sd.RECTANGULAR_GEOMETRY
        )

        sd.set_series_value( cursor, series_identifier, sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS, distance_between_pressure_taps, )

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

        sd.set_station_value( cursor, station_identifier, sd.Q_HYDRAULIC_DIAMETER,             hydraulic_diameter,             )
        sd.set_station_value( cursor, station_identifier, sd.Q_DEVELOPMENT_LENGTH,             development_length,             )
        sd.set_station_value( cursor, station_identifier, sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH, outer_layer_development_length, )
        sd.set_station_value( cursor, station_identifier, sd.Q_ASPECT_RATIO,                   aspect_ratio,                   )
        sd.set_station_value( cursor, station_identifier, sd.Q_CROSS_SECTIONAL_AREA,           cross_sectional_area,           )
        sd.set_station_value( cursor, station_identifier, sd.Q_WETTED_PERIMETER,               wetted_perimeter,               )
        sd.set_station_value( cursor, station_identifier, sd.Q_HEIGHT,                         height,                         )
        sd.set_station_value( cursor, station_identifier, sd.Q_WIDTH,                          width,                          )
        sd.set_station_value( cursor, station_identifier, sd.Q_HALF_HEIGHT,                    half_height,                    )
        sd.set_station_value( cursor, station_identifier, sd.Q_MASS_FLOW_RATE,                 mass_flow_rate,       value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[mt_flow_rate],      )
        sd.set_station_value( cursor, station_identifier, sd.Q_VOLUMETRIC_FLOW_RATE,           volumetric_flow_rate, value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[mt_flow_rate],      )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_VELOCITY,                  bulk_velocity,        value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[mt_flow_rate],      )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_REYNOLDS_NUMBER,           bulk_reynolds_number, value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION], )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_MACH_NUMBER,               bulk_mach_number,     value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION], )

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
            point_label=sd.PL_WALL,
        )

        # Assume a smooth surface.
        for quantity in [ sd.Q_ROUGHNESS_HEIGHT,
                          sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,
                          sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT, ]:
            sd.set_labeled_value(
                cursor,
                station_identifier,
                quantity,
                sd.PL_WALL,
                sd.sdfloat(0.0),
                measurement_techniques=[sd.MT_ASSUMPTION],
            )

        sd.set_labeled_value( cursor, station_identifier, sd.Q_MASS_DENSITY,                        sd.PL_WALL, mass_density,             value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION],    )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_KINEMATIC_VISCOSITY,                 sd.PL_WALL, kinematic_viscosity,      value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION],    )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_DYNAMIC_VISCOSITY,                   sd.PL_WALL, dynamic_viscosity,        value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION],    )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_TEMPERATURE,                         sd.PL_WALL, temperature,              value_type=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_SPEED_OF_SOUND,                      sd.PL_WALL, speed_of_sound,           value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION],     )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_STREAMWISE_VELOCITY,                 sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_DISTANCE_FROM_WALL,                  sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_OUTER_LAYER_COORDINATE,              sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_SHEAR_STRESS,                        sd.PL_WALL, wall_shear_stress,        value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[mt_wall_shear_stress], )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_FANNING_FRICTION_FACTOR,             sd.PL_WALL, fanning_friction_factor,  value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[mt_wall_shear_stress], )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_VELOCITY,                   sd.PL_WALL, friction_velocity,        value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION],    )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_VISCOUS_LENGTH_SCALE,                sd.PL_WALL, viscous_length_scale,     value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION],    )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_REYNOLDS_NUMBER,            sd.PL_WALL, friction_reynolds_number, value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION],    )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER, sd.PL_WALL, friction_reynolds_number, value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION],    )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_MACH_NUMBER,                sd.PL_WALL, friction_mach_number,     value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION],    )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_HEAT_FLUX,                           sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION],     )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_INNER_LAYER_HEAT_FLUX,               sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION],     )
        sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_TEMPERATURE,                sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION],     )

        for quantity in sd.INCOMPRESSIBLE_RATIO_PROFILES:
            sd.set_constant_profile( cursor, station_identifier, quantity, sd.sdfloat( 1.0, 0.0 ), value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION], )

conn.commit()
conn.close()
