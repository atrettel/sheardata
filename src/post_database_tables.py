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

with open( "text-quantities-table.tex.tmp", "w" ) as f:
    f.write( r"\begin{itemize}"+"\n" )

    cursor.execute(
    """
    SELECT identifier, quantity_name
    FROM quantities
    ORDER BY identifier COLLATE NOCASE;
    """
    )
    for result in cursor.fetchall():
        line = r"\item \texttt{"+"{:s}".format(
            str(result[0]),
        )+r"}"+" --- {:s}".format(
            str(result[1]),
        )+"\n"
        f.write( line.replace( "_", r"\_" ) )

    f.write( r"\end{itemize}"+"\n" )

conn.commit()
conn.close()
