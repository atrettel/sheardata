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

with open( "list-notes.tex.tmp", "w" ) as f:
    f.write( r"\begin{itemize}"+"\n" )

    cursor.execute(
    """
    SELECT note_id, note_contents
    FROM notes
    ORDER BY note_id;
    """
    )
    for result in cursor.fetchall():
        note_id  = int(result[0])
        contents = str(result[1])
        line = r"\item[{:d}] ".format(note_id)+contents+"\n"
        f.write( line )

    f.write( r"\end{itemize}"+"\n" )

conn.commit()
conn.close()
