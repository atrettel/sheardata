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
year         = 1932
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.ST_EXPERIMENT,
)

sd.add_source( cursor, study_identifier, "NikuradseJ+1932+deu+JOUR",      sd.PRIMARY_SOURCE )
sd.add_source( cursor, study_identifier, "NikuradseJ+1933+deu+JOUR",      sd.PRIMARY_SOURCE )
sd.add_source( cursor, study_identifier, "RobertsonJM+1957+eng+CPAPER", sd.SECONDARY_SOURCE )
sd.add_source( cursor, study_identifier, "LindgrenER+1965+eng+RPRT",    sd.SECONDARY_SOURCE )
sd.add_source( cursor, study_identifier, "BeattieDRH+1995+eng+CPAPER",  sd.SECONDARY_SOURCE )
sd.add_source( cursor, study_identifier, "HagerWH+2008+eng+JOUR",       sd.SECONDARY_SOURCE )
sd.add_source( cursor, study_identifier, "LaVioletteM+2017+eng+JOUR",   sd.SECONDARY_SOURCE )

conn.commit()
conn.close()
