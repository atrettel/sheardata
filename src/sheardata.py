#!/usr/bin/env python3

# Copyright (C) 2020 Andrew Trettel
# 
# This file is licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import math
import sqlite3
from uncertainties import ufloat

EXPERIMENTAL_STUDY_TYPE = "E"
NUMERICAL_STUDY_TYPE    = "N"

def split_float( value ):
    if ( isinstance( value, float ) ):
        sql_value       = value
        sql_uncertainty = None
    else:
        sql_value       = value.n
        sql_uncertainty = value.s
        if ( math.isnan(sql_uncertainty) ):
            sql_uncertainty = None
    return sql_value, sql_uncertainty

def join_float( sql_value, sql_uncertainty=None ):
    uncertainty = float(0.0)
    if ( sql_uncertainty == None ):
        uncertainty = float("nan")
    else:
        uncertainty = float(sql_uncertainty)
    return ufloat( float(sql_value), uncertainty )

def identify_study( flow_class, year, study_number, readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:1s}{:s}{:4d}{:s}{:3d}".format(
        str(flow_class),
        str(separator),
        int(year),
        str(separator),
        int(study_number),
    ).replace(" ","0")

def identify_series( flow_class, year, study_number, series_number, \
                     readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:s}{:s}{:3d}".format(
        identify_study( flow_class, year, study_number, readable=readable, ),
        str(separator),
        int(series_number),
    ).replace(" ","0")

def identify_station( flow_class, year, study_number, series_number, \
                      station_number, readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:s}{:s}{:3d}".format(
        identify_series(
            flow_class, year, study_number, series_number, readable=readable,
        ),
        str(separator),
        int(station_number),
    ).replace(" ","0")

def identify_point( flow_class, year, study_number, series_number, \
                    station_number, point_number, readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:s}{:s}{:4d}".format(
        identify_station(
            flow_class, year, study_number, series_number, station_number, \
            readable=readable,
        ),
        str(separator),
        int(point_number),
    ).replace(" ","0")

def sanitize_identifier( identifier ):
    return identifier.replace("-","")

def add_study( cursor, flow_class, year, study_number, study_type ):
    identifier = identify_study( flow_class, year, study_number )
    cursor.execute(
    """
    INSERT INTO studies( identifier, flow_class, year, study_number, study_type
    ) VALUES( ?, ?, ?, ?, ? );
    """,
    (
        identifier,
        str(flow_class),
        int(year),
        int(study_number),
        str(study_type),
    )
    )

    return identifier

def update_study_description( cursor, identifier, description ):
    cursor.execute(
    """
    UPDATE studies SET description=? WHERE identifier=?
    """,
    (
        description.strip(),
        identifier,
    )
    )

def update_study_provenance( cursor, identifier, provenance ):
    cursor.execute(
    """
    UPDATE studies SET provenance=? WHERE identifier=?
    """,
    (
        provenance.strip(),
        identifier,
    )
    )

def update_study_notes( cursor, identifier, notes ):
    cursor.execute(
    """
    UPDATE studies SET notes=? WHERE identifier=?
    """,
    (
        notes.strip(),
        identifier,
    )
    )

def set_study_value( cursor, study, quantity, value, averaging_system=None, \
                     measurement_technique=None, outlier=False, notes=None ):
    study_value, study_uncertainty = split_float( value )
    cursor.execute(
    """
    INSERT INTO study_values( study, quantity, study_value, study_uncertainty,
    averaging_system, measurement_technique, outlier, notes ) VALUES( ?, ?, ?,
    ?, ?, ?, ?, ? );
    """,
    (
        str(study),
        str(quantity),
        study_value,
        study_uncertainty,
        averaging_system,
        measurement_technique,
        int(outlier),
        notes,
    )
    )
