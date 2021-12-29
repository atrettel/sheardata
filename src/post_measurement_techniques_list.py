#!/usr/bin/env python3

# Copyright (C) 2020-2021 Andrew Trettel
#
# SPDX-License-Identifier: MIT

import sheardata as sd
import sqlite3
import sys

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

def create_measurement_techniques_tree( parent ):
    cursor.execute(
    """
    SELECT meastech_id, meastech_name
    FROM measurement_techniques
    WHERE meastech_parent_id=?
    ORDER BY meastech_name COLLATE NOCASE;
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
        tree += create_measurement_techniques_tree( child )
    if ( len(results) != 0 ):
        tree += r"\end{itemize}"+"\n"
    return tree

with open( "list-measurement-techniques.tex.tmp", "w" ) as f:
    f.write( create_measurement_techniques_tree( sd.MT_ROOT ) )

conn.commit()
conn.close()
