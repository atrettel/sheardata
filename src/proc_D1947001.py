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
year         = 1947
study_number = 1

study_id = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type_id=sd.ST_EXPERIMENT,
)

sd.add_study_source( cursor, study_id, "HuebscherRG+1947+eng+JOUR", sd.PRIMARY_SOURCE )

conn.commit()
conn.close()
exit()

assumption_id = sd.add_instrument( cursor, sd.IC_ASSUMPTION, )

# p. 128
#
# \begin{quote}
# The mean air velocity was determined from the measurement of the air quantity
# and the duct area.  \ldots  Air quantity was measured by the use of five cast
# aluminum nozzles made approximately to ASME log-radius, low-ratio proportions
# and equiped with throat static taps.  \ldots  The nozzles were calibrated in
# place by impact tube traverses at the throat over the full flow range.
# \end{quote}
impact_tube_id = sd.add_instrument( cursor, sd.IC_IMPACT_TUBE, )

# p. 129
momentum_balance_id = sd.add_instrument( cursor, sd.IC_MOMENTUM_BALANCE, )

mass_density_note = sd.add_note(
    cursor,
    "../data/{:s}/note_mass_density.tex".format( study_id ),
)

# Distance between pressure taps
#
# p. 129
#
# \begin{quote}
# Static pressure explorations made within the rectangular duct on a single
# plane perpendicular to the long axis of the duct disclosed no measureable
# variation over the cross-section.  A single internal static pressure taken at
# the axis of the duct at several locations along the duct length served to
# define the static friction pressure gradient.
#
# It was found that insertion of the tubes into the duct caused sufficient
# resistance to decrease the air flow in the round and square ducts.  Since
# this eeffect was negligible when insertion was less than 2 in. the tubes were
# never inserted for more than 2 in.  Openings for static tube insertion were
# located every 3 ft along the length of the duct.
# \end{quote}
#
# Note that this does not give any information about the distance that was used
# in the study, just that it was in 3 foot increments.

class Duct:
    aspect_ratio = None
    length       = None

    def __init__( self, aspect_ratio, length ):
        self.aspect_ratio = sd.sdfloat(aspect_ratio)
        self.length       = sd.sdfloat(length)

ducts = {}
globals_filename = "../data/{:s}/globals.csv".format( study_id )
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

model_ids = {}
for duct in ducts:
    model_class_id = sd.MC_INTERIOR_RECTANGULAR_CROSS_SECTION
    if ( duct == "Round" ):
        model_class_id = sd.MC_INTERIOR_ELLIPTICAL_CROSS_SECTION
    
    model_ids[duct] = sd.add_model(
        cursor,
        model_class_id,
        duct,
    )

# TODO: Add model values.

series_number = 0
for duct in ducts:
    duct_globals_filename = "../data/{:s}/{:s}_duct_globals.csv".format(
        study_id,
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
            temperature        = sd.fahrenheit_to_kelvin( sd.sdfloat(duct_globals_row[2]) )
            mass_density       = sd.sdfloat(duct_globals_row[4]) * sd.KILOGRAM_PER_POUND_MASS / sd.METERS_PER_FOOT**3.0
            bulk_velocity      = sd.sdfloat(duct_globals_row[5]) * sd.METERS_PER_FOOT / sd.SECONDS_PER_MINUTE
            hydraulic_diameter = sd.sdfloat(duct_globals_row[6]) * sd.METERS_PER_INCH
            pressure_gradient  = sd.sdfloat(duct_globals_row[7]) * sd.PASCALS_PER_INCH_OF_WATER / sd.METERS_PER_FOOT
            Re_bulk_value      = sd.sdfloat(duct_globals_row[10])

            # Duct dimensions
            #
            # p. 128
            #
            # \begin{quote}
            # The first part of the paper gives the results of an experimental
            # investigation using three ducts of different forms but each of 8
            # in.  equivalent diameter.  The duct sizes were 8 in. ID round, 8
            # in. square and 4.5 in. by 36 in. rectangular (8:1 aspect ratio).
            # Air velocities used ranged from 300 to 9310 fpm.
            # \end{quote}
            #
            # However, the hydraulic diameter column in tables 2 to 4 makes it
            # clear that these dimensions are only approximate.  Indeed, the
            # rectangular duct appears to vary in cross section between tests,
            # while the round and square ducts have the same cross section.
            #
            # For the rectangular case, assume that the aspect ratio is
            # constant.
            height      = None
            width       = None
            half_height = None
            if ( duct == "Square" ):
                height      = hydraulic_diameter
                width       = hydraulic_diameter
                half_height = 0.5 * height
            elif ( duct == "Rectangular" ):
                height      = 0.5 * ( 1.0 + ducts[duct].aspect_ratio ) * hydraulic_diameter / ducts[duct].aspect_ratio
                width       = ducts[duct].aspect_ratio * height
                half_height = 0.5 * height

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

            friction_velocity    = ( wall_shear_stress / mass_density )**0.5
            viscous_length_scale = kinematic_viscosity / friction_velocity

            Re_tau = None
            if ( duct == "Round" ):
                Re_tau = 0.5 * hydraulic_diameter / viscous_length_scale
            else:
                Re_tau = half_height / viscous_length_scale

            speed_of_sound = sd.calculate_ideal_gas_speed_of_sound_from_amount_fractions( cursor, temperature, sd.dry_air_amount_fractions() )
            Ma_bulk        = bulk_velocity     / speed_of_sound
            Ma_tau         = friction_velocity / speed_of_sound

            series_id = None
            if ( duct == "Round" ):
                series_id = sd.add_series(
                    cursor,
                    flow_class_id=flow_class,
                    year=year,
                    study_number=study_number,
                    series_number=series_number,
                    number_of_dimensions=2,
                    coordinate_system_id=sd.CS_CYLINDRICAL,
                    model_id=model_ids[duct],
                    series_external_ids={ sd.C_SELF : originators_identifier },
                )
            else:
                series_id = sd.add_series(
                    cursor,
                    flow_class_id=flow_class,
                    year=year,
                    study_number=study_number,
                    series_number=series_number,
                    number_of_dimensions=2,
                    coordinate_system_id=sd.CS_RECTANGULAR,
                    model_id=model_ids[duct],
                    series_external_ids={ sd.C_SELF : originators_identifier },
                )

            # TODO: set air as the working fluid.

            station_number = 1
            station_id = sd.add_station(
                cursor,
                flow_class_id=flow_class,
                year=year,
                study_number=study_number,
                series_number=series_number,
                station_number=station_number,
                streamwise_periodic=True,
                spanwise_periodic=True,
                station_external_ids={ sd.C_SELF : originators_identifier },
            )

            sd.set_station_value( cursor, station_id, sd.Q_HYDRAULIC_DIAMETER,             hydraulic_diameter,                                                                )
            sd.set_station_value( cursor, station_id, sd.Q_DEVELOPMENT_LENGTH,             ducts[duct].length,                                                                )
            sd.set_station_value( cursor, station_id, sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH, ducts[duct].length / hydraulic_diameter,                                           )
            sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_ASPECT_RATIO,   ducts[duct].aspect_ratio,                                                          )
            sd.set_station_value( cursor, station_id, sd.Q_BULK_VELOCITY,                  bulk_velocity, value_type_id=sd.VT_BOTH_AVERAGES, instrument_ids=[impact_tube_id], )
            sd.set_station_value( cursor, station_id, sd.Q_BULK_REYNOLDS_NUMBER,           Re_bulk,       value_type_id=sd.VT_BOTH_AVERAGES,                                  )
            sd.set_station_value( cursor, station_id, sd.Q_BULK_MACH_NUMBER,               Ma_bulk,       value_type_id=sd.VT_BOTH_AVERAGES,                                  )

            if ( duct != "Round" ):
                sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_HEIGHT,      height,      )
                sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_WIDTH,       width,       )
                sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_HALF_HEIGHT, half_height, )

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
            for quantity_id in [ sd.Q_ROUGHNESS_HEIGHT,
                                 sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,
                                 sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT, ]:
                sd.set_labeled_value(
                    cursor,
                    station_id,
                    quantity_id,
                    sd.PL_WALL,
                    sd.sdfloat(0.0),
                    instrument_ids=[assumption_id],
                )

            current_notes = []
            if ( test_number == 17 and duct == "Square" ):
                current_notes = [mass_density_note]

            sd.set_labeled_value( cursor, station_id, sd.Q_MASS_DENSITY,                        sd.PL_WALL, mass_density,            value_type_id=sd.VT_BOTH_AVERAGES, note_ids=current_notes,               )
            sd.set_labeled_value( cursor, station_id, sd.Q_KINEMATIC_VISCOSITY,                 sd.PL_WALL, kinematic_viscosity,     value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_DYNAMIC_VISCOSITY,                   sd.PL_WALL, dynamic_viscosity,       value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_TEMPERATURE,                         sd.PL_WALL, temperature,             value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_STREAMWISE_VELOCITY,                 sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),  value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_DISTANCE_FROM_WALL,                  sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),  value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_OUTER_LAYER_COORDINATE,              sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),  value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_SPEED_OF_SOUND,                      sd.PL_WALL, speed_of_sound,          value_type_id=sd.VT_BOTH_AVERAGES, instrument_ids=[assumption_id],       )
            sd.set_labeled_value( cursor, station_id, sd.Q_SHEAR_STRESS,                        sd.PL_WALL, wall_shear_stress,       value_type_id=sd.VT_BOTH_AVERAGES, instrument_ids=[momentum_balance_id], )
            sd.set_labeled_value( cursor, station_id, sd.Q_FANNING_FRICTION_FACTOR,             sd.PL_WALL, fanning_friction_factor, value_type_id=sd.VT_BOTH_AVERAGES, instrument_ids=[momentum_balance_id], )
            sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_VELOCITY,                   sd.PL_WALL, friction_velocity,       value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_VISCOUS_LENGTH_SCALE,                sd.PL_WALL, viscous_length_scale,    value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_REYNOLDS_NUMBER,            sd.PL_WALL, Re_tau,                  value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER, sd.PL_WALL, Re_tau,                  value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_MACH_NUMBER,                sd.PL_WALL, Ma_tau,                  value_type_id=sd.VT_BOTH_AVERAGES,                                       )
            sd.set_labeled_value( cursor, station_id, sd.Q_HEAT_FLUX,                           sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),  value_type_id=sd.VT_BOTH_AVERAGES, instrument_ids=[assumption_id],       )
            sd.set_labeled_value( cursor, station_id, sd.Q_INNER_LAYER_HEAT_FLUX,               sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),  value_type_id=sd.VT_BOTH_AVERAGES, instrument_ids=[assumption_id],       )
            sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_TEMPERATURE,                sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),  value_type_id=sd.VT_BOTH_AVERAGES, instrument_ids=[assumption_id],       )

            for quantity_id in sd.INCOMPRESSIBLE_RATIO_PROFILES:
                sd.set_constant_profile( cursor, station_id, quantity_id, sd.sdfloat( 1.0, 0.0 ), value_type_id=sd.VT_BOTH_AVERAGES, instrument_ids=[assumption_id], )

conn.commit()
conn.close()
