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
year         = 2010
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type_id=sd.ST_DIRECT_NUMERICAL_SIMULATION,
)

sd.add_study_source( cursor, study_identifier, "JimenezJ+2010+eng+JOUR",  sd.PRIMARY_SOURCE )
sd.add_study_source( cursor, study_identifier, "SilleroJA+2013+eng+JOUR", sd.PRIMARY_SOURCE )
sd.add_study_source( cursor, study_identifier, "SilleroJA+2014+eng+JOUR", sd.PRIMARY_SOURCE )

conn.commit()
conn.close()
