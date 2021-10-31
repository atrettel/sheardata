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
year         = 1947
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "HuebscherRG+1947+eng+JOUR", sd.PRIMARY_SOURCE )

mass_density_note = sd.add_note(
    cursor,
    "../data/{:s}/note_mass_density.tex".format( study_identifier ),
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

            speed_of_sound = sd.ideal_gas_speed_of_sound( temperature )
            Ma_bulk        = bulk_velocity     / speed_of_sound
            Ma_tau         = friction_velocity / speed_of_sound

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
                    identifiers={ sd.C_SELF : originators_identifier },
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
                    identifiers={ sd.C_SELF : originators_identifier },
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
                identifiers={ sd.C_SELF : originators_identifier },
            )

            sd.mark_station_as_periodic( cursor, station_identifier )

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
            mt_bulk_velocity = sd.MT_IMPACT_TUBE

            sd.set_station_value( cursor, station_identifier, sd.Q_HYDRAULIC_DIAMETER,             hydraulic_diameter,                      )
            sd.set_station_value( cursor, station_identifier, sd.Q_DEVELOPMENT_LENGTH,             ducts[duct].length,                      )
            sd.set_station_value( cursor, station_identifier, sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH, ducts[duct].length / hydraulic_diameter, )
            sd.set_station_value( cursor, station_identifier, sd.Q_ASPECT_RATIO,                   ducts[duct].aspect_ratio,                )
            sd.set_station_value( cursor, station_identifier, sd.Q_BULK_VELOCITY,                  bulk_velocity, averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[mt_bulk_velocity],  )
            sd.set_station_value( cursor, station_identifier, sd.Q_BULK_REYNOLDS_NUMBER,           Re_bulk,       averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_CALCULATION], )
            sd.set_station_value( cursor, station_identifier, sd.Q_BULK_MACH_NUMBER,               Ma_bulk,       averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_CALCULATION], )

            if ( duct != "Round" ):
                sd.set_station_value( cursor, station_identifier, sd.Q_HEIGHT,      height,      measurement_techniques=[sd.MT_CALCULATION], )
                sd.set_station_value( cursor, station_identifier, sd.Q_WIDTH,       width,       measurement_techniques=[sd.MT_CALCULATION], )
                sd.set_station_value( cursor, station_identifier, sd.Q_HALF_HEIGHT, half_height, measurement_techniques=[sd.MT_CALCULATION], )

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
                    sd.sdfloat(0.0),
                    measurement_techniques=[sd.MT_ASSUMPTION],
                )

            current_notes = []
            if ( test_number == 17 and duct == "Square" ):
                current_notes = [mass_density_note]

            # p. 129
            mt_wall_shear_stress = sd.MT_MOMENTUM_BALANCE

            sd.set_labeled_value( cursor, station_identifier, sd.Q_MASS_DENSITY,                          sd.WALL_POINT_LABEL, mass_density,            averaging_system=sd.BOTH_AVERAGING_SYSTEMS, notes=current_notes,                             )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_KINEMATIC_VISCOSITY,                   sd.WALL_POINT_LABEL, kinematic_viscosity,     averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_DYNAMIC_VISCOSITY,                     sd.WALL_POINT_LABEL, dynamic_viscosity,       averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_TEMPERATURE,                           sd.WALL_POINT_LABEL, temperature,             averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_STREAMWISE_VELOCITY,                   sd.WALL_POINT_LABEL, sd.sdfloat( 0.0, 0.0 ),  averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_DISTANCE_FROM_WALL,                    sd.WALL_POINT_LABEL, sd.sdfloat( 0.0, 0.0 ),  averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_OUTER_LAYER_COORDINATE,                sd.WALL_POINT_LABEL, sd.sdfloat( 0.0, 0.0 ),  averaging_system=sd.BOTH_AVERAGING_SYSTEMS,                                                )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_SPEED_OF_SOUND,                        sd.WALL_POINT_LABEL, speed_of_sound,          averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_ASSUMPTION],     )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_SHEAR_STRESS,                          sd.WALL_POINT_LABEL, wall_shear_stress,       averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[mt_wall_shear_stress], )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_FANNING_FRICTION_FACTOR,               sd.WALL_POINT_LABEL, fanning_friction_factor, averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[mt_wall_shear_stress], )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_VELOCITY,                     sd.WALL_POINT_LABEL, friction_velocity,       averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_CALCULATION],    )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_VISCOUS_LENGTH_SCALE,                  sd.WALL_POINT_LABEL, viscous_length_scale,    averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_CALCULATION],    )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_REYNOLDS_NUMBER,              sd.WALL_POINT_LABEL, Re_tau,                  averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_CALCULATION],    )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER,   sd.WALL_POINT_LABEL, Re_tau,                  averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_CALCULATION],    )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_MACH_NUMBER,                  sd.WALL_POINT_LABEL, Ma_tau,                  averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_CALCULATION],    )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_HEAT_FLUX,                             sd.WALL_POINT_LABEL, sd.sdfloat( 0.0, 0.0 ),  averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_ASSUMPTION],     )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_INNER_LAYER_HEAT_FLUX,                 sd.WALL_POINT_LABEL, sd.sdfloat( 0.0, 0.0 ),  averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_ASSUMPTION],     )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_CENTER_LINE_TO_WALL_TEMPERATURE_RATIO, sd.WALL_POINT_LABEL, sd.sdfloat( 1.0, 0.0 ),  averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_ASSUMPTION],     )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_WALL_TO_RECOVERY_TEMPERATURE_RATIO,    sd.WALL_POINT_LABEL, sd.sdfloat( 1.0, 0.0 ),  averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_ASSUMPTION],     )
            sd.set_labeled_value( cursor, station_identifier, sd.Q_FRICTION_TEMPERATURE,                  sd.WALL_POINT_LABEL, sd.sdfloat( 0.0, 0.0 ),  averaging_system=sd.BOTH_AVERAGING_SYSTEMS, measurement_techniques=[sd.MT_ASSUMPTION],     )

conn.commit()
conn.close()
