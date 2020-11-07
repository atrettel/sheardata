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

# Averaging systems
ANY_AVERAGING_SYSTEM              = "ANY"
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
SHEAR_FLOW_CLASS           = "S"
UNCLASSIFIED_FLOW_CLASS    = "U"
WAKE_FLOW_CLASS            = "W"

# Flow regimes
LAMINAR_FLOW_REGIME      = "LA"
TRANSITIONAL_FLOW_REGIME = "TR"
TURBULENT_FLOW_REGIME    = "TU"

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

# Geometries
ELLIPTICAL_GEOMETRY  = "E"
RECTANGULAR_GEOMETRY = "R"

# Measurement techniques
ANY_MEASUREMENT_TECHNIQUE                      = "ANY"
ASSUMPTION_MEASUREMENT_TECHNIQUE               = "A"
CALCULATION_MEASUREMENT_TECHNIQUE              = "C"
ESTIMATION_MEASUREMENT_TECHNIQUE               = "E"
FLOATING_ELEMENT_BALANCE_MEASUREMENT_TECHNIQUE = "FEB"
IMPACT_TUBE_MEASUREMENT_TECHNIQUE              = "IT"
PITOT_STATIC_TUBE_MEASUREMENT_TECHNIQUE        = "PST"
STATIC_PRESSURE_TAP_MEASUREMENT_TECHNIQUE      = "SPT"

# Point labels
CENTER_LINE_POINT_LABEL = "CL"
EDGE_POINT_LABEL        = "E"
WALL_POINT_LABEL        = "W"

# Quantities, series
ANGLE_OF_ATTACK_QUANTITY                = "alpha"
BODY_REYNOLDS_NUMBER_QUANTITY           = "Re_inf"
BODY_STROUHAL_NUMBER_QUANTITY           = "Sr"
DEVELOPMENT_LENGTH_QUANTITY             = "L_d"
DISTANCE_BETWEEN_PRESSURE_TAPS_QUANTITY = "L_p"
DRAG_COEFFICIENT_QUANTITY               = "C_D"
DRAG_FORCE_QUANTITY                     = "F_D"
FREESTREAM_MACH_NUMBER                  = "Ma_inf"
FREESTREAM_SPEED_OF_SOUND_QUANTITY      = "a_inf"
FREESTREAM_TEMPERATURE_QUANTITY         = "T_inf"
FREESTREAM_VELOCITY_QUANTITY            = "u_inf"
LIFT_COEFFICIENT_QUANTITY               = "C_L"
LIFT_FORCE_QUANTITY                     = "F_L"
LIFT_TO_DRAG_RATIO_QUANTITY             = "L/D"
MASS_FLOW_RATE_QUANTITY                 = "mdot"
TEST_LENGTH_QUANTITY                    = "L_t"
VOLUME_FLOW_RATE_QUANTITY               = "Vdot"

# Quantities, station
ASPECT_RATIO_QUANTITY          = "AR"
BULK_VELOCITY_QUANTITY         = "u_b"
CROSS_SECTIONAL_AREA_QUANTITY  = "A"
EQUILIBRIUM_PARAMETER_QUANTITY = "PI"
HEIGHT_QUANTITY                = "h"
HYDRAULIC_DIAMETER_QUANTITY    = "D_H"
INNER_DIAMETER_QUANTITY        = "D_i"
OUTER_DIAMETER_QUANTITY        = "D_o"
PRESSURE_GRADIENT_QUANTITY     = "PG"
RECOVERY_FACTOR_QUANTITY       = "RF"
WETTED_PERIMETER_QUANTITY      = "P"
WIDTH_QUANTITY                 = "w"

# Quantities, wall point
DARCY_FRICTION_FACTOR_QUANTITY           = "f_D"
FANNING_FRICTION_FACTOR_QUANTITY         = "f"
FRICTION_MACH_NUMBER_QUANTITY            = "Ma_tau"
FRICTION_REYNOLDS_NUMBER_QUANTITY        = "Re_tau"
FRICTION_TEMPERATURE_QUANTITY            = "T_tau"
FRICTION_VELOCITY_QUANTITY               = "u_tau"
LOCAL_SKIN_FRICTION_COEFFICIENT_QUANTITY = "c_f"
PRESSURE_COEFFICIENT_QUANTITY            = "C_p"
ROUGHNESS_HEIGHT_QUANTITY                = "eps"
SPANWISE_WALL_CURVATURE                  = "kappa_z"
STREAMWISE_WALL_CURVATURE                = "kappa_x"
VISCOUS_LENGTH_SCALE                     = "l_nu"

# Quantities, point
DISTANCE_FROM_WALL_QUANTITY               = "y"
DYNAMIC_VISCOSITY_QUANTITY                = "mu"
HEAT_CAPACITY_RATIO_QUANTITY              = "gamma"
KINEMATIC_VISCOSITY_QUANTITY              = "nu"
MACH_NUMBER_QUANTITY                      = "Ma"
MASS_DENSITY_QUANTITY                     = "rho"
PRANDTL_NUMBER_QUANTITY                   = "Pr"
PRESSURE_QUANTITY                         = "p"
SHEAR_STRESS_QUANTITY                     = "tau"
SPANWISE_COORDINATE_QUANTITY              = "Z"
SPANWISE_VELOCITY_QUANTITY                = "w"
SPECIFIC_ENTHALPY_QUANTITY                = "h"
SPECIFIC_INTERNAL_ENERGY_QUANTITY         = "e"
SPECIFIC_ISOBARIC_HEAT_CAPACITY_QUANTITY  = "c_p"
SPECIFIC_ISOCHORIC_HEAT_CAPACITY_QUANTITY = "c_v"
SPECIFIC_TOTAL_ENTHALPY_QUANTITY          = "h_0"
SPECIFIC_TOTAL_INTERNAL_ENERGY_QUANTITY   = "e_0"
SPECIFIC_VOLUME_QUANTITY                  = "vbar"
SPEED_OF_SOUND_QUANTITY                   = "a"
SPEED_QUANTITY                            = "V"
STREAMWISE_COORDINATE_QUANTITY            = "X"
STREAMWISE_VELOCITY_QUANTITY              = "u"
TEMPERATURE_QUANTITY                      = "T"
TOTAL_PRESSURE_QUANTITY                   = "p_0"
TOTAL_TEMPERATURE_QUANTITY                = "T_0"
TRANSVERSE_COORDINATE_QUANTITY            = "Y"
TRANSVERSE_VELOCITY_QUANTITY              = "v"

AMOUNT_CONCENTRATION_PREFIX = "C_"
AMOUNT_FRACTION_PREFIX      = "X_"
MASS_CONCENTRATION_PREFIX   = "rho_"
MASS_FRACTION_PREFIX        = "Y_"

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
        sanitize_identifier(study),
        str(quantity),
        study_value,
        study_uncertainty,
        averaging_system,
        measurement_technique,
        int(outlier),
        notes,
    )
    )

def get_study_value( cursor, study, quantity,               \
                     averaging_system=ANY_AVERAGING_SYSTEM, \
                     measurement_technique=ANY_MEASUREMENT_TECHNIQUE, ):
    if ( averaging_system == ANY_AVERAGING_SYSTEM ):
        if ( measurement_technique == ANY_MEASUREMENT_TECHNIQUE ):
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
        if ( measurement_technique == ANY_MEASUREMENT_TECHNIQUE ):
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

def add_series( cursor, flow_class, year, study_number, series_number, \
                number_of_dimensions, coordinate_system ):
    identifier = identify_series(
        flow_class,
        year,
        study_number,
        series_number,
    )
    cursor.execute(
    """
    INSERT INTO series( identifier, series_number, number_of_dimensions,
    coordinate_system ) VALUES( ?, ?, ?, ? );
    """,
    (
        identifier,
        int(series_number),
        int(number_of_dimensions),
        str(coordinate_system),
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
    cursor.execute(
    """
    INSERT INTO series_values( series, quantity, series_value,
    series_uncertainty, averaging_system, measurement_technique, outlier, notes
    ) VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        sanitize_identifier(series),
        str(quantity),
        series_value,
        series_uncertainty,
        averaging_system,
        measurement_technique,
        int(outlier),
        notes,
    )
    )

def get_series_value( cursor, series, quantity,              \
                      averaging_system=ANY_AVERAGING_SYSTEM, \
                      measurement_technique=ANY_MEASUREMENT_TECHNIQUE, ):
    if ( averaging_system == ANY_AVERAGING_SYSTEM ):
        if ( measurement_technique == ANY_MEASUREMENT_TECHNIQUE ):
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
        if ( measurement_technique == ANY_MEASUREMENT_TECHNIQUE ):
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

def set_station_value( cursor, station, quantity, value, averaging_system=None, \
                     measurement_technique=None, outlier=False, notes=None ):
    station_value, station_uncertainty = split_float( value )
    cursor.execute(
    """
    INSERT INTO station_values( station, quantity, station_value,
    station_uncertainty, averaging_system, measurement_technique, outlier,
    notes ) VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        sanitize_identifier(station),
        str(quantity),
        station_value,
        station_uncertainty,
        averaging_system,
        measurement_technique,
        int(outlier),
        notes,
    )
    )

def get_station_value( cursor, station, quantity,             \
                       averaging_system=ANY_AVERAGING_SYSTEM, \
                       measurement_technique=ANY_MEASUREMENT_TECHNIQUE, ):
    if ( averaging_system == ANY_AVERAGING_SYSTEM ):
        if ( measurement_technique == ANY_MEASUREMENT_TECHNIQUE ):
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
        if ( measurement_technique == ANY_MEASUREMENT_TECHNIQUE ):
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
        point_label,
    )
    )
    return identifier

def set_point_value( cursor, point, quantity, value, averaging_system=None, \
                     measurement_technique=None, outlier=False, notes=None ):
    point_value, point_uncertainty = split_float( value )
    cursor.execute(
    """
    INSERT INTO point_values( point, quantity, point_value,
    point_uncertainty, averaging_system, measurement_technique, outlier,
    notes ) VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        sanitize_identifier(point),
        str(quantity),
        point_value,
        point_uncertainty,
        averaging_system,
        measurement_technique,
        int(outlier),
        notes,
    )
    )

def get_point_value( cursor, point, quantity,               \
                     averaging_system=ANY_AVERAGING_SYSTEM, \
                     measurement_technique=ANY_MEASUREMENT_TECHNIQUE, ):
    if ( averaging_system == ANY_AVERAGING_SYSTEM ):
        if ( measurement_technique == ANY_MEASUREMENT_TECHNIQUE ):
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
        if ( measurement_technique == ANY_MEASUREMENT_TECHNIQUE ):
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
                     measurement_technique=ANY_MEASUREMENT_TECHNIQUE, ):
    return get_point_value(
        cursor,
        locate_labeled_point( cursor, station, label ),
        quantity,
        averaging_system=averaging_system,
        measurement_technique=measurement_technique,
    )

def add_component( cursor, series, fluid ):
    cursor.execute(
    """
    INSERT INTO components( series, fluid )
    VALUES( ?, ? );
    """,
    ( sanitize_identifier(series), str(fluid), )
    )

def add_air_components( cursor, series ):
    for fluid in [ NITROGEN_GAS,
                   OXYGEN_GAS,
                   ARGON_GAS,
                   CARBON_DIOXIDE_GAS,
                   WATER_VAPOR, ]:
        add_component( cursor, series, fluid )

def get_components( cursor, series ):
    cursor.execute(
    """
    SELECT fluid FROM components WHERE series=? ORDER BY fluid;
    """,
    ( sanitize_identifier(series), )
    )
    components = []
    for component in cursor.fetchall():
        components.append( str(component[0]) )
    return components
