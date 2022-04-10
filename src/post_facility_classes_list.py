#!/usr/bin/env python3

# Copyright (C) 2022 Andrew Trettel
#
# SPDX-License-Identifier: MIT

import sheardata as sd
import sqlite3
import sys

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

with open( "list-facility-classes.tex.tmp", "w" ) as f:
    f.write( r"\begin{itemize}"+"\n" )

    cursor.execute(
    """
    SELECT facility_class_id, facility_class_name
    FROM facility_classes
    ORDER BY facility_class_id;
    """
    )
    for result in cursor.fetchall():
        f.write(
            r"\item "+"Class {:s} --- {:s}\n".format(
                r"\texttt{"+result[0]+r"}",
                result[1]+"s"
            )
        )

    f.write( r"\end{itemize}"+"\n" )

conn.commit()
conn.close()
