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

flow_class   = sd.FC_DUCT_FLOW
year         = 1911
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "StantonTE+1911+eng+JOUR",   sd.PRIMARY_SOURCE )
sd.add_source( cursor, study_identifier, "KooEC+1932+eng+THES",     sd.SECONDARY_SOURCE )

center_line_velocity_note = sd.add_note(
    cursor,
    "../data/{:s}/note_series_1_center_line_velocity.tex".format( study_identifier ),
)

globals_filename = "../data/{:s}/globals.csv".format( study_identifier )
with open( globals_filename, "r" ) as globals_file:
    globals_reader = csv.reader( globals_file, delimiter=",", quotechar='"', \
        skipinitialspace=True )
    next(globals_reader)
    for globals_row in globals_reader:
        series_number = int(globals_row[0])
        diameter      = sd.sdfloat(globals_row[2]) * 1.0e-2

        # p. 367
        #
        # \begin{quote}
        # The arrangement of one of the experimental pipes and the air fan used
        # to set up the current is shown in fig. I. The air fan discharges into
        # a horizontal pipe 3.5 metres in length.  This pipe is connected by a
        # bendto a vertical pipe 5.5 metres high.  The experimental portion, 61
        # cm. long, is at the upper extremity of the vertical pipe.
        # \end{quote}
        #
        # However, figure 1 remarks that the development section is 5.0 meters
        # in length.  Assume that the development section is the
        # difference between the quoted measurements and that the precision of
        # the value in the figure is too low.
        distance_between_pressure_taps = sd.sdfloat(61.0e-2)
        development_length             = sd.sdfloat(5.5) - distance_between_pressure_taps
        outer_layer_development_length = development_length / diameter

        # The rough pipe measurements are in the fully-rough regime.
        #
        # p. 369
        #
        # \begin{quote}
        # In order to simplify the problem, an attempt was made to eliminate
        # any effect due to a variation in $f( \nu / v_c \ell )$ by
        # artificially roughening the pipes used until the friction was
        # proportional to the square of the velocity.
        # \end{quote}
        #
        # This does not tell the precise roughness height, but it does indicate
        # that it is very large for the rough wall cases.
        is_rough_wall = ( int(globals_row[1]) == 1 )

        series_identifier = sd.add_series(
            cursor,
            flow_class=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            number_of_dimensions=2,
            coordinate_system=sd.CS_CYLINDRICAL,
        )

        sd.set_series_value( cursor, series_identifier, sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS, distance_between_pressure_taps, )

        # Working fluid
        #
        # pp. 366-367
        #
        # \begin{quote}
        # air was the fluid chosen for the experiments
        # \end{quote}

        # TODO: set air as the working fluid.

        sd.update_series_geometry(
            cursor,
            series_identifier,
            sd.GM_ELLIPTICAL
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

        station_filename = "../data/{:s}/series_{:d}.csv".format(
            study_identifier,
            series_number,
        )

        sd.set_station_value( cursor, station_identifier, sd.Q_HYDRAULIC_DIAMETER,             diameter,                       )
        sd.set_station_value( cursor, station_identifier, sd.Q_DEVELOPMENT_LENGTH,             development_length,             )
        sd.set_station_value( cursor, station_identifier, sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH, outer_layer_development_length, )
        sd.set_station_value( cursor, station_identifier, sd.Q_ASPECT_RATIO,                   1.0,                            )
        
        # Pitot-static tube dimensions
        #
        # p. 367
        #
        # \begin{quotation}
        # The Pitot tube was of rectangular section, the dimensions at the
        # orifice being:---
        # 
        # In the direction of the radius of the pipe \ldots External, 0.33 mm.
        # Internal, 0.25 mm.
        # 
        # Perpendicular to the radius of the pipe \ldots External, 1.27 mm.,
        # Internal, 1.20 mm.
        # \end{quotation}
        pitot_tube_height = 1.27e-3
        r_uncertainty = pitot_tube_height / 3.0**0.5

        # Accuracy of pressure measurements
        #
        # p. 368
        #
        # \begin{quote}
        # The pressure difference was measured by a sensitive oil and water
        # tilting gauge, whose indications could be relied upon within an
        # accuracy of 0.005 mm of water.
        # \end{quote}
        #
        # However, the resulting uncertainties from this value, once propagated
        # from the pressure measurements to the velocity measurements, appear
        # to be far too small by several orders of magnitude.  To that end, the
        # uncertainty of the velocity measurements is unknown.  It is likely
        # that this is the smallest pressure difference value that the
        # instrument could detect and not necessarily that range of values
        # plausibly being measured.

        # Note that the profiles lack the wall point and are presented in order
        # from the center-line to wall.  The profiles need to be assembled
        # point-by-point.
        r_reversed = []
        u_reversed = []
        with open( station_filename, "r" ) as station_file:
            station_reader = csv.reader( station_file, delimiter=",", \
                quotechar='"', skipinitialspace=True )
            next(station_reader)
            for station_row in station_reader:
                r_reversed.append(
                    sd.sdfloat( float(station_row[0]) * 1.0e-2, r_uncertainty )
                )

                u_reversed.append( sd.sdfloat(station_row[1]) * 1.0e-2 )

        r_reversed.append( sd.sdfloat( 0.5*diameter.n, 0.0 ) )
        u_reversed.append( sd.sdfloat( 0.0,            0.0 ) )

        n_points = len(r_reversed)

        # This temperature is an assumption.  It is not stated in the paper.
        temperature         = sd.sdfloat( 15.0 + sd.ABSOLUTE_ZERO )
        mass_density        = sd.ideal_gas_mass_density( temperature )
        speed_of_sound      = sd.ideal_gas_speed_of_sound( temperature )
        dynamic_viscosity   = sd.sutherlands_law_dynamic_viscosity( temperature )
        kinematic_viscosity = dynamic_viscosity / mass_density

        i = 0
        for point_number in range( n_points, 0, -1 ):
            point_label = None
            if ( point_number == 1 ):
                point_label = sd.PL_WALL
            elif ( point_number == n_points ):
                point_label = sd.PL_CENTER_LINE

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

            distance_from_wall = 0.5 * diameter - r_reversed[i]
            outer_layer_coordinate = 2.0 * distance_from_wall / diameter

            # Velocity measurement technique
            #
            # p. 367
            #
            # \begin{quote}
            # The values of $v$ where determined from the difference between
            # the pressure in a small Pitot tube facing the current and that in
            # a small orifice in the side of the pipe.
            # \end{quote}
            mt_velocity = sd.MT_PITOT_STATIC_TUBE

            current_notes = []
            if ( series_number == 1 and point_number == n_points ):
                current_notes = [center_line_velocity_note]

            sd.set_point_value( cursor, point_identifier, sd.Q_DISTANCE_FROM_WALL,     distance_from_wall,     )
            sd.set_point_value( cursor, point_identifier, sd.Q_OUTER_LAYER_COORDINATE, outer_layer_coordinate, )
            sd.set_point_value( cursor, point_identifier, sd.Q_STREAMWISE_COORDINATE,  sd.sdfloat(0.0),        )
            sd.set_point_value( cursor, point_identifier, sd.Q_TRANSVERSE_COORDINATE,  r_reversed[i],          )
            sd.set_point_value( cursor, point_identifier, sd.Q_SPANWISE_COORDINATE,    sd.sdfloat(0.0),        )
            sd.set_point_value( cursor, point_identifier, sd.Q_STREAMWISE_VELOCITY,    u_reversed[i], value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[mt_velocity], notes=current_notes, )

            for quantity in [ sd.Q_TRANSVERSE_VELOCITY,
                              sd.Q_SPANWISE_VELOCITY, ]:
                sd.set_point_value(
                    cursor,
                    point_identifier,
                    quantity,
                    sd.sdfloat(0.0),
                    value_type=sd.VT_BOTH_AVERAGES,
                    measurement_techniques=[sd.MT_ASSUMPTION],
                )

            # Assumed constant profiles
            sd.set_point_value( cursor, point_identifier, sd.Q_TEMPERATURE,         temperature,         value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION],  )
            sd.set_point_value( cursor, point_identifier, sd.Q_MASS_DENSITY,        mass_density,        value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION],  )
            sd.set_point_value( cursor, point_identifier, sd.Q_KINEMATIC_VISCOSITY, kinematic_viscosity, value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION],  )
            sd.set_point_value( cursor, point_identifier, sd.Q_DYNAMIC_VISCOSITY,   dynamic_viscosity,   value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION],  )
            sd.set_point_value( cursor, point_identifier, sd.Q_SPEED_OF_SOUND,      speed_of_sound,      value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION], )

            i += 1

        if ( is_rough_wall == False ):
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

        r_prof, u_prof = sd.get_twin_profiles(
            cursor,
            station_identifier,
            sd.Q_TRANSVERSE_COORDINATE,
            sd.Q_STREAMWISE_VELOCITY,
        )

        volumetric_flow_rate = -2.0 * math.pi * sd.integrate_using_trapezoid_rule( r_prof, u_prof * r_prof )
        mass_flow_rate       = mass_density * volumetric_flow_rate
        bulk_velocity        = 4.0 * volumetric_flow_rate / ( math.pi * diameter**2.0 )
        Re_bulk              = bulk_velocity * diameter / kinematic_viscosity
        Ma_bulk              = bulk_velocity / speed_of_sound
        center_line_velocity = sd.get_labeled_value( cursor, station_identifier, sd.Q_STREAMWISE_VELOCITY, sd.PL_CENTER_LINE, )

        maximum_velocity = sd.get_labeled_value(
            cursor,
            station_identifier,
            sd.Q_STREAMWISE_VELOCITY,
            sd.PL_CENTER_LINE,
            value_type=sd.VT_UNWEIGHTED_AVERAGE,
        )

        sd.set_station_value( cursor, station_identifier, sd.Q_VOLUMETRIC_FLOW_RATE,               volumetric_flow_rate,             value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION], )
        sd.set_station_value( cursor, station_identifier, sd.Q_MASS_FLOW_RATE,                     mass_flow_rate,                   value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION], )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_VELOCITY,                      bulk_velocity,                    value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION], )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_REYNOLDS_NUMBER,               Re_bulk,                          value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION], )
        sd.set_station_value( cursor, station_identifier, sd.Q_BULK_MACH_NUMBER,                   Ma_bulk,                          value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_CALCULATION], )

        sd.set_labeled_value( cursor, station_identifier, sd.Q_HEAT_FLUX, sd.PL_WALL, sd.sdfloat( 0.0, 0.0 ), value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION], )

        for quantity in sd.INCOMPRESSIBLE_RATIO_PROFILES:
            sd.set_constant_profile( cursor, station_identifier, quantity, sd.sdfloat( 1.0, 0.0 ), value_type=sd.VT_BOTH_AVERAGES, measurement_techniques=[sd.MT_ASSUMPTION], )

        for point_identifier in sd.get_points_at_station( cursor, station_identifier ):
            streamwise_velocity = sd.get_point_value( cursor, point_identifier, sd.Q_STREAMWISE_VELOCITY )
            sd.set_point_value( cursor, point_identifier,        sd.Q_LOCAL_TO_BULK_STREAMWISE_VELOCITY_RATIO, streamwise_velocity /        bulk_velocity, value_type=sd.VT_BOTH_AVERAGES, )
            sd.set_point_value( cursor, point_identifier, sd.Q_LOCAL_TO_CENTER_LINE_STREAMWISE_VELOCITY_RATIO, streamwise_velocity / center_line_velocity, value_type=sd.VT_BOTH_AVERAGES, )

        # Wall shear stress measurements
        #
        # p. 368
        #
        # \begin{quote}
        # The determination of the shearing stress on any cylindrical portion
        # of the fluid of radius $r$ was made by a direct measurement of the
        # drop of pressure at the surface along the pipe, together with the
        # measurement of the variation of pressure along the radius.
        # \end{quote}
        #
        # p. 369
        #
        # \begin{quote}
        # After several trials, two pipes were produced, of diameters 7.35 and
        # 5.08 cm., in which the friction varied as the square of the velocity,
        # and consequently the friction per unit are at the same velocities was
        # found to be the same for each pipe, the numerical value being $4.6
        # v_c^2 \times 10^{-6}$ dynes per square centimeter.
        # \end{quote}

conn.commit()
conn.close()
