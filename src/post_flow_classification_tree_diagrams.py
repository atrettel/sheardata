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

with open( "figure-flow-classification-tree-diagram.gv", "w" ) as f:
    f.write( 'digraph taxonomy {\n' )
    f.write( 'concentrate=true;\n' )
    f.write( 'rankdir=TB;\n' )
    f.write( 'ranksep="0.25";\n' )
    f.write( 'node [shape=circle, fixedsize=true, width="0.5", height="0.5", margin="0.25"];\n' )

    cursor.execute(
    """
    SELECT flow_class_id
    FROM flow_classes
    ORDER BY flow_class_id;
    """
    )
    for result in cursor.fetchall():
        f.write( '"{:s}" [texlbl="{:s}"]'.format(
            result[0],
            r"\texttt{"+result[0]+r"}",
        )+";\n" )
    
    cursor.execute(
    """
    SELECT flow_class_parent_id, flow_class_id
    FROM flow_classes
    WHERE flow_class_parent_id IS NOT NULL
    ORDER BY flow_class_parent_id;
    """
    )
    for result in cursor.fetchall():
        f.write( '"{:s}" -> "{:s}"'.format(
            result[0],
            result[1],
        )+"\n" )

    f.write( '{rank = same; edge[style=invis]; '+'{:s} -> {:s} -> {:s}'.format(
        sd.FC_FREE_SHEAR_FLOW,
        sd.FC_EXTERNAL_FLOW,
        sd.FC_INTERNAL_FLOW,
    )+'; rankdir=LR;}\n' )

    f.write( '{rank = same; edge[style=invis]; '+'{:s} -> {:s} -> {:s}'.format(
        sd.FC_FREE_JET,
        sd.FC_MIXING_LAYER,
        sd.FC_WAKE,
    )+'; rankdir=LR;}\n' )

    f.write( '{rank = same; edge[style=invis]; '+'{:s} -> {:s}'.format(
        sd.FC_BOUNDARY_LAYER,
        sd.FC_WALL_JET,
    )+'; rankdir=LR;}\n' )

    f.write( '{rank = same; edge[style=invis]; '+'{:s} -> {:s}'.format(
        sd.FC_DUCT_FLOW,
        sd.FC_BOUNDARY_DRIVEN_FLOW,
    )+'; rankdir=LR;}\n' )

    f.write( '}\n' )

conn.commit()
conn.close()
