#!/usr/bin/env python3

# Copyright (C) 2021 Andrew Trettel
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

flow_class   = sd.BOUNDARY_LAYER_FLOW_CLASS
year         = 1914
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
    identifiers={sd.C_CH_1969 : "1600"},
)

sd.add_source( cursor, study_identifier, "RiabouchinskyD+1914+fra+JOUR",   sd.PRIMARY_SOURCE )
sd.add_source( cursor, study_identifier, "ColesDE+1969+eng+BOOK",        sd.SECONDARY_SOURCE )

station_4_velocity_note = sd.add_note(
    cursor,
    "../data/{:s}/note_station_4_velocity.tex".format( study_identifier ),
)


conn.commit()
conn.close()
