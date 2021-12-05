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

with open( "list-flow-classes.tex.tmp", "w" ) as f:
    f.write( r"\begin{itemize}"+"\n" )

    cursor.execute(
    """
    SELECT flow_class_id, flow_class_name
    FROM flow_classes
    ORDER BY flow_class_id;
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

with open( "list-quantities.tex.tmp", "w" ) as f:
    f.write( r"\begin{itemize}"+"\n" )

    cursor.execute(
    """
    SELECT quantity_id, quantity_name
    FROM quantities
    ORDER BY quantity_id COLLATE NOCASE;
    """
    )
    for result in cursor.fetchall():
        line = r"\item \texttt{"+"{:s}".format(
            str(result[0]),
        )+r"}"+" --- {:s}".format(
            str(result[1]),
        )+"\n"
        f.write( line.replace( "_", r"\_" ).replace( "^", r"\string^" ) )

    f.write( r"\end{itemize}"+"\n" )

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
