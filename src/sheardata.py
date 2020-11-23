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
import numpy as np
import sqlite3
from uncertainties import ufloat

# Physical constants
ABSOLUTE_ZERO                       =    273.15
DRY_AIR_HEAT_CAPACITY_RATIO         =      1.4
DRY_AIR_SPECIFIC_GAS_CONSTANT       =    287.058
STANDARD_ATMOSPHERIC_PRESSURE       = 101325.0
STANDARD_GRAVITATIONAL_ACCELERATION =      9.80665

# Unit conversion factors
INCHES_PER_FOOT         = 12.0
KILOGRAM_PER_POUND_MASS =  0.45359237
METERS_PER_INCH         =  2.54e-2
SECONDS_PER_MINUTE      = 60.0

METERS_PER_FOOT             = METERS_PER_INCH * INCHES_PER_FOOT
PASCALS_PER_METER_OF_WATER  = 1000.0 * STANDARD_GRAVITATIONAL_ACCELERATION
PASCALS_PER_INCH_OF_WATER   = PASCALS_PER_METER_OF_WATER * METERS_PER_INCH
PASCALS_PER_INCH_OF_MERCURY = 3376.85

# Averaging systems
ANY_AVERAGING_SYSTEM              = "ANY"
DENSITY_WEIGHTED_AVERAGING_SYSTEM = "DW"
UNWEIGHTED_AVERAGING_SYSTEM       = "UW"
BOTH_AVERAGING_SYSTEMS            = "BOTH"

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
BOUNDARY_DRIVEN_FLOW_CLASS = "R"
SHEAR_FLOW_CLASS           = "S"
UNCLASSIFIED_FLOW_CLASS    = "U"
WAKE_FLOW_CLASS            = "W"

# Flow regimes
LAMINAR_FLOW_REGIME      = "lam"
TRANSITIONAL_FLOW_REGIME = "trans"
TURBULENT_FLOW_REGIME    = "turb"

# Phases
GAS_PHASE    = "g"
LIQUID_PHASE = "l"
SOLID_PHASE  = "s"

# Fluids
ARGON_GAS          = "Ar(g)"
CARBON_DIOXIDE_GAS = "CO2(g)"
HELIUM_GAS         = "He(g)"
HYDROGEN_GAS       = "H(g)"
NITROGEN_GAS       = "N2(g)"
OXYGEN_GAS         = "O2(g)"
WATER_LIQUID       = "H2O(l)"
WATER_VAPOR        = "H2O(g)"

AIR_COMPONENTS = [ NITROGEN_GAS,
                   OXYGEN_GAS,
                   ARGON_GAS,
                   CARBON_DIOXIDE_GAS,
                   WATER_VAPOR, ]

# Geometries
ELLIPTICAL_GEOMETRY  = "E"
RECTANGULAR_GEOMETRY = "R"

# Measurement techniques (and other sources of information)
MT_APPROXIMATION                            = "APPR"
MT_ASSUMPTION                               = "A"
MT_CALCULATION                              = "C"
MT_CLAUSER_METHOD                           = "CC"
MT_CONSTANT_CURRENT_HOT_WIRE_ANEMOMETRY     = "CCHWA"
MT_CONSTANT_TEMPERATURE_HOT_WIRE_ANEMOMETRY = "CTHWA"
MT_DIFFERENTIAL_PRESSURE_METHOD             = "P"
MT_DIRECT_INJECTION_METHOD                  = "DI"
MT_EMPIRICISM                               = "E"
MT_FLOATING_ELEMENT_BALANCE                 = "FEB"
MT_FLOW_RATE_MEASUREMENT                    = "F"
MT_HOT_WIRE_ANEMOMETRY                      = "HWA"
MT_IMPACT_TUBE                              = "IT"
MT_INDEX_OF_REFRACTION_METHOD               = "RI"
MT_LASER_DOPPLER_ANEMOMETRY                 = "LDA"
MT_MACH_ZEHNDER_INTERFEROMETRY              = "MZI"
MT_MOMENTUM_BALANCE                         = "MB"
MT_OPTICAL_METHOD                           = "O"
MT_PARTICLE_IMAGE_VELOCIMETRY               = "PIV"
MT_PITOT_STATIC_TUBE                        = "PST"
MT_PRESTON_TUBE                             = "PT"
MT_REASONING                                = "R"
MT_ROOT                                     = "M"
MT_SCHLIEREN_PHOTOGRAPHY                    = "SP"
MT_SHADOWGRAPH_PHOTOGRAPHY                  = "SG"
MT_STANTON_TUBE                             = "ST"
MT_THERMAL_ANEMOMETRY                       = "T"
MT_VELOCITY_PROFILE_METHOD                  = "VP"
MT_VISCOUS_SUBLAYER_SLOPE_METHOD            = "VS"
MT_WALL_SHEAR_STRESS_METHOD                 = "W"
MT_WEIGHING_METHOD                          = "WM"

# Point labels
CENTER_LINE_POINT_LABEL = "CL"
EDGE_POINT_LABEL        = "E"
WALL_POINT_LABEL        = "W"

# Quantities, series
Q_ANGLE_OF_ATTACK                = "alpha"
Q_BODY_REYNOLDS_NUMBER           = "Re_inf"
Q_BODY_STROUHAL_NUMBER           = "Sr"
Q_DISTANCE_BETWEEN_PRESSURE_TAPS = "L_p"
Q_DRAG_COEFFICIENT               = "C_D"
Q_DRAG_FORCE                     = "F_D"
Q_FREESTREAM_MACH_NUMBER         = "Ma_inf"
Q_FREESTREAM_SPEED_OF_SOUND      = "a_inf"
Q_FREESTREAM_TEMPERATURE         = "T_inf"
Q_FREESTREAM_VELOCITY            = "U_inf"
Q_LIFT_COEFFICIENT               = "C_L"
Q_LIFT_FORCE                     = "F_L"
Q_LIFT_TO_DRAG_RATIO             = "L/D"
Q_MASS_FLOW_RATE                 = "mdot"
Q_TEST_LENGTH                    = "L_t"
Q_VOLUMETRIC_FLOW_RATE           = "Vdot"

# Quantities, station
Q_ASPECT_RATIO                           = "AR"
Q_BULK_MACH_NUMBER                       = "Ma_b"
Q_BULK_REYNOLDS_NUMBER                   = "Re_b"
Q_BULK_TO_CENTER_LINE_VELOCITY_RATIO     = "U_b/U_c"
Q_BULK_VELOCITY                          = "U_b"
Q_CLAUSER_THICKNESS                      = "delta_C"
Q_CROSS_SECTIONAL_AREA                   = "A"
Q_DEVELOPMENT_LENGTH                     = "L_d"
Q_DISPLACEMENT_THICKNESS                 = "delta_1"
Q_DISPLACEMENT_THICKNESS_REYNOLDS_NUMBER = "Re_delta_1"
Q_ENERGY_THICKNESS                       = "delta_3"
Q_EQUILIBRIUM_PARAMETER                  = "Pi_2"
Q_HALF_HEIGHT                            = "b"
Q_HEIGHT                                 = "h"
Q_HYDRAULIC_DIAMETER                     = "D_H"
Q_INNER_DIAMETER                         = "D_i"
Q_MOMENTUM_THICKNESS                     = "delta_2"
Q_MOMENTUM_THICKNESS_REYNOLDS_NUMBER     = "Re_delta_2"
Q_OUTER_DIAMETER                         = "D_o"
Q_OUTER_LAYER_DEVELOPMENT_LENGTH         = "L_d/D_H"
Q_RECOVERY_FACTOR                        = "RF"
Q_SHAPE_FACTOR_1_TO_2                    = "H_12"
Q_SHAPE_FACTOR_3_TO_2                    = "H_32"
Q_SPANWISE_PRESSURE_GRADIENT             = "PG_z"
Q_STREAMWISE_COORDINATE_REYNOLDS_NUMBER  = "Re_x"
Q_STREAMWISE_PRESSURE_GRADIENT           = "PG_x"
Q_WETTED_PERIMETER                       = "P"
Q_WIDTH                                  = "w"

# Quantities, wall point
Q_CENTER_LINE_TO_WALL_TEMPERATURE_RATIO = "T_c/T_w"
Q_DARCY_FRICTION_FACTOR                 = "f_D"
Q_FANNING_FRICTION_FACTOR               = "f"
Q_FRICTION_MACH_NUMBER                  = "Ma_tau"
Q_FRICTION_REYNOLDS_NUMBER              = "Re_tau"
Q_FRICTION_TEMPERATURE                  = "T_tau"
Q_FRICTION_VELOCITY                     = "U_tau"
Q_HEAT_TRANSFER_COEFFICIENT             = "c_q"
Q_INNER_LAYER_HEAT_FLUX                 = "B_q"
Q_INNER_LAYER_ROUGHNESS_HEIGHT          = "eps+"
Q_OUTER_LAYER_ROUGHNESS_HEIGHT          = "eps/D_H"
Q_PRESSURE_COEFFICIENT                  = "C_p"
Q_ROUGHNESS_HEIGHT                      = "eps"
Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER   = "Re_tau*"
Q_SKIN_FRICTION_COEFFICIENT             = "c_f"
Q_SPANWISE_WALL_CURVATURE               = "kappa_z"
Q_STREAMWISE_WALL_CURVATURE             = "kappa_x"
Q_VISCOUS_LENGTH_SCALE                  = "l_nu"
Q_WALL_TO_EDGE_TEMPERATURE_RATIO        = "T_w/T_e"
Q_WALL_TO_RECOVERY_TEMPERATURE_RATIO    = "T_w/T_r"

# Quantities, point
Q_DISTANCE_FROM_WALL               = "y"
Q_DYNAMIC_VISCOSITY                = "mu"
Q_HEAT_CAPACITY_RATIO              = "gamma"
Q_HEAT_FLUX                        = "q"
Q_INNER_LAYER_COORDINATE           = "y+"
Q_INNER_LAYER_TEMPERATURE          = "T+"
Q_INNER_LAYER_VELOCITY             = "U+"
Q_KINEMATIC_VISCOSITY              = "nu"
Q_MACH_NUMBER                      = "Ma"
Q_MASS_DENSITY                     = "rho"
Q_OUTER_LAYER_COORDINATE           = "eta"
Q_OUTER_LAYER_TEMPERATURE          = "Theta"
Q_OUTER_LAYER_VELOCITY             = "F"
Q_PRANDTL_NUMBER                   = "Pr"
Q_PRESSURE                         = "p"
Q_SEMI_LOCAL_COORDINATE            = "y*"
Q_SHEAR_STRESS                     = "tau"
Q_SPANWISE_COORDINATE              = "Z"
Q_SPANWISE_VELOCITY                = "W"
Q_SPECIFIC_ENTHALPY                = "h"
Q_SPECIFIC_GAS_CONSTANT            = "R"
Q_SPECIFIC_INTERNAL_ENERGY         = "e"
Q_SPECIFIC_ISOBARIC_HEAT_CAPACITY  = "c_p"
Q_SPECIFIC_ISOCHORIC_HEAT_CAPACITY = "c_v"
Q_SPECIFIC_TOTAL_ENTHALPY          = "h_0"
Q_SPECIFIC_TOTAL_INTERNAL_ENERGY   = "e_0"
Q_SPECIFIC_VOLUME                  = "vbar"
Q_SPEED                            = "v"
Q_SPEED_OF_SOUND                   = "a"
Q_STREAMWISE_COORDINATE            = "X"
Q_STREAMWISE_VELOCITY              = "U"
Q_TEMPERATURE                      = "T"
Q_TOTAL_PRESSURE                   = "p_0"
Q_TOTAL_TEMPERATURE                = "T_0"
Q_TRANSVERSE_COORDINATE            = "Y"
Q_TRANSVERSE_VELOCITY              = "V"

AMOUNT_FRACTION_PREFIX      = "X_"
MASS_FRACTION_PREFIX        = "Y_"

# Study types
DIRECT_NUMERICAL_SIMULATION_STUDY_TYPE = "DNS"
EXPERIMENTAL_STUDY_TYPE                = "EXP"
LARGE_EDDY_SIMULATION_STUDY_TYPE       = "LES"

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

def sdfloat( sql_value, sql_uncertainty=None ):
    uncertainty = float(0.0)
    if ( sql_uncertainty == None ):
        uncertainty = float("nan")
    else:
        uncertainty = float(sql_uncertainty)
    return ufloat( float(sql_value), uncertainty )

def fetch_float( cursor ):
    result = cursor.fetchone()
    return sdfloat( result[0], result[1] )

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

def truncate_to_study( identifier ):
    sanitized_identifier = sanitize_identifier( identifier )
    return sanitized_identifier[0:8]

def truncate_to_series( identifier ):
    sanitized_identifier = sanitize_identifier( identifier )
    return sanitized_identifier[0:11]

def truncate_to_station( identifier ):
    sanitized_identifier = sanitize_identifier( identifier )
    return sanitized_identifier[0:14]

def add_study( cursor, flow_class, year, study_number, study_type, \
               outlier=False, notes=None, ):
    study = identify_study( flow_class, year, study_number )
    cursor.execute(
    """
    INSERT INTO studies( identifier, flow_class, year, study_number,
    study_type, outlier, notes ) VALUES( ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        study,
        str(flow_class),
        int(year),
        int(study_number),
        str(study_type),
        int(outlier),
        notes,
    )
    )
    return study

def update_study_description( cursor, identifier, description ):
    cursor.execute(
    """
    UPDATE studies SET description=? WHERE identifier=?
    """,
    (
        description.strip(),
        sanitize_identifier(identifier),
    )
    )

def update_study_provenance( cursor, identifier, provenance ):
    cursor.execute(
    """
    UPDATE studies SET provenance=? WHERE identifier=?
    """,
    (
        provenance.strip(),
        sanitize_identifier(identifier),
    )
    )

def update_study_notes( cursor, identifier, notes ):
    cursor.execute(
    """
    UPDATE studies SET notes=? WHERE identifier=?
    """,
    (
        notes.strip(),
        sanitize_identifier(identifier),
    )
    )

def create_averaging_systems_list( averaging_system ):
    if ( averaging_system == BOTH_AVERAGING_SYSTEMS ):
        return [ DENSITY_WEIGHTED_AVERAGING_SYSTEM,
                       UNWEIGHTED_AVERAGING_SYSTEM, ]
    else:
        return [ averaging_system ]

def set_study_value( cursor, study, quantity, value, averaging_system=None, \
                     measurement_technique=None, outlier=False, notes=None ):
    study_value, study_uncertainty = split_float( value )
    for avg_sys in create_averaging_systems_list( averaging_system ):
        cursor.execute(
        """
        INSERT INTO study_values( study, quantity, study_value,
        study_uncertainty, averaging_system, measurement_technique, outlier,
        notes )
        VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(study),
            str(quantity),
            study_value,
            study_uncertainty,
            avg_sys,
            measurement_technique,
            int(outlier),
            notes,
        )
        )

def get_study_value( cursor, study, quantity,               \
                     averaging_system=ANY_AVERAGING_SYSTEM, \
                     measurement_technique=MT_ROOT, ):
    if ( averaging_system == ANY_AVERAGING_SYSTEM ):
        if ( measurement_technique == MT_ROOT ):
            cursor.execute(
            """
            SELECT study_value, study_uncertainty FROM study_values WHERE
            study=?  AND quantity=? LIMIT 1;
            """,
            (
                sanitize_identifier(study),
                str(quantity),
            )
            )
        else:
            cursor.execute(
            """
            SELECT study_value, study_uncertainty FROM study_values WHERE
            study=?  AND quantity=? AND measurement_technique=? LIMIT 1;
            """,
            (
                sanitize_identifier(study),
                str(quantity),
                measurement_technique,
            )
            )
    else:
        if ( measurement_technique == MT_ROOT ):
            cursor.execute(
            """
            SELECT study_value, study_uncertainty FROM study_values WHERE
            study=?  AND quantity=? AND averaging_system=? LIMIT 1;
            """,
            (
                sanitize_identifier(study),
                str(quantity),
                averaging_system,
            )
            )
        else:
            cursor.execute(
            """
            SELECT study_value, study_uncertainty FROM study_values WHERE
            study=?  AND quantity=? AND averaging_system=? AND
            measurement_technique=? LIMIT 1;
            """,
            (
                sanitize_identifier(study),
                str(quantity),
                averaging_system,
                measurement_technique,
            )
            )
    return fetch_float( cursor )

def add_source( cursor, study, source, classification ):
    cursor.execute(
    """
    INSERT INTO sources( study, source, classification ) VALUES( ?, ?, ? );
    """,
    (
        sanitize_identifier(study),
        str(source),
        int(classification),
    )
    )

def add_series( cursor, flow_class, year, study_number, series_number,  \
                number_of_dimensions, coordinate_system, outlier=False, \
                notes=None, ):
    series = identify_series(
        flow_class,
        year,
        study_number,
        series_number,
    )
    study = identify_study(
        flow_class,
        year,
        study_number,
    )
    cursor.execute(
    """
    INSERT INTO series( identifier, study, series_number, number_of_dimensions,
    coordinate_system, outlier, notes )
    VALUES( ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        series,
        study,
        int(series_number),
        int(number_of_dimensions),
        str(coordinate_system),
        int(outlier),
        notes,
    )
    )
    return series

def update_series_geometry( cursor, identifier, geometry ):
    cursor.execute(
    """
    UPDATE series SET geometry=? WHERE identifier=?
    """,
    (
        str(geometry),
        sanitize_identifier(identifier),
    )
    )

def update_series_number_of_sides( cursor, identifier, number_of_sides ):
    cursor.execute(
    """
    UPDATE series SET number_of_sides=? WHERE identifier=?
    """,
    (
        int(number_of_sides),
        sanitize_identifier(identifier),
    )
    )

def update_series_description( cursor, identifier, description ):
    cursor.execute(
    """
    UPDATE series SET description=? WHERE identifier=?
    """,
    (
        description.strip(),
        sanitize_identifier(identifier),
    )
    )

def update_series_notes( cursor, identifier, notes ):
    cursor.execute(
    """
    UPDATE series SET notes=? WHERE identifier=?
    """,
    (
        notes.strip(),
        sanitize_identifier(identifier),
    )
    )

def set_series_value( cursor, series, quantity, value, averaging_system=None, \
                     measurement_technique=None, outlier=False, notes=None ):
    series_value, series_uncertainty = split_float( value )
    for avg_sys in create_averaging_systems_list( averaging_system ):
        cursor.execute(
        """
        INSERT INTO series_values( series, quantity, series_value,
        series_uncertainty, averaging_system, measurement_technique, outlier,
        notes)
        VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(series),
            str(quantity),
            series_value,
            series_uncertainty,
            avg_sys,
            measurement_technique,
            int(outlier),
            notes,
        )
        )

def get_series_value( cursor, series, quantity,              \
                      averaging_system=ANY_AVERAGING_SYSTEM, \
                      measurement_technique=MT_ROOT, ):
    if ( averaging_system == ANY_AVERAGING_SYSTEM ):
        if ( measurement_technique == MT_ROOT ):
            cursor.execute(
            """
            SELECT series_value, series_uncertainty FROM series_values WHERE
            series=? AND quantity=? LIMIT 1;
            """,
            (
                sanitize_identifer(series),
                str(quantity),
            )
            )
        else:
            cursor.execute(
            """
            SELECT series_value, series_uncertainty FROM series_values WHERE
            series=? AND quantity=? AND measurement_technique=? LIMIT 1;
            """,
            (
                sanitize_identifer(series),
                str(quantity),
                measurement_technique,
            )
            )
    else:
        if ( measurement_technique == MT_ROOT ):
            cursor.execute(
            """
            SELECT series_value, series_uncertainty FROM series_values WHERE
            series=? AND quantity=? AND averaging_system=? LIMIT 1;
            """,
            (
                sanitize_identifer(series),
                str(quantity),
                averaging_system,
            )
            )
        else:
            cursor.execute(
            """
            SELECT series_value, series_uncertainty FROM series_values WHERE
            series=? AND quantity=? AND averaging_system=? AND
            measurement_technique=? LIMIT 1;
            """,
            (
                sanitize_identifer(series),
                str(quantity),
                averaging_system,
                measurement_technique,
            )
            )
    return fetch_float( cursor )

def add_station( cursor, flow_class, year, study_number, series_number,     \
                station_number, originators_identifier=None, outlier=False, \
                notes=None ):
    station = identify_station(
        flow_class,
        year,
        study_number,
        series_number,
        station_number,
    )
    series = identify_series(
        flow_class,
        year,
        study_number,
        series_number,
    )
    study = identify_study(
        flow_class,
        year,
        study_number,
    )
    cursor.execute(
    """
    INSERT INTO stations( identifier, series, study, station_number,
    originators_identifier, outlier, notes )
    VALUES( ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        station,
        series,
        study,
        int(station_number),
        originators_identifier,
        int(outlier),
        notes,
    )
    )
    return station

def set_station_value( cursor, station, quantity, value, averaging_system=None, \
                     measurement_technique=None, outlier=False, notes=None ):
    station_value, station_uncertainty = split_float( value )
    for avg_sys in create_averaging_systems_list( averaging_system ):
        cursor.execute(
        """
        INSERT INTO station_values( station, quantity, station_value,
        station_uncertainty, averaging_system, measurement_technique, outlier,
        notes )
        VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(station),
            str(quantity),
            station_value,
            station_uncertainty,
            avg_sys,
            measurement_technique,
            int(outlier),
            notes,
        )
        )

def get_station_value( cursor, station, quantity,             \
                       averaging_system=ANY_AVERAGING_SYSTEM, \
                       measurement_technique=MT_ROOT, ):
    if ( averaging_system == ANY_AVERAGING_SYSTEM ):
        if ( measurement_technique == MT_ROOT ):
            cursor.execute(
            """
            SELECT station_value, station_uncertainty FROM station_values WHERE
            station=? AND quantity=? LIMIT 1;
            """,
            (
                sanitize_identifier(station),
                str(quantity),
            )
            )
        else:
            cursor.execute(
            """
            SELECT station_value, station_uncertainty FROM station_values WHERE
            station=? AND quantity=? AND measurement_technique=? LIMIT 1;
            """,
            (
                sanitize_identifier(station),
                str(quantity),
                measurement_technique,
            )
            )
    else:
        if ( measurement_technique == MT_ROOT ):
            cursor.execute(
            """
            SELECT station_value, station_uncertainty FROM station_values WHERE
            station=? AND quantity=? AND averaging_system=? LIMIT 1;
            """,
            (
                sanitize_identifier(station),
                str(quantity),
                averaging_system,
            )
            )
        else:
            cursor.execute(
            """
            SELECT station_value, station_uncertainty FROM station_values WHERE
            station=? AND quantity=? AND averaging_system=? AND
            measurement_technique=? LIMIT 1;
            """,
            (
                sanitize_identifier(station),
                str(quantity),
                averaging_system,
                measurement_technique,
            )
            )
    return fetch_float( cursor )

def add_point( cursor, flow_class, year, study_number, series_number, \
                station_number, point_number, point_label=None,       \
                outlier=False, notes=None ):
    point = identify_point(
        flow_class,
        year,
        study_number,
        series_number,
        station_number,
        point_number,
    )
    station = identify_station(
        flow_class,
        year,
        study_number,
        series_number,
        station_number,
    )
    series = identify_series(
        flow_class,
        year,
        study_number,
        series_number,
    )
    study = identify_study(
        flow_class,
        year,
        study_number,
    )
    cursor.execute(
    """
    INSERT INTO points( identifier, station, series, study, point_number,
    point_label, outlier, notes )
    VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        point,
        station,
        series,
        study,
        int(point_number),
        point_label,
        int(outlier),
        notes,
    )
    )
    return point

def set_point_value( cursor, point, quantity, value, averaging_system=None, \
                     measurement_technique=None, outlier=False, notes=None ):
    point_value, point_uncertainty = split_float( value )
    for avg_sys in create_averaging_systems_list( averaging_system ):
        cursor.execute(
        """
        INSERT INTO point_values( point, quantity, point_value,
        point_uncertainty, averaging_system, measurement_technique, outlier,
        notes )
        VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(point),
            str(quantity),
            point_value,
            point_uncertainty,
            avg_sys,
            measurement_technique,
            int(outlier),
            notes,
        )
        )

def get_point_value( cursor, point, quantity,               \
                     averaging_system=ANY_AVERAGING_SYSTEM, \
                     measurement_technique=MT_ROOT, ):
    if ( averaging_system == ANY_AVERAGING_SYSTEM ):
        if ( measurement_technique == MT_ROOT ):
            cursor.execute(
            """
            SELECT point_value, point_uncertainty FROM point_values WHERE
            point=?  AND quantity=? LIMIT 1;
            """,
            (
                sanitize_identifier(point),
                str(quantity),
            )
            )
        else:
            cursor.execute(
            """
            SELECT point_value, point_uncertainty FROM point_values WHERE
            point=?  AND quantity=? AND measurement_technique=? LIMIT 1;
            """,
            (
                sanitize_identifier(point),
                str(quantity),
                measurement_technique,
            )
            )
    else:
        if ( measurement_technique == MT_ROOT ):
            cursor.execute(
            """
            SELECT point_value, point_uncertainty FROM point_values WHERE
            point=?  AND quantity=? AND averaging_system=? LIMIT 1;
            """,
            (
                sanitize_identifier(point),
                str(quantity),
                averaging_system,
            )
            )
        else:
            cursor.execute(
            """
            SELECT point_value, point_uncertainty FROM point_values WHERE
            point=?  AND quantity=? AND averaging_system=? AND
            measurement_technique=? LIMIT 1;
            """,
            (
                sanitize_identifier(point),
                str(quantity),
                averaging_system,
                measurement_technique,
            )
            )
    return fetch_float( cursor )

def get_twin_profiles( cursor, station, quantity1, quantity2 ):
    cursor.execute(
    """
    SELECT point FROM point_values WHERE point LIKE ? AND quantity=? AND
    outlier=0 INTERSECT SELECT point FROM point_values WHERE point LIKE ? AND
    quantity=? AND outlier=0 ORDER BY point;
    """,
    (
        sanitize_identifier(station)+'%',
        str(quantity1),
        sanitize_identifier(station)+'%',
        str(quantity2),
    )
    )
    results = cursor.fetchall()

    points = []
    for result in results:
        points.append( result[0] )
    n_points = len(points)

    profile1 = []
    profile2 = []
    for point in points:
        profile1.append( get_point_value(
            cursor,
            point,
            quantity1,
        ) )
        profile2.append( get_point_value(
            cursor,
            point,
            quantity2,
        ) )

    return np.array(profile1), np.array(profile2)

def locate_labeled_point( cursor, station, label ):
    cursor.execute(
    """
    SELECT identifier FROM points WHERE identifier LIKE ? AND point_label=?
    ORDER BY identifier LIMIT 1;
    """,
    (
        sanitize_identifier(station)+'%',
        str(label),
    )
    )
    result = cursor.fetchone()
    return result[0]

def set_labeled_value( cursor, station, quantity, label, value,           \
                       averaging_system=None, measurement_technique=None, \
                       outlier=False, notes=None ):
    set_point_value(
        cursor,
        locate_labeled_point( cursor, station, label ),
        quantity,
        value,
        averaging_system=averaging_system,
        measurement_technique=measurement_technique,
        outlier=outlier,
        notes=notes,
    )

def get_labeled_value( cursor, station, quantity, label,    \
                     averaging_system=ANY_AVERAGING_SYSTEM, \
                     measurement_technique=MT_ROOT, ):
    return get_point_value(
        cursor,
        locate_labeled_point( cursor, station, label ),
        quantity,
        averaging_system=averaging_system,
        measurement_technique=measurement_technique,
    )

def add_working_fluid_component( cursor, series, fluid ):
    cursor.execute(
    """
    INSERT INTO components( series, fluid )
    VALUES( ?, ? );
    """,
    ( sanitize_identifier(series), str(fluid), )
    )

def set_working_fluid_name( cursor, series, name ):
    cursor.execute(
    """
    INSERT INTO components( series, name )
    VALUES( ?, ? );
    """,
    ( sanitize_identifier(series), str(name), )
    )

def add_air_components( cursor, series ):
    for fluid in AIR_COMPONENTS:
        add_working_fluid_component( cursor, series, fluid )

def get_working_fluid_components( cursor, series ):
    cursor.execute(
    """
    SELECT fluid FROM components WHERE series=? ORDER BY fluid;
    """,
    ( sanitize_identifier(series), )
    )
    components = []
    for component in cursor.fetchall():
        if ( component[0] != None ):
            components.append( str(component[0]) )
    return components

def get_working_fluid_name( cursor, series ):
    components = get_working_fluid_components( cursor, series )
    n_components = len(components)
    if not components:
        cursor.execute(
        """
        SELECT name FROM components WHERE series=? LIMIT 1;
        """,
        ( sanitize_identifier(series), )
        )
        result = cursor.fetchone()
        return result[0]
    else:
        if all( comp in components for comp in AIR_COMPONENTS ):
            return "air (g)"
        elif ( n_components == 1 ):
            cursor.execute(
            """
            SELECT fluid_name, phase FROM fluids WHERE identifier=? LIMIT 1;
            """,
            ( str(components[0]), )
            )
            result = cursor.fetchone()
            return "{:s} ({:s})".format( result[0], result[1] )
        else:
            name = "mixture of "
            i_component = 0
            for component in components:
                cursor.execute(
                """
                SELECT fluid_name, phase FROM fluids WHERE identifier=?
                LIMIT 1;
                """,
                ( str(component), )
                )
                result = cursor.fetchone()
                name += "{:s} ({:s})".format( result[0], result[1] )
                i_component += 1
                if ( i_component != n_components ):
                    name += " and "
            return name

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

def calculate_molar_mass_of_molecular_formula( cursor, formula ):
    element_counts = extract_element_counts( formula )
    molar_mass      = 0.0
    for element in element_counts:
        count = element_counts[element]
        cursor.execute(
        """
        SELECT atomic_weight FROM elements WHERE element_symbol=?
        """,
        ( element, )
        )
        result = cursor.fetchone()
        atomic_weight = float(result[0])
        molar_mass += count * 1.0e-3 * atomic_weight
    return molar_mass

def mark_station_as_periodic( cursor, station, \
                              streamwise=True, spanwise=False ):
    if ( streamwise ):
        cursor.execute(
        """
        UPDATE stations
        SET previous_streamwise_station=?, next_streamwise_station=?
        WHERE identifier=?;
        """,
        (
            sanitize_identifier( station ),
            sanitize_identifier( station ),
            sanitize_identifier( station ),
        )
        )
    if ( spanwise ):
        cursor.execute(
        """
        UPDATE stations
        SET previous_spanwise_station=?, next_spanwise_station=?
        WHERE identifier=?;
        """,
        (
            sanitize_identifier( station ),
            sanitize_identifier( station ),
            sanitize_identifier( station ),
        )
        )

def count_studies( identifiers ):
    studies = {}
    for identifier in identifiers:
        study = truncate_to_study( identifier )
        if ( study not in studies ):
            studies[study] = 1
        else:
            studies[study] += 1
    return studies

# TODO: Later, make the pressure a required argument.
def ideal_gas_mass_density( temperature,                            \
                            pressure=STANDARD_ATMOSPHERIC_PRESSURE, \
                            specific_gas_constant=DRY_AIR_SPECIFIC_GAS_CONSTANT, ):
    return pressure / ( specific_gas_constant * temperature )
def ideal_gas_speed_of_sound( temperature, \
        heat_capacity_ratio=DRY_AIR_HEAT_CAPACITY_RATIO, \
        specific_gas_constant=DRY_AIR_SPECIFIC_GAS_CONSTANT, ):
    return ( heat_capacity_ratio * specific_gas_constant * temperature )**0.5

def fahrenheit_to_kelvin( fahrenheit ):
    return ( fahrenheit - 32.0 ) / 1.8 + ABSOLUTE_ZERO

# Air is the default.
def sutherlands_law_dynamic_viscosity( temperature, T_0=273.0, mu_0=1.716e-5, \
                                       S=111.0 ):
    return mu_0 * ( temperature / T_0 )**1.5 * ( T_0 + S ) / ( temperature + S )

# TODO: Find a better method.
def liquid_water_speed_of_sound( temperature ):
    return ( 1481.0 - 1447.0 ) * ( temperature - 263.15 ) / 10.0 + 1447.0

# TODO: Change this.
def liquid_water_mass_density( temperature ):
    return ( 998.0 - 1000.0 ) * ( temperature - ABSOLUTE_ZERO ) / 20.0 + 1000.0

# TODO: Change this.
def liquid_water_dynamic_viscosity( temperature ):
    return ( 1.002e-3 - 1.792e-3 ) * ( temperature - ABSOLUTE_ZERO ) / 20.0 + 1.792e-3

