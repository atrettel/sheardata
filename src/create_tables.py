#!/usr/bin/env python3

# Copyright (C) 2020-2021 Andrew Trettel
#
# SPDX-License-Identifier: MIT

import csv
import sqlite3
import sheardata as sd
import sys

conn = sqlite3.connect( sys.argv[1] )
cursor =  conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

# Value types
cursor.execute(
"""
CREATE TABLE value_types (
    identifier  TEXT PRIMARY KEY UNIQUE,
    system_name TEXT NOT NULL
);
"""
)

value_types = {}
value_types[ sd.VT_UNAVERAGED_VALUE         ] = "unaveraged value"
value_types[ sd.VT_UNWEIGHTED_AVERAGE       ] = "unweighted averaging"
value_types[ sd.VT_DENSITY_WEIGHTED_AVERAGE ] = "density-weighted averaging"

for identifier in value_types:
    cursor.execute(
    """
    INSERT INTO value_types( identifier, system_name )
    VALUES( ?, ? );
    """,
    ( identifier, value_types[identifier], )
    )

# Coordinate systems
cursor.execute(
"""
CREATE TABLE coordinate_systems (
    identifier  TEXT PRIMARY KEY UNIQUE,
    system_name TEXT NOT NULL
);
"""
)

coordinate_systems = {}
coordinate_systems[ sd.CS_RECTANGULAR ] = "rectangular coordinates"
coordinate_systems[ sd.CS_CYLINDRICAL ] = "cylindrical coordinates"

for identifier in coordinate_systems:
    cursor.execute(
    """
    INSERT INTO coordinate_systems( identifier, system_name )
    VALUES( ?, ? );
    """,
    ( identifier, coordinate_systems[identifier], )
    )

# Flow classes
cursor.execute(
"""
CREATE TABLE flow_classes (
    identifier TEXT PRIMARY KEY UNIQUE CHECK ( length(identifier) = 1 ),
    class_name TEXT NOT NULL,
    parent     TEXT DEFAULT NULL,
    FOREIGN KEY(parent) REFERENCES flow_classes(identifier)
);
"""
)

class flow_class:
    name   = None
    parent = None

    def is_child( self ):
        return self.parent != None

    def __init__( self, name, parent ):
        self.name   = name
        self.parent = parent

flow_classes = {}
flow_classes[ sd.FC_BOUNDARY_LAYER       ] = flow_class( "boundary layer",            sd.FC_EXTERNAL_FLOW )
flow_classes[ sd.FC_DUCT_FLOW            ] = flow_class( "duct flow",                 sd.FC_INTERNAL_FLOW )
flow_classes[ sd.FC_EXTERNAL_FLOW        ] = flow_class( "external flow",         sd.FC_WALL_BOUNDED_FLOW )
flow_classes[ sd.FC_FREE_JET             ] = flow_class( "free jet",                sd.FC_FREE_SHEAR_FLOW )
flow_classes[ sd.FC_FREE_SHEAR_FLOW      ] = flow_class( "free shear flow",              sd.FC_SHEAR_FLOW )
flow_classes[ sd.FC_HOMOGENEOUS_FLOW     ] = flow_class( "homogeneous flow",      sd.FC_UNCLASSIFIED_FLOW )
flow_classes[ sd.FC_INHOMOGENEOUS_FLOW   ] = flow_class( "inhomogeneous flow",    sd.FC_UNCLASSIFIED_FLOW )
flow_classes[ sd.FC_INTERNAL_FLOW        ] = flow_class( "internal flow",         sd.FC_WALL_BOUNDED_FLOW )
flow_classes[ sd.FC_ISOTROPIC_FLOW       ] = flow_class( "isotropic flow",         sd.FC_HOMOGENEOUS_FLOW )
flow_classes[ sd.FC_MIXING_LAYER         ] = flow_class( "mixing layer",            sd.FC_FREE_SHEAR_FLOW )
flow_classes[ sd.FC_BOUNDARY_DRIVEN_FLOW ] = flow_class( "boundary-driven flow",      sd.FC_INTERNAL_FLOW )
flow_classes[ sd.FC_SHEAR_FLOW           ] = flow_class( "shear flow",           sd.FC_INHOMOGENEOUS_FLOW )
flow_classes[ sd.FC_UNCLASSIFIED_FLOW    ] = flow_class( "flow",                                     None )
flow_classes[ sd.FC_WAKE                 ] = flow_class( "wake",                    sd.FC_FREE_SHEAR_FLOW )
flow_classes[ sd.FC_WALL_BOUNDED_FLOW    ] = flow_class( "wall-bounded flow",            sd.FC_SHEAR_FLOW )
flow_classes[ sd.FC_WALL_JET             ] = flow_class( "wall jet",                  sd.FC_EXTERNAL_FLOW )

for identifier in flow_classes:
    cursor.execute(
    """
    INSERT INTO flow_classes( identifier, class_name )
    VALUES( ?, ? );
    """,
    ( identifier, flow_classes[identifier].name, )
    )

# Two separate loops MUST occur due to foreign key constraints.
for identifier in flow_classes:
    if ( flow_classes[identifier].is_child() ):
        cursor.execute(
        """
        UPDATE flow_classes SET parent=? WHERE identifier=?;
        """,
        ( flow_classes[identifier].parent, identifier, )
        )

# Flow regimes
cursor.execute(
"""
CREATE TABLE flow_regimes (
    identifier  TEXT PRIMARY KEY UNIQUE,
    regime_name TEXT NOT NULL
);
"""
)

flow_regimes = {}
flow_regimes[      sd.LAMINAR_FLOW_REGIME ] =      "laminar flow"
flow_regimes[ sd.TRANSITIONAL_FLOW_REGIME ] = "transitional flow"
flow_regimes[    sd.TURBULENT_FLOW_REGIME ] =    "turbulent flow"

for identifier in flow_regimes:
    cursor.execute(
    """
    INSERT INTO flow_regimes( identifier, regime_name )
    VALUES( ?, ? );
    """,
    ( identifier, flow_regimes[identifier], )
    )

# Phases
cursor.execute(
"""
CREATE TABLE phases (
    identifier TEXT PRIMARY KEY UNIQUE,
    phase_name TEXT NOT NULL
);
"""
)

phases = {}
phases[ sd.GAS_PHASE    ] =    "gas"
phases[ sd.LIQUID_PHASE ] = "liquid"
phases[ sd.SOLID_PHASE  ] =  "solid"

for identifier in phases:
    cursor.execute(
    """
    INSERT INTO phases( identifier, phase_name )
    VALUES( ?, ? );
    """,
    ( identifier, phases[identifier], )
    )

# Elements
cursor.execute(
"""
CREATE TABLE elements (
    atomic_number  INTEGER PRIMARY KEY UNIQUE,
    element_symbol TEXT NOT NULL,
    element_name   TEXT NOT NULL,
    atomic_weight  REAL NOT NULL CHECK ( atomic_weight > 0.0 )
);
"""
)

elements_filename = "../data/elements.csv"
with open( elements_filename, "r" ) as elements_file:
    elements_reader = csv.reader( elements_file, delimiter=",", quotechar='"', \
        skipinitialspace=True )
    next(elements_reader)
    for elements_row in elements_reader:
        atomic_number  =   int(elements_row[0])
        element_symbol =   str(elements_row[1])
        element_name   =   str(elements_row[2])
        atomic_weight  = float(elements_row[3])

        cursor.execute(
        """
        INSERT INTO elements VALUES( ?, ?, ?, ? );
        """,
        (
            atomic_number,
            element_symbol,
            element_name,
            atomic_weight,
        )
        )

# Fluids
#
# This table is vestigial at the moment until a better way to handle fluid
# mixtures and properties is implemented.
cursor.execute(
"""
CREATE TABLE fluids (
    identifier TEXT PRIMARY KEY UNIQUE,
    fluid_name TEXT NOT NULL,
    phase      TEXT NOT NULL,
    FOREIGN KEY(phase) REFERENCES phases(identifier)
);
"""
)

# Geometries
cursor.execute(
"""
CREATE TABLE geometries (
    identifier    TEXT PRIMARY KEY UNIQUE,
    geometry_name TEXT NOT NULL
);
"""
)

geometries = {}
geometries[ sd.ELLIPTICAL_GEOMETRY  ] =  "elliptical geometry"
geometries[ sd.RECTANGULAR_GEOMETRY ] = "rectangular geometry"

for identifier in geometries:
    cursor.execute(
    """
    INSERT INTO geometries( identifier, geometry_name )
    VALUES( ?, ? );
    """,
    ( identifier, geometries[identifier], )
    )

# Measurement techniques
cursor.execute(
"""
CREATE TABLE measurement_techniques (
    identifier     TEXT PRIMARY KEY UNIQUE,
    technique_name TEXT NOT NULL,
    intrusive      INTEGER NOT NULL DEFAULT 0 CHECK ( intrusive = 0 OR intrusive = 1 ),
    parent         TEXT DEFAULT NULL,
    FOREIGN KEY(parent) REFERENCES measurement_techniques(identifier)
);
"""
)

class MeasTech:
    name      = None
    intrusive = None
    parent    = None

    def is_child( self ):
        return self.parent != None

    def __init__( self, name, parent, intrusive=False, ):
        self.name      = str(name)
        self.intrusive = 1 if intrusive else 0
        self.parent    = parent

measurement_techniques = {}
measurement_techniques[ sd.MT_ROOT                                     ] = MeasTech( "knowledge source",                         None,                                               )
measurement_techniques[ sd.MT_REASONING                                ] = MeasTech( "reasoning",                                sd.MT_ROOT,                                         )
measurement_techniques[ sd.MT_APPROXIMATION                            ] = MeasTech( "approximation",                            sd.MT_REASONING,                                    )
measurement_techniques[ sd.MT_ZEROTH_ORDER_APPROXIMATION               ] = MeasTech( "zeroth-order approximation",               sd.MT_APPROXIMATION,                                )
measurement_techniques[ sd.MT_CLAIM                                    ] = MeasTech( "claim",                                    sd.MT_REASONING,                                    )
measurement_techniques[ sd.MT_ASSUMPTION                               ] = MeasTech( "assumption",                               sd.MT_REASONING,                                    )
measurement_techniques[ sd.MT_CALCULATION                              ] = MeasTech( "calculation",                              sd.MT_REASONING,                                    )
measurement_techniques[ sd.MT_OBSERVATION                              ] = MeasTech( "observation",                              sd.MT_ROOT,                                         )
measurement_techniques[ sd.MT_DIFFERENTIAL_PRESSURE_METHOD             ] = MeasTech( "differential pressure method",             sd.MT_OBSERVATION,                                  )
measurement_techniques[ sd.MT_IMPACT_TUBE                              ] = MeasTech( "impact tube",                              sd.MT_DIFFERENTIAL_PRESSURE_METHOD, intrusive=True, )
measurement_techniques[ sd.MT_PITOT_STATIC_TUBE                        ] = MeasTech( "Pitot-static tube",                        sd.MT_DIFFERENTIAL_PRESSURE_METHOD, intrusive=True, )
measurement_techniques[ sd.MT_FLOW_RATE_MEASUREMENT                    ] = MeasTech( "flow rate measurement",                    sd.MT_OBSERVATION,                                  )
measurement_techniques[ sd.MT_WEIGHING_METHOD                          ] = MeasTech( "weighing method",                          sd.MT_FLOW_RATE_MEASUREMENT,                        )
measurement_techniques[ sd.MT_OPTICAL_METHOD                           ] = MeasTech( "optical method",                           sd.MT_OBSERVATION,                                  )
measurement_techniques[ sd.MT_DIRECT_INJECTION_METHOD                  ] = MeasTech( "direct injection method",                  sd.MT_OPTICAL_METHOD,                               )
measurement_techniques[ sd.MT_INDEX_OF_REFRACTION_METHOD               ] = MeasTech( "index-of-refraction method",               sd.MT_OPTICAL_METHOD,                               )
measurement_techniques[ sd.MT_MACH_ZEHNDER_INTERFEROMETRY              ] = MeasTech( "Mach-Zehnder interferometry",              sd.MT_INDEX_OF_REFRACTION_METHOD,                   )
measurement_techniques[ sd.MT_SCHLIEREN_PHOTOGRAPHY                    ] = MeasTech( "schlieren photography",                    sd.MT_INDEX_OF_REFRACTION_METHOD,                   )
measurement_techniques[ sd.MT_SHADOWGRAPH_PHOTOGRAPHY                  ] = MeasTech( "shadowgraph photography",                  sd.MT_INDEX_OF_REFRACTION_METHOD,                   )
measurement_techniques[ sd.MT_LASER_DOPPLER_ANEMOMETRY                 ] = MeasTech( "laser Doppler anemometry",                 sd.MT_OPTICAL_METHOD,                               )
measurement_techniques[ sd.MT_PARTICLE_IMAGE_VELOCIMETRY               ] = MeasTech( "particle image velocimetry",               sd.MT_OPTICAL_METHOD,                               )
measurement_techniques[ sd.MT_THERMAL_ANEMOMETRY                       ] = MeasTech( "thermal anemometry",                       sd.MT_OBSERVATION,                                  )
measurement_techniques[ sd.MT_HOT_WIRE_ANEMOMETRY                      ] = MeasTech( "hot-wire anemometry",                      sd.MT_THERMAL_ANEMOMETRY,           intrusive=True, )
measurement_techniques[ sd.MT_CONSTANT_CURRENT_HOT_WIRE_ANEMOMETRY     ] = MeasTech( "constant-current hot-wire anemometry",     sd.MT_HOT_WIRE_ANEMOMETRY,          intrusive=True, )
measurement_techniques[ sd.MT_CONSTANT_TEMPERATURE_HOT_WIRE_ANEMOMETRY ] = MeasTech( "constant-temperature hot-wire anemometry", sd.MT_HOT_WIRE_ANEMOMETRY,          intrusive=True, )
measurement_techniques[ sd.MT_WALL_SHEAR_STRESS_METHOD                 ] = MeasTech( "wall shear stress method",                 sd.MT_OBSERVATION,                                  )
measurement_techniques[ sd.MT_FLOATING_ELEMENT_BALANCE                 ] = MeasTech( "floating element balance",                 sd.MT_WALL_SHEAR_STRESS_METHOD,                     )
measurement_techniques[ sd.MT_MOMENTUM_BALANCE                         ] = MeasTech( "momentum balance",                         sd.MT_WALL_SHEAR_STRESS_METHOD,                     )
measurement_techniques[ sd.MT_STANTON_TUBE                             ] = MeasTech( "Stanton tube",                             sd.MT_WALL_SHEAR_STRESS_METHOD,     intrusive=True, )
measurement_techniques[ sd.MT_PRESTON_TUBE                             ] = MeasTech( "Preston tube",                             sd.MT_WALL_SHEAR_STRESS_METHOD,     intrusive=True, )
measurement_techniques[ sd.MT_VELOCITY_PROFILE_METHOD                  ] = MeasTech( "velocity profile method",                  sd.MT_WALL_SHEAR_STRESS_METHOD,                     )
measurement_techniques[ sd.MT_CLAUSER_METHOD                           ] = MeasTech( "Clauser method",                           sd.MT_VELOCITY_PROFILE_METHOD,                      )
measurement_techniques[ sd.MT_VISCOUS_SUBLAYER_SLOPE_METHOD            ] = MeasTech( "viscous sublayer slope method",            sd.MT_VELOCITY_PROFILE_METHOD,                      )

for identifier in measurement_techniques:
    cursor.execute(
    """
    INSERT INTO measurement_techniques( identifier, technique_name, intrusive )
    VALUES( ?, ?, ? );
    """,
    (
        identifier,
        measurement_techniques[identifier].name,
        measurement_techniques[identifier].intrusive,
    )
    )

# Two separate loops MUST occur due to foreign key constraints.
for identifier in measurement_techniques:
    if ( measurement_techniques[identifier].is_child() ):
        cursor.execute(
        """
        UPDATE measurement_techniques SET parent=? WHERE identifier=?;
        """,
        ( measurement_techniques[identifier].parent, identifier, )
        )

# Notes
cursor.execute(
"""
CREATE TABLE notes (
    note_id  INTEGER PRIMARY KEY CHECK ( note_id > 0 ),
    contents TEXT NOT NULL
);
"""
)

# Point labels
cursor.execute(
"""
CREATE TABLE point_labels (
    identifier TEXT PRIMARY KEY UNIQUE,
    label_name TEXT NOT NULL
);
"""
)

point_labels = {}
point_labels[ sd.PL_CENTER_LINE ] = "center-line"
point_labels[ sd.PL_EDGE        ] = "edge"
point_labels[ sd.PL_WALL        ] = "wall"

for identifier in point_labels:
    cursor.execute(
    """
    INSERT INTO point_labels( identifier, label_name )
    VALUES( ?, ? );
    """,
    ( identifier, point_labels[identifier], )
    )

# Quantities
cursor.execute(
"""
CREATE TABLE quantities (
    identifier           TEXT PRIMARY KEY UNIQUE,
    quantity_name        TEXT NOT NULL,
    length_exponent      REAL NOT NULL DEFAULT 0.0,
    mass_exponent        REAL NOT NULL DEFAULT 0.0,
    time_exponent        REAL NOT NULL DEFAULT 0.0,
    temperature_exponent REAL NOT NULL DEFAULT 0.0
);
"""
)

class quantity:
    name                 = None
    length_exponent      = None
    mass_exponent        = None
    time_exponent        = None
    temperature_exponent = None
    amount_exponent      = None

    def __init__( self, name, length_exponent=0.0, mass_exponent=0.0, \
                  time_exponent=0.0, temperature_exponent=0.0,        \
                  amount_exponent=0.0, ):
        self.name                 = str(name)
        self.length_exponent      = length_exponent
        self.mass_exponent        = mass_exponent
        self.time_exponent        = time_exponent
        self.temperature_exponent = temperature_exponent
        self.amount_exponent      = amount_exponent

quantities = {}

# Quantities for series
quantities[ sd.Q_ANGLE_OF_ATTACK                ] = quantity( "angle of attack",                                                                                   )
quantities[ sd.Q_BODY_HEIGHT                    ] = quantity( "body height",                         length_exponent=+1.0,                                         )
quantities[ sd.Q_BODY_LENGTH                    ] = quantity( "body length",                         length_exponent=+1.0,                                         )
quantities[ sd.Q_BODY_REYNOLDS_NUMBER           ] = quantity( "body Reynolds number",                                                                              )
quantities[ sd.Q_BODY_STROUHAL_NUMBER           ] = quantity( "body Strouhal number",                                                                              )
quantities[ sd.Q_BODY_WIDTH                     ] = quantity( "body width",                          length_exponent=+1.0,                                         )
quantities[ sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS ] = quantity( "distance between pressure taps",      length_exponent=+1.0,                                         )
quantities[ sd.Q_DRAG_COEFFICIENT               ] = quantity( "drag coefficient",                                                                                  )
quantities[ sd.Q_DRAG_FORCE                     ] = quantity( "drag force",                          length_exponent=+1.0, mass_exponent=+1.0, time_exponent=-2.0, )
quantities[ sd.Q_FREESTREAM_MACH_NUMBER         ] = quantity( "freestream Mach number",                                                                            )
quantities[ sd.Q_FREESTREAM_SPEED_OF_SOUND      ] = quantity( "freestream speed of sound",           length_exponent=+1.0, time_exponent=-1.0,                     )
quantities[ sd.Q_FREESTREAM_TEMPERATURE         ] = quantity( "freestream temperature",         temperature_exponent=+1.0,                                         )
quantities[ sd.Q_FREESTREAM_VELOCITY            ] = quantity( "freestream velocity",                 length_exponent=+1.0, time_exponent=-1.0,                     )
quantities[ sd.Q_LEADING_EDGE_LENGTH            ] = quantity( "leading edge length",                 length_exponent=+1.0,                                         )
quantities[ sd.Q_LEADING_EDGE_RADIUS            ] = quantity( "leading edge radius",                 length_exponent=+1.0,                                         )
quantities[ sd.Q_LIFT_COEFFICIENT               ] = quantity( "lift coefficient",                                                                                  )
quantities[ sd.Q_LIFT_FORCE                     ] = quantity( "lift force",                          length_exponent=+1.0, mass_exponent=+1.0, time_exponent=-2.0, )
quantities[ sd.Q_LIFT_TO_DRAG_RATIO             ] = quantity( "lift-to-drag ratio",                                                                                )
quantities[ sd.Q_MASS_FLOW_RATE                 ] = quantity( "mass flow rate",                        mass_exponent=+1.0, time_exponent=-1.0,                     )
quantities[ sd.Q_SPANWISE_NUMBER_OF_POINTS      ] = quantity( "spanwise number of points",                                                                         )
quantities[ sd.Q_STREAMWISE_NUMBER_OF_POINTS    ] = quantity( "streamwise number of points",                                                                       )
quantities[ sd.Q_TEST_LENGTH                    ] = quantity( "test length",                         length_exponent=+1.0,                                         )
quantities[ sd.Q_TRANSVERSE_NUMBER_OF_POINTS    ] = quantity( "transverse number of points",                                                                       )
quantities[ sd.Q_VOLUMETRIC_FLOW_RATE           ] = quantity( "volumetric flow rate",                length_exponent=+3.0, time_exponent=-1.0,                     )

# Quantities, station
quantities[ sd.Q_ASPECT_RATIO                           ] = quantity( "aspect ratio",                                                                                           )
quantities[ sd.Q_BULK_DYNAMIC_VISCOSITY                 ] = quantity( "bulk_dynamic viscosity",                 mass_exponent=+1.0,   length_exponent=-1.0, time_exponent=-1.0, )
quantities[ sd.Q_BULK_KINEMATIC_VISCOSITY               ] = quantity( "bulk kinematic viscosity",               length_exponent=+2.0,   time_exponent=-1.0,                     )
quantities[ sd.Q_BULK_MACH_NUMBER                       ] = quantity( "bulk Mach number",                                                                                       )
quantities[ sd.Q_BULK_MASS_DENSITY                      ] = quantity( "bulk mass density",                      mass_exponent=+1.0,   length_exponent=-3.0,                     )
quantities[ sd.Q_BULK_REYNOLDS_NUMBER                   ] = quantity( "bulk Reynolds number",                                                                                   )
quantities[ sd.Q_BULK_SPEED_OF_SOUND                    ] = quantity( "bulk speed of sound",                    length_exponent=+1.0,   time_exponent=-1.0,                     )
quantities[ sd.Q_BULK_VELOCITY                          ] = quantity( "bulk velocity",                          length_exponent=+1.0,   time_exponent=-1.0,                     )
quantities[ sd.Q_CLAUSER_THICKNESS                      ] = quantity( "Clauser thickness",                      length_exponent=+1.0,                                           )
quantities[ sd.Q_CROSS_SECTIONAL_AREA                   ] = quantity( "cross-sectional area",                   length_exponent=+2.0,                                           )
quantities[ sd.Q_DEVELOPMENT_LENGTH                     ] = quantity( "development length",                     length_exponent=+1.0,                                           )
quantities[ sd.Q_DISPLACEMENT_THICKNESS                 ] = quantity( "displacement thickness",                 length_exponent=+1.0,                                           )
quantities[ sd.Q_DISPLACEMENT_THICKNESS_REYNOLDS_NUMBER ] = quantity( "displacement thickness Reynolds number",                                                                 )
quantities[ sd.Q_ENERGY_THICKNESS                       ] = quantity( "energy thickness",                       length_exponent=+1.0,                                           )
quantities[ sd.Q_EQUILIBRIUM_PARAMETER                  ] = quantity( "equilibrium parameter",                                                                                  )
quantities[ sd.Q_HALF_HEIGHT                            ] = quantity( "half height",                            length_exponent=+1.0,                                           )
quantities[ sd.Q_HEIGHT                                 ] = quantity( "height",                                 length_exponent=+1.0,                                           )
quantities[ sd.Q_HYDRAULIC_DIAMETER                     ] = quantity( "hydraulic diameter",                     length_exponent=+1.0,                                           )
quantities[ sd.Q_INNER_DIAMETER                         ] = quantity( "inner diameter",                         length_exponent=+1.0,                                           )
quantities[ sd.Q_MOMENTUM_INTEGRAL_LHS                  ] = quantity( "momentum integral left-hand side",                                                                       )
quantities[ sd.Q_MOMENTUM_INTEGRAL_RHS                  ] = quantity( "momentum integral right-hand side",                                                                      )
quantities[ sd.Q_MOMENTUM_THICKNESS                     ] = quantity( "momentum thickness",                     length_exponent=+1.0,                                           )
quantities[ sd.Q_MOMENTUM_THICKNESS_REYNOLDS_NUMBER     ] = quantity( "momentum thickness Reynolds number",                                                                     )
quantities[ sd.Q_OUTER_DIAMETER                         ] = quantity( "outer diameter",                         length_exponent=+1.0,                                           )
quantities[ sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH         ] = quantity( "outer-layer development length",                                                                         )
quantities[ sd.Q_RECOVERY_FACTOR                        ] = quantity( "recovery factor",                                                                                        )
quantities[ sd.Q_SHAPE_FACTOR_1_TO_2                    ] = quantity( "shape factor 1-to-2",                                                                                    )
quantities[ sd.Q_SHAPE_FACTOR_3_TO_2                    ] = quantity( "shape factor 3-to-2",                                                                                    )
quantities[ sd.Q_SPANWISE_PRESSURE_GRADIENT             ] = quantity( "spanwise pressure gradient",               mass_exponent=+1.0, length_exponent=-2.0, time_exponent=-2.0, )
quantities[ sd.Q_STREAMWISE_COORDINATE_REYNOLDS_NUMBER  ] = quantity( "streamwise coordinate Reynolds number",                                                                  )
quantities[ sd.Q_STREAMWISE_PRESSURE_GRADIENT           ] = quantity( "streamwise pressure gradient",             mass_exponent=+1.0, length_exponent=-2.0, time_exponent=-2.0, )
quantities[ sd.Q_TRANSVERSE_PRESSURE_GRADIENT           ] = quantity( "transverse pressure gradient",             mass_exponent=+1.0, length_exponent=-2.0, time_exponent=-2.0, )
quantities[ sd.Q_WETTED_PERIMETER                       ] = quantity( "wetted perimeter",                       length_exponent=+2.0,                                           )
quantities[ sd.Q_WIDTH                                  ] = quantity( "width",                                  length_exponent=+1.0,                                           )

# Quantities, wall point
quantities[ sd.Q_AVERAGE_SKIN_FRICTION_COEFFICIENT     ] = quantity( "average skin friction coefficient",                                                  )
quantities[ sd.Q_DARCY_FRICTION_FACTOR                 ] = quantity( "Darcy friction factor",                                                              )
quantities[ sd.Q_FANNING_FRICTION_FACTOR               ] = quantity( "Fanning friction factor",                                                            )
quantities[ sd.Q_FRICTION_MACH_NUMBER                  ] = quantity( "friction Mach number",                                                               )
quantities[ sd.Q_FRICTION_REYNOLDS_NUMBER              ] = quantity( "friction Reynolds number",                                                           )
quantities[ sd.Q_FRICTION_TEMPERATURE                  ] = quantity( "friction temperature",                temperature_exponent=+1.0,                     )
quantities[ sd.Q_FRICTION_VELOCITY                     ] = quantity( "friction velocity",                        length_exponent=+1.0, time_exponent=-1.0, )
quantities[ sd.Q_HEAT_TRANSFER_COEFFICIENT             ] = quantity( "heat transfer coefficient",                                                          )
quantities[ sd.Q_INNER_LAYER_HEAT_FLUX                 ] = quantity( "inner-layer heat flux",                                                              )
quantities[ sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT          ] = quantity( "inner-layer roughness height",                                                       )
quantities[ sd.Q_LOCAL_SKIN_FRICTION_COEFFICIENT       ] = quantity( "local skin friction coefficient",                                                    )
quantities[ sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT          ] = quantity( "outer-layer roughness height",                                                       )
quantities[ sd.Q_PRESSURE_COEFFICIENT                  ] = quantity( "pressure coefficient",                                                               )
quantities[ sd.Q_ROUGHNESS_HEIGHT                      ] = quantity( "roughness height",                         length_exponent=+1.0,                     )
quantities[ sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER   ] = quantity( "semi-local friction Reynolds number",                                                )
quantities[ sd.Q_SPANWISE_WALL_CURVATURE               ] = quantity( "spanwise wall curvature",                  length_exponent=-1.0,                     )
quantities[ sd.Q_STREAMWISE_WALL_CURVATURE             ] = quantity( "streamwise wall curvature",                length_exponent=-1.0,                     )
quantities[ sd.Q_VISCOUS_LENGTH_SCALE                  ] = quantity( "viscous length scale",                     length_exponent=+1.0                      )

# Quantities, point
quantities[ sd.Q_DILATATION_RATE                                    ] = quantity( "dilatation rate",                         time_exponent=-1.0,                                                                             )
quantities[ sd.Q_DISTANCE_FROM_WALL                                 ] = quantity( "distance from wall",                    length_exponent=+1.0,                                                                             )
quantities[ sd.Q_DYNAMIC_VISCOSITY                                  ] = quantity( "dynamic viscosity",                       mass_exponent=+1.0, length_exponent=-1.0,        time_exponent=-1.0,                            )
quantities[ sd.Q_HEAT_CAPACITY_RATIO                                ] = quantity( "gamma",                                                                                                                                   )
quantities[ sd.Q_HEAT_FLUX                                          ] = quantity( "heat flux",                               mass_exponent=+1.0,   time_exponent=-3.0,                                                       )
quantities[ sd.Q_INNER_LAYER_COORDINATE                             ] = quantity( "inner-layer coordinate",                                                                                                                  )
quantities[ sd.Q_INNER_LAYER_TEMPERATURE                            ] = quantity( "inner-layer temperature",                                                                                                                 )
quantities[ sd.Q_INNER_LAYER_VELOCITY                               ] = quantity( "inner-layer velocity",                                                                                                                    )
quantities[ sd.Q_INNER_LAYER_VELOCITY_DEFECT                        ] = quantity( "inner-layer velocity defect",                                                                                                             )
quantities[ sd.Q_KINEMATIC_VISCOSITY                                ] = quantity( "kinematic viscosity",                   length_exponent=+2.0,   time_exponent=-1.0,                                                       )
quantities[ sd.Q_MACH_NUMBER                                        ] = quantity( "Mach number",                                                                                                                             )
quantities[ sd.Q_MASS_DENSITY                                       ] = quantity( "mass density",                            mass_exponent=+1.0, length_exponent=-3.0,                                                       )
quantities[ sd.Q_OUTER_LAYER_COORDINATE                             ] = quantity( "outer-layer coordinate",                                                                                                                  )
quantities[ sd.Q_OUTER_LAYER_TEMPERATURE                            ] = quantity( "outer-layer temperature",                                                                                                                 )
quantities[ sd.Q_OUTER_LAYER_VELOCITY                               ] = quantity( "outer-layer velocity",                                                                                                                    )
quantities[ sd.Q_OUTER_LAYER_VELOCITY_DEFECT                        ] = quantity( "outer-layer velocity defect",                                                                                                             )
quantities[ sd.Q_PRANDTL_NUMBER                                     ] = quantity( "Prandtl number",                                                                                                                          )
quantities[ sd.Q_PRESSURE                                           ] = quantity( "pressure",                                mass_exponent=+1.0, length_exponent=-1.0,        time_exponent=-2.0,                            )
quantities[ sd.Q_SEMI_LOCAL_COORDINATE                              ] = quantity( "semi-local inner-layer coordinate",                                                                                                       )
quantities[ sd.Q_SPANWISE_COORDINATE                                ] = quantity( "spanwise coordinate",                   length_exponent=+1.0,                                                                             )
quantities[ sd.Q_SPANWISE_VELOCITY                                  ] = quantity( "spanwise velocity",                     length_exponent=+1.0,   time_exponent=-1.0,                                                       )
quantities[ sd.Q_SPECIFIC_ENTHALPY                                  ] = quantity( "specific enthalpy",                     length_exponent=+2.0,   time_exponent=-2.0,                                                       )
quantities[ sd.Q_SPECIFIC_GAS_CONSTANT                              ] = quantity( "specific gas constant",                 length_exponent=+2.0,   time_exponent=-2.0, temperature_exponent=-1.0,                            )
quantities[ sd.Q_SPECIFIC_INTERNAL_ENERGY                           ] = quantity( "specific internal energy",              length_exponent=+2.0,   time_exponent=-2.0,                                                       )
quantities[ sd.Q_SPECIFIC_ISOBARIC_HEAT_CAPACITY                    ] = quantity( "specific isobaric heat capacity",       length_exponent=+2.0,   time_exponent=-2.0, temperature_exponent=-1.0,                            )
quantities[ sd.Q_SPECIFIC_ISOCHORIC_HEAT_CAPACITY                   ] = quantity( "specific isochoric heat capacity",      length_exponent=+2.0,   time_exponent=-2.0, temperature_exponent=-1.0,                            )
quantities[ sd.Q_SPECIFIC_TOTAL_ENTHALPY                            ] = quantity( "specific total enthalpy",               length_exponent=+2.0,   time_exponent=-2.0,                                                       )
quantities[ sd.Q_SPECIFIC_TOTAL_INTERNAL_ENERGY                     ] = quantity( "specific total internal energy",        length_exponent=+2.0,   time_exponent=-2.0,                                                       )
quantities[ sd.Q_SPECIFIC_VOLUME                                    ] = quantity( "specific volume",                       length_exponent=+3.0,   mass_exponent=-1.0,                                                       )
quantities[ sd.Q_SPEED                                              ] = quantity( "speed",                                 length_exponent=+1.0,   time_exponent=-1.0,                                                       )
quantities[ sd.Q_SPEED_OF_SOUND                                     ] = quantity( "speed of sound",                        length_exponent=+1.0,   time_exponent=-1.0,                                                       )
quantities[ sd.Q_STREAMWISE_COORDINATE                              ] = quantity( "streamwise coordinate",                 length_exponent=+1.0,                                                                             )
quantities[ sd.Q_STREAMWISE_VELOCITY                                ] = quantity( "streamwise velocity",                   length_exponent=+1.0,   time_exponent=-1.0,                                                       )
quantities[ sd.Q_TEMPERATURE                                        ] = quantity( "temperature",                      temperature_exponent=+1.0,                                                                             )
quantities[ sd.Q_THERMAL_CONDUCTIVITY                               ] = quantity( "thermal conductivity",                  length_exponent=+1.0,   mass_exponent=+1.0,        time_exponent=-3.0, temperature_exponent=-1.0, )
quantities[ sd.Q_THERMAL_DIFFUSIVITY                                ] = quantity( "thermal diffusivity",                   length_exponent=+2.0,   time_exponent=-1.0,                                                       )
quantities[ sd.Q_TOTAL_PRESSURE                                     ] = quantity( "total pressure",                          mass_exponent=+1.0, length_exponent=-1.0,        time_exponent=-2.0,                            )
quantities[ sd.Q_TOTAL_TEMPERATURE                                  ] = quantity( "total temperature",                temperature_exponent=+1.0,                                                                             )
quantities[ sd.Q_TRANSVERSE_COORDINATE                              ] = quantity( "transverse coordinate",                 length_exponent=+1.0,                                                                             )
quantities[ sd.Q_TRANSVERSE_VELOCITY                                ] = quantity( "transverse velocity",                   length_exponent=+1.0,   time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_DEFECT                                    ] = quantity( "velocity defect",                       length_exponent=+1.0,   time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_STREAMWISE] ] = quantity( "streamwise velocity gradient in streamwise direction",          time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_TRANSVERSE] ] = quantity( "streamwise velocity gradient in transverse direction",          time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_SPANWISE  ] ] = quantity( "streamwise velocity gradient in spanwise direction",            time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_STREAMWISE] ] = quantity( "transverse velocity gradient in streamwise direction",          time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_TRANSVERSE] ] = quantity( "transverse velocity gradient in transverse direction",          time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_SPANWISE  ] ] = quantity( "transverse velocity gradient in spanwise direction",            time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_STREAMWISE] ] = quantity( "spanwise velocity gradient in streamwise direction",            time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_TRANSVERSE] ] = quantity( "spanwise velocity gradient in transverse direction",            time_exponent=-1.0,                                                       )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_SPANWISE  ] ] = quantity( "spanwise velocity gradient in spanwise direction",              time_exponent=-1.0,                                                       )

quantities[ sd.Q_STRESS[sd.D_STREAMWISE,sd.D_STREAMWISE] ] = quantity(           "streamwise normal stress", mass_exponent=+1.0, length_exponent=-1.0, time_exponent=-2.0, )
quantities[ sd.Q_STRESS[sd.D_STREAMWISE,sd.D_TRANSVERSE] ] = quantity( "streamwise-transverse shear stress", mass_exponent=+1.0, length_exponent=-1.0, time_exponent=-2.0, )
quantities[ sd.Q_STRESS[sd.D_STREAMWISE,sd.D_SPANWISE  ] ] = quantity(   "streamwise-spanwise shear stress", mass_exponent=+1.0, length_exponent=-1.0, time_exponent=-2.0, )
quantities[ sd.Q_STRESS[sd.D_TRANSVERSE,sd.D_TRANSVERSE] ] = quantity(           "transverse normal stress", mass_exponent=+1.0, length_exponent=-1.0, time_exponent=-2.0, )
quantities[ sd.Q_STRESS[sd.D_TRANSVERSE,sd.D_SPANWISE  ] ] = quantity(   "transverse-spanwise shear stress", mass_exponent=+1.0, length_exponent=-1.0, time_exponent=-2.0, )
quantities[ sd.Q_STRESS[sd.D_SPANWISE,  sd.D_SPANWISE  ] ] = quantity(             "spanwise normal stress", mass_exponent=+1.0, length_exponent=-1.0, time_exponent=-2.0, )

# Quantities, point, turbulence
quantities[ sd.Q_MASS_DENSITY_AUTOCOVARIANCE                        ] = quantity( "mass density autocovariance",                     mass_exponent=+2.0, length_exponent=-6.0,                     )
quantities[ sd.Q_NORMALIZED_MASS_DENSITY_AUTOCOVARIANCE             ] = quantity( "normalized mass density autocovariance",                                                                        )
quantities[ sd.Q_NORMALIZED_PRESSURE_AUTOCOVARIANCE                 ] = quantity( "normalized pressure autocovariance",                                                                            )
quantities[ sd.Q_NORMALIZED_TEMPERATURE_AUTOCOVARIANCE              ] = quantity( "normalized temperature autocovariance",                                                                         )
quantities[ sd.Q_PRESSURE_AUTOCOVARIANCE                            ] = quantity( "pressure autocovariance",                         mass_exponent=+2.0, length_exponent=-2.0, time_exponent=-4.0, )
quantities[ sd.Q_INNER_LAYER_SPECIFIC_TURBULENT_KINETIC_ENERGY      ] = quantity( "inner-layer turbulent kinetic energy",                                                                          )
quantities[ sd.Q_MORKOVIN_SCALED_SPECIFIC_TURBULENT_KINETIC_ENERGY  ] = quantity( "Morkovin-scaled turbulent kinetic energy",                                                                      )
quantities[ sd.Q_SPECIFIC_TURBULENT_KINETIC_ENERGY                  ] = quantity( "specific turbulent kinetic energy",             length_exponent=+2.0,   time_exponent=-2.0,                     )
quantities[ sd.Q_TEMPERATURE_AUTOCOVARIANCE                         ] = quantity( "temperature autocovariance",               temperature_exponent=+2.0,                                           )

quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE] ] = quantity(              "streamwise velocity autocovariance", length_exponent=+2.0, time_exponent=-2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE] ] = quantity( "streamwise-transverse velocity cross covariance", length_exponent=+2.0, time_exponent=-2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ] ] = quantity(   "streamwise-spanwise velocity cross covariance", length_exponent=+2.0, time_exponent=-2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE] ] = quantity(              "transverse velocity autocovariance", length_exponent=+2.0, time_exponent=-2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ] ] = quantity(   "transverse-spanwise velocity cross covariance", length_exponent=+2.0, time_exponent=-2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ] ] = quantity(                "spanwise velocity autocovariance", length_exponent=+2.0, time_exponent=-2.0, )

quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE] ] = quantity(              "inner-layer streamwise velocity autocovariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE] ] = quantity( "inner-layer streamwise-transverse velocity cross covariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ] ] = quantity(   "inner-layer streamwise-spanwise velocity cross covariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE] ] = quantity(              "inner-layer transverse velocity autocovariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ] ] = quantity(   "inner-layer transverse-spanwise velocity cross covariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ] ] = quantity(                "inner-layer spanwise velocity autocovariance", )

quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE] ] = quantity(              "Morkovin-scaled streamwise velocity autocovariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE] ] = quantity( "Morkovin-scaled streamwise-transverse velocity cross covariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ] ] = quantity(   "Morkovin-scaled streamwise-spanwise velocity cross covariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE] ] = quantity(              "Morkovin-scaled transverse velocity autocovariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ] ] = quantity(   "Morkovin-scaled transverse-spanwise velocity cross covariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ] ] = quantity(                "Morkovin-scaled spanwise velocity autocovariance", )

# Quantities, point, ratios
quantities[ sd.Q_LOCAL_TO_BULK_STREAMWISE_VELOCITY_RATIO        ] = quantity( "local-to-bulk streamwise velocity ratio",        )
quantities[ sd.Q_LOCAL_TO_BULK_TEMPERATURE_RATIO                ] = quantity( "local-to-bulk temperature ratio",                )
quantities[ sd.Q_LOCAL_TO_CENTER_LINE_DYNAMIC_VISCOSITY_RATIO   ] = quantity( "local-to-center-line dynamic viscosity ratio",   )
quantities[ sd.Q_LOCAL_TO_CENTER_LINE_MASS_DENSITY_RATIO        ] = quantity( "local-to-center-line density ratio",             )
quantities[ sd.Q_LOCAL_TO_CENTER_LINE_STREAMWISE_VELOCITY_RATIO ] = quantity( "local-to-center-line streamwise velocity ratio", )
quantities[ sd.Q_LOCAL_TO_CENTER_LINE_TEMPERATURE_RATIO         ] = quantity( "local-to-center-line temperature ratio",         )
quantities[ sd.Q_LOCAL_TO_EDGE_DYNAMIC_VISCOSITY_RATIO          ] = quantity( "local-to-edge dynamic viscosity ratio",          )
quantities[ sd.Q_LOCAL_TO_EDGE_MASS_DENSITY_RATIO               ] = quantity( "local-to-edge density ratio",                    )
quantities[ sd.Q_LOCAL_TO_EDGE_STREAMWISE_VELOCITY_RATIO        ] = quantity( "local-to-edge streamwise velocity ratio",        )
quantities[ sd.Q_LOCAL_TO_EDGE_TEMPERATURE_RATIO                ] = quantity( "local-to-edge temperature ratio",                )
quantities[ sd.Q_LOCAL_TO_RECOVERY_TEMPERATURE_RATIO            ] = quantity( "local-to-recovery temperature ratio",            )
quantities[ sd.Q_LOCAL_TO_WALL_DYNAMIC_VISCOSITY_RATIO          ] = quantity( "local-to-wall dynamic viscosity ratio",          )
quantities[ sd.Q_LOCAL_TO_WALL_MASS_DENSITY_RATIO               ] = quantity( "local-to-wall density ratio",                    )
quantities[ sd.Q_LOCAL_TO_WALL_STREAMWISE_VELOCITY_RATIO        ] = quantity( "local-to-wall streamwise velocity ratio",        )
quantities[ sd.Q_LOCAL_TO_WALL_TEMPERATURE_RATIO                ] = quantity( "local-to-wall temperature ratio",                )

for identifier in quantities:
    cursor.execute(
    """
    INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent, time_exponent, temperature_exponent )
    VALUES( ?, ?, ?, ?, ?, ? );
    """,
    (
        identifier,
        quantities[identifier].name,
        quantities[identifier].length_exponent,
        quantities[identifier].mass_exponent,
        quantities[identifier].time_exponent,
        quantities[identifier].temperature_exponent,
    )
    )

# Study types
cursor.execute(
"""
CREATE TABLE study_types (
    identifier TEXT PRIMARY KEY UNIQUE,
    type_name  TEXT NOT NULL
);
"""
)

study_types = {}
study_types[ sd.DIRECT_NUMERICAL_SIMULATION_STUDY_TYPE ] = "direct numerical simulation"
study_types[                sd.EXPERIMENTAL_STUDY_TYPE ] = "experiment"
study_types[       sd.LARGE_EDDY_SIMULATION_STUDY_TYPE ] = "large eddy simulation"

for identifier in study_types:
    cursor.execute(
    """
    INSERT INTO study_types( identifier, type_name )
    VALUES( ?, ? );
    """,
    ( identifier, study_types[identifier], )
    )

# Studies
cursor.execute(
"""
CREATE TABLE studies (
    identifier            TEXT PRIMARY KEY UNIQUE,
    flow_class            TEXT NOT NULL DEFAULT 'U',
    year                  INTEGER NOT NULL CHECK (        year  >= 0 AND         year <= 9999 ),
    study_number          INTEGER NOT NULL CHECK ( study_number >  0 AND study_number <=  999 ),
    study_type            TEXT NOT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    description           TEXT DEFAULT NULL,
    provenance            TEXT DEFAULT NULL,
    FOREIGN KEY(flow_class) REFERENCES flow_classes(identifier),
    FOREIGN KEY(study_type) REFERENCES  study_types(identifier)
);
"""
)

# Series
cursor.execute(
"""
CREATE TABLE series (
    identifier           TEXT PRIMARY KEY UNIQUE,
    study                TEXT NOT NULL,
    series_number        INTEGER NOT NULL CHECK ( series_number > 0 AND series_number <= 999 ),
    number_of_dimensions INTEGER NOT NULL DEFAULT 2 CHECK ( number_of_dimensions > 0 AND number_of_dimensions <= 3 ),
    coordinate_system    TEXT NOT NULL DEFAULT 'XYZ',
    geometry             TEXT DEFAULT NULL,
    number_of_sides      TEXT DEFAULT NULL CHECK ( number_of_sides > 1 ),
    outlier              INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    description          TEXT DEFAULT NULL,
    FOREIGN KEY(coordinate_system) REFERENCES coordinate_systems(identifier),
    FOREIGN KEY(geometry)          REFERENCES         geometries(identifier)
);
"""
)

# Stations
cursor.execute(
"""
CREATE TABLE stations (
    identifier                   TEXT PRIMARY KEY UNIQUE,
    series                       TEXT NOT NULL,
    study                        TEXT NOT NULL,
    station_number               INTEGER NOT NULL CHECK ( station_number > 0 AND station_number <= 999 ),
    flow_regime                  TEXT DEFAULT NULL,
    previous_streamwise_station  TEXT DEFAULT NULL,
    next_streamwise_station      TEXT DEFAULT NULL,
    previous_spanwise_station    TEXT DEFAULT NULL,
    next_spanwise_station        TEXT DEFAULT NULL,
    outlier                      INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    description                  TEXT DEFAULT NULL,
    FOREIGN KEY(flow_regime)                 REFERENCES flow_regimes(identifier),
    FOREIGN KEY(previous_streamwise_station) REFERENCES     stations(identifier),
    FOREIGN KEY(next_streamwise_station)     REFERENCES     stations(identifier),
    FOREIGN KEY(previous_spanwise_station)   REFERENCES     stations(identifier),
    FOREIGN KEY(next_spanwise_station)       REFERENCES     stations(identifier)
);
"""
)

# Points
cursor.execute(
"""
CREATE TABLE points (
    identifier           TEXT PRIMARY KEY UNIQUE,
    station              TEXT NOT NULL,
    series               TEXT NOT NULL,
    study                TEXT NOT NULL,
    point_number         INTEGER NOT NULL CHECK ( point_number > 0 AND point_number <= 9999 ),
    point_label          TEXT DEFAULT NULL,
    outlier              INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    description          TEXT DEFAULT NULL,
    FOREIGN KEY(point_label) REFERENCES point_labels(identifier)
);
"""
)

# Sources (literature references)
#
# The classification refers to whether this source (reference) is a primary
# source (1) created during the study or whether this source is a secondary
# source (2) created later.
cursor.execute(
"""
CREATE TABLE sources (
    study          TEXT NOT NULL,
    source         TEXT NOT NULL,
    classification INTEGER NOT NULL DEFAULT 1 CHECK ( classification = 1 OR classification = 2 ),
    PRIMARY KEY(study, source),
    FOREIGN KEY(study) REFERENCES studies(identifier)
);
"""
)

# Components
#
# This table is vestigial at the moment until a better way to handle fluid
# mixtures and properties is implemented.
cursor.execute(
"""
CREATE TABLE components (
    series TEXT NOT NULL,
    fluid  TEXT DEFAULT NULL,
    name   TEXT DEFAULT NULL CHECK (
        fluid IS NULL     AND name IS NOT NULL
        OR
        fluid IS NOT NULL AND name IS NULL ),
    PRIMARY KEY(series, fluid),
    FOREIGN KEY(series) REFERENCES series(identifier),
    FOREIGN KEY(fluid)  REFERENCES fluids(identifier)
);
"""
)

# Study values
#
# Technically, there are no quantities that could be study values, but the
# table is included here for the sake of completeness.
cursor.execute(
"""
CREATE TABLE study_values (
    study             TEXT NOT NULL,
    quantity          TEXT NOT NULL,
    study_value       REAL NOT NULL,
    study_uncertainty REAL DEFAULT NULL CHECK ( study_uncertainty >= 0.0 ),
    value_type        TEXT NOT NULL,
    mt_set            INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    outlier           INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    PRIMARY KEY(study, quantity, value_type, mt_set),
    FOREIGN KEY(study)      REFERENCES     studies(identifier),
    FOREIGN KEY(quantity)   REFERENCES  quantities(identifier),
    FOREIGN KEY(value_type) REFERENCES value_types(identifier)
);
"""
)

# Series values
cursor.execute(
"""
CREATE TABLE series_values (
    series             TEXT NOT NULL,
    quantity           TEXT NOT NULL,
    series_value       REAL NOT NULL,
    series_uncertainty REAL DEFAULT NULL CHECK ( series_uncertainty >= 0.0 ),
    value_type         TEXT NOT NULL,
    mt_set             INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    outlier            INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    PRIMARY KEY(series, quantity, value_type, mt_set),
    FOREIGN KEY(series)     REFERENCES      series(identifier),
    FOREIGN KEY(quantity)   REFERENCES  quantities(identifier),
    FOREIGN KEY(value_type) REFERENCES value_types(identifier)
);
"""
)

# Station values
cursor.execute(
"""
CREATE TABLE station_values (
    station             TEXT NOT NULL,
    quantity            TEXT NOT NULL,
    station_value       REAL NOT NULL,
    station_uncertainty REAL DEFAULT NULL CHECK ( station_uncertainty >= 0.0 ),
    value_type          TEXT NOT NULL,
    mt_set              INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    outlier             INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    PRIMARY KEY(station, quantity, value_type, mt_set),
    FOREIGN KEY(station)    REFERENCES    stations(identifier),
    FOREIGN KEY(quantity)   REFERENCES  quantities(identifier),
    FOREIGN KEY(value_type) REFERENCES value_types(identifier)
);
"""
)

# Point values
cursor.execute(
"""
CREATE TABLE point_values (
    point             TEXT NOT NULL,
    quantity          TEXT NOT NULL,
    point_value       REAL NOT NULL,
    point_uncertainty REAL DEFAULT NULL CHECK ( point_uncertainty >= 0.0 ),
    value_type        TEXT NOT NULL,
    mt_set            INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    outlier           INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    PRIMARY KEY(point, quantity, value_type, mt_set),
    FOREIGN KEY(point)      REFERENCES      points(identifier),
    FOREIGN KEY(quantity)   REFERENCES  quantities(identifier),
    FOREIGN KEY(value_type) REFERENCES value_types(identifier)
);
"""
)

# Measurement techniques for study values
cursor.execute(
"""
CREATE TABLE study_values_mt (
    study      TEXT NOT NULL,
    quantity   TEXT NOT NULL,
    value_type TEXT NOT NULL,
    mt_set     INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    measurement_technique TEXT DEFAULT NULL,
    PRIMARY KEY(study, quantity, value_type, mt_set, measurement_technique),
    FOREIGN KEY(study)                 REFERENCES                studies(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(value_type)      REFERENCES      value_types(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);
"""
)

# Measurement techniques for series values
cursor.execute(
"""
CREATE TABLE series_values_mt (
    series     TEXT NOT NULL,
    quantity   TEXT NOT NULL,
    value_type TEXT NOT NULL,
    mt_set     INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    measurement_technique TEXT DEFAULT NULL,
    PRIMARY KEY(series, quantity, value_type, mt_set, measurement_technique),
    FOREIGN KEY(series)                REFERENCES                 series(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(value_type)            REFERENCES            value_types(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);
"""
)

# Measurement techniques for station values
cursor.execute(
"""
CREATE TABLE station_values_mt (
    station    TEXT NOT NULL,
    quantity   TEXT NOT NULL,
    value_type TEXT NOT NULL,
    mt_set     INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    measurement_technique TEXT DEFAULT NULL,
    PRIMARY KEY(station, quantity, value_type, mt_set, measurement_technique),
    FOREIGN KEY(station)               REFERENCES               stations(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(value_type)            REFERENCES            value_types(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);
"""
)

# Measurement techniques for point values
cursor.execute(
"""
CREATE TABLE point_values_mt (
    point      TEXT NOT NULL,
    quantity   TEXT NOT NULL,
    value_type TEXT NOT NULL,
    mt_set     INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    measurement_technique TEXT DEFAULT NULL,
    PRIMARY KEY(point, quantity, value_type, mt_set, measurement_technique),
    FOREIGN KEY(point)                 REFERENCES                 points(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(value_type)            REFERENCES            value_types(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);
"""
)

# Notes for studies
cursor.execute(
"""
CREATE TABLE study_notes (
    study TEXT NOT NULL,
    note  INTEGER NOT NULL CHECK ( note > 0 ),
    PRIMARY KEY(study, note),
    FOREIGN KEY(study) REFERENCES studies(identifier),
    FOREIGN KEY(note)  REFERENCES   notes(note_id)
);
"""
)

# Notes for study values
cursor.execute(
"""
CREATE TABLE study_value_notes (
    study      TEXT NOT NULL,
    quantity   TEXT NOT NULL,
    value_type TEXT NOT NULL,
    mt_set     INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    note       INTEGER NOT NULL CHECK ( note > 0 ),
    PRIMARY KEY(study, quantity, value_type, mt_set, note),
    FOREIGN KEY(study)            REFERENCES     studies(identifier),
    FOREIGN KEY(quantity)         REFERENCES  quantities(identifier),
    FOREIGN KEY(value_type)       REFERENCES value_types(identifier),
    FOREIGN KEY(note)             REFERENCES          notes(note_id)
);
"""
)

# Notes for series
cursor.execute(
"""
CREATE TABLE series_notes (
    series TEXT NOT NULL,
    note   INTEGER NOT NULL CHECK ( note > 0 ),
    PRIMARY KEY(series, note),
    FOREIGN KEY(series) REFERENCES series(identifier),
    FOREIGN KEY(note)   REFERENCES  notes(note_id)
);
"""
)

# Notes for series values
cursor.execute(
"""
CREATE TABLE series_value_notes (
    series     TEXT NOT NULL,
    quantity   TEXT NOT NULL,
    value_type TEXT NOT NULL,
    mt_set     INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    note       INTEGER NOT NULL CHECK ( note > 0 ),
    PRIMARY KEY(series, quantity, value_type, mt_set, note),
    FOREIGN KEY(series)     REFERENCES      series(identifier),
    FOREIGN KEY(quantity)   REFERENCES  quantities(identifier),
    FOREIGN KEY(value_type) REFERENCES value_types(identifier),
    FOREIGN KEY(note)       REFERENCES          notes(note_id)
);
"""
)

# Notes for stations
cursor.execute(
"""
CREATE TABLE station_notes (
    station TEXT NOT NULL,
    note    INTEGER NOT NULL CHECK ( note > 0 ),
    PRIMARY KEY(station, note),
    FOREIGN KEY(station) REFERENCES stations(identifier),
    FOREIGN KEY(note)    REFERENCES    notes(note_id)
);
"""
)

# Notes for station values
cursor.execute(
"""
CREATE TABLE station_value_notes (
    station    TEXT NOT NULL,
    quantity   TEXT NOT NULL,
    value_type TEXT NOT NULL,
    mt_set     INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    note       INTEGER NOT NULL CHECK ( note > 0 ),
    PRIMARY KEY(station, quantity, value_type, mt_set, note),
    FOREIGN KEY(station)    REFERENCES    stations(identifier),
    FOREIGN KEY(quantity)   REFERENCES  quantities(identifier),
    FOREIGN KEY(value_type) REFERENCES value_types(identifier),
    FOREIGN KEY(note)       REFERENCES          notes(note_id)
);
"""
)

# Notes for points
cursor.execute(
"""
CREATE TABLE point_notes (
    point TEXT NOT NULL,
    note  INTEGER NOT NULL CHECK ( note > 0 ),
    PRIMARY KEY(point, note),
    FOREIGN KEY(point) REFERENCES points(identifier),
    FOREIGN KEY(note)  REFERENCES  notes(note_id)
);
"""
)

# Notes for point values
cursor.execute(
"""
CREATE TABLE point_value_notes (
    point      TEXT NOT NULL,
    quantity   TEXT NOT NULL,
    value_type TEXT NOT NULL,
    mt_set     INTEGER NOT NULL DEFAULT 1 CHECK ( mt_set > 0 ),
    note       INTEGER NOT NULL CHECK ( note > 0 ),
    PRIMARY KEY(point, quantity, value_type, mt_set, note),
    FOREIGN KEY(point)      REFERENCES      points(identifier),
    FOREIGN KEY(quantity)   REFERENCES  quantities(identifier),
    FOREIGN KEY(value_type) REFERENCES value_types(identifier),
    FOREIGN KEY(note)       REFERENCES          notes(note_id)
);
"""
)

# Compilations
cursor.execute(
"""
CREATE TABLE compilations (
    compilation_id   INTEGER PRIMARY KEY CHECK ( compilation_id >= 0 ),
    compilation_name TEXT NOT NULL
);
"""
)

compilations = {}
compilations[ sd.C_SELF    ] = "Originator"
compilations[ sd.C_CH_1969 ] = "Coles and Hirst"
compilations[ sd.C_BE_1973 ] = "Birch and Eggers"
compilations[ sd.C_FF_1977 ] = "Fernholz and Finley"

for compilation_id in compilations:
    cursor.execute(
    """
    INSERT INTO compilations( compilation_id, compilation_name )
    VALUES( ?, ? );
    """,
    ( compilation_id, compilations[compilation_id], )
    )

# Compilation sources
cursor.execute(
"""
CREATE TABLE compilation_sources (
    compilation INTEGER NOT NULL CHECK ( compilation >= 0 ),
    source      TEXT NOT NULL,
    PRIMARY KEY(compilation, source),
    FOREIGN KEY(compilation) REFERENCES compilations(compilation_id)
);
"""
)

compilation_sources = {}
compilation_sources[ sd.C_CH_1969 ] = [ "ColesDE+1969+eng+BOOK" ]
compilation_sources[ sd.C_BE_1973 ] = [ "BirchSF+1973+eng+BOOK" ]
compilation_sources[ sd.C_FF_1977 ] = [ "FernholzFF+1977+eng+RPRT",
                                        "FernholzFF+1980+eng+RPRT",
                                        "FernholzFF+1981+eng+RPRT",
                                        "FernholzFF+1989+eng+RPRT" ]

for compilation_id in compilation_sources:
    for source in compilation_sources[compilation_id]:
        cursor.execute(
        """
        INSERT INTO compilation_sources( compilation, source )
        VALUES( ?, ? );
        """,
        ( compilation_id, source, )
        )

# Study identifiers
cursor.execute(
"""
CREATE TABLE study_identifiers (
    study       TEXT NOT NULL,
    compilation INTEGER NOT NULL CHECK ( compilation >= 0 ),
    identifier  TEXT NOT NULL,
    PRIMARY KEY(study, compilation),
    FOREIGN KEY(study)       REFERENCES      studies(identifier),
    FOREIGN KEY(compilation) REFERENCES compilations(compilation_id)
);
"""
)

# Series identifiers
cursor.execute(
"""
CREATE TABLE series_identifiers (
    series      TEXT NOT NULL,
    compilation INTEGER NOT NULL CHECK ( compilation >= 0 ),
    identifier  TEXT NOT NULL,
    PRIMARY KEY(series, compilation),
    FOREIGN KEY(series)      REFERENCES       series(identifier),
    FOREIGN KEY(compilation) REFERENCES compilations(compilation_id)
);
"""
)

# Station identifiers
cursor.execute(
"""
CREATE TABLE station_identifiers (
    station     TEXT NOT NULL,
    compilation INTEGER NOT NULL CHECK ( compilation >= 0 ),
    identifier  TEXT NOT NULL,
    PRIMARY KEY(station, compilation),
    FOREIGN KEY(station)     REFERENCES     stations(identifier),
    FOREIGN KEY(compilation) REFERENCES compilations(compilation_id)
);
"""
)

# Point identifiers
cursor.execute(
"""
CREATE TABLE point_identifiers (
    point       TEXT NOT NULL,
    compilation INTEGER NOT NULL CHECK ( compilation >= 0 ),
    identifier  TEXT NOT NULL,
    PRIMARY KEY(point, compilation),
    FOREIGN KEY(point)       REFERENCES       points(identifier),
    FOREIGN KEY(compilation) REFERENCES compilations(compilation_id)
);
"""
)

#CREATE VIEW confined_flow_classes   AS WITH RECURSIVE children(identifier) AS ( VALUES('C') UNION SELECT flow_classes.identifier FROM flow_classes, children WHERE flow_classes.parent=children.identifier ) SELECT identifier FROM children ORDER BY identifier;
#CREATE VIEW external_flow_classes   AS WITH RECURSIVE children(identifier) AS ( VALUES('E') UNION SELECT flow_classes.identifier FROM flow_classes, children WHERE flow_classes.parent=children.identifier ) SELECT identifier FROM children ORDER BY identifier;
#CREATE VIEW free_shear_flow_classes AS WITH RECURSIVE children(identifier) AS ( VALUES('F') UNION SELECT flow_classes.identifier FROM flow_classes, children WHERE flow_classes.parent=children.identifier ) SELECT identifier FROM children ORDER BY identifier;
#CREATE VIEW internal_flow_classes   AS WITH RECURSIVE children(identifier) AS ( VALUES('I') UNION SELECT flow_classes.identifier FROM flow_classes, children WHERE flow_classes.parent=children.identifier ) SELECT identifier FROM children ORDER BY identifier;
#CREATE VIEW shear_layer_classes     AS WITH RECURSIVE children(identifier) AS ( VALUES('S') UNION SELECT flow_classes.identifier FROM flow_classes, children WHERE flow_classes.parent=children.identifier ) SELECT identifier FROM children ORDER BY identifier;

#CREATE VIEW confined_flow_studies   AS SELECT studies.identifier FROM studies WHERE studies.flow_class IN ( SELECT identifier FROM confined_flow_classes   );
#CREATE VIEW external_flow_studies   AS SELECT studies.identifier FROM studies WHERE studies.flow_class IN ( SELECT identifier FROM external_flow_classes   );
#CREATE VIEW free_shear_flow_studies AS SELECT studies.identifier FROM studies WHERE studies.flow_class IN ( SELECT identifier FROM free_shear_flow_classes );
#CREATE VIEW internal_flow_studies   AS SELECT studies.identifier FROM studies WHERE studies.flow_class IN ( SELECT identifier FROM internal_flow_classes   );
#CREATE VIEW shear_layer_studies     AS SELECT studies.identifier FROM studies WHERE studies.flow_class IN ( SELECT identifier FROM shear_layer_classes     );

conn.commit()
conn.close()
