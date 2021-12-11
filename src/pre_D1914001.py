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

flow_class    = sd.FC_DUCT_FLOW
year          = 1914
study_number  = 1

study_id = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type_id=sd.ST_EXPERIMENT,
)

sd.add_study_source( cursor, study_id, "StantonTE+1914+eng+JOUR",   sd.PRIMARY_SOURCE )
sd.add_study_source( cursor, study_id, "ObotNT+1988+eng+JOUR",    sd.SECONDARY_SOURCE )

development_length_note = sd.add_note(
    cursor,
    "../data/{:s}/note_development_length.tex".format( study_id ),
)

mass_density_note = sd.add_note(
    cursor,
    "../data/{:s}/note_mass_density.tex".format( study_id ),
)

class Pipe:
    diameter                       = None
    distance_between_pressure_taps = None
    material                       = None

    # p. 202
    #
    # \begin{quote}
    # The length of ``leading in'' pipe, of the same diameter as the
    # experimental portion, through which the fluid passed before any
    # observations of its velocity or pressure were made, varied from 90 to 140
    # diameters, as it was considered that this length was sufficient both to
    # enable any irregularities in the distribution of velocity to die away, or
    # any stream-line motion at the inlet to break up, before the measurements
    # were taken.
    # \end{quote}
    #
    # For the sake of simplicity, assume that the development length is the
    # minimum of these.  It is long enough that its precise value does not
    # matter.
    def outer_layer_development_length( self ):
        return sd.sdfloat(90.0)

    def development_length( self ):
        return diameter * self.outer_layer_development_length()

    def __init__( self, diameter, distance_between_pressure_taps, material ):
        self.diameter = sd.sdfloat(diameter)
        if ( distance_between_pressure_taps == 0.0 ):
            self.distance_between_pressure_taps = None
        else:
            self.distance_between_pressure_taps = distance_between_pressure_taps
        self.material = str(material)

# Pipe 12A
#
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

pipes = {}
pipes_filename = "../data/{:s}/pipes.csv".format( study_id )
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

# p. 203
#
# \begin{quote}
# The form of the tilting manometer used for the estimation of both the surface
# friction and the axial velocity, is that devised by Dr. A. P.  Chattock and
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
#
# This appears to be the only information given about the uncertainty of the
# experiments.  It is less useful than it appears, since according to the table
# on page 207, different manometers and gauges were used seemingly at random,
# making it unclear where the cutoff for "higher pressures" really is.
#
# Moreover, just as in the 1911 case, the uncertainties produced after
# propagating this from the pressure measurements to the velocities and shear
# stresses are many orders of magnitude too small.  Therefore it is difficult
# to estimate the uncertainties of these measurements.

# Set 1: velocity ratio data
series_number = 0
ratio_filename = "../data/{:s}/bulk_and_maximum_velocities.csv".format( study_id )
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

        # Series 49, the one with the bulk velocity of 115.5 cm/s, appears to
        # be a turbulent value at a laminar Reynolds number.
        outlier = True if series_number == 49 else False

        bulk_velocity        = sd.sdfloat(ratio_row[0]) * 1.0e-2
        center_line_velocity = sd.sdfloat(ratio_row[1]) * 1.0e-2
        working_fluid        =        str(ratio_row[2])
        pipe                 =        str(ratio_row[3])

        diameter                       = pipes[pipe].diameter
        distance_between_pressure_taps = pipes[pipe].distance_between_pressure_taps
        development_length             = pipes[pipe].development_length()
        outer_layer_development_length = pipes[pipe].outer_layer_development_length()

        # The velocity ratio experiments do not give the test conditions like
        # the temperature.  Graphical extraction from figure 1 reveals that the
        # kinematic viscosity used there is consistent with the value around
        # 15°C.
        #
        # These values were extracted graphically from figure 1 and averaged to
        # a single value.
        #
        # TODO: Calculate the density values rather than just assuming them.
        temperature = sd.sdfloat( 15.0 + sd.ABSOLUTE_ZERO )
        dynamic_viscosity   = None
        kinematic_viscosity = None
        mass_density        = None
        if ( working_fluid == "Water" ):
            mass_density        = sd.liquid_water_mass_density( temperature )
            dynamic_viscosity   = sd.liquid_water_dynamic_viscosity( temperature )
            kinematic_viscosity = dynamic_viscosity / mass_density
        elif ( working_fluid == "Air" ):
            mass_density        = sd.ideal_gas_mass_density( temperature )
            dynamic_viscosity   = sd.sutherlands_law_dynamic_viscosity( temperature )
            kinematic_viscosity = dynamic_viscosity / mass_density

        Re_bulk = bulk_velocity * diameter / kinematic_viscosity

        volumetric_flow_rate = 0.25 * math.pi * diameter**2.0 * bulk_velocity

        speed_of_sound = sd.sdfloat("inf")
        if ( working_fluid == "Air" ):
            speed_of_sound = sd.ideal_gas_speed_of_sound( temperature )
        elif ( working_fluid == "Water" ):
            speed_of_sound = sd.liquid_water_speed_of_sound( temperature )
        Ma_bulk = bulk_velocity / speed_of_sound

        series_id = sd.add_series(
            cursor,
            flow_class_id=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            number_of_dimensions=2,
            coordinate_system_id=sd.CS_CYLINDRICAL,
        )

        # TODO: set working fluids.

        sd.update_series_geometry(
            cursor,
            series_id,
            sd.GM_ELLIPTICAL
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
        )

        sd.mark_station_as_periodic( cursor, station_id )

        sd.set_station_value( cursor, station_id, sd.Q_HYDRAULIC_DIAMETER,                 diameter,                                                                                               )
        sd.set_station_value( cursor, station_id, sd.Q_DEVELOPMENT_LENGTH,                 development_length,               meastech_ids=[sd.MT_ASSUMPTION], note_ids=[development_length_note], )
        sd.set_station_value( cursor, station_id, sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH,     outer_layer_development_length,   meastech_ids=[sd.MT_ASSUMPTION], note_ids=[development_length_note], )
        sd.set_station_value( cursor, station_id, sd.Q_ASPECT_RATIO,                       1.0,                                                                                                    )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_VELOCITY,                      bulk_velocity,                    value_type_id=sd.VT_BOTH_AVERAGES,                                             outlier=outlier, )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_REYNOLDS_NUMBER,               Re_bulk,                          value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION], outlier=outlier, )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_MACH_NUMBER,                   Ma_bulk,                          value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION], outlier=outlier, )
        sd.set_station_value( cursor, station_id, sd.Q_VOLUMETRIC_FLOW_RATE,               volumetric_flow_rate,             value_type_id=sd.VT_BOTH_AVERAGES,                                             outlier=outlier, )

        n_points = 2
        for point_number in [1, n_points]:
            point_label = None
            if ( point_number == 1 ):
                point_label = sd.PL_WALL
            elif ( point_number == n_points ):
                point_label = sd.PL_CENTER_LINE

            point_id = sd.add_point(
                cursor,
                flow_class_id=flow_class,
                year=year,
                study_number=study_number,
                series_number=series_number,
                station_number=station_number,
                point_number=point_number,
                point_label_id=point_label,
            )

        # Measurement techniques for flow rate and center-line velocities
        #
        # p. 203
        #
        # \begin{quote}
        # To measure the velocity of the current, one of two methods was used
        # according to convenience.  By one method the total quantity of fluid
        # passing through the pipe in a given time was either weighed directly,
        # or passed through a water-meter or a gas-holder, which had been
        # designed for the purpose of the experiments and carefully calibrated.
        # By the other method the velocity at the axis of the pipe was
        # estimated by measuring the difference of pressure between that in a
        # small Pitot tube facing the current and placed in the axis of the
        # pipe and that in a small hole in the wall of the pipe.
        # \end{quote}
        #
        # Page 207 contains a table of global parameters listing the
        # measurement techniques for different series of measurements.
        # However, the flow rate measurement technique varies for different
        # pipes and often 2 or more measurement techniques were used in an
        # unclear manner for a given pipe.
        #
        # In addition to that, the paper contains no information on the
        # uncertainty of the flow rate measuremnt.
        mt_velocity = sd.MT_IMPACT_TUBE

        for label in [ sd.PL_WALL, sd.PL_CENTER_LINE ]:
            sd.set_labeled_value( cursor, station_id, sd.Q_MASS_DENSITY,        label, mass_density,        value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION], )
            sd.set_labeled_value( cursor, station_id, sd.Q_DYNAMIC_VISCOSITY,   label, dynamic_viscosity,   value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION], )
            sd.set_labeled_value( cursor, station_id, sd.Q_KINEMATIC_VISCOSITY, label, kinematic_viscosity, value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION], )
            sd.set_labeled_value( cursor, station_id, sd.Q_TEMPERATURE,         label, temperature,         value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_ASSUMPTION],  )
            sd.set_labeled_value( cursor, station_id, sd.Q_SPEED_OF_SOUND,      label, speed_of_sound,      value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_ASSUMPTION],  )

        for quantity_id in [ sd.Q_ROUGHNESS_HEIGHT,
                             sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,
                             sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT, ]:
            sd.set_labeled_value(
                cursor,
                station_id,
                quantity_id,
                sd.PL_WALL,
                sd.sdfloat(0.0),
                meastech_ids=[sd.MT_ASSUMPTION],
            )

        sd.set_labeled_value( cursor, station_id, sd.Q_STREAMWISE_VELOCITY,    sd.PL_WALL,        sd.sdfloat( 0.0, 0.0 ),            value_type_id=sd.VT_BOTH_AVERAGES, )
        sd.set_labeled_value( cursor, station_id, sd.Q_STREAMWISE_VELOCITY,    sd.PL_CENTER_LINE, center_line_velocity,              value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[mt_velocity], outlier=outlier,)
        sd.set_labeled_value( cursor, station_id, sd.Q_TRANSVERSE_COORDINATE,  sd.PL_WALL,        sd.sdfloat( 0.5*diameter.n, 0.0 ), value_type_id=sd.VT_BOTH_AVERAGES, )
        sd.set_labeled_value( cursor, station_id, sd.Q_TRANSVERSE_COORDINATE,  sd.PL_CENTER_LINE, 0.0,                               value_type_id=sd.VT_BOTH_AVERAGES, )
        sd.set_labeled_value( cursor, station_id, sd.Q_DISTANCE_FROM_WALL,     sd.PL_WALL,        sd.sdfloat( 0.0, 0.0 ),            value_type_id=sd.VT_BOTH_AVERAGES, )
        sd.set_labeled_value( cursor, station_id, sd.Q_DISTANCE_FROM_WALL,     sd.PL_CENTER_LINE, 0.5*diameter,                      value_type_id=sd.VT_BOTH_AVERAGES, )
        sd.set_labeled_value( cursor, station_id, sd.Q_OUTER_LAYER_COORDINATE, sd.PL_WALL,        sd.sdfloat( 0.0, 0.0 ),            value_type_id=sd.VT_BOTH_AVERAGES, )
        sd.set_labeled_value( cursor, station_id, sd.Q_OUTER_LAYER_COORDINATE, sd.PL_CENTER_LINE, 1.0,                               value_type_id=sd.VT_BOTH_AVERAGES, )

        sd.set_labeled_value( cursor, station_id, sd.Q_HEAT_FLUX, sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ), value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_ASSUMPTION], )

        for quantity_id in sd.INCOMPRESSIBLE_RATIO_PROFILES:
            sd.set_constant_profile( cursor, station_id, quantity_id, sd.sdfloat( 1.0, 0.0 ), value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_ASSUMPTION], )

        for point_id in sd.get_points_at_station( cursor, station_id ):
            streamwise_velocity = sd.get_point_value( cursor, point_id, sd.Q_STREAMWISE_VELOCITY )
            sd.set_point_value( cursor, point_id,        sd.Q_LOCAL_TO_BULK_STREAMWISE_VELOCITY_RATIO, streamwise_velocity /        bulk_velocity, value_type_id=sd.VT_BOTH_AVERAGES, )
            sd.set_point_value( cursor, point_id, sd.Q_LOCAL_TO_CENTER_LINE_STREAMWISE_VELOCITY_RATIO, streamwise_velocity / center_line_velocity, value_type_id=sd.VT_BOTH_AVERAGES, )

# Set 2: wall shear stress data
shear_stress_filename = "../data/{:s}/wall_shear_stress_measurements.csv".format( study_id )
with open( shear_stress_filename, "r" ) as shear_stress_file:
    shear_stress_reader = csv.reader(
        shear_stress_file,
        delimiter=",",
        quotechar='"', \
        skipinitialspace=True,
    )
    next(shear_stress_reader)
    for shear_stress_row in shear_stress_reader:
        series_number += 1

        bulk_velocity                 = sd.sdfloat(shear_stress_row[0]) * 1.0e-2
        wall_shear_stress             = sd.sdfloat(shear_stress_row[1]) * 1.0e-1
        fanning_friction_factor       = sd.sdfloat(shear_stress_row[2]) * 2.0
        Re_bulk                       = sd.sdfloat(shear_stress_row[3])
        temperature                   = sd.sdfloat(shear_stress_row[4]) + sd.ABSOLUTE_ZERO
        working_fluid                 =        str(shear_stress_row[5])
        pipe                          =        str(shear_stress_row[6])

        diameter                       = pipes[pipe].diameter
        distance_between_pressure_taps = pipes[pipe].distance_between_pressure_taps
        development_length             = pipes[pipe].development_length()
        outer_layer_development_length = pipes[pipe].outer_layer_development_length()

        mass_density        = 2.0 * wall_shear_stress / ( fanning_friction_factor * bulk_velocity**2.0 )
        kinematic_viscosity = bulk_velocity * diameter / Re_bulk
        dynamic_viscosity   = mass_density * kinematic_viscosity

        volumetric_flow_rate = 0.25 * math.pi * diameter**2.0 * bulk_velocity

        friction_velocity    = ( wall_shear_stress / mass_density )**0.5
        viscous_length_scale = kinematic_viscosity / friction_velocity
        Re_tau               = 0.5 * diameter / viscous_length_scale

        outlier = False
        current_notes = []
        if ( working_fluid == "Air" and pipe == "S" ):
            outlier = True
            current_notes = [mass_density_note]

        series_id = sd.add_series(
            cursor,
            flow_class_id=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            number_of_dimensions=2,
            coordinate_system_id=sd.CS_CYLINDRICAL,
            outlier=outlier,
        )

        # TODO: add working fluid components.

        # Without knowing precisely what "thick oil" is it is difficult to
        # assume anything else.
        speed_of_sound_measurement_technique = sd.MT_ASSUMPTION
        speed_of_sound = sd.sdfloat("inf")
        if ( working_fluid == "Air" ):
            speed_of_sound = sd.ideal_gas_speed_of_sound( temperature )
            speed_of_sound_measurement_technique = sd.MT_CALCULATION
        elif ( working_fluid == "Water" ):
            speed_of_sound = sd.liquid_water_speed_of_sound( temperature )
            speed_of_sound_measurement_technique = sd.MT_CALCULATION
        Ma_bulk = bulk_velocity     / speed_of_sound
        Ma_tau  = friction_velocity / speed_of_sound

        sd.update_series_geometry(
            cursor,
            series_id,
            sd.GM_ELLIPTICAL
        )

        if ( distance_between_pressure_taps != None ):
            sd.set_series_value(
                cursor,
                series_id,
                sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS,
                distance_between_pressure_taps,
            )

        station_number = 1
        station_id = sd.add_station(
            cursor,
            flow_class_id=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            station_number=station_number,
            outlier=outlier,
        )

        sd.mark_station_as_periodic( cursor, station_id )

        sd.set_station_value( cursor, station_id, sd.Q_DEVELOPMENT_LENGTH,             development_length,             meastech_ids=[sd.MT_ASSUMPTION], note_ids=[development_length_note], )
        sd.set_station_value( cursor, station_id, sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH, outer_layer_development_length, meastech_ids=[sd.MT_ASSUMPTION], note_ids=[development_length_note], )
        sd.set_station_value( cursor, station_id, sd.Q_HYDRAULIC_DIAMETER,             diameter,                                                                                                     outlier=outlier, )
        sd.set_station_value( cursor, station_id, sd.Q_ASPECT_RATIO,                   1.0,                                                                                                          outlier=outlier, )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_VELOCITY,                  bulk_velocity,        value_type_id=sd.VT_BOTH_AVERAGES,                                             outlier=outlier, )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_REYNOLDS_NUMBER,           Re_bulk,              value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION], outlier=outlier, )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_MACH_NUMBER,               Ma_bulk,              value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION], outlier=outlier, )
        sd.set_station_value( cursor, station_id, sd.Q_VOLUMETRIC_FLOW_RATE,           volumetric_flow_rate, value_type_id=sd.VT_BOTH_AVERAGES,                                             outlier=outlier, )

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

        for quantity_id in [ sd.Q_ROUGHNESS_HEIGHT,
                             sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,
                             sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT, ]:
            sd.set_labeled_value(
                cursor,
                station_id,
                quantity_id,
                sd.PL_WALL,
                sd.sdfloat(0.0),
                meastech_ids=[sd.MT_ASSUMPTION],
                outlier=outlier,
            )

        # Wall shear stress measurement technique
        #
        # p. 203
        #
        # \begin{quote}
        # To determine the amount of the surface friction two small holes were
        # made in the walls of the experimental portion of the pipe, one at
        # each extremity, at a known distance apart, and connected to a tilting
        # manometer.  \ldots  In this way the fall of pressure along a given
        # length of the pipe was determined, and from the known diameter of the
        # pipe the surface friction per unit area was calculated.
        # \end{quote}
        mt_wall_shear_stress = sd.MT_MOMENTUM_BALANCE

        sd.set_labeled_value( cursor, station_id, sd.Q_MASS_DENSITY,                        sd.PL_WALL, mass_density,                      value_type_id=sd.VT_BOTH_AVERAGES,                                                                outlier=outlier, note_ids=current_notes, )
        sd.set_labeled_value( cursor, station_id, sd.Q_DYNAMIC_VISCOSITY,                   sd.PL_WALL, dynamic_viscosity,                 value_type_id=sd.VT_BOTH_AVERAGES,                                                                outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_KINEMATIC_VISCOSITY,                 sd.PL_WALL, kinematic_viscosity,               value_type_id=sd.VT_BOTH_AVERAGES,                                                                outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_TEMPERATURE,                         sd.PL_WALL, temperature,                       value_type_id=sd.VT_BOTH_AVERAGES,                                                                outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_SPEED_OF_SOUND,                      sd.PL_WALL, speed_of_sound,                    value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[speed_of_sound_measurement_technique], outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_STREAMWISE_VELOCITY,                 sd.PL_WALL, sd.sdfloat( 0.0,            0.0 ), value_type_id=sd.VT_BOTH_AVERAGES,                                                                outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_TRANSVERSE_COORDINATE,               sd.PL_WALL, sd.sdfloat( 0.5*diameter.n, 0.0 ), value_type_id=sd.VT_BOTH_AVERAGES,                                                                outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_DISTANCE_FROM_WALL,                  sd.PL_WALL, sd.sdfloat( 0.0,            0.0 ), value_type_id=sd.VT_BOTH_AVERAGES,                                                                outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_OUTER_LAYER_COORDINATE,              sd.PL_WALL, sd.sdfloat( 0.0,            0.0 ), value_type_id=sd.VT_BOTH_AVERAGES,                                                                outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_SHEAR_STRESS,                        sd.PL_WALL, wall_shear_stress,                 value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[mt_wall_shear_stress],                 outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_FANNING_FRICTION_FACTOR,             sd.PL_WALL, fanning_friction_factor,           value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[mt_wall_shear_stress],                 outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_VELOCITY,                   sd.PL_WALL, friction_velocity,                 value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION],                    outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_VISCOUS_LENGTH_SCALE,                sd.PL_WALL, viscous_length_scale,              value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION],                    outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_REYNOLDS_NUMBER,            sd.PL_WALL, Re_tau,                            value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION],                    outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER, sd.PL_WALL, Re_tau,                            value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION],                    outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_MACH_NUMBER,                sd.PL_WALL, Ma_tau,                            value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_CALCULATION],                    outlier=outlier,                    )
        sd.set_labeled_value( cursor, station_id, sd.Q_HEAT_FLUX,                           sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),            value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_ASSUMPTION],                                                         )
        sd.set_labeled_value( cursor, station_id, sd.Q_INNER_LAYER_HEAT_FLUX,               sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),            value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_ASSUMPTION],                                                         )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_TEMPERATURE,                sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ),            value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_ASSUMPTION],                                                         )

        for quantity_id in sd.INCOMPRESSIBLE_RATIO_PROFILES:
            sd.set_constant_profile( cursor, station_id, quantity_id, sd.sdfloat( 1.0, 0.0 ), value_type_id=sd.VT_BOTH_AVERAGES, meastech_ids=[sd.MT_ASSUMPTION], )

conn.commit()
conn.close()
