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

total_number_of_series   = 0
total_number_of_stations = 0
total_number_of_points   = 0

with open( "table-all-studies.tex.tmp", "w" ) as f:
    f.write( r"\begin{tabular}{ r | l l r r r }"+"\n" )
    f.write( r"Study & Type & Primary sources & \# series & " )
    f.write( r"\# stations & \# points \\"+"\n" )
    f.write( r"\hline"+"\n" )

    cursor.execute(
    """
    SELECT study_id
    FROM studies
    ORDER BY study_id;
    """
    )
    for result in cursor.fetchall():
        study = result[0]

        cursor.execute(
        """
        SELECT citation_key
        FROM study_sources
        WHERE study_id=? AND classification=?
        ORDER BY citation_key COLLATE NOCASE;
        """,
        (
            study,
            sd.PRIMARY_SOURCE,
        )
        )
        primary_sources = []
        for result in cursor.fetchall():
            primary_sources.append( str(result[0]) )

        cursor.execute(
        """
        SELECT study_type_id
        FROM studies
        WHERE study_id=?;
        """,
        ( study, )
        )
        study_type = str(cursor.fetchone()[0])

        cursor.execute(
        """
        SELECT COUNT(*)
        FROM series
        WHERE study_id=?;
        """,
        ( study, )
        )
        number_of_series = int(cursor.fetchone()[0])

        cursor.execute(
        """
        SELECT COUNT(*)
        FROM stations
        WHERE study_id=?;
        """,
        ( study, )
        )
        number_of_stations = int(cursor.fetchone()[0])

        cursor.execute(
        """
        SELECT COUNT(*)
        FROM points
        WHERE study_id=?;
        """,
        ( study, )
        )
        number_of_points = int(cursor.fetchone()[0])

        line = r"\texttt{"+"{:s}".format(
            sd.make_readable_identifier( study ),
        )+r"} & \texttt{"+"{:s}".format(
            study_type,
        )+r"} & \parbox[t]{0.4\textwidth}{\citet{"

        i = 0
        for primary_source in primary_sources:
            if ( i != 0 ):
                line += ","
            i += 1
            line += primary_source

        line += r"}} & "+"{:d} & {:d} & {:d}".format(
            number_of_series,
            number_of_stations,
            number_of_points,
        )+r"\\"+"\n"

        f.write( line )

        total_number_of_series   += number_of_series
        total_number_of_stations += number_of_stations
        total_number_of_points   += number_of_points

    f.write( r"\hline"+"\n" )

    f.write( r"Totals & & & "+"{:d}".format(
        total_number_of_series,
    )+r" & "+"{:d}".format(
        total_number_of_stations,
    )+r" & "+"{:d}".format(
        total_number_of_points,
    )+r"\\"+"\n" )

    f.write( r"\end{tabular}"+"\n" )

conn.commit()
conn.close()
