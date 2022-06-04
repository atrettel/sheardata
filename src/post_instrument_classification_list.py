#!/usr/bin/env python3

# Copyright (C) 2020-2022 Andrew Trettel
#
# SPDX-License-Identifier: MIT

import sheardata as sd
import sqlite3
import sys

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

def create_instruments_tree( parent ):
    cursor.execute(
    """
    SELECT instrument_class_id, instrument_class_name
    FROM instrument_classes
    WHERE instrument_class_parent_id=?
    ORDER BY instrument_class_name COLLATE NOCASE;
    """,
    ( parent, )
    )
    tree = ""
    results = cursor.fetchall()
    if ( len(results) != 0 ):
        tree += r"\begin{itemize}"+"\n"
    for result in results:
        child = str(result[0])
        name  = str(result[1])
        tree += r"\item[$\bullet$] "+"{:s} ({:s})\n".format(
            result[1],
            r"\texttt{"+result[0]+r"}",
        )
        tree += create_instruments_tree( child )
    if ( len(results) != 0 ):
        tree += r"\end{itemize}"+"\n"
    return tree

with open( "list-instrument-classification.tex.tmp", "w" ) as f:
    f.write( create_instruments_tree( sd.IT_ROOT ) )

conn.commit()
conn.close()
