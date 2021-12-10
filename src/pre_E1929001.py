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

flow_class   = sd.FC_EXTERNAL_FLOW
year         = 1929
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.ST_EXPERIMENT,
)

sd.add_study_source( cursor, study_identifier, "StantonTE+1929+eng+RPRT", sd.PRIMARY_SOURCE )

conn.commit()
conn.close()
