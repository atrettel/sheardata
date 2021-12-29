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

with open( "list-quantities.tex.tmp", "w" ) as f:
    f.write( r"\begin{itemize}"+"\n" )

    cursor.execute(
    """
    SELECT quantity_id
    FROM quantities
    ORDER BY quantity_id COLLATE NOCASE;
    """
    )
    for result in cursor.fetchall():
        quantity_id = str(result[0])
        quantity_name = sd.quantity_name( cursor, quantity_id )

        line = r"\item \texttt{"+"{:s}".format(
            quantity_id
        )+r"}"+" --- {:s}".format(
            quantity_name,
        )+"\n"
        f.write( line.replace( "_", r"\_" ).replace( "^", r"\string^" ) )

    f.write( r"\end{itemize}"+"\n" )

conn.commit()
conn.close()
