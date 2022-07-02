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

study_id = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type_id=sd.ST_EXPERIMENT,
)

sd.add_study_source( cursor, study_id, "NikuradseJ+1932+deu+JOUR",      sd.PRIMARY_SOURCE )
sd.add_study_source( cursor, study_id, "NikuradseJ+1933+deu+JOUR",      sd.PRIMARY_SOURCE )
sd.add_study_source( cursor, study_id, "BeattieDRH+1995+eng+CPAPER",  sd.SECONDARY_SOURCE )
sd.add_study_source( cursor, study_id, "BrownlieWR+1981+eng+JOUR",    sd.SECONDARY_SOURCE )
sd.add_study_source( cursor, study_id, "HagerWH+2008+eng+JOUR",       sd.SECONDARY_SOURCE )
sd.add_study_source( cursor, study_id, "LaVioletteM+2017+eng+JOUR",   sd.SECONDARY_SOURCE )
sd.add_study_source( cursor, study_id, "LindgrenER+1965+eng+RPRT",    sd.SECONDARY_SOURCE )
sd.add_study_source( cursor, study_id, "MillerB+1949+eng+JOUR",       sd.SECONDARY_SOURCE )
sd.add_study_source( cursor, study_id, "RobertsonJM+1957+eng+CPAPER", sd.SECONDARY_SOURCE )
sd.add_study_source( cursor, study_id, "RossD+1953+eng+CPAPER",       sd.SECONDARY_SOURCE )

conn.commit()
conn.close()
exit()


conn.commit()
conn.close()
