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

flow_class   = sd.FC_BOUNDARY_LAYER
year         = 1940
study_number = 1

study_id = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type_id=sd.ST_EXPERIMENT,
)

sd.add_study_source( cursor, study_id, "SchultzGrunowF+1940+deu+JOUR", sd.PRIMARY_SOURCE )

reynolds_number_typo_note = sd.add_note(
    cursor,
    "../data/{:s}/note_reynolds_number_typo.tex".format( study_id ),
)

station_1_outlier_note = sd.add_note(
    cursor,
    "../data/{:s}/note_station_1_outlier.tex".format( study_id ),
)

velocity_method_note = sd.add_note(
    cursor,
    "../data/{:s}/note_velocity_method.tex".format( study_id ),
)

conn.commit()
conn.close()
