#!/usr/bin/env python3

# Copyright (C) 2020 Andrew Trettel
#
# This file is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This file is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this file.  If not, see <https://www.gnu.org/licenses/>.

import csv
import math
import sqlite3
import sheardata as sd
import sys

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

flow_class   = sd.BOUNDARY_LAYER_FLOW_CLASS
year         = 2010
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.DIRECT_NUMERICAL_SIMULATION_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "JimenezJ+2010+eng+JOUR",  1 )
sd.add_source( cursor, study_identifier, "SilleroJA+2013+eng+JOUR", 1 )
sd.add_source( cursor, study_identifier, "SilleroJA+2014+eng+JOUR", 1 )

conn.commit()
conn.close()
