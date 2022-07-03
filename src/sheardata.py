#!/usr/bin/env python3

# Copyright (C) 2020-2022 Andrew Trettel
#
# SPDX-License-Identifier: MIT

import math
import numpy as np
import sqlite3
from uncertainties import ufloat
import sys

# Physical constants
ABSOLUTE_ZERO                       =    273.15
STANDARD_ATMOSPHERIC_PRESSURE       = 101325.0
STANDARD_GRAVITATIONAL_ACCELERATION =      9.80665

AVOGADRO_CONSTANT  = 6.02214076e+23
BOLTZMANN_CONSTANT = 1.38064900e-23
MOLAR_GAS_CONSTANT = AVOGADRO_CONSTANT * BOLTZMANN_CONSTANT

# Unit conversion factors
INCHES_PER_FOOT         = 12.0
KILOGRAM_PER_POUND_MASS =  0.45359237
METERS_PER_INCH         =  2.54e-2
SECONDS_PER_MINUTE      = 60.0

METERS_PER_FOOT             = METERS_PER_INCH * INCHES_PER_FOOT
NEWTONS_PER_POUND_FORCE     = 1.0 * KILOGRAM_PER_POUND_MASS * STANDARD_GRAVITATIONAL_ACCELERATION

PASCALS_PER_INCH_OF_MERCURY = 3376.85
PASCALS_PER_METER_OF_WATER  = 1000.0 * STANDARD_GRAVITATIONAL_ACCELERATION
PASCALS_PER_INCH_OF_WATER   = PASCALS_PER_METER_OF_WATER * METERS_PER_INCH
PASCALS_PER_PSI             = NEWTONS_PER_POUND_FORCE / METERS_PER_INCH**2.0
PASCALS_PER_BAR             = 100000.0

# Uncertainties
UNKNOWN_UNCERTAINTY = None

# Value types
VT_ANY_AVERAGE              = "A"
VT_BOTH_AVERAGES            = "B"
VT_DENSITY_WEIGHTED_AVERAGE = "D"
VT_MAXIMUM_VALUE            = "N"
VT_MINIMUM_VALUE            = "M"
VT_UNAVERAGED_VALUE         = "V"
VT_UNWEIGHTED_AVERAGE       = "U"

# Facility classes
FT_FACILITY                   = "F"

FT_EXPERIMENTAL_FACILITY      = "X"
FT_TUNNEL                     = "T"
FT_WIND_TUNNEL                = "W"
FT_OPEN_CIRCUIT_WIND_TUNNEL   = "O"
FT_CLOSED_CIRCUIT_WIND_TUNNEL = "C"
FT_BLOWDOWN_WIND_TUNNEL       = "B"
FT_LUDWIEG_TUBE               = "L"
FT_SHOCK_TUBE                 = "S"
FT_WATER_TUNNEL               = "H"
FT_RANGE                      = "R"
FT_TOWING_TANK                = "M"

FT_NUMERICAL_FACILITY         = "N"
FT_FINITE_DIFFERENCE_METHOD   = "D"
FT_FINITE_ELEMENT_METHOD      = "E"
FT_FINITE_VOLUME_METHOD       = "V"
FT_SPECTRAL_METHOD            = "Z"

# Flow classes
FC_BOUNDARY_LAYER       = "B"
FC_WALL_BOUNDED_FLOW    = "C"
FC_DUCT_FLOW            = "D"
FC_EXTERNAL_FLOW        = "E"
FC_FREE_SHEAR_FLOW      = "F"
FC_ISOTROPIC_FLOW       = "G"
FC_HOMOGENEOUS_FLOW     = "H"
FC_INTERNAL_FLOW        = "I"
FC_FREE_JET             = "J"
FC_WALL_JET             = "K"
FC_MIXING_LAYER         = "M"
FC_INHOMOGENEOUS_FLOW   = "N"
FC_BOUNDARY_DRIVEN_FLOW = "R"
FC_SHEAR_FLOW           = "S"
FC_UNCLASSIFIED_FLOW    = "U"
FC_WAKE                 = "W"

# Flow regimes
FR_LAMINAR      = "L"
FR_TRANSITIONAL = "D"
FR_TURBULENT    = "T"

# Phases
#
# The multiphase global can be used for searching in Python functions, but it
# MUST only be used for the mixture fluid in the fluids table.
PH_GAS        = "g"
PH_LIQUID     = "l"
PH_SOLID      = "s"
PH_MULTIPHASE = "m"

# Fluids
F_MIXTURE     = "_mixture"
F_GASEOUS_AIR = "_gaseous_air"
F_LIQUID_AIR  = "_liquid_air"
F_GASEOUS_ARGON             = "Ar(g)"
F_GASEOUS_CARBON_DIOXIDE    = "CO2(g)"
F_GASEOUS_DIATOMIC_HYDROGEN = "H2(g)"
F_GASEOUS_DIATOMIC_NITROGEN = "N2(g)"
F_GASEOUS_DIATOMIC_OXYGEN   = "O2(g)"
F_GASEOUS_HELIUM            = "He(g)"
F_GASEOUS_KRYPTON           = "Kr(g)"
F_GASEOUS_METHANE           = "CH4(g)"
F_GASEOUS_NEON              = "Ne(g)"
F_GASEOUS_NITROGEN_DIOXIDE  = "NO2(g)"
F_GASEOUS_NITROUS_OXIDE     = "N2O(g)"
F_GASEOUS_OZONE             = "O3(g)"
F_GASEOUS_XENON             = "Xe(g)"
F_LIQUID_WATER              = "H2O(l)"
F_GASEOUS_WATER             = "H2O(g)"

# Classes for instruments and methods (and other sources of information)
IC_APPROXIMATION                            = "APP"
IC_ASSUMPTION                               = "ASM"
IC_CALCULATION                              = "CLC"
IC_CLAIM                                    = "CLM"
IC_CLAUSER_METHOD                           = "TCC"
IC_CONSTANT_CURRENT_HOT_WIRE_ANEMOMETER     = "HWC"
IC_CONSTANT_TEMPERATURE_HOT_WIRE_ANEMOMETER = "HWT"
IC_DIFFERENTIAL_PRESSURE_METHOD             = "PTA"
IC_DIRECT_INJECTION_METHOD                  = "DIJ"
IC_FLOATING_ELEMENT_BALANCE                 = "FEB"
IC_FLOWMETER                                = "FQM"
IC_HOT_WIRE_ANEMOMETER                      = "HWA"
IC_IMPACT_TUBE                              = "PTI"
IC_INDEX_OF_REFRACTION_METHOD               = "ORI"
IC_LASER_DOPPLER_ANEMOMETER                 = "LDA"
IC_MACH_ZEHNDER_INTERFEROMETER              = "MZI"
IC_MOMENTUM_BALANCE                         = "TMB"
IC_OBSERVATION                              = "OBS"
IC_OPTICAL_SYSTEM                           = "OPT"
IC_PARTICLE_IMAGE_VELOCIMETER               = "PIV"
IC_PITOT_STATIC_TUBE                        = "PST"
IC_PRESTON_TUBE                             = "TPT"
IC_REASONING                                = "RSN"
IC_INSTRUMENT                               = "INS"
IC_SCHLIEREN_SYSTEM                         = "SCH"
IC_SHADOWGRAPH_SYSTEM                       = "SHD"
IC_SIMULATION                               = "SIM"
IC_STANTON_TUBE                             = "TST"
IC_THERMAL_ANEMOMETER                       = "TAN"
IC_VELOCITY_PROFILE_METHOD                  = "TVP"
IC_VISCOUS_SUBLAYER_SLOPE_METHOD            = "TVS"
IC_WALL_SHEAR_STRESS_METHOD                 = "TWL"
IC_WEIGHING_METHOD                          = "QWM"

# Model classes
MC_MODEL                                = "ML"
MC_INTERIOR_MODEL                       = "IM"
MC_INTERIOR_CONSTANT_CROSS_SECTION      = "IC"
MC_INTERIOR_POLYGONAL_CROSS_SECTION     = "IP"
MC_INTERIOR_RECTANGULAR_CROSS_SECTION   = "IR"
MC_INTERIOR_ELLIPTICAL_CROSS_SECTION    = "IE"
MC_INTERIOR_VARIABLE_CROSS_SECTION      = "IV"
MC_EXTERIOR_MODEL                       = "XM"
MC_EXTERIOR_BODY                        = "BD"
MC_EXTERIOR_ELLIPSOID                   = "EL"
MC_EXTERIOR_ELLIPTIC_CONE               = "EC"
MC_EXTERIOR_WING                        = "WG"
MC_EXTERIOR_CONSTANT_CROSS_SECTION_WING = "WC"
MC_EXTERIOR_PLATE                       = "PL",
MC_EXTERIOR_WEDGE                       = "WD"
MC_EXTERIOR_CYLINDER                    = "CY"
MC_EXTERIOR_DIAMOND_WING                = "DW"
MC_EXTERIOR_VARIABLE_CROSS_SECTION_WING = "WV"

# Point labels
PL_CENTER_LINE = "C"
PL_EDGE        = "E"
PL_WALL        = "W"

# These point labels are only used to get data.  They are not used inside the
# database itself.  They distinguish between different situations where there
# might be multiple walls or edges, with lower having lower point number and
# upper having the higher point number.  See the method locate_labeled_point()
# for the implementation.
PL_LOWER_EDGE = "LE"
PL_LOWER_WALL = "LW"
PL_UPPER_EDGE = "UE"
PL_UPPER_WALL = "UW"

PL_EDGES = [ PL_LOWER_EDGE, PL_UPPER_EDGE ]
PL_WALLS = [ PL_LOWER_WALL, PL_UPPER_WALL ]

PL_LOWER = [ PL_LOWER_EDGE, PL_LOWER_WALL ]
PL_UPPER = [ PL_UPPER_EDGE, PL_UPPER_WALL ]

PL_LOWER_UPPER = [ PL_LOWER_EDGE, PL_LOWER_WALL,
                   PL_UPPER_EDGE, PL_UPPER_WALL, ]

# Study types
ST_DIRECT_NUMERICAL_SIMULATION = "DNS"
ST_EXPERIMENT                  = "EXP"
ST_LARGE_EDDY_SIMULATION       = "LES"

# Compilations
C_SELF         = 0 # Originator
C_CH_1969      = 1 # Coles and Hirst
C_BE_1973      = 2 # Birch and Eggers
C_FF_1977      = 3 # Fernholz and Finley
C_ERCOFTAC     = 4 # ERCOFTAC Classic Collection
C_AGARD_AR_345 = 5 # AGARD-AR-345 (Test cases for LES)

# Source classifications
PRIMARY_SOURCE   = 1
SECONDARY_SOURCE = 2
TERTIARY_SOURCE  = 3

def split_float( value ):
    if ( isinstance( value, float ) ):
        sql_value       = value
        sql_uncertainty = UNKNOWN_UNCERTAINTY
    else:
        sql_value       = value.n
        sql_uncertainty = value.s
        if ( math.isnan(sql_uncertainty) ):
            sql_uncertainty = UNKNOWN_UNCERTAINTY
    return sql_value, sql_uncertainty

def sdfloat( sql_value, sql_uncertainty=UNKNOWN_UNCERTAINTY ):
    uncertainty = float(0.0)
    if ( sql_uncertainty == UNKNOWN_UNCERTAINTY ):
        uncertainty = float("nan")
    else:
        uncertainty = float(sql_uncertainty)
    return ufloat( float(sql_value), uncertainty )

def sdfloat_value( value ):
    value, uncertainty = split_float(value)
    return value

def sdfloat_uncertainty( value ):
    value, uncertainty = split_float(value)
    return uncertainty

def fetch_float( cursor ):
    result = cursor.fetchone()
    return sdfloat( result[0], result[1] )

def uniform_distribution_sdfloat( min_value, max_value ):
    value = 0.5 * ( min_value + max_value )
    uncertainty = ( max_value - min_value ) / 12.0**0.5
    return sdfloat( value, uncertainty )

def uniform_distribution_sdfloat_magnitude( value, uncertainty_magnitude ):
    return uniform_distribution_sdfloat( value - uncertainty_magnitude,
                                         value + uncertainty_magnitude )

def uniform_distribution_sdfloat_percent( value, uncertainty_percent ):
    return uniform_distribution_sdfloat_magnitude( value, value * uncertainty_percent / 100.0 )

def pick_any_average_value_type( value_type_ids ):
    assert( len(value_type_ids) != 0 )
    if ( len(value_type_ids) == 1 ):
        return value_type_ids[0]
    else:
        # Prefer density-weighted averages over unweighted averages.
        if ( VT_DENSITY_WEIGHTED_AVERAGE in value_type_ids ):
            return VT_DENSITY_WEIGHTED_AVERAGE
        elif ( VT_UNWEIGHTED_AVERAGE in value_type_ids ):
            return VT_UNWEIGHTED_AVERAGE
        else:
            return value_type_ids[0]

def identify_study( flow_class_id, year, study_number, readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:1s}{:s}{:4d}{:s}{:3d}".format(
        str(flow_class_id),
        str(separator),
        int(year),
        str(separator),
        int(study_number),
    ).replace(" ","0")

def identify_series( flow_class_id, year, study_number, series_number, \
                     readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:s}{:s}{:3d}".format(
        identify_study( flow_class_id, year, study_number, readable=readable, ),
        str(separator),
        int(series_number),
    ).replace(" ","0")

def identify_station( flow_class_id, year, study_number, series_number, \
                      station_number, readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:s}{:s}{:3d}".format(
        identify_series(
            flow_class_id, year, study_number, series_number, readable=readable,
        ),
        str(separator),
        int(station_number),
    ).replace(" ","0")

def identify_point( flow_class_id, year, study_number, series_number, \
                    station_number, point_number, readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:s}{:s}{:4d}".format(
        identify_station(
            flow_class_id, year, study_number, series_number, station_number, \
            readable=readable,
        ),
        str(separator),
        int(point_number),
    ).replace(" ","0")

def sanitize_identifier( identifier ):
    return identifier.replace("-","")

def make_readable_identifier( identifier ):
    sanitized_identifier = sanitize_identifier( identifier )
    readable_identifier = sanitized_identifier[0:1] \
                        + "-"                       \
                        + sanitized_identifier[1:5] \
                        + "-"                       \
                        + sanitized_identifier[5:8]
    if ( len(sanitized_identifier) > 8 ):
        readable_identifier += "-" + sanitized_identifier[8:11]
    if ( len(sanitized_identifier) > 11 ):
        readable_identifier += "-" + sanitized_identifier[11:14]
    if ( len(sanitized_identifier) > 14 ):
        readable_identifier += "-" + sanitized_identifier[14:18]
    return readable_identifier

def truncate_to_study_id( identifier ):
    sanitized_identifier = sanitize_identifier( identifier )
    return sanitized_identifier[0:8]

def truncate_to_series_id( identifier ):
    sanitized_identifier = sanitize_identifier( identifier )
    return sanitized_identifier[0:11]

def truncate_to_station_id( identifier ):
    sanitized_identifier = sanitize_identifier( identifier )
    return sanitized_identifier[0:14]

def add_study( cursor, flow_class_id, year, study_number, study_type_id,
               outlier=False, note_ids=[], study_external_ids={}, ):
    study_id = identify_study( flow_class_id, year, study_number )
    cursor.execute(
    """
    INSERT INTO studies( study_id, flow_class_id, year, study_number,
                         study_type_id, outlier )
    VALUES( ?, ?, ?, ?, ?, ? );
    """,
    (
        study_id,
        str(flow_class_id),
        int(year),
        int(study_number),
        str(study_type_id),
        int(outlier),
    )
    )

    for note_id in note_ids:
        cursor.execute(
        """
        INSERT INTO study_notes( study_id, note_id )
        VALUES( ?, ? );
        """,
        (
            study_id,
            int(note_id),
        )
        )

    for compilation_id in study_external_ids:
        cursor.execute(
        """
        INSERT INTO study_external_ids( study_id, compilation_id,
                                        study_external_id )
        VALUES( ?, ?, ? );
        """,
        (
            study_id,
            int(compilation_id),
            study_external_ids[compilation_id],
        )
        )

    return study_id

def update_study_description( cursor, study_id, study_description ):
    cursor.execute(
    """
    UPDATE studies
    SET study_description=?
    WHERE study_id=?;
    """,
    (
        study_description.strip(),
        sanitize_identifier(study_id),
    )
    )

def update_study_provenance( cursor, study_id, study_provenance ):
    cursor.execute(
    """
    UPDATE studies
    SET study_provenance=?
    WHERE study_id=?:
    """,
    (
        study_provenance.strip(),
        sanitize_identifier(study_id),
    )
    )

def create_value_types_list( value_type_id ):
    if ( value_type_id == VT_BOTH_AVERAGES ):
        return [ VT_DENSITY_WEIGHTED_AVERAGE,
                       VT_UNWEIGHTED_AVERAGE, ]
    else:
        return [ value_type_id ]

def add_study_source( cursor, study_id, citation_key,
                      source_classification_id=PRIMARY_SOURCE ):
    cursor.execute(
    """
    INSERT INTO study_sources( study_id, citation_key, source_classification_id )
    VALUES( ?, ?, ? );
    """,
    (
        sanitize_identifier(study_id),
        str(citation_key),
        int(source_classification_id),
    )
    )

def add_series( cursor, flow_class_id, year, study_number, series_number,  \
                number_of_dimensions, facility_id=None,
                model_id=None, outlier=False, note_ids=[],
                series_external_ids={}, ):
    series_id = identify_series(
        flow_class_id,
        year,
        study_number,
        series_number,
    )
    study_id = identify_study(
        flow_class_id,
        year,
        study_number,
    )
    cursor.execute(
    """
    INSERT INTO series( series_id, study_id, series_number,
                        number_of_dimensions, facility_id, model_id, outlier )
    VALUES( ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        series_id,
        study_id,
        int(series_number),
        int(number_of_dimensions),
        facility_id,
        model_id,
        int(outlier),
    )
    )

    for note_id in note_ids:
        cursor.execute(
        """
        INSERT INTO series_notes( series_id, note_id )
        VALUES( ?, ? );
        """,
        (
            series_id,
            int(note_id),
        )
        )

    for compilation_id in series_external_ids:
        cursor.execute(
        """
        INSERT INTO series_external_ids( series_id, compilation_id,
                                         series_external_id )
        VALUES( ?, ?, ? );
        """,
        (
            series_id,
            int(compilation_id),
            series_external_ids[compilation_id],
        )
        )

    return series_id

def update_series_description( cursor, series_id, series_description ):
    cursor.execute(
    """
    UPDATE series
    SET series_description=?
    WHERE series_id=?;
    """,
    (
        series_description.strip(),
        sanitize_identifier(series_id),
    )
    )

def add_series_component( cursor, series_id, fluid_id ):
    cursor.execute(
    """
    INSERT INTO series_components( series_id, fluid_id )
    VALUES( ?, ? );
    """,
    (
        series_id,
        fluid_id,
    )
    )

def add_air_components_to_series( cursor, series_id ):
    air_mixture = [
        F_GASEOUS_ARGON,
        F_GASEOUS_CARBON_DIOXIDE,
        F_GASEOUS_DIATOMIC_NITROGEN,
        F_GASEOUS_DIATOMIC_OXYGEN,
        F_WATER_VAPOR,
    ]
    for fluid_id in air_mixture:
        add_series_component( cursor, series_id, fluid_id )

def get_series_components( cursor, series_id ):
    cursor.execute(
    """
    SELECT fluid_id
    FROM series_components
    WHERE series_id=?;
    """,
    (
        series_id,
    )
    )

    results = cursor.fetchall()
    fluid_ids = []
    for result in results:
        fluid_ids.append( result[0] )

    return fluid_ids

# TODO: There probably is a better way to do this.
def is_air_working_fluid( cursor, series_id ):
    fluid_ids = get_series_components( cursor, series_id )
    minimum_air_components = [
        GASEOUS_DIATOMIC_NITROGEN,
        GASEOUS_DIATOMIC_OXYGEN,
    ]
    for fluid_id in minimum_air_components:
        if ( fluid_id not in fluid_ids ):
            return False
    return True

def add_station( cursor, flow_class_id, year, study_number, series_number,
                 station_number, streamwise_periodic=False,
                 spanwise_periodic=True, outlier=False, parent_station_id=None,
                 note_ids=[], station_external_ids={}, ):
    station_id = identify_station(
        flow_class_id,
        year,
        study_number,
        series_number,
        station_number,
    )
    series_id = identify_series(
        flow_class_id,
        year,
        study_number,
        series_number,
    )
    cursor.execute(
    """
    INSERT INTO stations( station_id, series_id, station_number,
                          streamwise_periodic, spanwise_periodic, outlier )
    VALUES( ?, ?, ?, ?, ?, ? );
    """,
    (
        station_id,
        series_id,
        int(station_number),
        int(streamwise_periodic),
        int(spanwise_periodic),
        int(outlier),
    )
    )

    if ( parent_station_id == None ):
        cursor.execute(
        """
        INSERT INTO station_paths( station_ancestor_id,
                                   station_descendant_id,
                                   station_path_length )
        VALUES( ?, ?, 0 );
        """,
        (
            str(station_id),
            str(station_id),
        )
        )
    else:
        cursor.execute(
        """
        INSERT INTO station_paths( station_ancestor_id,
                                   station_descendant_id,
                                   station_path_length )
        SELECT ?, ?, 0
        UNION ALL
        SELECT tmp.station_ancestor_id, ?, tmp.station_path_length+1
        FROM station_paths as tmp
        WHERE tmp.station_descendant_id = ?;
        """,
        (
            str(station_id),
            str(station_id),
            str(station_id),
            str(parent_station_id),
        )
        )

    for note_id in note_ids:
        cursor.execute(
        """
        INSERT INTO station_notes( station_id, note_id )
        VALUES( ?, ? );
        """,
        (
            station_id,
            int(note_id),
        )
        )

    for compilation_id in station_external_ids:
        cursor.execute(
        """
        INSERT INTO station_external_ids( station_id, compilation_id,
                                          station_external_id )
        VALUES( ?, ?, ? );
        """,
        (
            station_id,
            int(compilation_id),
            station_external_ids[compilation_id],
        )
        )

    return station_id

def get_points_at_station( cursor, station_id ):
    cursor.execute(
    """
    SELECT point_id
    FROM points
    WHERE station_id=?;
    """,
    (
        station_id,
    )
    )

    results = cursor.fetchall()
    point_ids = []
    for result in results:
        point_ids.append( str(result[0]) )

    return point_ids

def add_point( cursor, flow_class_id, year, study_number, series_number,
               station_number, point_number, point_label_id=None,
               outlier=False, note_ids=[], point_external_ids={}, ):
    point_id = identify_point(
        flow_class_id,
        year,
        study_number,
        series_number,
        station_number,
        point_number,
    )
    station_id = identify_station(
        flow_class_id,
        year,
        study_number,
        series_number,
        station_number,
    )
    cursor.execute(
    """
    INSERT INTO points( point_id, station_id, point_number, point_label_id,
                        outlier )
    VALUES( ?, ?, ?, ?, ? );
    """,
    (
        point_id,
        station_id,
        int(point_number),
        point_label_id,
        int(outlier),
    )
    )

    for note_id in note_ids:
        cursor.execute(
        """
        INSERT INTO point_notes( point_id, note_id )
        VALUES( ?, ? );
        """,
        (
            point_id,
            int(note_id),
        )
        )

    for compilation_id in point_external_ids:
        cursor.execute(
        """
        INSERT INTO point_external_ids( point_id, compilation_id,
                                        point_external_id )
        VALUES( ?, ?, ? );
        """,
        (
            point_id,
            int(compilation_id),
            point_external_ids[compilation_id],
        )
        )

    return point_id

def sanitize_point_label( point_label_id ):
    sanitized_point_label_id = str(point_label_id)
    if ( point_label_id in PL_EDGES ):
        sanitized_point_label_id = PL_EDGE
    elif ( point_label_id in PL_WALLS ):
        sanitized_point_label_id = PL_WALL
    return sanitized_point_label_id

def locate_labeled_points( cursor, station_id, point_label_id ):
    if ( point_label_id in PL_LOWER_UPPER ):
        return [ locate_labeled_point( cursor, station_label ) ]

    cursor.execute(
    """
    SELECT point_id
    FROM points
    WHERE station_id=? AND point_label_id=?
    ORDER BY point_id;
    """,
    (
        sanitize_identifier(station_id),
        str(point_label_id),
    )
    )

    results = cursor.fetchall()
    point_ids = []
    for result in results:
        point_ids.append( str(result[0]) )

    return point_ids

def locate_labeled_point( cursor, station_id, point_label_id ):
    point_ids = locate_labeled_points( cursor, station_id,
                                       sanitize_point_label(point_label_id) )

    point_numbers = {}
    for point_id in point_ids:
        cursor.execute(
        """
        SELECT point_number
        FROM points
        WHERE point_id=?;
        """,
        (
            point_id,
        )
        )
        point_numbers[point_id] = int(cursor.fetchone()[0])

    lower_point_id = min( point_numbers, key=point_numbers.get )
    upper_point_id = max( point_numbers, key=point_numbers.get )

    point_id = lower_point_id
    if ( point_label_id in PL_LOWER ):
        point_id = lower_point_id
    elif ( point_label_id in PL_UPPER ):
        point_id = upper_point_id

    return point_id

def add_facility( cursor, facility_class_id, facility_name, iso_country_code,
                  organization_name=None, start_year=None, end_year=None,
                  predecessor_facility_id=None, successor_facility_id=None,
                  note_ids=[] ):
    cursor.execute(
    """
    INSERT INTO facilities( facility_class_id, facility_name, iso_country_code,
                            organization_name, start_year, end_year,
                            predecessor_facility_id, successor_facility_id )
    VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        str(facility_class_id),
        str(facility_name),
        str(iso_country_code),
        organization_name,
        start_year,
        end_year,
        predecessor_facility_id,
        successor_facility_id,
    )
    )

    cursor.execute(
    """
    SELECT last_insert_rowid();
    """
    )
    facility_id = int(cursor.fetchone()[0])

    for note_id in note_ids:
        cursor.execute(
        """
        INSERT INTO facility_notes( facility_id, note_id )
        VALUES( ?, ? );
        """,
        (
            int(facility_id),
            int(note_id),
        )
        )

    return facility_id

def add_facility_source( cursor, facility_id, citation_key,
                         source_classification_id=PRIMARY_SOURCE ):
    cursor.execute(
    """
    INSERT INTO facility_sources( facility_id, citation_key,
                                  source_classification_id )
    VALUES( ?, ?, ? );
    """,
    (
        int(facility_id),
        str(citation_key),
        int(source_classification_id),
    )
    )

def add_instrument( cursor, instrument_class_id, instrument_name=None,
                    note_ids=[] ):
    cursor.execute(
    """
    INSERT INTO instruments( instrument_class_id, instrument_name )
    VALUES( ?, ? );
    """,
    (
        str(instrument_class_id),
        instrument_name,
    )
    )

    cursor.execute(
    """
    SELECT last_insert_rowid();
    """
    )
    instrument_id = int(cursor.fetchone()[0])

    for note_id in note_ids:
        cursor.execute(
        """
        INSERT INTO instrument_notes( instrument_id, note_id )
        VALUES( ?, ? );
        """,
        (
            int(instrument_id),
            int(note_id),
        )
        )

    return instrument_id

def add_instrument_source( cursor, instrument_id, citation_key,
                           source_classification_id=PRIMARY_SOURCE ):
    cursor.execute(
    """
    INSERT INTO instrument_sources( instrument_id, citation_key,
                                    source_classification_id )
    VALUES( ?, ?, ? );
    """,
    (
        int(instrument_id),
        str(citation_key),
        int(source_classification_id),
    )
    )

def add_model( cursor, model_class_id, model_name=None, note_ids=[] ):
    cursor.execute(
    """
    INSERT INTO models( model_class_id, model_name )
    VALUES( ?, ? );
    """,
    (
        str(model_class_id),
        model_name,
    )
    )

    cursor.execute(
    """
    SELECT last_insert_rowid();
    """
    )
    model_id = int(cursor.fetchone()[0])

    for note_id in note_ids:
        cursor.execute(
        """
        INSERT INTO model_notes( model_id, note_id )
        VALUES( ?, ? );
        """,
        (
            int(model_id),
            int(note_id),
        )
        )

    return model_id

def add_model_source( cursor, model_id, citation_key,
                      source_classification_id=PRIMARY_SOURCE ):
    cursor.execute(
    """
    INSERT INTO model_sources( model_id, citation_key, source_classification_id )
    VALUES( ?, ?, ? );
    """,
    (
        int(model_id),
        str(citation_key),
        int(source_classification_id),
    )
    )

def integrate_using_trapezoid_rule( x, f, F0=sdfloat(0.0,0.0) ):
    F = F0
    for i in range(len(x)-1):
        F += 0.5 * ( x[i+1] - x[i] ) * ( f[i+1] + f[i] )
    return F

def extract_element_counts( formula ):
    element_counts = {}

    fragments = []
    i_start = 0
    i_end   = 0
    for i_end in range(len(formula)):
        if ( formula[i_end].isupper() and i_end != 0 ):
            fragments.append( formula[i_start:i_end] )
            i_start = i_end
    fragments.append( formula[i_start:i_end+1] )

    for fragment in fragments:
        i = 0
        while ( i < len(fragment) and fragment[i].isdigit() == False ):
            i += 1
        if ( i == len(fragment) ):
            element = fragment
            count   = 1
        else:
            element = str(fragment[:i])
            count   = int(fragment[i:])
        element_counts[element] = count

    return element_counts

def count_total_atoms( formula ):
    element_counts = extract_element_counts( formula )
    total_atoms = 0
    for element in element_counts:
        total_atoms += element_counts[element]
    assert( total_atoms > 0 )
    return total_atoms

def get_degrees_of_freedom_for_element( formula ):
    total_atoms = count_total_atoms( formula )
    if ( total_atoms == 1 ):
        return 3
    elif ( total_atoms == 2 ):
        return 5
    # TODO: Develop a better method for this.
    assert( total_atoms < 3 )
    return 0

def calculate_molar_mass_of_molecular_formula( cursor, formula ):
    element_counts = extract_element_counts( formula )
    molar_mass      = sdfloat(0.0,0.0)
    for element in element_counts:
        count = element_counts[element]
        cursor.execute(
        """
        SELECT conventional_atomic_weight
        FROM elements
        WHERE element_symbol=?;
        """,
        ( element, )
        )
        result = cursor.fetchone()
        atomic_weight = sdfloat(result[0],0.0)
        molar_mass += count * 1.0e-3 * atomic_weight
    return molar_mass

def calculate_molar_mass_of_component( cursor, fluid_id ):
    molecular_formula = get_molecular_formula_for_component( cursor, fluid_id )
    molar_mass        = calculate_molar_mass_of_molecular_formula( cursor, molecular_formula )
    return molar_mass

def get_molecular_formula_for_component( cursor, fluid_id ):
    cursor.execute(
    """
    SELECT molecular_formula
    FROM fluids
    WHERE fluid_id=?;
    """,
    (
        fluid_id,
    )
    )

    return str(cursor.fetchone()[0])

def calculate_molar_mass_from_amount_fractions( cursor, amount_fractions ):
    mixture_amount_fraction = sdfloat(0.0,0.0)
    mixture_molar_mass      = sdfloat(0.0,0.0)
    for fluid_id in amount_fractions:
        molar_mass      = calculate_molar_mass_of_component( cursor, fluid_id )
        amount_fraction = amount_fractions[fluid_id]

        mixture_amount_fraction += amount_fraction
        mixture_molar_mass      += amount_fraction * molar_mass

    assert( math.fabs( sdfloat_value(mixture_amount_fraction) - 1.0 ) < sys.float_info.epsilon )
    return mixture_molar_mass

def calculate_mass_fractions_from_amount_fractions( cursor, amount_fractions ):
    mixture_molar_mass = calculate_molar_mass_from_amount_fractions( cursor, amount_fractions )

    mixture_mass_fraction = sdfloat(0.0,0.0)
    mass_fractions = {}
    for fluid_id in amount_fractions:
        molar_mass = calculate_molar_mass_of_component( cursor, fluid_id )
        mass_fraction = molar_mass * amount_fractions[fluid_id] / mixture_molar_mass

        mixture_mass_fraction   += mass_fraction
        mass_fractions[fluid_id] = mass_fraction

    assert( math.fabs( sdfloat_value(mixture_mass_fraction) - 1.0 ) < sys.float_info.epsilon )
    return mass_fractions

def calculate_specific_gas_constant_of_component( cursor, fluid_id ):
    molar_mass = calculate_molar_mass_of_component( cursor, fluid_id )
    return MOLAR_GAS_CONSTANT / molar_mass

def calculate_specific_gas_constant_from_mass_fractions( cursor, mass_fractions ):
    mixture_specific_gas_constant = sdfloat(0.0,0.0)
    for fluid_id in mass_fractions:
        mixture_specific_gas_constant += mass_fractions[fluid_id] * calculate_specific_gas_constant_of_component( cursor, fluid_id )
    return mixture_specific_gas_constant

def calculate_specific_gas_constant_from_amount_fractions( cursor, amount_fractions ):
    mass_fractions = calculate_mass_fractions_from_amount_fractions( cursor, amount_fractions )
    return calculate_specific_gas_constant_from_mass_fractions( cursor, mass_fractions )

def calculate_ideal_gas_specific_isochoric_heat_capacity_of_component( cursor, fluid_id ):
    formula = get_molecular_formula_for_component( cursor, fluid_id )
    degrees_of_freedom = get_degrees_of_freedom_for_element( formula )
    specific_gas_constant = calculate_specific_gas_constant_of_component( cursor, fluid_id )
    c_v = 0.5 * degrees_of_freedom * specific_gas_constant
    return c_v

def calculate_ideal_gas_specific_isobaric_heat_capacity_of_component( cursor, fluid_id ):
    formula = get_molecular_formula_for_component( cursor, fluid_id )
    degrees_of_freedom = get_degrees_of_freedom_for_element( formula )
    specific_gas_constant = calculate_specific_gas_constant_of_component( cursor, fluid_id )
    c_P = 0.5 * ( degrees_of_freedom + 2 ) * specific_gas_constant
    return c_P

def calculate_ideal_gas_heat_capacity_ratio_of_component( cursor, fluid_id ):
    c_v = calculate_ideal_gas_specific_isochoric_heat_capacity_of_component( cursor, fluid_id )
    c_P = calculate_ideal_gas_specific_isobaric_heat_capacity_of_component( cursor, fluid_id )
    gamma = c_P / c_v
    return gamma

def calculate_ideal_gas_specific_isochoric_heat_capacity_from_mass_fractions( cursor, mass_fractions ):
    specific_isochoric_heat_capacity = 0.0
    for fluid_id in mass_fractions:
        specific_isochoric_heat_capacity += mass_fractions[fluid_id] * calculate_ideal_gas_specific_isochoric_heat_capacity_of_component( cursor, fluid_id )
    return specific_isochoric_heat_capacity

def calculate_ideal_gas_specific_isobaric_heat_capacity_from_mass_fractions( cursor, mass_fractions ):
    specific_isobaric_heat_capacity = 0.0
    for fluid_id in mass_fractions:
        specific_isobaric_heat_capacity += mass_fractions[fluid_id] * calculate_ideal_gas_specific_isobaric_heat_capacity_of_component( cursor, fluid_id )
    return specific_isobaric_heat_capacity

def calculate_ideal_gas_heat_capacity_ratio_from_mass_fractions( cursor, mass_fractions ):
    specific_isochoric_heat_capacity = calculate_ideal_gas_specific_isochoric_heat_capacity_from_mass_fractions( cursor, mass_fractions )
    specific_isobaric_heat_capacity  = calculate_ideal_gas_specific_isobaric_heat_capacity_from_mass_fractions(  cursor, mass_fractions )
    return specific_isobaric_heat_capacity / specific_isochoric_heat_capacity

def calculate_ideal_gas_specific_isochoric_heat_capacity_from_amount_fractions( cursor, amount_fractions ):
    mass_fractions = calculate_mass_fractions_from_amount_fractions( cursor, amount_fractions )
    return calculate_ideal_gas_specific_isochoric_heat_capacity_from_mass_fractions( cursor, mass_fractions )

def calculate_ideal_gas_specific_isobaric_heat_capacity_from_amount_fractions( cursor, amount_fractions ):
    mass_fractions = calculate_mass_fractions_from_amount_fractions( cursor, amount_fractions )
    return calculate_ideal_gas_specific_isobaric_heat_capacity_from_mass_fractions( cursor, mass_fractions )

def calculate_ideal_gas_heat_capacity_ratio_from_amount_fractions( cursor, amount_fractions ):
    mass_fractions = calculate_mass_fractions_from_amount_fractions( cursor, amount_fractions )
    return calculate_ideal_gas_heat_capacity_ratio_from_mass_fractions( cursor, mass_fractions )

def count_studies( identifiers ):
    study_ids = {}
    for identifier in identifiers:
        study_id = truncate_to_study_id( identifier )
        if ( study_id not in study_ids ):
            study_ids[study_id] = 1
        else:
            study_ids[study_id] += 1
    return study_ids

# TODO: Add more components.  Note that for the specific heats, I need to
# include additional information about the degrees of freedom for triatomic and
# polyatomic molecules to return correct answers.
def dry_air_amount_fractions():
    return {
        F_GASEOUS_DIATOMIC_NITROGEN: sdfloat(0.78,0.0),
        F_GASEOUS_DIATOMIC_OXYGEN:   sdfloat(0.21,0.0),
        F_GASEOUS_ARGON:             sdfloat(0.01,0.0),
    }

def calculate_ideal_gas_mass_density_from_mass_fractions( cursor, pressure, temperature, mass_fractions ):
    specific_gas_constant = calculate_specific_gas_constant_from_mass_fractions( cursor, mass_fractions )
    return pressure / ( specific_gas_constant * temperature )

def calculate_ideal_gas_mass_density_from_amount_fractions( cursor, pressure, temperature, amount_fractions ):
    mass_fractions = calculate_mass_fractions_from_amount_fractions( cursor, amount_fractions )
    return calculate_ideal_gas_mass_density_from_mass_fractions( cursor, pressure, temperature, mass_fractions )

def calculate_ideal_gas_speed_of_sound_from_mass_fractions( cursor, temperature, mass_fractions ):
    specific_gas_constant = calculate_specific_gas_constant_from_mass_fractions( cursor, mass_fractions )
    heat_capacity_ratio   = calculate_ideal_gas_heat_capacity_ratio_from_mass_fractions( cursor, mass_fractions )
    return ( heat_capacity_ratio * specific_gas_constant * temperature )**0.5

def calculate_ideal_gas_speed_of_sound_from_amount_fractions( cursor, temperature, amount_fractions ):
    mass_fractions = calculate_mass_fractions_from_amount_fractions( cursor, amount_fractions )
    return calculate_ideal_gas_speed_of_sound_from_mass_fractions( cursor, temperature, mass_fractions )

def fahrenheit_to_kelvin( fahrenheit ):
    return ( fahrenheit - 32.0 ) / 1.8 + ABSOLUTE_ZERO

def add_note( cursor, filename ):
    contents = None
    with open( filename, "r" ) as f:
        contents = f.read().strip()

    cursor.execute(
    """
    INSERT INTO notes( note_contents )
    VALUES( ? );
    """,
    (
        str(contents),
    )
    )

    cursor.execute(
    """
    SELECT last_insert_rowid();
    """
    )
    return int(cursor.fetchone()[0])

