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

flow_class   = sd.BOUNDARY_DRIVEN_FLOW_CLASS
year         = 1956
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "ReichardtH+1956+deu+JOUR", sd.PRIMARY_SOURCE )
sd.add_source( cursor, study_identifier, "ReichardtH+1959+deu+RPRT", sd.PRIMARY_SOURCE )

conn.commit()
conn.close()
