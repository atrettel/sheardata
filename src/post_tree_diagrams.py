#!/usr/bin/env python3

# Copyright (C) 2020-2021 Andrew Trettel
#
# SPDX-License-Identifier: MIT

import sqlite3
import sys

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

with open( "figure-flow-classification-tree-diagram.gv", "w" ) as f:
    f.write( 'digraph taxonomy {\n' )
    f.write( 'concentrate=true;\n' )
    f.write( 'rankdir=TB;\n' )
    f.write( 'ranksep="0.25";\n' )
    f.write( 'node [shape=circle, fixedsize=true, width="0.5", height="0.5", margin="0.25"];\n' )

    cursor.execute(
    """
    SELECT identifier
    FROM flow_classes
    ORDER BY identifier;
    """
    )
    for result in cursor.fetchall():
        f.write( '"{:s}" [texlbl="{:s}"]'.format(
            result[0],
            r"\texttt{"+result[0]+r"}",
        )+";\n" )
    
    cursor.execute(
    """
    SELECT parent, identifier
    FROM flow_classes
    WHERE parent IS NOT NULL
    ORDER BY parent;
    """
    )
    for result in cursor.fetchall():
        f.write( '"{:s}" -> "{:s}"'.format(
            result[0],
            result[1],
        )+"\n" )

    f.write( '{rank = same; edge[style=invis]; F -> E -> I; rankdir=LR;}\n' )
    f.write( '{rank = same; edge[style=invis]; J -> M -> W; rankdir=LR;}\n' )
    f.write( '{rank = same; edge[style=invis]; B -> K; rankdir=LR;}\n' )
    f.write( '{rank = same; edge[style=invis]; D -> R; rankdir=LR;}\n' )

    f.write( '}\n' )

conn.commit()
conn.close()
