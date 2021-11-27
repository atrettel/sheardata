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
year         = 1999
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.ST_DIRECT_NUMERICAL_SIMULATION,
)

sd.add_source( cursor, study_identifier, "MoserRD+1999+eng+JOUR", sd.PRIMARY_SOURCE )

# The primary difficulty with this data is that only the friction Reynolds
# number is given.  The rest of the data is dimensionless profiles.  The trick
# is to manipulate some of the basic equations to be in terms of the bulk
# velocity.

# bulk_reynolds_number    = 4.0 * bulk_velocity_plus * friction_reynolds_number
# fanning_friction_factor = 2.0 * ( bulk_velocity_plus )**(-2.0)

conn.commit()
conn.close()
