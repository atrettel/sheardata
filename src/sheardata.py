#!/usr/bin/env python3

# Copyright (C) 2020-2021 Andrew Trettel
#
# SPDX-License-Identifier: MIT

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

# Value types
VT_ANY_AVERAGE              = "A"
VT_BOTH_AVERAGES            = "B"
VT_DENSITY_WEIGHTED_AVERAGE = "D"
VT_UNAVERAGED_VALUE         = "V"
VT_UNWEIGHTED_AVERAGE       = "U"

# Coordinate systems
CS_CYLINDRICAL = "XRT"
CS_RECTANGULAR = "XYZ"

# Directions
#
# Keep things as abstract but precise as possible.  The only times these
# numbers should change is if a user prefers to say that the transverse
# direction is direction 3.  These variables are left here to provide the
# option of redefining the order (if deemed necessary).
D_STREAMWISE = 1
D_TRANSVERSE = 2 # 2 is the engineering convention;
                 # 3 is the geophysical convention.
D_SPANWISE   = (3 if D_TRANSVERSE == 2 else 2 )

assert( D_STREAMWISE != D_TRANSVERSE )
assert( D_STREAMWISE !=   D_SPANWISE )
assert( D_TRANSVERSE !=   D_SPANWISE )

STREAMWISE_COORDINATE_SYMBOL = "x"
TRANSVERSE_COORDINATE_SYMBOL = ("y" if D_TRANSVERSE == 2 else "z")
SPANWISE_COORDINATE_SYMBOL   = ("z" if D_TRANSVERSE == 2 else "y")

STREAMWISE_VELOCITY_SYMBOL = "u"
TRANSVERSE_VELOCITY_SYMBOL = ("v" if D_TRANSVERSE == 2 else "w")
SPANWISE_VELOCITY_SYMBOL   = ("w" if D_TRANSVERSE == 2 else "v")

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
FR_LAMINAR      = "lam"
FR_TRANSITIONAL = "trans"
FR_TURBULENT    = "turb"

# Phases
PH_GAS    = "g"
PH_LIQUID = "l"
PH_SOLID  = "s"

# Geometries
GM_ELLIPTICAL  = "E"
GM_RECTANGULAR = "R"

# Measurement techniques (and other sources of information)
MT_APPROXIMATION                            = "APP"
MT_ASSUMPTION                               = "ASM"
MT_CALCULATION                              = "CLC"
MT_CLAIM                                    = "CLM"
MT_CLAUSER_METHOD                           = "TCC"
MT_CONSTANT_CURRENT_HOT_WIRE_ANEMOMETRY     = "HWC"
MT_CONSTANT_TEMPERATURE_HOT_WIRE_ANEMOMETRY = "HWT"
MT_DIFFERENTIAL_PRESSURE_METHOD             = "PTA"
MT_DIRECT_INJECTION_METHOD                  = "DIJ"
MT_FLOATING_ELEMENT_BALANCE                 = "FEB"
MT_FLOW_RATE_MEASUREMENT                    = "FQM"
MT_HOT_WIRE_ANEMOMETRY                      = "HWA"
MT_IMPACT_TUBE                              = "PTI"
MT_INDEX_OF_REFRACTION_METHOD               = "ORI"
MT_LASER_DOPPLER_ANEMOMETRY                 = "LDA"
MT_MACH_ZEHNDER_INTERFEROMETRY              = "MZI"
MT_MOMENTUM_BALANCE                         = "TMB"
MT_OBSERVATION                              = "OBS"
MT_OPTICAL_METHOD                           = "OPT"
MT_PARTICLE_IMAGE_VELOCIMETRY               = "PIV"
MT_PITOT_STATIC_TUBE                        = "PST"
MT_PRESTON_TUBE                             = "TPT"
MT_REASONING                                = "RSN"
MT_ROOT                                     = "RTX"
MT_SCHLIEREN_PHOTOGRAPHY                    = "SCH"
MT_SHADOWGRAPH_PHOTOGRAPHY                  = "SHD"
MT_STANTON_TUBE                             = "TST"
MT_THERMAL_ANEMOMETRY                       = "TAN"
MT_VELOCITY_PROFILE_METHOD                  = "TVP"
MT_VISCOUS_SUBLAYER_SLOPE_METHOD            = "TVS"
MT_WALL_SHEAR_STRESS_METHOD                 = "TWL"
MT_WEIGHING_METHOD                          = "QWM"
MT_ZEROTH_ORDER_APPROXIMATION               = "AP0"

# Point labels
PL_CENTER_LINE = "CL"
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

# Quantities, series
Q_ANGLE_OF_ATTACK                = "AOA"
Q_BODY_HEIGHT                    = "h_b"
Q_BODY_LENGTH                    = "L_b"
Q_BODY_REYNOLDS_NUMBER           = "Re_inf"
Q_BODY_STROUHAL_NUMBER           = "Sr"
Q_BODY_WIDTH                     = "w_b"
Q_DISTANCE_BETWEEN_PRESSURE_TAPS = "L_p"
Q_DRAG_COEFFICIENT               = "C_D"
Q_DRAG_FORCE                     = "F_D"
Q_FREESTREAM_MACH_NUMBER         = "Ma_inf"
Q_FREESTREAM_SPEED_OF_SOUND      = "a_inf"
Q_FREESTREAM_TEMPERATURE         = "T_inf"
Q_FREESTREAM_VELOCITY            = "U_inf"
Q_LEADING_EDGE_LENGTH            = "L_le"
Q_LEADING_EDGE_RADIUS            = "R_le"
Q_LIFT_COEFFICIENT               = "C_L"
Q_LIFT_FORCE                     = "F_L"
Q_LIFT_TO_DRAG_RATIO             = "L/D"
Q_MASS_FLOW_RATE                 = "mdot"
Q_SPANWISE_NUMBER_OF_POINTS      = "N_{:s}".format(SPANWISE_COORDINATE_SYMBOL)
Q_STREAMWISE_NUMBER_OF_POINTS    = "N_{:s}".format(STREAMWISE_COORDINATE_SYMBOL)
Q_TEST_LENGTH                    = "L_t"
Q_TRANSVERSE_NUMBER_OF_POINTS    = "N_{:s}".format(TRANSVERSE_COORDINATE_SYMBOL)
Q_VOLUMETRIC_FLOW_RATE           = "Vdot"

Q_BODY_DIMENSIONS = {
    D_STREAMWISE: Q_BODY_LENGTH,
    D_TRANSVERSE: Q_BODY_HEIGHT,
    D_SPANWISE:   Q_BODY_WIDTH,
}

Q_NUMBER_OF_POINTS = {
    D_STREAMWISE: Q_STREAMWISE_NUMBER_OF_POINTS,
    D_TRANSVERSE: Q_TRANSVERSE_NUMBER_OF_POINTS,
    D_SPANWISE:     Q_SPANWISE_NUMBER_OF_POINTS,
}

# Quantities, station
Q_ASPECT_RATIO                           = "AR"
Q_BULK_DYNAMIC_VISCOSITY                 = "mu_b"
Q_BULK_KINEMATIC_VISCOSITY               = "nu_b"
Q_BULK_MACH_NUMBER                       = "Ma_b"
Q_BULK_MASS_DENSITY                      = "rho_b"
Q_BULK_REYNOLDS_NUMBER                   = "Re_b"
Q_BULK_SPEED_OF_SOUND                    = "a_b"
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
Q_MOMENTUM_INTEGRAL_LHS                  = "P_l"
Q_MOMENTUM_INTEGRAL_RHS                  = "P_r"
Q_MOMENTUM_THICKNESS                     = "delta_2"
Q_MOMENTUM_THICKNESS_REYNOLDS_NUMBER     = "Re_delta_2"
Q_OUTER_DIAMETER                         = "D_o"
Q_OUTER_LAYER_DEVELOPMENT_LENGTH         = "L_d/D_H"
Q_RECOVERY_FACTOR                        = "RF"
Q_SHAPE_FACTOR_1_TO_2                    = "H_12"
Q_SHAPE_FACTOR_3_TO_2                    = "H_32"
Q_SPANWISE_PRESSURE_GRADIENT             = "PG_{:s}".format(SPANWISE_COORDINATE_SYMBOL)
Q_STREAMWISE_COORDINATE_REYNOLDS_NUMBER  = "Re_{:s}".format(STREAMWISE_COORDINATE_SYMBOL)
Q_STREAMWISE_PRESSURE_GRADIENT           = "PG_{:s}".format(STREAMWISE_COORDINATE_SYMBOL)
Q_TRANSVERSE_PRESSURE_GRADIENT           = "PG_{:s}".format(TRANSVERSE_COORDINATE_SYMBOL)
Q_WETTED_PERIMETER                       = "P"
Q_WIDTH                                  = "w"

Q_PRESSURE_GRADIENT = {
    D_STREAMWISE: Q_STREAMWISE_PRESSURE_GRADIENT,
    D_TRANSVERSE: Q_TRANSVERSE_PRESSURE_GRADIENT,
    D_SPANWISE:     Q_SPANWISE_PRESSURE_GRADIENT,
}

# Quantities, wall point
Q_AVERAGE_SKIN_FRICTION_COEFFICIENT     = "C_tau"
Q_DARCY_FRICTION_FACTOR                 = "f_D"
Q_FANNING_FRICTION_FACTOR               = "f"
Q_FRICTION_MACH_NUMBER                  = "Ma_tau"
Q_FRICTION_REYNOLDS_NUMBER              = "Re_tau"
Q_FRICTION_TEMPERATURE                  = "T_tau"
Q_FRICTION_VELOCITY                     = "U_tau"
Q_HEAT_TRANSFER_COEFFICIENT             = "c_q"
Q_INNER_LAYER_HEAT_FLUX                 = "B_q"
Q_INNER_LAYER_ROUGHNESS_HEIGHT          = "eps+"
Q_LOCAL_SKIN_FRICTION_COEFFICIENT       = "c_tau"
Q_OUTER_LAYER_ROUGHNESS_HEIGHT          = "eps/D_H"
Q_PRESSURE_COEFFICIENT                  = "C_p"
Q_ROUGHNESS_HEIGHT                      = "eps"
Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER   = "Re_tau*"
Q_SPANWISE_WALL_CURVATURE               = "kappa_{:s}".format(SPANWISE_COORDINATE_SYMBOL)
Q_STREAMWISE_WALL_CURVATURE             = "kappa_{:s}".format(STREAMWISE_COORDINATE_SYMBOL)
Q_VISCOUS_LENGTH_SCALE                  = "l_nu"

# Quantities, point
Q_DILATATION_RATE                  = "Thetadot"
Q_DISTANCE_FROM_WALL               = TRANSVERSE_COORDINATE_SYMBOL
Q_DYNAMIC_VISCOSITY                = "mu"
Q_HEAT_CAPACITY_RATIO              = "gamma"
Q_HEAT_FLUX                        = "q"
Q_INNER_LAYER_COORDINATE           = "{:s}+".format(TRANSVERSE_COORDINATE_SYMBOL)
Q_INNER_LAYER_TEMPERATURE          = "T+"
Q_INNER_LAYER_VELOCITY             = "U+"
Q_INNER_LAYER_VELOCITY_DEFECT      = "deltaU+"
Q_KINEMATIC_VISCOSITY              = "nu"
Q_MACH_NUMBER                      = "Ma"
Q_MASS_DENSITY                     = "rho"
Q_OUTER_LAYER_COORDINATE           = "eta"
Q_OUTER_LAYER_TEMPERATURE          = "Theta"
Q_OUTER_LAYER_VELOCITY             = "F"
Q_OUTER_LAYER_VELOCITY_DEFECT      = "deltaU+/delta"
Q_PRANDTL_NUMBER                   = "Pr"
Q_PRESSURE                         = "p"
Q_SEMI_LOCAL_COORDINATE            = "{:s}*".format(TRANSVERSE_COORDINATE_SYMBOL)
Q_SPANWISE_COORDINATE              = SPANWISE_COORDINATE_SYMBOL.upper()
Q_SPANWISE_VELOCITY                = SPANWISE_VELOCITY_SYMBOL.upper()
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
Q_STREAMWISE_COORDINATE            = STREAMWISE_COORDINATE_SYMBOL.upper()
Q_STREAMWISE_VELOCITY              = STREAMWISE_VELOCITY_SYMBOL.upper()
Q_TEMPERATURE                      = "T"
Q_THERMAL_CONDUCTIVITY             = "lambda"
Q_THERMAL_DIFFUSIVITY              = "alpha"
Q_TOTAL_PRESSURE                   = "p_0"
Q_TOTAL_TEMPERATURE                = "T_0"
Q_TRANSVERSE_COORDINATE            = TRANSVERSE_COORDINATE_SYMBOL.upper()
Q_TRANSVERSE_VELOCITY              = TRANSVERSE_VELOCITY_SYMBOL.upper()
Q_VELOCITY_DEFECT                  = "deltaU"

# TODO: Consider defining the numbers 1, 2, or 3 here as D_STREAMWISE, etc.
Q_COORDINATE = {
    D_STREAMWISE: Q_STREAMWISE_COORDINATE,
    D_TRANSVERSE: Q_TRANSVERSE_COORDINATE,
    D_SPANWISE:     Q_SPANWISE_COORDINATE,
}

Q_VELOCITY = {
    D_STREAMWISE: Q_STREAMWISE_VELOCITY,
    D_TRANSVERSE: Q_TRANSVERSE_VELOCITY,
    D_SPANWISE:     Q_SPANWISE_VELOCITY,
}

Q_VELOCITY_GRADIENT = {
    (D_STREAMWISE,D_STREAMWISE): "eps_{:s}{:s}".format(STREAMWISE_COORDINATE_SYMBOL,STREAMWISE_COORDINATE_SYMBOL),
    (D_STREAMWISE,D_TRANSVERSE): "eps_{:s}{:s}".format(STREAMWISE_COORDINATE_SYMBOL,TRANSVERSE_COORDINATE_SYMBOL),
    (D_STREAMWISE,D_SPANWISE  ): "eps_{:s}{:s}".format(STREAMWISE_COORDINATE_SYMBOL,  SPANWISE_COORDINATE_SYMBOL),
    (D_TRANSVERSE,D_STREAMWISE): "eps_{:s}{:s}".format(TRANSVERSE_COORDINATE_SYMBOL,STREAMWISE_COORDINATE_SYMBOL),
    (D_TRANSVERSE,D_TRANSVERSE): "eps_{:s}{:s}".format(TRANSVERSE_COORDINATE_SYMBOL,TRANSVERSE_COORDINATE_SYMBOL),
    (D_TRANSVERSE,D_SPANWISE  ): "eps_{:s}{:s}".format(TRANSVERSE_COORDINATE_SYMBOL,  SPANWISE_COORDINATE_SYMBOL),
    (D_SPANWISE,  D_STREAMWISE): "eps_{:s}{:s}".format(  SPANWISE_COORDINATE_SYMBOL,STREAMWISE_COORDINATE_SYMBOL),
    (D_SPANWISE,  D_TRANSVERSE): "eps_{:s}{:s}".format(  SPANWISE_COORDINATE_SYMBOL,TRANSVERSE_COORDINATE_SYMBOL),
    (D_SPANWISE,  D_SPANWISE  ): "eps_{:s}{:s}".format(  SPANWISE_COORDINATE_SYMBOL,  SPANWISE_COORDINATE_SYMBOL),
}

Q_STRESS = {
    (D_STREAMWISE,D_STREAMWISE): "sigma_{:s}{:s}".format(STREAMWISE_COORDINATE_SYMBOL,STREAMWISE_COORDINATE_SYMBOL),
    (D_STREAMWISE,D_TRANSVERSE):   "tau_{:s}{:s}".format(STREAMWISE_COORDINATE_SYMBOL,TRANSVERSE_COORDINATE_SYMBOL),
    (D_STREAMWISE,D_SPANWISE  ):   "tau_{:s}{:s}".format(STREAMWISE_COORDINATE_SYMBOL,  SPANWISE_COORDINATE_SYMBOL),
    (D_TRANSVERSE,D_STREAMWISE):   "tau_{:s}{:s}".format(TRANSVERSE_COORDINATE_SYMBOL,STREAMWISE_COORDINATE_SYMBOL),
    (D_TRANSVERSE,D_TRANSVERSE): "sigma_{:s}{:s}".format(TRANSVERSE_COORDINATE_SYMBOL,TRANSVERSE_COORDINATE_SYMBOL),
    (D_TRANSVERSE,D_SPANWISE  ):   "tau_{:s}{:s}".format(TRANSVERSE_COORDINATE_SYMBOL,  SPANWISE_COORDINATE_SYMBOL),
    (D_SPANWISE,  D_STREAMWISE):   "tau_{:s}{:s}".format(  SPANWISE_COORDINATE_SYMBOL,STREAMWISE_COORDINATE_SYMBOL),
    (D_SPANWISE,  D_TRANSVERSE):   "tau_{:s}{:s}".format(  SPANWISE_COORDINATE_SYMBOL,TRANSVERSE_COORDINATE_SYMBOL),
    (D_SPANWISE,  D_SPANWISE  ): "sigma_{:s}{:s}".format(  SPANWISE_COORDINATE_SYMBOL,  SPANWISE_COORDINATE_SYMBOL),
}

Q_SHEAR_STRESS = Q_STRESS[D_STREAMWISE,D_TRANSVERSE]

# Quantities, point, turbulence
Q_INNER_LAYER_SPECIFIC_TURBULENT_KINETIC_ENERGY      = "k+"
Q_MASS_DENSITY_AUTOCOVARIANCE                        = "rho'rho'"
Q_MORKOVIN_SCALED_SPECIFIC_TURBULENT_KINETIC_ENERGY  = "k*"
Q_NORMALIZED_MASS_DENSITY_AUTOCOVARIANCE             = "rho'rho'/rho^2"
Q_NORMALIZED_PRESSURE_AUTOCOVARIANCE                 = "p'p'/p^2"
Q_NORMALIZED_TEMPERATURE_AUTOCOVARIANCE              = "T'T'/T^2"
Q_PRESSURE_AUTOCOVARIANCE                            = "p'p'"
Q_SPECIFIC_TURBULENT_KINETIC_ENERGY                  = "k"
Q_TEMPERATURE_AUTOCOVARIANCE                         = "T'T'"

Q_VELOCITY_COVARIANCE = {
    (D_STREAMWISE,D_STREAMWISE): "({:s}'{:s}')".format(STREAMWISE_VELOCITY_SYMBOL,STREAMWISE_VELOCITY_SYMBOL),
    (D_STREAMWISE,D_TRANSVERSE): "({:s}'{:s}')".format(STREAMWISE_VELOCITY_SYMBOL,TRANSVERSE_VELOCITY_SYMBOL),
    (D_STREAMWISE,D_SPANWISE  ): "({:s}'{:s}')".format(STREAMWISE_VELOCITY_SYMBOL,  SPANWISE_VELOCITY_SYMBOL),
    (D_TRANSVERSE,D_STREAMWISE): "({:s}'{:s}')".format(TRANSVERSE_VELOCITY_SYMBOL,STREAMWISE_VELOCITY_SYMBOL),
    (D_TRANSVERSE,D_TRANSVERSE): "({:s}'{:s}')".format(TRANSVERSE_VELOCITY_SYMBOL,TRANSVERSE_VELOCITY_SYMBOL),
    (D_TRANSVERSE,D_SPANWISE  ): "({:s}'{:s}')".format(TRANSVERSE_VELOCITY_SYMBOL,  SPANWISE_VELOCITY_SYMBOL),
    (D_SPANWISE,  D_STREAMWISE): "({:s}'{:s}')".format(  SPANWISE_VELOCITY_SYMBOL,STREAMWISE_VELOCITY_SYMBOL),
    (D_SPANWISE,  D_TRANSVERSE): "({:s}'{:s}')".format(  SPANWISE_VELOCITY_SYMBOL,TRANSVERSE_VELOCITY_SYMBOL),
    (D_SPANWISE,  D_SPANWISE  ): "({:s}'{:s}')".format(  SPANWISE_VELOCITY_SYMBOL,  SPANWISE_VELOCITY_SYMBOL),
}

Q_INNER_LAYER_VELOCITY_COVARIANCE = {
    (D_STREAMWISE,D_STREAMWISE): "({:s}'{:s}')+".format(STREAMWISE_VELOCITY_SYMBOL,STREAMWISE_VELOCITY_SYMBOL),
    (D_STREAMWISE,D_TRANSVERSE): "({:s}'{:s}')+".format(STREAMWISE_VELOCITY_SYMBOL,TRANSVERSE_VELOCITY_SYMBOL),
    (D_STREAMWISE,D_SPANWISE  ): "({:s}'{:s}')+".format(STREAMWISE_VELOCITY_SYMBOL,  SPANWISE_VELOCITY_SYMBOL),
    (D_TRANSVERSE,D_STREAMWISE): "({:s}'{:s}')+".format(TRANSVERSE_VELOCITY_SYMBOL,STREAMWISE_VELOCITY_SYMBOL),
    (D_TRANSVERSE,D_TRANSVERSE): "({:s}'{:s}')+".format(TRANSVERSE_VELOCITY_SYMBOL,TRANSVERSE_VELOCITY_SYMBOL),
    (D_TRANSVERSE,D_SPANWISE  ): "({:s}'{:s}')+".format(TRANSVERSE_VELOCITY_SYMBOL,  SPANWISE_VELOCITY_SYMBOL),
    (D_SPANWISE,  D_STREAMWISE): "({:s}'{:s}')+".format(  SPANWISE_VELOCITY_SYMBOL,STREAMWISE_VELOCITY_SYMBOL),
    (D_SPANWISE,  D_TRANSVERSE): "({:s}'{:s}')+".format(  SPANWISE_VELOCITY_SYMBOL,TRANSVERSE_VELOCITY_SYMBOL),
    (D_SPANWISE,  D_SPANWISE  ): "({:s}'{:s}')+".format(  SPANWISE_VELOCITY_SYMBOL,  SPANWISE_VELOCITY_SYMBOL),
}

Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE = {
    (D_STREAMWISE,D_STREAMWISE): "({:s}'{:s}')*".format(STREAMWISE_VELOCITY_SYMBOL,STREAMWISE_VELOCITY_SYMBOL),
    (D_STREAMWISE,D_TRANSVERSE): "({:s}'{:s}')*".format(STREAMWISE_VELOCITY_SYMBOL,TRANSVERSE_VELOCITY_SYMBOL),
    (D_STREAMWISE,D_SPANWISE  ): "({:s}'{:s}')*".format(STREAMWISE_VELOCITY_SYMBOL,  SPANWISE_VELOCITY_SYMBOL),
    (D_TRANSVERSE,D_STREAMWISE): "({:s}'{:s}')*".format(TRANSVERSE_VELOCITY_SYMBOL,STREAMWISE_VELOCITY_SYMBOL),
    (D_TRANSVERSE,D_TRANSVERSE): "({:s}'{:s}')*".format(TRANSVERSE_VELOCITY_SYMBOL,TRANSVERSE_VELOCITY_SYMBOL),
    (D_TRANSVERSE,D_SPANWISE  ): "({:s}'{:s}')*".format(TRANSVERSE_VELOCITY_SYMBOL,  SPANWISE_VELOCITY_SYMBOL),
    (D_SPANWISE,  D_STREAMWISE): "({:s}'{:s}')*".format(  SPANWISE_VELOCITY_SYMBOL,STREAMWISE_VELOCITY_SYMBOL),
    (D_SPANWISE,  D_TRANSVERSE): "({:s}'{:s}')*".format(  SPANWISE_VELOCITY_SYMBOL,TRANSVERSE_VELOCITY_SYMBOL),
    (D_SPANWISE,  D_SPANWISE  ): "({:s}'{:s}')*".format(  SPANWISE_VELOCITY_SYMBOL,  SPANWISE_VELOCITY_SYMBOL),
}

# Quantities, point, ratios
Q_LOCAL_TO_BULK_STREAMWISE_VELOCITY_RATIO        = "u/u_b"
Q_LOCAL_TO_BULK_TEMPERATURE_RATIO                = "T/T_b"
Q_LOCAL_TO_CENTER_LINE_DYNAMIC_VISCOSITY_RATIO   = "mu/mu_c"
Q_LOCAL_TO_CENTER_LINE_MASS_DENSITY_RATIO        = "rho/rho_c"
Q_LOCAL_TO_CENTER_LINE_STREAMWISE_VELOCITY_RATIO = "u/u_c"
Q_LOCAL_TO_CENTER_LINE_TEMPERATURE_RATIO         = "T/T_c"
Q_LOCAL_TO_EDGE_DYNAMIC_VISCOSITY_RATIO          = "mu/mu_e"
Q_LOCAL_TO_EDGE_MASS_DENSITY_RATIO               = "rho/rho_e"
Q_LOCAL_TO_EDGE_STREAMWISE_VELOCITY_RATIO        = "u/u_e"
Q_LOCAL_TO_EDGE_TEMPERATURE_RATIO                = "T/T_e"
Q_LOCAL_TO_RECOVERY_TEMPERATURE_RATIO            = "T/T_r"
Q_LOCAL_TO_WALL_DYNAMIC_VISCOSITY_RATIO          = "mu/mu_w"
Q_LOCAL_TO_WALL_MASS_DENSITY_RATIO               = "rho/rho_w"
Q_LOCAL_TO_WALL_STREAMWISE_VELOCITY_RATIO        = "u/u_w"
Q_LOCAL_TO_WALL_TEMPERATURE_RATIO                = "T/T_w"

INCOMPRESSIBLE_RATIO_PROFILES = [
    Q_LOCAL_TO_CENTER_LINE_DYNAMIC_VISCOSITY_RATIO,
    Q_LOCAL_TO_CENTER_LINE_MASS_DENSITY_RATIO,
    Q_LOCAL_TO_CENTER_LINE_TEMPERATURE_RATIO,
    Q_LOCAL_TO_EDGE_DYNAMIC_VISCOSITY_RATIO,
    Q_LOCAL_TO_EDGE_MASS_DENSITY_RATIO,
    Q_LOCAL_TO_EDGE_TEMPERATURE_RATIO,
    Q_LOCAL_TO_RECOVERY_TEMPERATURE_RATIO,
    Q_LOCAL_TO_WALL_DYNAMIC_VISCOSITY_RATIO,
    Q_LOCAL_TO_WALL_MASS_DENSITY_RATIO,
    Q_LOCAL_TO_WALL_TEMPERATURE_RATIO,
]

# Study types
ST_DIRECT_NUMERICAL_SIMULATION = "DNS"
ST_EXPERIMENT                  = "EXP"
ST_LARGE_EDDY_SIMULATION       = "LES"

# Compilations
C_SELF    = 0 # Originator
C_CH_1969 = 1 # Coles and Hirst
C_BE_1973 = 2 # Birch and Eggers
C_FF_1977 = 3 # Fernholz and Finley

# Source classifications
PRIMARY_SOURCE   = 1
SECONDARY_SOURCE = 2

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
               outlier=False, notes=[], identifiers={}, ):
    study = identify_study( flow_class, year, study_number )
    cursor.execute(
    """
    INSERT INTO studies( identifier, flow_class, year, study_number,
                         study_type, outlier )
    VALUES( ?, ?, ?, ?, ?, ? );
    """,
    (
        study,
        str(flow_class),
        int(year),
        int(study_number),
        str(study_type),
        int(outlier),
    )
    )

    for note in notes:
        cursor.execute(
        """
        INSERT INTO study_notes( study, note )
        VALUES( ?, ? );
        """,
        (
            study,
            int(note),
        )
        )

    for compilation in identifiers:
        cursor.execute(
        """
        INSERT INTO study_identifiers( study, compilation, identifier )
        VALUES( ?, ?, ? );
        """,
        (
            study,
            int(compilation),
            identifiers[compilation],
        )
        )

    return study

def update_study_description( cursor, identifier, description ):
    cursor.execute(
    """
    UPDATE studies
    SET description=?
    WHERE identifier=?;
    """,
    (
        description.strip(),
        sanitize_identifier(identifier),
    )
    )

def update_study_provenance( cursor, identifier, provenance ):
    cursor.execute(
    """
    UPDATE studies
    SET provenance=?
    WHERE identifier=?:
    """,
    (
        provenance.strip(),
        sanitize_identifier(identifier),
    )
    )

def create_value_types_list( value_type ):
    if ( value_type == VT_BOTH_AVERAGES ):
        return [ VT_DENSITY_WEIGHTED_AVERAGE,
                       VT_UNWEIGHTED_AVERAGE, ]
    else:
        return [ value_type ]

def set_study_value( cursor, study, quantity, value,
                     value_type=VT_UNAVERAGED_VALUE,
                     measurement_techniques=[], mt_set=1,
                     outlier=False, notes=[] ):
    study_value, study_uncertainty = split_float( value )
    for avg_sys in create_value_types_list( value_type ):
        cursor.execute(
        """
        INSERT INTO study_values( study, quantity, study_value,
                                  study_uncertainty, value_type_id, mt_set,
                                  outlier )
        VALUES( ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(study),
            str(quantity),
            study_value,
            study_uncertainty,
            avg_sys,
            mt_set,
            int(outlier),
        )
        )

        for measurement_technique in measurement_techniques:
            cursor.execute(
            """
            INSERT INTO study_values_mt( study, quantity, value_type_id,
                                         mt_set, measurement_technique )
            VALUES( ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(study),
                str(quantity),
                avg_sys,
                mt_set,
                measurement_technique,
            )
            )

        for note in notes:
            cursor.execute(
            """
            INSERT INTO study_value_notes( study, quantity, value_type_id,
                                           mt_set, note )
            VALUES( ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(study),
                str(quantity),
                avg_sys,
                mt_set,
                int(note),
            )
            )

def get_study_value( cursor, study, quantity, value_type=VT_ANY_AVERAGE,
                     mt_set=1, ):
    if ( value_type == VT_ANY_AVERAGE ):
        cursor.execute(
        """
        SELECT study_value, study_uncertainty
        FROM study_values
        WHERE study=? AND quantity=? AND mt_set=?
        LIMIT 1;
        """,
        (
            sanitize_identifier(study),
            str(quantity),
            mt_set,
        )
        )
    else:
        cursor.execute(
        """
        SELECT study_value, study_uncertainty
        FROM study_values
        WHERE study=? AND quantity=? AND value_type_id=? AND mt_set=?
        LIMIT 1;
        """,
        (
            sanitize_identifier(study),
            str(quantity),
            value_type,
            mt_set,
        )
        )
    return fetch_float( cursor )

def add_source( cursor, study, source, classification ):
    cursor.execute(
    """
    INSERT INTO sources( study, source, classification )
    VALUES( ?, ?, ? );
    """,
    (
        sanitize_identifier(study),
        str(source),
        int(classification),
    )
    )

def add_series( cursor, flow_class, year, study_number, series_number,  \
                number_of_dimensions, coordinate_system, outlier=False, \
                notes=[], identifiers={}, ):
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
                        coordinate_system_id, outlier )
    VALUES( ?, ?, ?, ?, ?, ? );
    """,
    (
        series,
        study,
        int(series_number),
        int(number_of_dimensions),
        str(coordinate_system),
        int(outlier),
    )
    )

    for note in notes:
        cursor.execute(
        """
        INSERT INTO series_notes( series, note )
        VALUES( ?, ? );
        """,
        (
            series,
            int(note),
        )
        )

    for compilation in identifiers:
        cursor.execute(
        """
        INSERT INTO series_identifiers( series, compilation, identifier )
        VALUES( ?, ?, ? );
        """,
        (
            series,
            int(compilation),
            identifiers[compilation],
        )
        )

    return series

def update_series_geometry( cursor, identifier, geometry ):
    cursor.execute(
    """
    UPDATE series
    SET geometry=?
    WHERE identifier=?;
    """,
    (
        str(geometry),
        sanitize_identifier(identifier),
    )
    )

def update_series_number_of_sides( cursor, identifier, number_of_sides ):
    cursor.execute(
    """
    UPDATE series
    SET number_of_sides=?
    WHERE identifier=?;
    """,
    (
        int(number_of_sides),
        sanitize_identifier(identifier),
    )
    )

def update_series_description( cursor, identifier, description ):
    cursor.execute(
    """
    UPDATE series
    SET description=?
    WHERE identifier=?;
    """,
    (
        description.strip(),
        sanitize_identifier(identifier),
    )
    )

def set_series_value( cursor, series, quantity, value,
                      value_type=VT_UNAVERAGED_VALUE,
                      measurement_techniques=[], mt_set=1,
                      outlier=False, notes=[] ):
    series_value, series_uncertainty = split_float( value )
    for avg_sys in create_value_types_list( value_type ):
        cursor.execute(
        """
        INSERT INTO series_values( series, quantity, series_value,
                                   series_uncertainty, value_type_id,
                                   mt_set, outlier )
        VALUES( ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(series),
            str(quantity),
            series_value,
            series_uncertainty,
            avg_sys,
            mt_set,
            int(outlier),
        )
        )

        for measurement_technique in measurement_techniques:
            cursor.execute(
            """
            INSERT INTO series_values_mt( series, quantity, value_type_id,
                                          mt_set, measurement_technique )
            VALUES( ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(series),
                str(quantity),
                avg_sys,
                mt_set,
                measurement_technique,
            )
            )

        for note in notes:
            cursor.execute(
            """
            INSERT INTO series_value_notes( series, quantity, value_type_id,
                                            mt_set, note )
            VALUES( ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(series),
                str(quantity),
                avg_sys,
                mt_set,
                int(note),
            )
            )

def get_series_value( cursor, series, quantity, value_type=VT_ANY_AVERAGE, \
                      mt_set=1, ):
    if ( value_type == VT_ANY_AVERAGE ):
        cursor.execute(
        """
        SELECT series_value, series_uncertainty
        FROM series_values
        WHERE series=? AND quantity=? AND mt_set=?
        LIMIT 1;
        """,
        (
            sanitize_identifier(series),
            str(quantity),
            mt_set,
        )
        )
    else:
        cursor.execute(
        """
        SELECT series_value, series_uncertainty
        FROM series_values
        WHERE series=? AND quantity=? AND value_type_id=? AND mt_set=?
        LIMIT 1;
        """,
        (
            sanitize_identifier(series),
            str(quantity),
            value_type,
            mt_set,
        )
        )
    return fetch_float( cursor )

def add_station( cursor, flow_class, year, study_number, series_number, \
                station_number, outlier=False, notes=[], identifiers={}, ):
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
    INSERT INTO stations( identifier, series, study, station_number, outlier )
    VALUES( ?, ?, ?, ?, ? );
    """,
    (
        station,
        series,
        study,
        int(station_number),
        int(outlier),
    )
    )

    for note in notes:
        cursor.execute(
        """
        INSERT INTO station_notes( station, note )
        VALUES( ?, ? );
        """,
        (
            station,
            int(note),
        )
        )

    for compilation in identifiers:
        cursor.execute(
        """
        INSERT INTO station_identifiers( station, compilation, identifier )
        VALUES( ?, ?, ? );
        """,
        (
            station,
            int(compilation),
            identifiers[compilation],
        )
        )

    return station

def set_station_value( cursor, station, quantity, value,
                       value_type=VT_UNAVERAGED_VALUE,
                       measurement_techniques=[], mt_set=1,
                       outlier=False, notes=[] ):
    station_value, station_uncertainty = split_float( value )
    for avg_sys in create_value_types_list( value_type ):
        cursor.execute(
        """
        INSERT INTO station_values( station, quantity, station_value,
                                    station_uncertainty, value_type_id,
                                    mt_set, outlier )
        VALUES( ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(station),
            str(quantity),
            station_value,
            station_uncertainty,
            avg_sys,
            mt_set,
            int(outlier),
        )
        )

        for measurement_technique in measurement_techniques:
            cursor.execute(
            """
            INSERT INTO station_values_mt( station, quantity, value_type_id,
                                           mt_set, measurement_technique )
            VALUES( ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(station),
                str(quantity),
                avg_sys,
                mt_set,
                measurement_technique,
            )
            )

        for note in notes:
            cursor.execute(
            """
            INSERT INTO station_value_notes( station, quantity, value_type_id,
                                             mt_set, note )
            VALUES( ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(station),
                str(quantity),
                avg_sys,
                mt_set,
                int(note),
            )
            )

def get_points_at_station( cursor, station ):
    cursor.execute(
    """
    SELECT identifier
    FROM points
    WHERE station=?;
    """,
    (
        station,
    )
    )

    results = cursor.fetchall()
    points = []
    for result in results:
        points.append( str(result[0]) )

    return points

def set_constant_profile( cursor, station, quantity, value,
                          value_type=VT_UNAVERAGED_VALUE,
                          measurement_techniques=[], mt_set=1,
                          outlier=False, notes=[] ):
    for point in get_points_at_station( cursor, station ):
        set_point_value(
            cursor,
            point,
            quantity,
            value,
            value_type=value_type,
            measurement_techniques=measurement_techniques,
            mt_set=mt_set,
            outlier=outlier,
            notes=notes,
        )

def get_station_value( cursor, station, quantity, value_type=VT_ANY_AVERAGE, \
                       mt_set=1, ):
    if ( value_type == VT_ANY_AVERAGE ):
        cursor.execute(
        """
        SELECT station_value, station_uncertainty
        FROM station_values
        WHERE station=? AND quantity=? AND mt_set=?
        LIMIT 1;
        """,
        (
            sanitize_identifier(station),
            str(quantity),
            mt_set,
        )
        )
    else:
        cursor.execute(
        """
        SELECT station_value, station_uncertainty
        FROM station_values
        WHERE station=? AND quantity=? AND value_type_id=? AND mt_set=?
        LIMIT 1;
        """,
        (
            sanitize_identifier(station),
            str(quantity),
            value_type,
            mt_set,
        )
        )
    return fetch_float( cursor )

def add_point( cursor, flow_class, year, study_number, series_number,         \
               station_number, point_number, point_label=None, outlier=False, \
               notes=[], identifiers={}, ):
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
                        point_label, outlier )
    VALUES( ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        point,
        station,
        series,
        study,
        int(point_number),
        point_label,
        int(outlier),
    )
    )

    for note in notes:
        cursor.execute(
        """
        INSERT INTO point_notes( point, note )
        VALUES( ?, ? );
        """,
        (
            point,
            int(note),
        )
        )

    for compilation in identifiers:
        cursor.execute(
        """
        INSERT INTO point_identifiers( point, compilation, identifier )
        VALUES( ?, ?, ? );
        """,
        (
            point,
            int(compilation),
            identifiers[compilation],
        )
        )

    return point

def set_point_value( cursor, point, quantity, value,
                     value_type=VT_UNAVERAGED_VALUE,
                     measurement_techniques=[], mt_set=1,
                     outlier=False, notes=[] ):
    point_value, point_uncertainty = split_float( value )
    for avg_sys in create_value_types_list( value_type ):
        cursor.execute(
        """
        INSERT INTO point_values( point, quantity, point_value,
                                  point_uncertainty, value_type_id, mt_set,
                                  outlier )
        VALUES( ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(point),
            str(quantity),
            point_value,
            point_uncertainty,
            avg_sys,
            mt_set,
            int(outlier),
        )
        )

        for measurement_technique in measurement_techniques:
            cursor.execute(
            """
            INSERT INTO point_values_mt( point, quantity, value_type_id, mt_set,
                                         measurement_technique )
            VALUES( ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(point),
                str(quantity),
                avg_sys,
                mt_set,
                measurement_technique,
            )
            )

        for note in notes:
            cursor.execute(
            """
            INSERT INTO point_value_notes( point, quantity, value_type_id, mt_set,
                                           note )
            VALUES( ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(point),
                str(quantity),
                avg_sys,
                mt_set,
                int(note),
            )
            )

def get_point_value( cursor, point, quantity, value_type=VT_ANY_AVERAGE, \
                     mt_set=1, ):
    if ( value_type == VT_ANY_AVERAGE ):
        cursor.execute(
        """
        SELECT point_value, point_uncertainty
        FROM point_values
        WHERE point=? AND quantity=? AND mt_set=?
        LIMIT 1;
        """,
        (
            sanitize_identifier(point),
            str(quantity),
            mt_set,
        )
        )
    else:
        cursor.execute(
        """
        SELECT point_value, point_uncertainty
        FROM point_values
        WHERE point=? AND quantity=? AND value_type_id=? AND mt_set=?
        LIMIT 1;
        """,
        (
            sanitize_identifier(point),
            str(quantity),
            value_type,
            mt_set,
        )
        )
    return fetch_float( cursor )

# TODO: Change this to getting intersecting profiles.  Allow for an arbitrary
# number of quantities, so that requests can be made for more than 2 profiles
# at once.
def get_twin_profiles( cursor, station, quantity1, quantity2,
                       value_type1=None, value_type2=None,
                       excluded_point_labels=[], ):
    if ( value_type1 == None ):
        if ( value_type2 == None ):
            # Both value types are unspecified.
            cursor.execute(
            """
            SELECT point
            FROM point_values
            WHERE point LIKE ? AND quantity=? AND outlier=0
            INTERSECT
            SELECT point
            FROM point_values
            WHERE point LIKE ? AND quantity=? AND outlier=0
            ORDER BY point;
            """,
            (
                sanitize_identifier(station)+'%',
                str(quantity1),
                sanitize_identifier(station)+'%',
                str(quantity2),
            )
            )
        else:
            # Only the second value type is specified.
            cursor.execute(
            """
            SELECT point
            FROM point_values
            WHERE point LIKE ? AND quantity=? AND outlier=0
            INTERSECT
            SELECT point
            FROM point_values
            WHERE point LIKE ? AND quantity=? AND value_type_id=? AND outlier=0
            ORDER BY point;
            """,
            (
                sanitize_identifier(station)+'%',
                str(quantity1),
                sanitize_identifier(station)+'%',
                str(quantity2),
                str(value_type2),
            )
            )
    else:
        if ( value_type2 == None ):
            # Only the first value type is specified.
            cursor.execute(
            """
            SELECT point
            FROM point_values
            WHERE point LIKE ? AND quantity=? AND value_type_id=? AND outlier=0
            INTERSECT
            SELECT point
            FROM point_values
            WHERE point LIKE ? AND quantity=? AND outlier=0
            ORDER BY point;
            """,
            (
                sanitize_identifier(station)+'%',
                str(quantity1),
                str(value_type1),
                sanitize_identifier(station)+'%',
                str(quantity2),
            )
            )
        else:
            # Both value types are specified.
            cursor.execute(
            """
            SELECT point
            FROM point_values
            WHERE point LIKE ? AND quantity=? AND value_type_id=? AND outlier=0
            INTERSECT
            SELECT point
            FROM point_values
            WHERE point LIKE ? AND quantity=? AND value_type_id=? AND outlier=0
            ORDER BY point;
            """,
            (
                sanitize_identifier(station)+'%',
                str(quantity1),
                str(value_type1),
                sanitize_identifier(station)+'%',
                str(quantity2),
                str(value_type2),
            )
            )

    results = cursor.fetchall()
    points = []
    for result in results:
        point = str(result[0])

        cursor.execute(
        """
        SELECT point_label
        FROM points
        WHERE identifier=?;
        """,
        (
            point,
        )
        )
        point_label = cursor.fetchone()[0]

        if ( point_label not in excluded_point_labels ):
            points.append( result[0] )

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

def sanitize_point_label( label ):
    sanitized_label = str(label)
    if ( label in PL_EDGES ):
        sanitized_label = PL_EDGE
    elif ( label in PL_WALLS ):
        sanitized_label = PL_WALL
    return sanitized_label

def locate_labeled_points( cursor, station, label ):
    if ( label in PL_LOWER_UPPER ):
        return [ locate_labeled_point( cursor, station_label ) ]

    cursor.execute(
    """
    SELECT identifier
    FROM points
    WHERE identifier
    LIKE ? AND point_label=?
    ORDER BY identifier;
    """,
    (
        sanitize_identifier(station)+'%',
        str(label),
    )
    )

    results = cursor.fetchall()
    points = []
    for result in results:
        points.append( str(result[0]) )

    return points

def locate_labeled_point( cursor, station, label ):
    points = locate_labeled_points( cursor, station,
                                    sanitize_point_label(label) )

    point_numbers = {}
    for point in points:
        cursor.execute(
        """
        SELECT point_number
        FROM points
        WHERE identifier=?;
        """,
        (
            point,
        )
        )
        point_numbers[point] = int(cursor.fetchone()[0])

    lower_point = min( point_numbers, key=point_numbers.get )
    upper_point = max( point_numbers, key=point_numbers.get )

    point = lower_point
    if ( label in PL_LOWER ):
        point = lower_point
    elif ( label in PL_UPPER ):
        point = upper_point

    return point

def set_labeled_value( cursor, station, quantity, label, value,
                       value_type=VT_UNAVERAGED_VALUE,
                       measurement_techniques=[], mt_set=1,
                       outlier=False, notes=[] ):
    set_point_value(
        cursor,
        locate_labeled_point( cursor, station, label ),
        quantity,
        value,
        value_type=value_type,
        measurement_techniques=measurement_techniques,
        mt_set=mt_set,
        outlier=outlier,
        notes=notes,
    )

def get_labeled_value( cursor, station, quantity, label,
                       value_type=VT_ANY_AVERAGE, mt_set=1, ):
    return get_point_value(
        cursor,
        locate_labeled_point( cursor, station, label ),
        quantity,
        value_type=value_type,
        mt_set=1,
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

def calculate_molar_mass_of_molecular_formula( cursor, formula ):
    element_counts = extract_element_counts( formula )
    molar_mass      = 0.0
    for element in element_counts:
        count = element_counts[element]
        cursor.execute(
        """
        SELECT atomic_weight
        FROM elements
        WHERE element_symbol=?;
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

def add_note( cursor, filename ):
    contents = None
    with open( filename, "r" ) as f:
        contents = f.read().strip()

    cursor.execute(
    """
    INSERT INTO notes( contents )
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
