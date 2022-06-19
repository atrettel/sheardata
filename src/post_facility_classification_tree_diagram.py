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

with open( "figure-facility-classification-tree-diagram.gv", "w" ) as f:
    f.write( 'digraph taxonomy {\n' )
    f.write( 'concentrate=true;\n' )
    f.write( 'rankdir=TB;\n' )
    f.write( 'ranksep="0.25";\n' )
    f.write( 'node [shape=circle, fixedsize=true, width="0.5", height="0.5", margin="0.25"];\n' )

    cursor.execute(
    """
    SELECT facility_class_id
    FROM facility_classes
    ORDER BY facility_class_id;
    """
    )
    for result in cursor.fetchall():
        f.write( '"{:s}" [texlbl="{:s}"]'.format(
            result[0],
            r"\texttt{"+result[0]+r"}",
        )+";\n" )
    
    cursor.execute(
    """
    SELECT facility_class_ancestor_id, facility_class_descendant_id
    FROM facility_class_paths
    WHERE facility_class_path_length=1
    ORDER BY facility_class_ancestor_id;
    """
    )
    for result in cursor.fetchall():
        f.write( '"{:s}" -> "{:s}"'.format(
            result[0],
            result[1],
        )+"\n" )

    f.write( '}\n' )

conn.commit()
conn.close()
