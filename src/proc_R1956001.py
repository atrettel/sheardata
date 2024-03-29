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

flow_class   = sd.FC_BOUNDARY_DRIVEN_FLOW
year         = 1956
study_number = 1

study_id = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type_id=sd.ST_EXPERIMENT,
)

sd.add_study_source( cursor, study_id, "ReichardtH+1956+deu+JOUR", sd.PRIMARY_SOURCE )
sd.add_study_source( cursor, study_id, "ReichardtH+1959+deu+RPRT", sd.PRIMARY_SOURCE )

conn.commit()
conn.close()
exit()

conn.commit()
conn.close()
