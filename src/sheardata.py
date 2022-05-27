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

# Geometries
GM_ELLIPTICAL  = "E"
GM_RECTANGULAR = "R"

# Instruments and methods (and other sources of information)
IT_APPROXIMATION                            = "APP"
IT_ASSUMPTION                               = "ASM"
IT_CALCULATION                              = "CLC"
IT_CLAIM                                    = "CLM"
IT_CLAUSER_METHOD                           = "TCC"
IT_CONSTANT_CURRENT_HOT_WIRE_ANEMOMETRY     = "HWC"
IT_CONSTANT_TEMPERATURE_HOT_WIRE_ANEMOMETRY = "HWT"
IT_DIFFERENTIAL_PRESSURE_METHOD             = "PTA"
IT_DIRECT_INJECTION_METHOD                  = "DIJ"
IT_FLOATING_ELEMENT_BALANCE                 = "FEB"
IT_FLOW_RATE_MEASUREMENT                    = "FQM"
IT_HOT_WIRE_ANEMOMETRY                      = "HWA"
IT_IMPACT_TUBE                              = "PTI"
IT_INDEX_OF_REFRACTION_METHOD               = "ORI"
IT_LASER_DOPPLER_ANEMOMETRY                 = "LDA"
IT_MACH_ZEHNDER_INTERFEROMETRY              = "MZI"
IT_MOMENTUM_BALANCE                         = "TMB"
IT_OBSERVATION                              = "OBS"
IT_OPTICAL_METHOD                           = "OPT"
IT_PARTICLE_IMAGE_VELOCIMETRY               = "PIV"
IT_PITOT_STATIC_TUBE                        = "PST"
IT_PRESTON_TUBE                             = "TPT"
IT_REASONING                                = "RSN"
IT_ROOT                                     = "RTX"
IT_SCHLIEREN_PHOTOGRAPHY                    = "SCH"
IT_SHADOWGRAPH_PHOTOGRAPHY                  = "SHD"
IT_SIMULATION                               = "SIM"
IT_STANTON_TUBE                             = "TST"
IT_THERMAL_ANEMOMETRY                       = "TAN"
IT_VELOCITY_PROFILE_METHOD                  = "TVP"
IT_VISCOUS_SUBLAYER_SLOPE_METHOD            = "TVS"
IT_WALL_SHEAR_STRESS_METHOD                 = "TWL"
IT_WEIGHING_METHOD                          = "QWM"
IT_ZEROTH_ORDER_APPROXIMATION               = "AP0"

PRIMARY_IT_SET = 1

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

# Quantities, facility
Q_RUN_TIME                   = "t_run"
Q_SPATIAL_ORDER_OF_ACCURACY  = "OOA_x"
Q_TEMPORAL_ORDER_OF_ACCURACY = "OOA_t"
Q_TEST_SECTION_HEIGHT        = "h_ts"
Q_TEST_SECTION_LENGTH        = "L_ts"
Q_TEST_SECTION_WIDTH         = "w_ts"

# Quantities, series
Q_ANGLE_OF_ATTACK                = "AOA"
Q_BODY_HEIGHT                    = "h_b"
Q_BODY_LENGTH                    = "L_b"
Q_BODY_PROJECTED_FRONTAL_AREA    = "A_f"
Q_BODY_REYNOLDS_NUMBER           = "Re_inf"
Q_BODY_STROUHAL_NUMBER           = "Sr"
Q_BODY_VOLUME                    = "V_b"
Q_BODY_WETTED_SURFACE_AREA       = "A_s"
Q_BODY_WIDTH                     = "w_b"
Q_DISTANCE_BETWEEN_PRESSURE_TAPS = "L_p"
Q_DRAG_COEFFICIENT               = "C_D"
Q_DRAG_FORCE                     = "F_D"
Q_FREESTREAM_MACH_NUMBER         = "Ma_inf"
Q_FREESTREAM_SPEED_OF_SOUND      = "a_inf"
Q_FREESTREAM_TEMPERATURE         = "T_inf"
Q_FREESTREAM_VELOCITY            = "{:s}_inf".format(STREAMWISE_VELOCITY_SYMBOL)
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
Q_BULK_DYNAMIC_VISCOSITY                 = "mu_b"
Q_BULK_KINEMATIC_VISCOSITY               = "nu_b"
Q_BULK_MACH_NUMBER                       = "Ma_b"
Q_BULK_MASS_DENSITY                      = "rho_b"
Q_BULK_REYNOLDS_NUMBER                   = "Re_b"
Q_BULK_SPEED_OF_SOUND                    = "a_b"
Q_BULK_VELOCITY                          = "{:s}_b".format(STREAMWISE_VELOCITY_SYMBOL)
Q_CLAUSER_THICKNESS                      = "delta_C"
Q_CROSS_SECTIONAL_AREA                   = "A_cs"
Q_CROSS_SECTIONAL_ASPECT_RATIO           = "AR_cs"
Q_CROSS_SECTIONAL_HALF_HEIGHT            = "b_cs"
Q_CROSS_SECTIONAL_HEIGHT                 = "h_cs"
Q_CROSS_SECTIONAL_WIDTH                  = "w_cs"
Q_DEVELOPMENT_LENGTH                     = "L_d"
Q_DISPLACEMENT_THICKNESS                 = "delta_1"
Q_DISPLACEMENT_THICKNESS_REYNOLDS_NUMBER = "Re_delta_1"
Q_ENERGY_THICKNESS                       = "delta_3"
Q_EQUILIBRIUM_PARAMETER                  = "Pi_2"
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

Q_PRESSURE_GRADIENT = {
    D_STREAMWISE: Q_STREAMWISE_PRESSURE_GRADIENT,
    D_TRANSVERSE: Q_TRANSVERSE_PRESSURE_GRADIENT,
    D_SPANWISE:     Q_SPANWISE_PRESSURE_GRADIENT,
}

# Quantities, wall point
Q_AVERAGE_SKIN_FRICTION_COEFFICIENT     = "C_f"
Q_DARCY_FRICTION_FACTOR                 = "f_D"
Q_FANNING_FRICTION_FACTOR               = "f"
Q_FRICTION_MACH_NUMBER                  = "Ma_tau"
Q_FRICTION_REYNOLDS_NUMBER              = "Re_tau"
Q_FRICTION_TEMPERATURE                  = "T_tau"
Q_FRICTION_VELOCITY                     = "U_tau"
Q_HEAT_TRANSFER_COEFFICIENT             = "c_q"
Q_INNER_LAYER_HEAT_FLUX                 = "B_q"
Q_INNER_LAYER_ROUGHNESS_HEIGHT          = "eps+"
Q_LOCAL_SKIN_FRICTION_COEFFICIENT       = "c_f"
Q_OUTER_LAYER_ROUGHNESS_HEIGHT          = "eps/D_H"
Q_PRESSURE_COEFFICIENT                  = "C_p"
Q_ROUGHNESS_HEIGHT                      = "eps"
Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER   = "Re_tau*"
Q_SPANWISE_WALL_CURVATURE               = "kappa_{:s}".format(SPANWISE_COORDINATE_SYMBOL)
Q_STREAMWISE_WALL_CURVATURE             = "kappa_{:s}".format(STREAMWISE_COORDINATE_SYMBOL)
Q_VISCOUS_LENGTH_SCALE                  = "l_nu"

# Quantities, point
Q_AMOUNT_DENSITY                   = "C"
Q_DILATATION_RATE                  = "Thetadot"
Q_DISTANCE_FROM_WALL               = TRANSVERSE_COORDINATE_SYMBOL
Q_DYNAMIC_VISCOSITY                = "mu"
Q_HEAT_CAPACITY_RATIO              = "gamma"
Q_HEAT_FLUX                        = "q"
Q_INNER_LAYER_COORDINATE           = "{:s}+".format(TRANSVERSE_COORDINATE_SYMBOL)
Q_INNER_LAYER_TEMPERATURE          = "T+"
Q_INNER_LAYER_VELOCITY             = "{:s}+".format(STREAMWISE_VELOCITY_SYMBOL.upper())
Q_INNER_LAYER_VELOCITY_DEFECT      = "delta{:s}+".format(STREAMWISE_VELOCITY_SYMBOL.upper())
Q_KINEMATIC_VISCOSITY              = "nu"
Q_MACH_NUMBER                      = "Ma"
Q_MASS_DENSITY                     = "rho"
Q_OUTER_LAYER_COORDINATE           = "eta"
Q_OUTER_LAYER_TEMPERATURE          = "Theta"
Q_OUTER_LAYER_VELOCITY             = "F"
Q_OUTER_LAYER_VELOCITY_DEFECT      = "delta{:s}+/{:s}_e".format(STREAMWISE_COORDINATE_SYMBOL.upper(),STREAMWISE_COORDINATE_SYMBOL.upper())
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

Q_AMOUNT_FRACTION = "x" if Q_STREAMWISE_COORDINATE == "X" else "X"
Q_MASS_FRACTION   = "w" if Q_TRANSVERSE_COORDINATE == "Y" else "Y"

Q_AMOUNT_CONCENTRATION = Q_AMOUNT_DENSITY
Q_MASS_CONCENTRATION   = Q_MASS_DENSITY

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
C_SELF         = 0 # Originator
C_CH_1969      = 1 # Coles and Hirst
C_BE_1973      = 2 # Birch and Eggers
C_FF_1977      = 3 # Fernholz and Finley
C_ERCOFTAC     = 4 # ERCOFTAC Classic Collection
C_AGARD_AR_345 = 5 # AGARD-AR-345 (Test cases for LES)

# Source classifications
PRIMARY_SOURCE   = 1
SECONDARY_SOURCE = 2

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

def set_study_value( cursor, study_id, quantity_id, value,
                     value_type_id=VT_UNAVERAGED_VALUE,
                     method_ids=[], method_set=PRIMARY_IT_SET,
                     fluid_id=F_MIXTURE, corrected=False, outlier=False,
                     note_ids=[] ):
    study_value, study_uncertainty = split_float( value )
    for value_type_id in create_value_types_list( value_type_id ):
        cursor.execute(
        """
        INSERT INTO study_values( study_id, quantity_id, fluid_id,
                                  value_type_id, method_set,
                                  study_value, study_uncertainty,
                                  corrected, outlier )
        VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(study_id),
            str(quantity_id),
            fluid_id,
            value_type_id,
            method_set,
            study_value,
            study_uncertainty,
            int(corrected),
            int(outlier),
        )
        )

        for method_id in method_ids:
            cursor.execute(
            """
            INSERT INTO study_values_mt( study_id, quantity_id, fluid_id,
                                         value_type_id, method_set,
                                         method_id )
            VALUES( ?, ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(study_id),
                str(quantity_id),
                fluid_id,
                value_type_id,
                method_set,
                method_id,
            )
            )

        for note_id in note_ids:
            cursor.execute(
            """
            INSERT INTO study_value_notes( study_id, quantity_id, fluid_id,
                                           value_type_id, method_set,
                                           note_id )
            VALUES( ?, ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(study_id),
                str(quantity_id),
                fluid_id,
                value_type_id,
                method_set,
                int(note_id),
            )
            )

def get_study_value( cursor, study_id, quantity_id,
                     value_type_id=VT_ANY_AVERAGE,
                     fluid_id=F_MIXTURE, method_set=PRIMARY_IT_SET, ):
    final_value_type_id = value_type_id
    if ( value_type_id == VT_ANY_AVERAGE ):
        cursor.execute(
        """
        SELECT value_type_id
        FROM study_values
        WHERE study_id=? AND quantity_id=? AND fluid_id=? AND method_set=?;
        """,
        (
            sanitize_identifier(study_id),
            str(quantity_id),
            fluid_id,
            method_set,
        )
        )
        results = cursor.fetchall()
        value_type_ids = []
        for result in results:
            value_type_ids.append( str(result[0]) )
        final_value_type_id = pick_any_average_value_type( value_type_ids )

    cursor.execute(
    """
    SELECT study_value, study_uncertainty
    FROM study_values
    WHERE study_id=? AND quantity_id=? AND fluid_id=? AND value_type_id=? AND method_set=?;
    """,
    (
        sanitize_identifier(study_id),
        str(quantity_id),
        fluid_id,
        final_value_type_id,
        method_set,
    )
    )
    return fetch_float( cursor )

def add_study_source( cursor, study_id, citation_key, source_classification ):
    cursor.execute(
    """
    INSERT INTO study_sources( study_id, citation_key, source_classification )
    VALUES( ?, ?, ? );
    """,
    (
        sanitize_identifier(study_id),
        str(citation_key),
        int(source_classification),
    )
    )

def add_series( cursor, flow_class_id, year, study_number, series_number,  \
                number_of_dimensions, coordinate_system_id, outlier=False, \
                note_ids=[], series_external_ids={}, ):
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
    INSERT INTO series( series_id, study_id, series_number, number_of_dimensions,
                        coordinate_system_id, outlier )
    VALUES( ?, ?, ?, ?, ?, ? );
    """,
    (
        series_id,
        study_id,
        int(series_number),
        int(number_of_dimensions),
        str(coordinate_system_id),
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

def update_series_geometry( cursor, series_id, geometry_id ):
    cursor.execute(
    """
    UPDATE series
    SET geometry_id=?
    WHERE series_id=?;
    """,
    (
        str(geometry_id),
        sanitize_identifier(series_id),
    )
    )

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

def set_series_value( cursor, series_id, quantity_id, value,
                      value_type_id=VT_UNAVERAGED_VALUE,
                      method_ids=[], method_set=PRIMARY_IT_SET,
                      fluid_id=F_MIXTURE, corrected=False, outlier=False,
                      note_ids=[] ):
    series_value, series_uncertainty = split_float( value )
    for value_type_id in create_value_types_list( value_type_id ):
        cursor.execute(
        """
        INSERT INTO series_values( series_id, quantity_id, fluid_id,
                                   value_type_id, method_set,
                                   series_value, series_uncertainty,
                                   corrected, outlier )
        VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(series_id),
            str(quantity_id),
            fluid_id,
            value_type_id,
            method_set,
            series_value,
            series_uncertainty,
            int(corrected),
            int(outlier),
        )
        )

        for method_id in method_ids:
            cursor.execute(
            """
            INSERT INTO series_values_mt( series_id, quantity_id, fluid_id,
                                          value_type_id, method_set,
                                          method_id )
            VALUES( ?, ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(series_id),
                str(quantity_id),
                fluid_id,
                value_type_id,
                method_set,
                method_id,
            )
            )

        for note_id in note_ids:
            cursor.execute(
            """
            INSERT INTO series_value_notes( series_id, quantity_id, fluid_id,
                                            value_type_id, method_set,
                                            note_id )
            VALUES( ?, ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(series_id),
                str(quantity_id),
                fluid_id,
                value_type_id,
                method_set,
                int(note_id),
            )
            )

def get_series_value( cursor, series_id, quantity_id,
                      value_type_id=VT_ANY_AVERAGE,
                      fluid_id=F_MIXTURE, method_set=PRIMARY_IT_SET, ):
    final_value_type_id = value_type_id
    if ( value_type_id == VT_ANY_AVERAGE ):
        cursor.execute(
        """
        SELECT value_type_id
        FROM series_values
        WHERE series_id=? AND quantity_id=? AND fluid_id=? AND method_set=?;
        """,
        (
            sanitize_identifier(series_id),
            str(quantity_id),
            fluid_id,
            method_set,
        )
        )
        results = cursor.fetchall()
        value_type_ids = []
        for result in results:
            value_type_ids.append( str(result[0]) )
        final_value_type_id = pick_any_average_value_type( value_type_ids )

    cursor.execute(
    """
    SELECT series_value, series_uncertainty
    FROM series_values
    WHERE series_id=? AND quantity_id=? AND fluid_id=? AND value_type_id=? AND method_set=?;
    """,
    (
        sanitize_identifier(series_id),
        str(quantity_id),
        fluid_id,
        final_value_type_id,
        method_set,
    )
    )
    return fetch_float( cursor )

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

def add_station( cursor, flow_class_id, year, study_number, series_number, \
                station_number, outlier=False, note_ids=[], station_external_ids={}, ):
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
    study_id = identify_study(
        flow_class_id,
        year,
        study_number,
    )
    cursor.execute(
    """
    INSERT INTO stations( station_id, series_id, study_id, station_number, 
                          outlier )
    VALUES( ?, ?, ?, ?, ? );
    """,
    (
        station_id,
        series_id,
        study_id,
        int(station_number),
        int(outlier),
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

def set_station_value( cursor, station_id, quantity_id, value,
                       value_type_id=VT_UNAVERAGED_VALUE,
                       method_ids=[], method_set=PRIMARY_IT_SET,
                       fluid_id=F_MIXTURE, corrected=False, outlier=False,
                       note_ids=[] ):
    station_value, station_uncertainty = split_float( value )
    for value_type_id in create_value_types_list( value_type_id ):
        cursor.execute(
        """
        INSERT INTO station_values( station_id, quantity_id, fluid_id,
                                    value_type_id, method_set,
                                    station_value, station_uncertainty,
                                    corrected, outlier )
        VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(station_id),
            str(quantity_id),
            fluid_id,
            value_type_id,
            method_set,
            station_value,
            station_uncertainty,
            int(corrected),
            int(outlier),
        )
        )

        for method_id in method_ids:
            cursor.execute(
            """
            INSERT INTO station_values_mt( station_id, quantity_id, fluid_id,
                                           value_type_id, method_set,
                                           method_id )
            VALUES( ?, ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(station_id),
                str(quantity_id),
                fluid_id,
                value_type_id,
                method_set,
                method_id,
            )
            )

        for note_id in note_ids:
            cursor.execute(
            """
            INSERT INTO station_value_notes( station_id, quantity_id, fluid_id,
                                             value_type_id, method_set,
                                             note_id )
            VALUES( ?, ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(station_id),
                str(quantity_id),
                fluid_id,
                value_type_id,
                method_set,
                int(note_id),
            )
            )

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

def set_constant_profile( cursor, station_id, quantity_id, value,
                          value_type_id=VT_UNAVERAGED_VALUE,
                          method_ids=[], method_set=PRIMARY_IT_SET,
                          corrected=False, outlier=False, note_ids=[] ):
    for point_id in get_points_at_station( cursor, station_id ):
        set_point_value(
            cursor,
            point_id,
            quantity_id,
            value,
            value_type_id=value_type_id,
            method_ids=method_ids,
            method_set=method_set,
            corrected=False,
            outlier=outlier,
            note_ids=note_ids,
        )

def get_station_value( cursor, station_id, quantity_id,
                       value_type_id=VT_ANY_AVERAGE,
                       fluid_id=F_MIXTURE, method_set=PRIMARY_IT_SET, ):
    final_value_type_id = value_type_id
    if ( value_type_id == VT_ANY_AVERAGE ):
        cursor.execute(
        """
        SELECT value_type_id
        FROM station_values
        WHERE station_id=? AND quantity_id=? AND fluid_id=? AND method_set=?;
        """,
        (
            sanitize_identifier(station_id),
            str(quantity_id),
            fluid_id,
            method_set,
        )
        )
        results = cursor.fetchall()
        value_type_ids = []
        for result in results:
            value_type_ids.append( str(result[0]) )
        final_value_type_id = pick_any_average_value_type( value_type_ids )

    cursor.execute(
    """
    SELECT station_value, station_uncertainty
    FROM station_values
    WHERE station_id=? AND quantity_id=? AND fluid_id=? AND value_type_id=? AND
          method_set=?;
    """,
    (
        sanitize_identifier(station_id),
        str(quantity_id),
        fluid_id,
        final_value_type_id,
        method_set,
    )
    )
    return fetch_float( cursor )

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
    INSERT INTO points( point_id, station_id, series_id, study_id,
                        point_number, point_label_id, outlier )
    VALUES( ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        point_id,
        station_id,
        series_id,
        study_id,
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

def set_point_value( cursor, point_id, quantity_id, value,
                     value_type_id=VT_UNAVERAGED_VALUE,
                     method_ids=[], method_set=PRIMARY_IT_SET,
                     fluid_id=F_MIXTURE, corrected=False, outlier=False,
                     note_ids=[] ):
    point_value, point_uncertainty = split_float( value )
    for value_type_id in create_value_types_list( value_type_id ):
        cursor.execute(
        """
        INSERT INTO point_values( point_id, quantity_id, fluid_id,
                                  value_type_id, method_set,
                                  point_value, point_uncertainty,
                                  corrected, outlier )
        VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            sanitize_identifier(point_id),
            str(quantity_id),
            fluid_id,
            value_type_id,
            method_set,
            point_value,
            point_uncertainty,
            int(corrected),
            int(outlier),
        )
        )

        for method_id in method_ids:
            cursor.execute(
            """
            INSERT INTO point_values_mt( point_id, quantity_id, fluid_id,
                                         value_type_id, method_set,
                                         method_id )
            VALUES( ?, ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(point_id),
                str(quantity_id),
                fluid_id,
                value_type_id,
                method_set,
                method_id,
            )
            )

        for note_id in note_ids:
            cursor.execute(
            """
            INSERT INTO point_value_notes( point_id, quantity_id, fluid_id,
                                           value_type_id, method_set,
                                           note_id )
            VALUES( ?, ?, ?, ?, ?, ? );
            """,
            (
                sanitize_identifier(point_id),
                str(quantity_id),
                fluid_id,
                value_type_id,
                method_set,
                int(note_id),
            )
            )

def get_point_value( cursor, point_id, quantity_id,
                     value_type_id=VT_ANY_AVERAGE,
                     fluid_id=F_MIXTURE, method_set=PRIMARY_IT_SET, ):
    final_value_type_id = value_type_id
    if ( value_type_id == VT_ANY_AVERAGE ):
        cursor.execute(
        """
        SELECT value_type_id
        FROM point_values
        WHERE point_id=? AND quantity_id=? AND fluid_id=? AND method_set=?;
        """,
        (
            sanitize_identifier(point_id),
            str(quantity_id),
            fluid_id,
            method_set,
        )
        )
        results = cursor.fetchall()
        value_type_ids = []
        for result in results:
            value_type_ids.append( str(result[0]) )
        final_value_type_id = pick_any_average_value_type( value_type_ids )

    cursor.execute(
    """
    SELECT point_value, point_uncertainty
    FROM point_values
    WHERE point_id=? AND quantity_id=? AND fluid_id=? AND value_type_id=? AND
          method_set=?;
    """,
    (
        sanitize_identifier(point_id),
        str(quantity_id),
        fluid_id,
        final_value_type_id,
        method_set,
    )
    )
    return fetch_float( cursor )

def get_intersecting_profiles( cursor, station_id, quantity_ids,
                               fluid_ids=[],
                               value_type_ids=[],
                               method_sets=[],
                               excluded_point_label_ids=[], ):
    if ( len(fluid_ids) == 0 ):
        for i in range(len(quantity_ids)):
            fluid_ids.append(F_MIXTURE)

    # TODO: Should this really be `None`?
    if ( len(value_type_ids) == 0 ):
        for i in range(len(quantity_ids)):
            value_type_ids.append(None)

    if ( len(method_sets) == 0 ):
        for i in range(len(quantity_ids)):
            method_sets.append(PRIMARY_IT_SET)

    assert( len(quantity_ids) == len(fluid_ids)      )
    assert( len(quantity_ids) == len(value_type_ids) )
    assert( len(quantity_ids) == len(method_sets)  )

    query_string = ""
    query_inputs = []
    for i in range(len(quantity_ids)):
        if ( i > 0 ):
            query_string += "INTERSECT\n"
        query_string += "SELECT point_id\n"
        query_string += "FROM point_values\n"
        query_string += "WHERE quantity_id=? AND fluid_id=? AND method_set=? AND outlier=0"
        query_inputs.append( str(quantity_ids[i]) )
        query_inputs.append( str(fluid_ids[i]) )
        query_inputs.append( str(method_sets[i]) )
        if ( value_type_ids[i] != None ):
            query_string += " AND value_type_id=?"
            query_inputs.append( str(value_type_ids[i]) )
        query_string += " AND point_id IN ( SELECT point_id FROM points WHERE station_id=? )\n"
        query_inputs.append( sanitize_identifier(station_id) )
    query_string += "ORDER BY point_id\n"

    cursor.execute( query_string, tuple(query_inputs), )

    results = cursor.fetchall()
    point_ids = []
    for result in results:
        point_id = str(result[0])

        cursor.execute(
        """
        SELECT point_label_id
        FROM points
        WHERE point_id=?;
        """,
        (
            point_id,
        )
        )
        point_label_id = cursor.fetchone()[0]

        if ( point_label_id not in excluded_point_label_ids ):
            point_ids.append( result[0] )

    profiles = []
    for i in range(len(quantity_ids)):
        profile = []
        for point_id in point_ids:
            profile.append( get_point_value(
                cursor,
                point_id,
                quantity_ids[i],
                fluid_id=fluid_ids[i],
                value_type_id=(VT_ANY_AVERAGE if value_type_ids[i] == None else value_type_ids[i]),
                method_set=method_sets[i],
            ) )
        profiles.append( np.array(profile) )
    return tuple(profiles)

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

def set_labeled_value( cursor, station_id, quantity_id, point_label_id, value,
                       value_type_id=VT_UNAVERAGED_VALUE,
                       method_ids=[], method_set=PRIMARY_IT_SET,
                       corrected=False, outlier=False, note_ids=[] ):
    set_point_value(
        cursor,
        locate_labeled_point( cursor, station_id, point_label_id ),
        quantity_id,
        value,
        value_type_id=value_type_id,
        method_ids=method_ids,
        method_set=method_set,
        corrected=corrected,
        outlier=outlier,
        note_ids=note_ids,
    )

def get_labeled_value( cursor, station_id, quantity_id, point_label_id,
                       fluid_id=F_MIXTURE,
                       value_type_id=VT_ANY_AVERAGE,
                       method_set=PRIMARY_IT_SET, ):
    return get_point_value(
        cursor,
        locate_labeled_point( cursor, station_id, point_label_id ),
        quantity_id,
        fluid_id=fluid_id,
        value_type_id=value_type_id,
        method_set=1,
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

def mark_station_as_periodic( cursor, station_id, \
                              streamwise=True, spanwise=False ):
    if ( streamwise ):
        cursor.execute(
        """
        UPDATE stations
        SET previous_streamwise_station_id=?, next_streamwise_station_id=?
        WHERE station_id=?;
        """,
        (
            sanitize_identifier( station_id ),
            sanitize_identifier( station_id ),
            sanitize_identifier( station_id ),
        )
        )
    if ( spanwise ):
        cursor.execute(
        """
        UPDATE stations
        SET previous_spanwise_station_id=?, next_spanwise_station_id=?
        WHERE station_id=?;
        """,
        (
            sanitize_identifier( station_id ),
            sanitize_identifier( station_id ),
            sanitize_identifier( station_id ),
        )
        )

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

def _interpolate_fluid_property_value( cursor, pressure, temperature,
                                       fluid_id, quantity_id,
                                       citation_key=None, ):
    # If no citation key is given, find the citation key for the closest
    # possible preferred value.
    if ( citation_key == None ):
        cursor.execute(
        """
        SELECT ( pressure - ? ) * ( pressure - ? ) + ( temperature - ? ) * ( temperature - ? ) as measure,
               citation_key
        FROM fluid_property_values
        WHERE fluid_id=? AND quantity_id=? AND preferred=1
        ORDER BY measure ASC LIMIT 1;
        """,
        (
        sdfloat_value(pressure),
        sdfloat_value(pressure),
        sdfloat_value(temperature),
        sdfloat_value(temperature),
        fluid_id,
        quantity_id,
        )
        )

        result_closest = cursor.fetchone()
        assert( result_closest != None )

        citation_key = result_closest[1]

    # Find closest "southwest" value.
    cursor.execute(
    """
    SELECT ( pressure - ? ) * ( pressure - ? ) + ( temperature - ? ) * ( temperature - ? ) as measure,
           pressure, temperature, fluid_property_value, fluid_property_uncertainty
    FROM fluid_property_values
    WHERE fluid_id=?
      AND citation_key=?
      AND quantity_id=?
      AND pressure <= ?
      AND temperature <= ?
    ORDER BY measure ASC LIMIT 1;
    """,
    (
    sdfloat_value(pressure),
    sdfloat_value(pressure),
    sdfloat_value(temperature),
    sdfloat_value(temperature),
    fluid_id,
    citation_key,
    quantity_id,
    sdfloat_value(pressure),
    sdfloat_value(temperature),
    )
    )

    result_sw = cursor.fetchone()
    assert( result_sw != None )

    pressure_sw       = result_sw[1]
    temperature_sw    = result_sw[2]
    fluid_property_sw = sdfloat( result_sw[3], result_sw[4] )

    # Find closest "southeast" value.
    cursor.execute(
    """
    SELECT ( pressure - ? ) * ( pressure - ? ) + ( temperature - ? ) * ( temperature - ? ) as measure,
           pressure, temperature, fluid_property_value, fluid_property_uncertainty
    FROM fluid_property_values
    WHERE fluid_id=?
      AND citation_key=?
      AND quantity_id=?
      AND pressure >= ?
      AND temperature <= ?
    ORDER BY measure ASC LIMIT 1;
    """,
    (
    sdfloat_value(pressure),
    sdfloat_value(pressure),
    sdfloat_value(temperature),
    sdfloat_value(temperature),
    fluid_id,
    citation_key,
    quantity_id,
    sdfloat_value(pressure),
    sdfloat_value(temperature),
    )
    )

    result_se = cursor.fetchone()
    assert( result_se != None )

    pressure_se       = result_se[1]
    temperature_se    = result_se[2]
    fluid_property_se = sdfloat( result_se[3], result_se[4] )

    # Find closest "northwest" value.
    cursor.execute(
    """
    SELECT ( pressure - ? ) * ( pressure - ? ) + ( temperature - ? ) * ( temperature - ? ) as measure,
           pressure, temperature, fluid_property_value, fluid_property_uncertainty
    FROM fluid_property_values
    WHERE fluid_id=?
      AND citation_key=?
      AND quantity_id=?
      AND pressure <= ?
      AND temperature >= ?
    ORDER BY measure ASC LIMIT 1;
    """,
    (
    sdfloat_value(pressure),
    sdfloat_value(pressure),
    sdfloat_value(temperature),
    sdfloat_value(temperature),
    fluid_id,
    citation_key,
    quantity_id,
    sdfloat_value(pressure),
    sdfloat_value(temperature),
    )
    )

    result_nw = cursor.fetchone()
    assert( result_nw != None )

    pressure_nw       = result_nw[1]
    temperature_nw    = result_nw[2]
    fluid_property_nw = sdfloat( result_nw[3], result_nw[4] )

    # Find closest "northeast" value.
    cursor.execute(
    """
    SELECT ( pressure - ? ) * ( pressure - ? ) + ( temperature - ? ) * ( temperature - ? ) as measure,
           pressure, temperature, fluid_property_value, fluid_property_uncertainty
    FROM fluid_property_values
    WHERE fluid_id=?
      AND citation_key=?
      AND quantity_id=?
      AND pressure >= ?
      AND temperature >= ?
    ORDER BY measure ASC LIMIT 1;
    """,
    (
    sdfloat_value(pressure),
    sdfloat_value(pressure),
    sdfloat_value(temperature),
    sdfloat_value(temperature),
    fluid_id,
    citation_key,
    quantity_id,
    sdfloat_value(pressure),
    sdfloat_value(temperature),
    )
    )

    result_ne = cursor.fetchone()
    assert( result_ne != None )

    pressure_ne       = result_ne[1]
    temperature_ne    = result_ne[2]
    fluid_property_ne = sdfloat( result_ne[3], result_ne[4] )

    # Are all pressures or temperatures  the same?
    if ( all( element == pressure_sw for element in [
                pressure_sw, pressure_se,
                pressure_nw, pressure_ne
              ] ) ):
        # All of the pressures are the same.  Determine the different
        # temperatures and use linear interpolation.
        temperature_1    = temperature_sw
        fluid_property_1 = fluid_property_sw
        temperature_2    = temperature_se
        fluid_property_2 = fluid_property_se

        if ( temperature_1 == temperature_2 ):
            temperature_2    = temperature_nw
            fluid_property_2 = fluid_property_nw

        if ( temperature_1 == temperature_2 ):
            temperature_2    = temperature_ne
            fluid_property_2 = fluid_property_ne

        fluid_property = fluid_property_1 + ( temperature - temperature_1 ) * ( fluid_property_2 - fluid_property_1 ) / ( temperature_2 - temperature_1 )
    elif ( all( element == temperature_sw for element in [
                temperature_sw, temperature_se,
                temperature_nw, temperature_ne
              ] ) ):
        # All of the temperatures are the same.  Determine the different
        # pressures and use linear interpolation.
        pressure_1       = pressure_sw
        fluid_property_1 = fluid_property_sw
        pressure_2       = pressure_se
        fluid_property_2 = fluid_property_se

        if ( pressure_1 == pressure_2 ):
            pressure_2       = pressure_nw
            fluid_property_2 = fluid_property_nw

        if ( pressure_1 == pressure_2 ):
            pressure_2       = pressure_ne
            fluid_property_2 = fluid_property_ne

        fluid_property = fluid_property_1 + ( pressure - pressure_1 ) * ( fluid_property_2 - fluid_property_1 ) / ( pressure_2 - pressure_1 )
    else:
        # Calculate the interpolated value using bilinear interpolation.
        #
        # Solve for the coefficients x in A*x = b, where
        #
        # A = [ [ 1.0, pressure_sw, temperature_sw, pressure_sw * temperature_sw ],
        #       [ 1.0, pressure_se, temperature_se, pressure_se * temperature_se ],
        #       [ 1.0, pressure_nw, temperature_nw, pressure_nw * temperature_nw ],
        #       [ 1.0, pressure_ne, temperature_ne, pressure_ne * temperature_ne ] ]
        #
        # and
        #
        # b = [ [ fluid_property_sw ],
        #       [ fluid_property_se ],
        #       [ fluid_property_nw ],
        #       [ fluid_property_ne ] ]

        coefficients = [None] * 4

        # These lines were generated using SymPy.
        coefficients[0] = (-pressure_ne*pressure_nw*fluid_property_se*temperature_ne*temperature_sw + pressure_ne*pressure_nw*fluid_property_se*temperature_nw*temperature_sw + pressure_ne*pressure_nw*fluid_property_sw*temperature_ne*temperature_se - pressure_ne*pressure_nw*fluid_property_sw*temperature_nw*temperature_se + pressure_ne*pressure_se*fluid_property_nw*temperature_ne*temperature_sw - pressure_ne*pressure_se*fluid_property_nw*temperature_se*temperature_sw - pressure_ne*pressure_se*fluid_property_sw*temperature_ne*temperature_nw + pressure_ne*pressure_se*fluid_property_sw*temperature_nw*temperature_se - pressure_ne*pressure_sw*fluid_property_nw*temperature_ne*temperature_se + pressure_ne*pressure_sw*fluid_property_nw*temperature_se*temperature_sw + pressure_ne*pressure_sw*fluid_property_se*temperature_ne*temperature_nw - pressure_ne*pressure_sw*fluid_property_se*temperature_nw*temperature_sw - pressure_nw*pressure_se*fluid_property_ne*temperature_nw*temperature_sw + pressure_nw*pressure_se*fluid_property_ne*temperature_se*temperature_sw + pressure_nw*pressure_se*fluid_property_sw*temperature_ne*temperature_nw - pressure_nw*pressure_se*fluid_property_sw*temperature_ne*temperature_se + pressure_nw*pressure_sw*fluid_property_ne*temperature_nw*temperature_se - pressure_nw*pressure_sw*fluid_property_ne*temperature_se*temperature_sw - pressure_nw*pressure_sw*fluid_property_se*temperature_ne*temperature_nw + pressure_nw*pressure_sw*fluid_property_se*temperature_ne*temperature_sw - pressure_se*pressure_sw*fluid_property_ne*temperature_nw*temperature_se + pressure_se*pressure_sw*fluid_property_ne*temperature_nw*temperature_sw + pressure_se*pressure_sw*fluid_property_nw*temperature_ne*temperature_se - pressure_se*pressure_sw*fluid_property_nw*temperature_ne*temperature_sw)/(pressure_ne*pressure_nw*temperature_ne*temperature_se - pressure_ne*pressure_nw*temperature_ne*temperature_sw - pressure_ne*pressure_nw*temperature_nw*temperature_se + pressure_ne*pressure_nw*temperature_nw*temperature_sw - pressure_ne*pressure_se*temperature_ne*temperature_nw + pressure_ne*pressure_se*temperature_ne*temperature_sw + pressure_ne*pressure_se*temperature_nw*temperature_se - pressure_ne*pressure_se*temperature_se*temperature_sw + pressure_ne*pressure_sw*temperature_ne*temperature_nw - pressure_ne*pressure_sw*temperature_ne*temperature_se - pressure_ne*pressure_sw*temperature_nw*temperature_sw + pressure_ne*pressure_sw*temperature_se*temperature_sw + pressure_nw*pressure_se*temperature_ne*temperature_nw - pressure_nw*pressure_se*temperature_ne*temperature_se - pressure_nw*pressure_se*temperature_nw*temperature_sw + pressure_nw*pressure_se*temperature_se*temperature_sw - pressure_nw*pressure_sw*temperature_ne*temperature_nw + pressure_nw*pressure_sw*temperature_ne*temperature_sw + pressure_nw*pressure_sw*temperature_nw*temperature_se - pressure_nw*pressure_sw*temperature_se*temperature_sw + pressure_se*pressure_sw*temperature_ne*temperature_se - pressure_se*pressure_sw*temperature_ne*temperature_sw - pressure_se*pressure_sw*temperature_nw*temperature_se + pressure_se*pressure_sw*temperature_nw*temperature_sw)
        coefficients[1] = (pressure_ne*fluid_property_nw*temperature_ne*temperature_se - pressure_ne*fluid_property_nw*temperature_ne*temperature_sw - pressure_ne*fluid_property_se*temperature_ne*temperature_nw + pressure_ne*fluid_property_se*temperature_ne*temperature_sw + pressure_ne*fluid_property_sw*temperature_ne*temperature_nw - pressure_ne*fluid_property_sw*temperature_ne*temperature_se - pressure_nw*fluid_property_ne*temperature_nw*temperature_se + pressure_nw*fluid_property_ne*temperature_nw*temperature_sw + pressure_nw*fluid_property_se*temperature_ne*temperature_nw - pressure_nw*fluid_property_se*temperature_nw*temperature_sw - pressure_nw*fluid_property_sw*temperature_ne*temperature_nw + pressure_nw*fluid_property_sw*temperature_nw*temperature_se + pressure_se*fluid_property_ne*temperature_nw*temperature_se - pressure_se*fluid_property_ne*temperature_se*temperature_sw - pressure_se*fluid_property_nw*temperature_ne*temperature_se + pressure_se*fluid_property_nw*temperature_se*temperature_sw + pressure_se*fluid_property_sw*temperature_ne*temperature_se - pressure_se*fluid_property_sw*temperature_nw*temperature_se - pressure_sw*fluid_property_ne*temperature_nw*temperature_sw + pressure_sw*fluid_property_ne*temperature_se*temperature_sw + pressure_sw*fluid_property_nw*temperature_ne*temperature_sw - pressure_sw*fluid_property_nw*temperature_se*temperature_sw - pressure_sw*fluid_property_se*temperature_ne*temperature_sw + pressure_sw*fluid_property_se*temperature_nw*temperature_sw)/(pressure_ne*pressure_nw*temperature_ne*temperature_se - pressure_ne*pressure_nw*temperature_ne*temperature_sw - pressure_ne*pressure_nw*temperature_nw*temperature_se + pressure_ne*pressure_nw*temperature_nw*temperature_sw - pressure_ne*pressure_se*temperature_ne*temperature_nw + pressure_ne*pressure_se*temperature_ne*temperature_sw + pressure_ne*pressure_se*temperature_nw*temperature_se - pressure_ne*pressure_se*temperature_se*temperature_sw + pressure_ne*pressure_sw*temperature_ne*temperature_nw - pressure_ne*pressure_sw*temperature_ne*temperature_se - pressure_ne*pressure_sw*temperature_nw*temperature_sw + pressure_ne*pressure_sw*temperature_se*temperature_sw + pressure_nw*pressure_se*temperature_ne*temperature_nw - pressure_nw*pressure_se*temperature_ne*temperature_se - pressure_nw*pressure_se*temperature_nw*temperature_sw + pressure_nw*pressure_se*temperature_se*temperature_sw - pressure_nw*pressure_sw*temperature_ne*temperature_nw + pressure_nw*pressure_sw*temperature_ne*temperature_sw + pressure_nw*pressure_sw*temperature_nw*temperature_se - pressure_nw*pressure_sw*temperature_se*temperature_sw + pressure_se*pressure_sw*temperature_ne*temperature_se - pressure_se*pressure_sw*temperature_ne*temperature_sw - pressure_se*pressure_sw*temperature_nw*temperature_se + pressure_se*pressure_sw*temperature_nw*temperature_sw)
        coefficients[2] = (pressure_ne*pressure_nw*fluid_property_se*temperature_ne - pressure_ne*pressure_nw*fluid_property_se*temperature_nw - pressure_ne*pressure_nw*fluid_property_sw*temperature_ne + pressure_ne*pressure_nw*fluid_property_sw*temperature_nw - pressure_ne*pressure_se*fluid_property_nw*temperature_ne + pressure_ne*pressure_se*fluid_property_nw*temperature_se + pressure_ne*pressure_se*fluid_property_sw*temperature_ne - pressure_ne*pressure_se*fluid_property_sw*temperature_se + pressure_ne*pressure_sw*fluid_property_nw*temperature_ne - pressure_ne*pressure_sw*fluid_property_nw*temperature_sw - pressure_ne*pressure_sw*fluid_property_se*temperature_ne + pressure_ne*pressure_sw*fluid_property_se*temperature_sw + pressure_nw*pressure_se*fluid_property_ne*temperature_nw - pressure_nw*pressure_se*fluid_property_ne*temperature_se - pressure_nw*pressure_se*fluid_property_sw*temperature_nw + pressure_nw*pressure_se*fluid_property_sw*temperature_se - pressure_nw*pressure_sw*fluid_property_ne*temperature_nw + pressure_nw*pressure_sw*fluid_property_ne*temperature_sw + pressure_nw*pressure_sw*fluid_property_se*temperature_nw - pressure_nw*pressure_sw*fluid_property_se*temperature_sw + pressure_se*pressure_sw*fluid_property_ne*temperature_se - pressure_se*pressure_sw*fluid_property_ne*temperature_sw - pressure_se*pressure_sw*fluid_property_nw*temperature_se + pressure_se*pressure_sw*fluid_property_nw*temperature_sw)/(pressure_ne*pressure_nw*temperature_ne*temperature_se - pressure_ne*pressure_nw*temperature_ne*temperature_sw - pressure_ne*pressure_nw*temperature_nw*temperature_se + pressure_ne*pressure_nw*temperature_nw*temperature_sw - pressure_ne*pressure_se*temperature_ne*temperature_nw + pressure_ne*pressure_se*temperature_ne*temperature_sw + pressure_ne*pressure_se*temperature_nw*temperature_se - pressure_ne*pressure_se*temperature_se*temperature_sw + pressure_ne*pressure_sw*temperature_ne*temperature_nw - pressure_ne*pressure_sw*temperature_ne*temperature_se - pressure_ne*pressure_sw*temperature_nw*temperature_sw + pressure_ne*pressure_sw*temperature_se*temperature_sw + pressure_nw*pressure_se*temperature_ne*temperature_nw - pressure_nw*pressure_se*temperature_ne*temperature_se - pressure_nw*pressure_se*temperature_nw*temperature_sw + pressure_nw*pressure_se*temperature_se*temperature_sw - pressure_nw*pressure_sw*temperature_ne*temperature_nw + pressure_nw*pressure_sw*temperature_ne*temperature_sw + pressure_nw*pressure_sw*temperature_nw*temperature_se - pressure_nw*pressure_sw*temperature_se*temperature_sw + pressure_se*pressure_sw*temperature_ne*temperature_se - pressure_se*pressure_sw*temperature_ne*temperature_sw - pressure_se*pressure_sw*temperature_nw*temperature_se + pressure_se*pressure_sw*temperature_nw*temperature_sw)
        coefficients[3] = (fluid_property_ne*(pressure_se - pressure_sw)*((pressure_nw - pressure_sw)*(temperature_se - temperature_sw) - (pressure_se - pressure_sw)*(temperature_nw - temperature_sw)) - fluid_property_nw*(pressure_se - pressure_sw)*((pressure_ne - pressure_sw)*(temperature_se - temperature_sw) - (pressure_se - pressure_sw)*(temperature_ne - temperature_sw)) - fluid_property_se*((pressure_ne - pressure_sw)*((pressure_nw - pressure_sw)*(temperature_se - temperature_sw) - (pressure_se - pressure_sw)*(temperature_nw - temperature_sw)) - (pressure_nw - pressure_sw)*((pressure_ne - pressure_sw)*(temperature_se - temperature_sw) - (pressure_se - pressure_sw)*(temperature_ne - temperature_sw))) + fluid_property_sw*((pressure_ne - pressure_se)*((pressure_nw - pressure_sw)*(temperature_se - temperature_sw) - (pressure_se - pressure_sw)*(temperature_nw - temperature_sw)) - (pressure_nw - pressure_se)*((pressure_ne - pressure_sw)*(temperature_se - temperature_sw) - (pressure_se - pressure_sw)*(temperature_ne - temperature_sw))))/(((pressure_ne - pressure_sw)*(temperature_se - temperature_sw) - (pressure_se - pressure_sw)*(temperature_ne - temperature_sw))*((pressure_nw - pressure_sw)*(pressure_se*temperature_se - pressure_sw*temperature_sw) - (pressure_se - pressure_sw)*(pressure_nw*temperature_nw - pressure_sw*temperature_sw)) - ((pressure_ne - pressure_sw)*(pressure_se*temperature_se - pressure_sw*temperature_sw) - (pressure_se - pressure_sw)*(pressure_ne*temperature_ne - pressure_sw*temperature_sw))*((pressure_nw - pressure_sw)*(temperature_se - temperature_sw) - (pressure_se - pressure_sw)*(temperature_nw - temperature_sw)))

        fluid_property = coefficients[0]               \
                       + coefficients[1] * pressure    \
                       + coefficients[2] * temperature \
                       + coefficients[3] * pressure * temperature

    return fluid_property

# This version of the method calculates some additional quantities as function
# of other quantities.  This is easier to manage in this way and prevents some
# duplication in the database itself.  For example, rather than storing both
# mass density and specific volume, the database only stores mass density.
# This choice prevents duplicated values from disagreeing with corresponding
# values.
#
# To support this, the script for loading fluid property values MUST not allow
# any quantities used in the branching of this method to enter into the
# database.
def interpolate_fluid_property_value( cursor, pressure, temperature,
                                      fluid_id, quantity_id,
                                      citation_key=None, ):
    if ( quantity_id == Q_KINEMATIC_VISCOSITY ):
        dynamic_viscosity = interpolate_fluid_property_value( cursor, pressure, temperature, fluid_id, Q_DYNAMIC_VISCOSITY, citation_key=citation_key )
        mass_density      = interpolate_fluid_property_value( cursor, pressure, temperature, fluid_id, Q_MASS_DENSITY,      citation_key=citation_key )
        return dynamic_viscosity / mass_density
    elif ( quantity_id == Q_PRANDTL_NUMBER ):
        kinematic_viscosity = interpolate_fluid_property_value( cursor, pressure, temperature, fluid_id, Q_KINEMATIC_VISCOSITY, citation_key=citation_key )
        thermal_diffusivity = interpolate_fluid_property_value( cursor, pressure, temperature, fluid_id, Q_THERMAL_DIFFUSIVITY, citation_key=citation_key )
        return kinematic_viscosity / thermal_diffusivity
    elif ( quantity_id == Q_THERMAL_DIFFUSIVITY ):
        mass_density                    = interpolate_fluid_property_value( cursor, pressure, temperature, fluid_id, Q_MASS_DENSITY,                    citation_key=citation_key )
        specific_isobaric_heat_capacity = interpolate_fluid_property_value( cursor, pressure, temperature, fluid_id, Q_SPECIFIC_ISOBARIC_HEAT_CAPACITY, citation_key=citation_key )
        thermal_conductivity            = interpolate_fluid_property_value( cursor, pressure, temperature, fluid_id, Q_THERMAL_CONDUCTIVITY,            citation_key=citation_key )
        return thermal_conductivity / ( mass_density * specific_isobaric_heat_capacity )
    elif ( quantity_id == Q_SPECIFIC_VOLUME ):
        mass_density = interpolate_fluid_property_value( cursor, pressure, temperature, fluid_id, Q_MASS_DENSITY, citation_key=citation_key )
        return 1.0 / mass_density
    else:
        return _interpolate_fluid_property_value( cursor, pressure, temperature, fluid_id, quantity_id, citation_key=citation_key )

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

def quantity_name( cursor, quantity_id ):
    cursor.execute(
    """
    SELECT quantity_name
    FROM quantities
    WHERE quantity_id=?;
    """,
    ( quantity_id, ),
    )

    return str(cursor.fetchone()[0])

def quantity_bounds( cursor, quantity_id ):
    cursor.execute(
    """
    SELECT minimum_value, maximum_value
    FROM quantities
    WHERE quantity_id=?;
    """,
    ( quantity_id, ),
    )

    return cursor.fetchone()

def camel_case( name ):
    return name.replace("-"," ").replace("'",' ').title().replace(" ","")

def quantity_camel_case_name( cursor, quantity_id ):
    return camel_case( quantity_name( cursor, quantity_id ) )

