#!/usr/bin/env python3

# Copyright (C) 2020-2022 Andrew Trettel
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

flow_class   = sd.FC_DUCT_FLOW
year         = 1928
study_number = 1

study_id = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type_id=sd.ST_EXPERIMENT,
)

sd.add_study_source( cursor, study_id, "DaviesSJ+1928+eng+JOUR",   sd.PRIMARY_SOURCE )
sd.add_study_source( cursor, study_id, "DeanRB+1974+eng+RPRT",   sd.SECONDARY_SOURCE )
sd.add_study_source( cursor, study_id, "JonesOC+1976+eng+JOUR",  sd.SECONDARY_SOURCE )
sd.add_study_source( cursor, study_id, "DeanRB+1978+eng+JOUR",   sd.SECONDARY_SOURCE )

series_11_note = sd.add_note(
    cursor,
    "../data/{:s}/note_series_11.tex".format( study_id ),
)

# p. 93
#
# \begin{quote}
# The water under pressure was taken from the mains, with suitable arrangements
# to ensure sufficient constancy of flow.  The water flowing in a definite time
# was weighted.  Pressure differences were measured by a simple manometer,
# employing either mercury or water as a fluid according to the range of
# pressure.
# \end{quote}
assumption_id        = sd.add_instrument( cursor, sd.IT_ASSUMPTION,       )
flow_rate_id         = sd.add_instrument( cursor, sd.IT_WEIGHING_METHOD,  )
wall_shear_stress_id = sd.add_instrument( cursor, sd.IT_MOMENTUM_BALANCE, )

n   = 0
SSE = 0.0
series_filename = "../data/{:s}/series.csv".format( study_id, )
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
globals_filename = "../data/{:s}/globals.csv".format( study_id, )
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
        width                          = sd.sdfloat( 2.540e-2 )
        development_length             = sd.sdfloat( 0.100e-2 )
        distance_between_pressure_taps = sd.sdfloat( 0.780e-2 )

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
        height = sd.sdfloat( 0.025e-2, height_uncertainty )

        half_height          = 0.5 * height
        aspect_ratio         = width / height
        cross_sectional_area = width * height
        wetted_perimeter     = 2.0 * ( width + height )
        hydraulic_diameter   = 4.0 * cross_sectional_area / wetted_perimeter

        outer_layer_development_length = development_length / hydraulic_diameter

        test_number = int(globals_row[0])
        originators_identifier = "Series 11, test {:d}".format(
            test_number,
        )

        temperature_value         = float(globals_row[2]) + sd.ABSOLUTE_ZERO
        kinematic_viscosity_value = float(globals_row[3]) * 1.0e-4
        mass_flow_rate_value      = float(globals_row[4]) * 1.0e-3
        pressure_difference_value = float(globals_row[5]) * 1.0e-2 * sd.PASCALS_PER_METER_OF_WATER

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
        # In any particular series of observations it was found that a test
        # could be repeated with 0.3 per cent. of the previous value.
        # \end{quote}
        temperature         = sd.uniform_distribution_sdfloat_magnitude( temperature_value, 0.5 )
        kinematic_viscosity = sd.uniform_distribution_sdfloat_percent( kinematic_viscosity_value, 1.5 )
        mass_flow_rate      = sd.uniform_distribution_sdfloat_percent( mass_flow_rate_value,      0.3 )
        pressure_difference = sd.uniform_distribution_sdfloat_percent( pressure_difference_value, 0.3 )

        # TODO: Find the real pressure.
        pressure_tmp = sd.STANDARD_ATMOSPHERIC_PRESSURE

        mass_density = sd.interpolate_fluid_property_value(
            cursor,
            pressure_tmp,
            temperature,
            sd.F_LIQUID_WATER,
            sd.Q_MASS_DENSITY,
        )
        dynamic_viscosity       = mass_density * kinematic_viscosity
        volumetric_flow_rate    = mass_flow_rate / mass_density
        bulk_velocity           = volumetric_flow_rate / cross_sectional_area
        wall_shear_stress       = ( cross_sectional_area / wetted_perimeter ) * ( pressure_difference / distance_between_pressure_taps )
        fanning_friction_factor = 2.0 * wall_shear_stress / ( mass_density * bulk_velocity**2.0 )
        bulk_reynolds_number    = bulk_velocity * hydraulic_diameter / kinematic_viscosity

        friction_velocity        = ( wall_shear_stress / mass_density )**0.5
        viscous_length_scale     = kinematic_viscosity / friction_velocity
        friction_reynolds_number = half_height / viscous_length_scale

        speed_of_sound = sd.interpolate_fluid_property_value(
            cursor,
            pressure_tmp,
            temperature,
            sd.F_LIQUID_WATER,
            sd.Q_SPEED_OF_SOUND,
        )
        bulk_mach_number     = bulk_velocity / speed_of_sound
        friction_mach_number = friction_velocity /speed_of_sound

        series_id = sd.add_series(
            cursor,
            flow_class_id=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            number_of_dimensions=2,
            coordinate_system_id=sd.CS_RECTANGULAR,
            series_external_ids={ sd.C_SELF : originators_identifier },
            note_ids=[series_11_note],
        )

        # TODO: set liquid water as the working fluid.

        sd.update_series_geometry(
            cursor,
            series_id,
            sd.GM_RECTANGULAR
        )

        sd.set_series_value( cursor, series_id, sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS, distance_between_pressure_taps, )

        station_number = 1
        station_id = sd.add_station(
            cursor,
            flow_class_id=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            station_number=station_number,
            station_external_ids={ sd.C_SELF : originators_identifier },
        )

        sd.mark_station_as_periodic( cursor, station_id )

        sd.set_station_value( cursor, station_id, sd.Q_HYDRAULIC_DIAMETER,             hydraulic_diameter,                                                                                    )
        sd.set_station_value( cursor, station_id, sd.Q_DEVELOPMENT_LENGTH,             development_length,                                                                                    )
        sd.set_station_value( cursor, station_id, sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH, outer_layer_development_length,                                                                        )
        sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_ASPECT_RATIO,   aspect_ratio,                                                                                          )
        sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_HEIGHT,         height,                                                                                                )
        sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_WIDTH,          width,                                                                                                 )
        sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_HALF_HEIGHT,    half_height,                                                                                           )
        sd.set_station_value( cursor, station_id, sd.Q_MASS_FLOW_RATE,                 mass_flow_rate,       value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_WEIGHING_METHOD], )
        sd.set_station_value( cursor, station_id, sd.Q_VOLUMETRIC_FLOW_RATE,           volumetric_flow_rate, value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_WEIGHING_METHOD], )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_VELOCITY,                  bulk_velocity,        value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_WEIGHING_METHOD], )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_REYNOLDS_NUMBER,           bulk_reynolds_number, value_type_id=sd.VT_BOTH_AVERAGES,                                               )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_MACH_NUMBER,               bulk_mach_number,     value_type_id=sd.VT_BOTH_AVERAGES,                                               )

        # This set of data only considers wall quantities.
        point_number = 1
        point_id = sd.add_point(
            cursor,
            flow_class_id=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            station_number=station_number,
            point_number=point_number,
            point_label_id=sd.PL_WALL,
        )

        # In general, the surface is not well-described in this study at all.
        # The data is consistent with a smooth surface, though.
        for quantity_id in [ sd.Q_ROUGHNESS_HEIGHT,
                             sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,
                             sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT, ]:
            sd.set_labeled_value(
                cursor,
                station_id,
                quantity_id,
                sd.PL_WALL,
                sd.sdfloat(0.0),
                instrument_class_ids=[sd.IT_ASSUMPTION],
            )

        sd.set_labeled_value( cursor, station_id, sd.Q_MASS_DENSITY,                        sd.PL_WALL, mass_density,             value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_KINEMATIC_VISCOSITY,                 sd.PL_WALL, kinematic_viscosity,      value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_DYNAMIC_VISCOSITY,                   sd.PL_WALL, dynamic_viscosity,        value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_TEMPERATURE,                         sd.PL_WALL, temperature,              value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_SPEED_OF_SOUND,                      sd.PL_WALL, speed_of_sound,           value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_ASSUMPTION],       )
        sd.set_labeled_value( cursor, station_id, sd.Q_STREAMWISE_VELOCITY,                 sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_DISTANCE_FROM_WALL,                  sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_OUTER_LAYER_COORDINATE,              sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_SHEAR_STRESS,                        sd.PL_WALL, wall_shear_stress,        value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_MOMENTUM_BALANCE], )
        sd.set_labeled_value( cursor, station_id, sd.Q_FANNING_FRICTION_FACTOR,             sd.PL_WALL, fanning_friction_factor,  value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_MOMENTUM_BALANCE], )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_VELOCITY,                   sd.PL_WALL, friction_velocity,        value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_VISCOUS_LENGTH_SCALE,                sd.PL_WALL, viscous_length_scale,     value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_REYNOLDS_NUMBER,            sd.PL_WALL, friction_reynolds_number, value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER, sd.PL_WALL, friction_reynolds_number, value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_MACH_NUMBER,                sd.PL_WALL, friction_mach_number,     value_type_id=sd.VT_BOTH_AVERAGES,                                                )
        sd.set_labeled_value( cursor, station_id, sd.Q_HEAT_FLUX,                           sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_ASSUMPTION],       )
        sd.set_labeled_value( cursor, station_id, sd.Q_INNER_LAYER_HEAT_FLUX,               sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_ASSUMPTION],       )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_TEMPERATURE,                sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),   value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_ASSUMPTION],       )

        for quantity in sd.INCOMPRESSIBLE_RATIO_PROFILES:
            sd.set_constant_profile( cursor, station_id, quantity, sd.sdfloat( 1.0, 0.0 ), value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_ASSUMPTION], )

conn.commit()
conn.close()
