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

import math
import sqlite3
from uncertainties import ufloat

# Averaging systems
DENSITY_WEIGHTED_AVERAGING_SYSTEM = "DW"
UNWEIGHTED_AVERAGING_SYSTEM       = "UW"

# Coordinate systems
CYLINDRICAL_COORDINATE_SYSTEM = "XRT"
RECTANGULAR_COORDINATE_SYSTEM = "XYZ"

# Flow classes
BOUNDARY_LAYER_FLOW_CLASS  = "B"
WALL_BOUNDED_FLOW_CLASS    = "C"
DUCT_FLOW_CLASS            = "D"
EXTERNAL_FLOW_CLASS        = "E"
FREE_SHEAR_FLOW_CLASS      = "F"
ISOTROPIC_FLOW_CLASS       = "G"
HOMOGENEOUS_FLOW_CLASS     = "H"
INTERNAL_FLOW_CLASS        = "I"
FREE_JET_FLOW_CLASS        = "J"
WALL_JET_FLOW_CLASS        = "K"
MIXING_LAYER_FLOW_CLASS    = "M"
INHOMOGENEOUS_FLOW_CLASS   = "N"
RELATIVE_MOTION_FLOW_CLASS = "R"
SHEAR_LAYER_FLOW_CLASS     = "S"
UNCLASSIFIED_FLOW_CLASS    = "U"
WAKE_FLOW_CLASS            = "W"

# Fluids
DRY_AIR_FLUID = "dry_air"
WATER_FLUID   = "water"
STEAM         = "steam"

# Geometries
ELLIPTICAL_GEOMETRY  = "E"
RECTANGULAR_GEOMETRY = "R"

# Study types
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

def fetch_float( cursor ):
    result = cursor.fetchone()
    return join_float( result[0], result[1] )

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
    INSERT INTO studies( identifier, flow_class, year, study_number,
    study_type) VALUES( ?, ?, ?, ?, ? );
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

def get_study_value( cursor, study, quantity, averaging_system=None ):
    cursor.execute(
    """
    SELECT study_value, study_uncertainty FROM study_values WHERE study=? AND
    quantity=? AND averaging_system=?;
    """,
    (
        str(study),
        str(quantity),
        averaging_system,
    )
    )
    return fetch_float( cursor )

def add_source( cursor, study, source, classification ):
    cursor.execute(
    """
    INSERT INTO sources( study, source, classification ) VALUES( ?, ?, ? );
    """,
    (
        str(study),
        str(source),
        int(classification),
    )
    )

def add_series( cursor, flow_class, year, study_number, series_number, \
                number_of_dimensions, coordinate_system, working_fluid ):
    identifier = identify_series(
        flow_class,
        year,
        study_number,
        series_number,
    )
    cursor.execute(
    """
    INSERT INTO series( identifier, series_number, number_of_dimensions,
    coordinate_system, working_fluid ) VALUES( ?, ?, ?, ?, ? );
    """,
    (
        identifier,
        int(series_number),
        int(number_of_dimensions),
        str(coordinate_system),
        str(working_fluid),
    )
    )
    return identifier

def update_series_geometry( cursor, identifier, geometry ):
    cursor.execute(
    """
    UPDATE series SET geometry=? WHERE identifier=?
    """,
    (
        str(geometry),
        identifier,
    )
    )

def update_series_number_of_sides( cursor, identifier, number_of_sides ):
    cursor.execute(
    """
    UPDATE series SET number_of_sides=? WHERE identifier=?
    """,
    (
        int(number_of_sides),
        identifier,
    )
    )

def update_series_description( cursor, identifier, description ):
    cursor.execute(
    """
    UPDATE series SET description=? WHERE identifier=?
    """,
    (
        description.strip(),
        identifier,
    )
    )

def update_series_notes( cursor, identifier, notes ):
    cursor.execute(
    """
    UPDATE series SET notes=? WHERE identifier=?
    """,
    (
        notes.strip(),
        identifier,
    )
    )

def set_series_value( cursor, series, quantity, value, averaging_system=None, \
                     measurement_technique=None, outlier=False, notes=None ):
    series_value, series_uncertainty = split_float( value )
    cursor.execute(
    """
    INSERT INTO series_values( series, quantity, series_value,
    series_uncertainty, averaging_system, measurement_technique, outlier, notes
    ) VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        str(series),
        str(quantity),
        series_value,
        series_uncertainty,
        averaging_system,
        measurement_technique,
        int(outlier),
        notes,
    )
    )

def add_station( cursor, flow_class, year, study_number, series_number, \
                station_number ):
    identifier = identify_station(
        flow_class,
        year,
        study_number,
        series_number,
        station_number,
    )
    cursor.execute(
    """
    INSERT INTO stations( identifier, station_number ) VALUES( ?, ? );
    """,
    (
        identifier,
        int(station_number),
    )
    )
    return identifier

def add_point( cursor, flow_class, year, study_number, series_number, \
                station_number, point_number, point_label=None ):
    identifier = identify_point(
        flow_class,
        year,
        study_number,
        series_number,
        station_number,
        point_number,
    )
    cursor.execute(
    """
    INSERT INTO points( identifier, point_number, point_label ) VALUES( ?, ?,
    ?);
    """,
    (
        identifier,
        int(point_number),
        str(point_label),
    )
    )
    return identifier
