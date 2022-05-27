#!/usr/bin/env python3

# Copyright (C) 2021-2022 Andrew Trettel
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

flow_class   = sd.FC_BOUNDARY_LAYER
year         = 1914
study_number = 1

study_id = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type_id=sd.ST_EXPERIMENT,
    study_external_ids={sd.C_CH_1969 : "1600"},
)

sd.add_study_source( cursor, study_id, "RiabouchinskyD+1914+fra+JOUR",   sd.PRIMARY_SOURCE )
sd.add_study_source( cursor, study_id, "ColesDE+1969+eng+BOOK",        sd.SECONDARY_SOURCE )

station_4_velocity_note = sd.add_note(
    cursor,
    "../data/{:s}/note_station_4_velocity.tex".format( study_id ),
)

galilean_transformation_note = sd.add_note(
    cursor,
    "../data/{:s}/note_galilean_transformation.tex".format( study_id ),
)

series_number = 1
series_id = sd.add_series(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    series_number=series_number,
    number_of_dimensions=2,
    coordinate_system_id=sd.CS_RECTANGULAR,
    note_ids=[galilean_transformation_note,],
)

freestream_velocity = sd.sdfloat(16.0)

sd.set_series_value( cursor, series_id, sd.Q_FREESTREAM_VELOCITY, freestream_velocity, )

sd.update_series_geometry(
    cursor,
    series_id,
    sd.GM_RECTANGULAR
)

globals_filename = "../data/{:s}/globals.csv".format( study_id )
with open( globals_filename, "r" ) as globals_file:
    globals_reader = csv.reader( globals_file, delimiter=",", quotechar='"', \
        skipinitialspace=True )
    next(globals_reader)
    for globals_row in globals_reader:
        station_number = int(globals_row[0])
        x              = sd.sdfloat(globals_row[1])
        z              = sd.sdfloat(0.0)

        station_id = sd.add_station(
            cursor,
            flow_class_id=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            station_number=station_number,
        )

        # Add in previous and next stations.

        station_filename = "../data/{:s}/station_{:d}.csv".format(
            study_id,
            station_number,
        )

        point_number = 0
        y = []
        u = []
        with open( station_filename, "r" ) as station_file:
            station_reader = csv.reader( station_file, delimiter=",", \
                quotechar='"', skipinitialspace=True )
            next(station_reader)
            for station_row in station_reader:
                point_number += 1

                point_label = None
                if ( point_number == 1 ):
                    point_label = sd.PL_WALL

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

                y = sd.sdfloat( float(station_row[0]) )
                u = freestream_velocity - sd.sdfloat( float(station_row[1]) )
                w = sd.sdfloat( 0.0 )

                outer_layer_velocity = u / freestream_velocity

                current_notes = []
                if ( station_number == 4 and point_number == 10 ):
                    current_notes = [station_4_velocity_note]

                sd.set_point_value( cursor, point_id, sd.Q_DISTANCE_FROM_WALL,     y, )
                sd.set_point_value( cursor, point_id, sd.Q_STREAMWISE_COORDINATE,  x, )
                sd.set_point_value( cursor, point_id, sd.Q_TRANSVERSE_COORDINATE,  y, )
                sd.set_point_value( cursor, point_id, sd.Q_SPANWISE_COORDINATE,    z, )
                sd.set_point_value( cursor, point_id, sd.Q_STREAMWISE_VELOCITY,    u,                    value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_PITOT_STATIC_TUBE], note_ids=current_notes, )
                sd.set_point_value( cursor, point_id, sd.Q_SPANWISE_VELOCITY,      w,                    value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_ASSUMPTION],                             )
                sd.set_point_value( cursor, point_id, sd.Q_OUTER_LAYER_VELOCITY,   outer_layer_velocity, value_type_id=sd.VT_BOTH_AVERAGES, instrument_class_ids=[sd.IT_PITOT_STATIC_TUBE],                      )

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

conn.commit()
conn.close()
