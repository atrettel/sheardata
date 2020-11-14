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

import sheardata as sd
import sqlite3
import sys

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

with open( "table-all-studies.tex.tmp", "w" ) as f:
    f.write( r"\begin{tabular}{ r | l l r r r }"+"\n" )
    f.write( r"Study & Type & Primary sources & \# series & " )
    f.write( r"\# stations & \# points \\"+"\n" )
    f.write( r"\hline"+"\n" )

    cursor.execute(
    """
    SELECT identifier
    FROM studies
    ORDER BY identifier;
    """
    )
    for result in cursor.fetchall():
        study = result[0]

        cursor.execute(
        """
        SELECT source
        FROM sources
        WHERE study=? AND classification=1
        ORDER BY source COLLATE NOCASE;
        """,
        ( study, )
        )
        primary_sources = []
        for result in cursor.fetchall():
            primary_sources.append( str(result[0]) )

        cursor.execute(
        """
        SELECT study_type
        FROM studies
        WHERE identifier=?;
        """,
        ( study, )
        )
        study_type = str(cursor.fetchone()[0])

        cursor.execute(
        """
        SELECT COUNT(*)
        FROM series
        WHERE study=?;
        """,
        ( study, )
        )
        number_of_series = int(cursor.fetchone()[0])

        cursor.execute(
        """
        SELECT COUNT(*)
        FROM stations
        WHERE study=?;
        """,
        ( study, )
        )
        number_of_stations = int(cursor.fetchone()[0])

        cursor.execute(
        """
        SELECT COUNT(*)
        FROM points
        WHERE study=?;
        """,
        ( study, )
        )
        number_of_points = int(cursor.fetchone()[0])

        line = r"\texttt{"+"{:s}".format(
            sd.make_readable_identifier( study ),
        )+r"} & \texttt{"+"{:s}".format(
            study_type,
        )+r"} & \citet{"

        i = 0
        for primary_source in primary_sources:
            if ( i != 0 ):
                line += ","
            i += 1
            line += primary_source

        line += r"} & "+"{:d} & {:d} & {:d}".format(
            number_of_series,
            number_of_stations,
            number_of_points,
        )+r"\\"+"\n"

        f.write( line )

    f.write( r"\end{tabular}"+"\n" )

conn.commit()
conn.close()
