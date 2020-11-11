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

import sqlite3
import sys

conn = sqlite3.connect( sys.argv[1] )
cursor =  conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

with open( "figure-taxonomy.gv", "w" ) as f:
    f.write( 'digraph taxonomy {\n' )
    f.write( 'concentrate=true\n' )
    f.write( 'rankdir=LR\n' )
    f.write( 'ranksep="0.25"\n' )
    f.write( 'node [shape=circle, fixedsize=true, width="0.5", height="0.5", margin="0.25"]\n' )

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
        )+"\n" )
    
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

    f.write( '}\n' )

with open( "text-flow-classes.tex.tmp", "w" ) as f:
    f.write( r"\begin{itemize}"+"\n" )

    cursor.execute(
    """
    SELECT identifier, class_name
    FROM flow_classes
    ORDER BY identifier;
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
