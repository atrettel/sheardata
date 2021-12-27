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
    value_type_id   TEXT PRIMARY KEY UNIQUE,
    value_type_name TEXT NOT NULL
);
"""
)

value_types = {}
value_types[ sd.VT_UNAVERAGED_VALUE         ] = "unaveraged value"
value_types[ sd.VT_UNWEIGHTED_AVERAGE       ] = "unweighted averaging"
value_types[ sd.VT_DENSITY_WEIGHTED_AVERAGE ] = "density-weighted averaging"

for value_type_id in value_types:
    cursor.execute(
    """
    INSERT INTO value_types( value_type_id, value_type_name )
    VALUES( ?, ? );
    """,
    ( value_type_id, value_types[value_type_id], )
    )

# Coordinate systems
cursor.execute(
"""
CREATE TABLE coordinate_systems (
    coordinate_system_id   TEXT PRIMARY KEY UNIQUE,
    coordinate_system_name TEXT NOT NULL
);
"""
)

coordinate_systems = {}
coordinate_systems[ sd.CS_RECTANGULAR ] = "rectangular coordinates"
coordinate_systems[ sd.CS_CYLINDRICAL ] = "cylindrical coordinates"

for coordinate_system_id in coordinate_systems:
    cursor.execute(
    """
    INSERT INTO coordinate_systems( coordinate_system_id,
                                    coordinate_system_name )
    VALUES( ?, ? );
    """,
    ( coordinate_system_id, coordinate_systems[coordinate_system_id], )
    )

# Flow classes
cursor.execute(
"""
CREATE TABLE flow_classes (
    flow_class_id        TEXT PRIMARY KEY UNIQUE CHECK ( length(flow_class_id) = 1 ),
    flow_class_name      TEXT NOT NULL,
    flow_class_parent_id TEXT DEFAULT NULL,
    FOREIGN KEY(flow_class_parent_id) REFERENCES flow_classes(flow_class_id)
);
"""
)

class FlowClass:
    name   = None
    parent = None

    def is_child( self ):
        return self.parent != None

    def __init__( self, name, parent ):
        self.name   = name
        self.parent = parent

flow_classes = {}
flow_classes[ sd.FC_BOUNDARY_LAYER       ] = FlowClass( "boundary layer",            sd.FC_EXTERNAL_FLOW )
flow_classes[ sd.FC_DUCT_FLOW            ] = FlowClass( "duct flow",                 sd.FC_INTERNAL_FLOW )
flow_classes[ sd.FC_EXTERNAL_FLOW        ] = FlowClass( "external flow",         sd.FC_WALL_BOUNDED_FLOW )
flow_classes[ sd.FC_FREE_JET             ] = FlowClass( "free jet",                sd.FC_FREE_SHEAR_FLOW )
flow_classes[ sd.FC_FREE_SHEAR_FLOW      ] = FlowClass( "free shear flow",              sd.FC_SHEAR_FLOW )
flow_classes[ sd.FC_HOMOGENEOUS_FLOW     ] = FlowClass( "homogeneous flow",      sd.FC_UNCLASSIFIED_FLOW )
flow_classes[ sd.FC_INHOMOGENEOUS_FLOW   ] = FlowClass( "inhomogeneous flow",    sd.FC_UNCLASSIFIED_FLOW )
flow_classes[ sd.FC_INTERNAL_FLOW        ] = FlowClass( "internal flow",         sd.FC_WALL_BOUNDED_FLOW )
flow_classes[ sd.FC_ISOTROPIC_FLOW       ] = FlowClass( "isotropic flow",         sd.FC_HOMOGENEOUS_FLOW )
flow_classes[ sd.FC_MIXING_LAYER         ] = FlowClass( "mixing layer",            sd.FC_FREE_SHEAR_FLOW )
flow_classes[ sd.FC_BOUNDARY_DRIVEN_FLOW ] = FlowClass( "boundary-driven flow",      sd.FC_INTERNAL_FLOW )
flow_classes[ sd.FC_SHEAR_FLOW           ] = FlowClass( "shear flow",           sd.FC_INHOMOGENEOUS_FLOW )
flow_classes[ sd.FC_UNCLASSIFIED_FLOW    ] = FlowClass( "flow",                                     None )
flow_classes[ sd.FC_WAKE                 ] = FlowClass( "wake",                    sd.FC_FREE_SHEAR_FLOW )
flow_classes[ sd.FC_WALL_BOUNDED_FLOW    ] = FlowClass( "wall-bounded flow",            sd.FC_SHEAR_FLOW )
flow_classes[ sd.FC_WALL_JET             ] = FlowClass( "wall jet",                  sd.FC_EXTERNAL_FLOW )

for flow_class_id in flow_classes:
    cursor.execute(
    """
    INSERT INTO flow_classes( flow_class_id, flow_class_name )
    VALUES( ?, ? );
    """,
    ( flow_class_id, flow_classes[flow_class_id].name, )
    )

# Two separate loops MUST occur due to foreign key constraints.
for flow_class_id in flow_classes:
    if ( flow_classes[flow_class_id].is_child() ):
        cursor.execute(
        """
        UPDATE flow_classes
        SET flow_class_parent_id=?
        WHERE flow_class_id=?;
        """,
        ( flow_classes[flow_class_id].parent, flow_class_id, )
        )

# Flow regimes
cursor.execute(
"""
CREATE TABLE flow_regimes (
    flow_regime_id   TEXT PRIMARY KEY UNIQUE,
    flow_regime_name TEXT NOT NULL
);
"""
)

flow_regimes = {}
flow_regimes[      sd.FR_LAMINAR ] =      "laminar flow"
flow_regimes[ sd.FR_TRANSITIONAL ] = "transitional flow"
flow_regimes[    sd.FR_TURBULENT ] =    "turbulent flow"

for flow_regime_id in flow_regimes:
    cursor.execute(
    """
    INSERT INTO flow_regimes( flow_regime_id, flow_regime_name )
    VALUES( ?, ? );
    """,
    ( flow_regime_id, flow_regimes[flow_regime_id], )
    )

# Phases
cursor.execute(
"""
CREATE TABLE phases (
    phase_id   TEXT PRIMARY KEY UNIQUE,
    phase_name TEXT NOT NULL
);
"""
)

phases = {}
phases[ sd.PH_GAS    ] =    "gas"
phases[ sd.PH_LIQUID ] = "liquid"
phases[ sd.PH_SOLID  ] =  "solid"

for phase_id in phases:
    cursor.execute(
    """
    INSERT INTO phases( phase_id, phase_name )
    VALUES( ?, ? );
    """,
    ( phase_id, phases[phase_id], )
    )

# Elements
cursor.execute(
"""
CREATE TABLE elements (
    atomic_number  INTEGER PRIMARY KEY UNIQUE,
    element_symbol TEXT UNIQUE NOT NULL,
    element_name   TEXT UNIQUE NOT NULL,
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
    fluid_id   TEXT PRIMARY KEY UNIQUE,
    fluid_name TEXT NOT NULL,
    phase_id   TEXT NOT NULL,
    FOREIGN KEY(phase_id) REFERENCES phases(phase_id)
);
"""
)

# Geometries
#
# TODO: consider creating a hierarchy of geometries organized by the number of
# sides an object has.  For example, rectangles are a particular form of
# quadrilaterals, and circles are a particular form of ellipses, etc.  The
# point of this is to be able to select different duct flow cross sections or
# airfoil sections in a useful manner.  I still need to think about this more.
cursor.execute(
"""
CREATE TABLE geometries (
    geometry_id   TEXT PRIMARY KEY UNIQUE,
    geometry_name TEXT NOT NULL
);
"""
)

geometries = {}
geometries[ sd.GM_ELLIPTICAL  ] =  "elliptical geometry"
geometries[ sd.GM_RECTANGULAR ] = "rectangular geometry"

for geometry_id in geometries:
    cursor.execute(
    """
    INSERT INTO geometries( geometry_id, geometry_name )
    VALUES( ?, ? );
    """,
    ( geometry_id, geometries[geometry_id], )
    )

# Measurement techniques
cursor.execute(
"""
CREATE TABLE measurement_techniques (
    meastech_id        TEXT PRIMARY KEY UNIQUE,
    meastech_name      TEXT NOT NULL,
    intrusive          INTEGER NOT NULL DEFAULT 0 CHECK ( intrusive = 0 OR intrusive = 1 ),
    meastech_parent_id TEXT DEFAULT NULL,
    FOREIGN KEY(meastech_parent_id) REFERENCES measurement_techniques(meastech_id)
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

for meastech_id in measurement_techniques:
    cursor.execute(
    """
    INSERT INTO measurement_techniques( meastech_id, meastech_name, intrusive )
    VALUES( ?, ?, ? );
    """,
    (
        meastech_id,
        measurement_techniques[meastech_id].name,
        measurement_techniques[meastech_id].intrusive,
    )
    )

# Two separate loops MUST occur due to foreign key constraints.
for meastech_id in measurement_techniques:
    if ( measurement_techniques[meastech_id].is_child() ):
        cursor.execute(
        """
        UPDATE measurement_techniques
        SET meastech_parent_id=?
        WHERE meastech_id=?;
        """,
        ( measurement_techniques[meastech_id].parent, meastech_id, )
        )

# Notes
cursor.execute(
"""
CREATE TABLE notes (
    note_id       INTEGER PRIMARY KEY CHECK ( note_id > 0 ),
    note_contents TEXT NOT NULL
);
"""
)

# Point labels
cursor.execute(
"""
CREATE TABLE point_labels (
    point_label_id   TEXT PRIMARY KEY UNIQUE,
    point_label_name TEXT NOT NULL
);
"""
)

point_labels = {}
point_labels[ sd.PL_CENTER_LINE ] = "center-line"
point_labels[ sd.PL_EDGE        ] = "edge"
point_labels[ sd.PL_WALL        ] = "wall"

for point_label_id in point_labels:
    cursor.execute(
    """
    INSERT INTO point_labels( point_label_id, point_label_name )
    VALUES( ?, ? );
    """,
    ( point_label_id, point_labels[point_label_id], )
    )

# Quantities
#
# I have implemented all quantities in the same table, though I divide them up
# into categories based on whether they apply to a study, series, station, or
# point.  Separate tables may be a better design choice in the long run because
# it enforces the division, but for the moment I am leaving it with only one
# table for simplicity.
#
# The advantage of a single table is that it grants the ability to apply some
# quantities to both a point and a station, for example.  Coordinates are
# nominally point quantities, but it may also be a good idea to specify the x
# and z coordinates at the station level too if those coordinates are in fact
# constant for an entire station (they most likely will be).  That would allow
# for `SELECT` statements at the station level while also retaining the
# relevant data at another level.  The problem is that this duplication
# violates the idea that data should only be in one particular place in the
# database, and for that reason I have only implemented coordinates as point
# quantities so far.
cursor.execute(
"""
CREATE TABLE quantities (
    quantity_id               TEXT PRIMARY KEY UNIQUE,
    quantity_name             TEXT NOT NULL UNIQUE,
    time_exponent             REAL NOT NULL DEFAULT 0.0,
    length_exponent           REAL NOT NULL DEFAULT 0.0,
    mass_exponent             REAL NOT NULL DEFAULT 0.0,
    current_exponent          REAL NOT NULL DEFAULT 0.0,
    temperature_exponent      REAL NOT NULL DEFAULT 0.0,
    amount_exponent           REAL NOT NULL DEFAULT 0.0
);
"""
)

class Quantity:
    name                 = None
    time_exponent        = None
    length_exponent      = None
    mass_exponent        = None
    current_exponent     = None
    temperature_exponent = None
    amount_exponent      = None

    def __init__( self, name,
                  time_exponent=0.0,
                  length_exponent=0.0,
                  mass_exponent=0.0,
                  current_exponent=0.0,
                  temperature_exponent=0.0,
                  amount_exponent=0.0, ):
        self.name                 = str(name)
        self.time_exponent        = time_exponent
        self.length_exponent      = length_exponent
        self.mass_exponent        = mass_exponent
        self.current_exponent     = current_exponent
        self.temperature_exponent = temperature_exponent
        self.amount_exponent      = amount_exponent

quantities = {}

# Quantities for series
quantities[ sd.Q_ANGLE_OF_ATTACK                ] = Quantity( "angle of attack",                                                                                                              )
quantities[ sd.Q_BODY_HEIGHT                    ] = Quantity( "body height",                                             length_exponent=+1.0,                                                )
quantities[ sd.Q_BODY_LENGTH                    ] = Quantity( "body length",                                             length_exponent=+1.0,                                                )
quantities[ sd.Q_BODY_REYNOLDS_NUMBER           ] = Quantity( "body Reynolds number",                                                                                                         )
quantities[ sd.Q_BODY_STROUHAL_NUMBER           ] = Quantity( "body Strouhal number",                                                                                                         )
quantities[ sd.Q_BODY_WIDTH                     ] = Quantity( "body width",                                              length_exponent=+1.0,                                                )
quantities[ sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS ] = Quantity( "distance between pressure taps",                          length_exponent=+1.0,                                                )
quantities[ sd.Q_DRAG_COEFFICIENT               ] = Quantity( "drag coefficient",                                                                                                             )
quantities[ sd.Q_DRAG_FORCE                     ] = Quantity( "drag force",                          time_exponent=-2.0, length_exponent=+1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_FREESTREAM_MACH_NUMBER         ] = Quantity( "freestream Mach number",                                                                                                       )
quantities[ sd.Q_FREESTREAM_SPEED_OF_SOUND      ] = Quantity( "freestream speed of sound",           time_exponent=-1.0, length_exponent=+1.0,                                                )
quantities[ sd.Q_FREESTREAM_TEMPERATURE         ] = Quantity( "freestream temperature",                                                                            temperature_exponent=+1.0, )
quantities[ sd.Q_FREESTREAM_VELOCITY            ] = Quantity( "freestream velocity",                 time_exponent=-1.0, length_exponent=+1.0,                                                )
quantities[ sd.Q_LEADING_EDGE_LENGTH            ] = Quantity( "leading edge length",                                     length_exponent=+1.0,                                                )
quantities[ sd.Q_LEADING_EDGE_RADIUS            ] = Quantity( "leading edge radius",                                     length_exponent=+1.0,                                                )
quantities[ sd.Q_LIFT_COEFFICIENT               ] = Quantity( "lift coefficient",                                                                                                             )
quantities[ sd.Q_LIFT_FORCE                     ] = Quantity( "lift force",                          time_exponent=-2.0, length_exponent=+1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_LIFT_TO_DRAG_RATIO             ] = Quantity( "lift-to-drag ratio",                                                                                                           )
quantities[ sd.Q_MASS_FLOW_RATE                 ] = Quantity( "mass flow rate",                      time_exponent=-1.0,                       mass_exponent=+1.0,                            )
quantities[ sd.Q_SPANWISE_NUMBER_OF_POINTS      ] = Quantity( "spanwise number of points",                                                                                                    )
quantities[ sd.Q_STREAMWISE_NUMBER_OF_POINTS    ] = Quantity( "streamwise number of points",                                                                                                  )
quantities[ sd.Q_TEST_LENGTH                    ] = Quantity( "test length",                                             length_exponent=+1.0,                                                )
quantities[ sd.Q_TRANSVERSE_NUMBER_OF_POINTS    ] = Quantity( "transverse number of points",                                                                                                  )
quantities[ sd.Q_VOLUMETRIC_FLOW_RATE           ] = Quantity( "volumetric flow rate",                time_exponent=-1.0, length_exponent=+3.0,                                                )

# Quantities, station
quantities[ sd.Q_BULK_DYNAMIC_VISCOSITY                 ] = Quantity( "bulk dynamic viscosity",                 time_exponent=-1.0, length_exponent=-1.0, mass_exponent=+1.0, )
quantities[ sd.Q_BULK_KINEMATIC_VISCOSITY               ] = Quantity( "bulk kinematic viscosity",               time_exponent=-1.0, length_exponent=+2.0,                     )
quantities[ sd.Q_BULK_MACH_NUMBER                       ] = Quantity( "bulk Mach number",                                                                                     )
quantities[ sd.Q_BULK_MASS_DENSITY                      ] = Quantity( "bulk mass density",                                          length_exponent=-3.0, mass_exponent=+1.0, )
quantities[ sd.Q_BULK_REYNOLDS_NUMBER                   ] = Quantity( "bulk Reynolds number",                                                                                 )
quantities[ sd.Q_BULK_SPEED_OF_SOUND                    ] = Quantity( "bulk speed of sound",                    time_exponent=-1.0, length_exponent=+1.0,                     )
quantities[ sd.Q_BULK_VELOCITY                          ] = Quantity( "bulk velocity",                          time_exponent=-1.0, length_exponent=+1.0,                     )
quantities[ sd.Q_CLAUSER_THICKNESS                      ] = Quantity( "Clauser thickness",                                          length_exponent=+1.0,                     )
quantities[ sd.Q_CROSS_SECTIONAL_AREA                   ] = Quantity( "cross-sectional area",                                       length_exponent=+2.0,                     )
quantities[ sd.Q_CROSS_SECTIONAL_ASPECT_RATIO           ] = Quantity( "cross-sectional aspect ratio",                                                                         )
quantities[ sd.Q_CROSS_SECTIONAL_HALF_HEIGHT            ] = Quantity( "cross-sectional half height",                                length_exponent=+1.0,                     )
quantities[ sd.Q_CROSS_SECTIONAL_HEIGHT                 ] = Quantity( "cross-sectional height",                                     length_exponent=+1.0,                     )
quantities[ sd.Q_CROSS_SECTIONAL_WIDTH                  ] = Quantity( "cross-sectional width",                                      length_exponent=+1.0,                     )
quantities[ sd.Q_DEVELOPMENT_LENGTH                     ] = Quantity( "development length",                                         length_exponent=+1.0,                     )
quantities[ sd.Q_DISPLACEMENT_THICKNESS                 ] = Quantity( "displacement thickness",                                     length_exponent=+1.0,                     )
quantities[ sd.Q_DISPLACEMENT_THICKNESS_REYNOLDS_NUMBER ] = Quantity( "displacement thickness Reynolds number",                                                               )
quantities[ sd.Q_ENERGY_THICKNESS                       ] = Quantity( "energy thickness",                                           length_exponent=+1.0,                     )
quantities[ sd.Q_EQUILIBRIUM_PARAMETER                  ] = Quantity( "equilibrium parameter",                                                                                )
quantities[ sd.Q_HYDRAULIC_DIAMETER                     ] = Quantity( "hydraulic diameter",                                         length_exponent=+1.0,                     )
quantities[ sd.Q_INNER_DIAMETER                         ] = Quantity( "inner diameter",                                             length_exponent=+1.0,                     )
quantities[ sd.Q_MOMENTUM_INTEGRAL_LHS                  ] = Quantity( "momentum integral left-hand side",                                                                     )
quantities[ sd.Q_MOMENTUM_INTEGRAL_RHS                  ] = Quantity( "momentum integral right-hand side",                                                                    )
quantities[ sd.Q_MOMENTUM_THICKNESS                     ] = Quantity( "momentum thickness",                                         length_exponent=+1.0,                     )
quantities[ sd.Q_MOMENTUM_THICKNESS_REYNOLDS_NUMBER     ] = Quantity( "momentum thickness Reynolds number",                                                                   )
quantities[ sd.Q_OUTER_DIAMETER                         ] = Quantity( "outer diameter",                                             length_exponent=+1.0,                     )
quantities[ sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH         ] = Quantity( "outer-layer development length",                                                                       )
quantities[ sd.Q_RECOVERY_FACTOR                        ] = Quantity( "recovery factor",                                                                                      )
quantities[ sd.Q_SHAPE_FACTOR_1_TO_2                    ] = Quantity( "shape factor 1-to-2",                                                                                  )
quantities[ sd.Q_SHAPE_FACTOR_3_TO_2                    ] = Quantity( "shape factor 3-to-2",                                                                                  )
quantities[ sd.Q_SPANWISE_PRESSURE_GRADIENT             ] = Quantity( "spanwise pressure gradient",             time_exponent=-2.0, length_exponent=-2.0, mass_exponent=+1.0, )
quantities[ sd.Q_STREAMWISE_COORDINATE_REYNOLDS_NUMBER  ] = Quantity( "streamwise coordinate Reynolds number",                                                                )
quantities[ sd.Q_STREAMWISE_PRESSURE_GRADIENT           ] = Quantity( "streamwise pressure gradient",           time_exponent=-2.0, length_exponent=-2.0, mass_exponent=+1.0, )
quantities[ sd.Q_TRANSVERSE_PRESSURE_GRADIENT           ] = Quantity( "transverse pressure gradient",           time_exponent=-2.0, length_exponent=-2.0, mass_exponent=+1.0, )
quantities[ sd.Q_WETTED_PERIMETER                       ] = Quantity( "wetted perimeter",                                           length_exponent=+2.0,                     )

# Quantities, wall point
quantities[ sd.Q_AVERAGE_SKIN_FRICTION_COEFFICIENT     ] = Quantity( "average skin friction coefficient",                                                                        )
quantities[ sd.Q_DARCY_FRICTION_FACTOR                 ] = Quantity( "Darcy friction factor",                                                                                    )
quantities[ sd.Q_FANNING_FRICTION_FACTOR               ] = Quantity( "Fanning friction factor",                                                                                  )
quantities[ sd.Q_FRICTION_MACH_NUMBER                  ] = Quantity( "friction Mach number",                                                                                     )
quantities[ sd.Q_FRICTION_REYNOLDS_NUMBER              ] = Quantity( "friction Reynolds number",                                                                                 )
quantities[ sd.Q_FRICTION_TEMPERATURE                  ] = Quantity( "friction temperature",                                                          temperature_exponent=+1.0, )
quantities[ sd.Q_FRICTION_VELOCITY                     ] = Quantity( "friction velocity",                   time_exponent=-1.0, length_exponent=+1.0,                            )
quantities[ sd.Q_HEAT_TRANSFER_COEFFICIENT             ] = Quantity( "heat transfer coefficient",                                                                                )
quantities[ sd.Q_INNER_LAYER_HEAT_FLUX                 ] = Quantity( "inner-layer heat flux",                                                                                    )
quantities[ sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT          ] = Quantity( "inner-layer roughness height",                                                                             )
quantities[ sd.Q_LOCAL_SKIN_FRICTION_COEFFICIENT       ] = Quantity( "local skin friction coefficient",                                                                          )
quantities[ sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT          ] = Quantity( "outer-layer roughness height",                                                                             )
quantities[ sd.Q_PRESSURE_COEFFICIENT                  ] = Quantity( "pressure coefficient",                                                                                     )
quantities[ sd.Q_ROUGHNESS_HEIGHT                      ] = Quantity( "roughness height",                                        length_exponent=+1.0,                            )
quantities[ sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER   ] = Quantity( "semi-local friction Reynolds number",                                                                      )
quantities[ sd.Q_SPANWISE_WALL_CURVATURE               ] = Quantity( "spanwise wall curvature",                                 length_exponent=-1.0,                            )
quantities[ sd.Q_STREAMWISE_WALL_CURVATURE             ] = Quantity( "streamwise wall curvature",                               length_exponent=-1.0,                            )
quantities[ sd.Q_VISCOUS_LENGTH_SCALE                  ] = Quantity( "viscous length scale",                                    length_exponent=+1.0                             )

# Quantities, point
quantities[ sd.Q_DILATATION_RATE                                    ] = Quantity( "dilatation rate",                                      time_exponent=-1.0,                                                                      )
quantities[ sd.Q_DISTANCE_FROM_WALL                                 ] = Quantity( "distance from wall",                                                       length_exponent=+1.0,                                                )
quantities[ sd.Q_DYNAMIC_VISCOSITY                                  ] = Quantity( "dynamic viscosity",                                    time_exponent=-1.0, length_exponent=-1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_HEAT_CAPACITY_RATIO                                ] = Quantity( "gamma",                                                                                                                                         )
quantities[ sd.Q_HEAT_FLUX                                          ] = Quantity( "heat flux",                                            time_exponent=-3.0,                       mass_exponent=+1.0,                            )
quantities[ sd.Q_INNER_LAYER_COORDINATE                             ] = Quantity( "inner-layer coordinate",                                                                                                                        )
quantities[ sd.Q_INNER_LAYER_TEMPERATURE                            ] = Quantity( "inner-layer temperature",                                                                                                                       )
quantities[ sd.Q_INNER_LAYER_VELOCITY                               ] = Quantity( "inner-layer velocity",                                                                                                                          )
quantities[ sd.Q_INNER_LAYER_VELOCITY_DEFECT                        ] = Quantity( "inner-layer velocity defect",                                                                                                                   )
quantities[ sd.Q_KINEMATIC_VISCOSITY                                ] = Quantity( "kinematic viscosity",                                  time_exponent=-1.0, length_exponent=+2.0,                                                )
quantities[ sd.Q_MACH_NUMBER                                        ] = Quantity( "Mach number",                                                                                                                                   )
quantities[ sd.Q_MASS_DENSITY                                       ] = Quantity( "mass density",                                                             length_exponent=-3.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_OUTER_LAYER_COORDINATE                             ] = Quantity( "outer-layer coordinate",                                                                                                                        )
quantities[ sd.Q_OUTER_LAYER_TEMPERATURE                            ] = Quantity( "outer-layer temperature",                                                                                                                       )
quantities[ sd.Q_OUTER_LAYER_VELOCITY                               ] = Quantity( "outer-layer velocity",                                                                                                                          )
quantities[ sd.Q_OUTER_LAYER_VELOCITY_DEFECT                        ] = Quantity( "outer-layer velocity defect",                                                                                                                   )
quantities[ sd.Q_PRANDTL_NUMBER                                     ] = Quantity( "Prandtl number",                                                                                                                                )
quantities[ sd.Q_PRESSURE                                           ] = Quantity( "pressure",                                             time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_SEMI_LOCAL_COORDINATE                              ] = Quantity( "semi-local inner-layer coordinate",                                                                                                             )
quantities[ sd.Q_SPANWISE_COORDINATE                                ] = Quantity( "spanwise coordinate",                                                      length_exponent=+1.0,                                                )
quantities[ sd.Q_SPANWISE_VELOCITY                                  ] = Quantity( "spanwise velocity",                                    time_exponent=-1.0, length_exponent=+1.0,                                                )
quantities[ sd.Q_SPECIFIC_ENTHALPY                                  ] = Quantity( "specific enthalpy",                                    time_exponent=-2.0, length_exponent=+2.0,                                                )
quantities[ sd.Q_SPECIFIC_GAS_CONSTANT                              ] = Quantity( "specific gas constant",                                time_exponent=-2.0, length_exponent=+2.0,                     temperature_exponent=-1.0, )
quantities[ sd.Q_SPECIFIC_INTERNAL_ENERGY                           ] = Quantity( "specific internal energy",                             time_exponent=-2.0, length_exponent=+2.0,                                                )
quantities[ sd.Q_SPECIFIC_ISOBARIC_HEAT_CAPACITY                    ] = Quantity( "specific isobaric heat capacity",                      time_exponent=-2.0, length_exponent=+2.0,                     temperature_exponent=-1.0, )
quantities[ sd.Q_SPECIFIC_ISOCHORIC_HEAT_CAPACITY                   ] = Quantity( "specific isochoric heat capacity",                     time_exponent=-2.0, length_exponent=+2.0,                     temperature_exponent=-1.0, )
quantities[ sd.Q_SPECIFIC_TOTAL_ENTHALPY                            ] = Quantity( "specific total enthalpy",                              time_exponent=-2.0, length_exponent=+2.0,                                                )
quantities[ sd.Q_SPECIFIC_TOTAL_INTERNAL_ENERGY                     ] = Quantity( "specific total internal energy",                       time_exponent=-2.0, length_exponent=+2.0,                                                )
quantities[ sd.Q_SPECIFIC_VOLUME                                    ] = Quantity( "specific volume",                                                          length_exponent=+3.0, mass_exponent=-1.0,                            )
quantities[ sd.Q_SPEED                                              ] = Quantity( "speed",                                                time_exponent=-1.0, length_exponent=+1.0,                                                )
quantities[ sd.Q_SPEED_OF_SOUND                                     ] = Quantity( "speed of sound",                                       time_exponent=-1.0, length_exponent=+1.0,                                                )
quantities[ sd.Q_STREAMWISE_COORDINATE                              ] = Quantity( "streamwise coordinate",                                                    length_exponent=+1.0,                                                )
quantities[ sd.Q_STREAMWISE_VELOCITY                                ] = Quantity( "streamwise velocity",                                  time_exponent=-1.0, length_exponent=+1.0,                                                )
quantities[ sd.Q_STRESS[sd.D_STREAMWISE,sd.D_STREAMWISE]            ] = Quantity(           "streamwise normal stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_STRESS[sd.D_STREAMWISE,sd.D_TRANSVERSE]            ] = Quantity( "streamwise-transverse shear stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_STRESS[sd.D_STREAMWISE,sd.D_SPANWISE  ]            ] = Quantity(   "streamwise-spanwise shear stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_STRESS[sd.D_TRANSVERSE,sd.D_TRANSVERSE]            ] = Quantity(           "transverse normal stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_STRESS[sd.D_TRANSVERSE,sd.D_SPANWISE  ]            ] = Quantity(   "transverse-spanwise shear stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_STRESS[sd.D_SPANWISE,  sd.D_SPANWISE  ]            ] = Quantity(             "spanwise normal stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_TEMPERATURE                                        ] = Quantity( "temperature",                                                                                                        temperature_exponent=+1.0, )
quantities[ sd.Q_THERMAL_CONDUCTIVITY                               ] = Quantity( "thermal conductivity",                                 time_exponent=-3.0, length_exponent=+1.0, mass_exponent=+1.0, temperature_exponent=-1.0, )
quantities[ sd.Q_THERMAL_DIFFUSIVITY                                ] = Quantity( "thermal diffusivity",                                  time_exponent=-1.0, length_exponent=+2.0,                                                )
quantities[ sd.Q_TOTAL_PRESSURE                                     ] = Quantity( "total pressure",                                       time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                            )
quantities[ sd.Q_TOTAL_TEMPERATURE                                  ] = Quantity( "total temperature",                                                                                                  temperature_exponent=+1.0, )
quantities[ sd.Q_TRANSVERSE_COORDINATE                              ] = Quantity( "transverse coordinate",                                                    length_exponent=+1.0,                                                )
quantities[ sd.Q_TRANSVERSE_VELOCITY                                ] = Quantity( "transverse velocity",                                  time_exponent=-1.0, length_exponent=+1.0,                                                )
quantities[ sd.Q_VELOCITY_DEFECT                                    ] = Quantity( "velocity defect",                                      time_exponent=-1.0, length_exponent=+1.0,                                                )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_STREAMWISE] ] = Quantity( "streamwise velocity gradient in streamwise direction", time_exponent=-1.0,                                                                      )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_TRANSVERSE] ] = Quantity( "streamwise velocity gradient in transverse direction", time_exponent=-1.0,                                                                      )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_SPANWISE  ] ] = Quantity( "streamwise velocity gradient in spanwise direction",   time_exponent=-1.0,                                                                      )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_STREAMWISE] ] = Quantity( "transverse velocity gradient in streamwise direction", time_exponent=-1.0,                                                                      )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_TRANSVERSE] ] = Quantity( "transverse velocity gradient in transverse direction", time_exponent=-1.0,                                                                      )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_SPANWISE  ] ] = Quantity( "transverse velocity gradient in spanwise direction",   time_exponent=-1.0,                                                                      )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_STREAMWISE] ] = Quantity(   "spanwise velocity gradient in streamwise direction", time_exponent=-1.0,                                                                      )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_TRANSVERSE] ] = Quantity(   "spanwise velocity gradient in transverse direction", time_exponent=-1.0,                                                                      )
quantities[ sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_SPANWISE  ] ] = Quantity(   "spanwise velocity gradient in spanwise direction",   time_exponent=-1.0,                                                                      )

# Quantities, point, turbulence
quantities[ sd.Q_MASS_DENSITY_AUTOCOVARIANCE                        ] = Quantity( "mass density autocovariance",                                  length_exponent=-6.0, mass_exponent=+2.0,                            )
quantities[ sd.Q_NORMALIZED_MASS_DENSITY_AUTOCOVARIANCE             ] = Quantity( "normalized mass density autocovariance",                                                                                            )
quantities[ sd.Q_NORMALIZED_PRESSURE_AUTOCOVARIANCE                 ] = Quantity( "normalized pressure autocovariance",                                                                                                )
quantities[ sd.Q_NORMALIZED_TEMPERATURE_AUTOCOVARIANCE              ] = Quantity( "normalized temperature autocovariance",                                                                                             )
quantities[ sd.Q_PRESSURE_AUTOCOVARIANCE                            ] = Quantity( "pressure autocovariance",                  time_exponent=-4.0, length_exponent=-2.0, mass_exponent=+2.0,                            )
quantities[ sd.Q_INNER_LAYER_SPECIFIC_TURBULENT_KINETIC_ENERGY      ] = Quantity( "inner-layer turbulent kinetic energy",                                                                                              )
quantities[ sd.Q_MORKOVIN_SCALED_SPECIFIC_TURBULENT_KINETIC_ENERGY  ] = Quantity( "Morkovin-scaled turbulent kinetic energy",                                                                                          )
quantities[ sd.Q_SPECIFIC_TURBULENT_KINETIC_ENERGY                  ] = Quantity( "specific turbulent kinetic energy",        time_exponent=-2.0, length_exponent=+2.0,                                                )
quantities[ sd.Q_TEMPERATURE_AUTOCOVARIANCE                         ] = Quantity( "temperature autocovariance",                                                                             temperature_exponent=+2.0, )

quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE] ] = Quantity(              "streamwise velocity autocovariance", time_exponent=-2.0, length_exponent=+2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE] ] = Quantity( "streamwise-transverse velocity cross covariance", time_exponent=-2.0, length_exponent=+2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ] ] = Quantity(   "streamwise-spanwise velocity cross covariance", time_exponent=-2.0, length_exponent=+2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE] ] = Quantity(              "transverse velocity autocovariance", time_exponent=-2.0, length_exponent=+2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ] ] = Quantity(   "transverse-spanwise velocity cross covariance", time_exponent=-2.0, length_exponent=+2.0, )
quantities[ sd.Q_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ] ] = Quantity(                "spanwise velocity autocovariance", time_exponent=-2.0, length_exponent=+2.0, )

quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE] ] = Quantity(              "inner-layer streamwise velocity autocovariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE] ] = Quantity( "inner-layer streamwise-transverse velocity cross covariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ] ] = Quantity(   "inner-layer streamwise-spanwise velocity cross covariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE] ] = Quantity(              "inner-layer transverse velocity autocovariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ] ] = Quantity(   "inner-layer transverse-spanwise velocity cross covariance", )
quantities[ sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ] ] = Quantity(                "inner-layer spanwise velocity autocovariance", )

quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE] ] = Quantity(              "Morkovin-scaled streamwise velocity autocovariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE] ] = Quantity( "Morkovin-scaled streamwise-transverse velocity cross covariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ] ] = Quantity(   "Morkovin-scaled streamwise-spanwise velocity cross covariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE] ] = Quantity(              "Morkovin-scaled transverse velocity autocovariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ] ] = Quantity(   "Morkovin-scaled transverse-spanwise velocity cross covariance", )
quantities[ sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ] ] = Quantity(                "Morkovin-scaled spanwise velocity autocovariance", )

# Quantities, point, ratios
quantities[ sd.Q_LOCAL_TO_BULK_STREAMWISE_VELOCITY_RATIO        ] = Quantity( "local-to-bulk streamwise velocity ratio",        )
quantities[ sd.Q_LOCAL_TO_BULK_TEMPERATURE_RATIO                ] = Quantity( "local-to-bulk temperature ratio",                )
quantities[ sd.Q_LOCAL_TO_CENTER_LINE_DYNAMIC_VISCOSITY_RATIO   ] = Quantity( "local-to-center-line dynamic viscosity ratio",   )
quantities[ sd.Q_LOCAL_TO_CENTER_LINE_MASS_DENSITY_RATIO        ] = Quantity( "local-to-center-line density ratio",             )
quantities[ sd.Q_LOCAL_TO_CENTER_LINE_STREAMWISE_VELOCITY_RATIO ] = Quantity( "local-to-center-line streamwise velocity ratio", )
quantities[ sd.Q_LOCAL_TO_CENTER_LINE_TEMPERATURE_RATIO         ] = Quantity( "local-to-center-line temperature ratio",         )
quantities[ sd.Q_LOCAL_TO_EDGE_DYNAMIC_VISCOSITY_RATIO          ] = Quantity( "local-to-edge dynamic viscosity ratio",          )
quantities[ sd.Q_LOCAL_TO_EDGE_MASS_DENSITY_RATIO               ] = Quantity( "local-to-edge density ratio",                    )
quantities[ sd.Q_LOCAL_TO_EDGE_STREAMWISE_VELOCITY_RATIO        ] = Quantity( "local-to-edge streamwise velocity ratio",        )
quantities[ sd.Q_LOCAL_TO_EDGE_TEMPERATURE_RATIO                ] = Quantity( "local-to-edge temperature ratio",                )
quantities[ sd.Q_LOCAL_TO_RECOVERY_TEMPERATURE_RATIO            ] = Quantity( "local-to-recovery temperature ratio",            )
quantities[ sd.Q_LOCAL_TO_WALL_DYNAMIC_VISCOSITY_RATIO          ] = Quantity( "local-to-wall dynamic viscosity ratio",          )
quantities[ sd.Q_LOCAL_TO_WALL_MASS_DENSITY_RATIO               ] = Quantity( "local-to-wall density ratio",                    )
quantities[ sd.Q_LOCAL_TO_WALL_STREAMWISE_VELOCITY_RATIO        ] = Quantity( "local-to-wall streamwise velocity ratio",        )
quantities[ sd.Q_LOCAL_TO_WALL_TEMPERATURE_RATIO                ] = Quantity( "local-to-wall temperature ratio",                )

for quantity_id in quantities:
    cursor.execute(
    """
    INSERT INTO quantities( quantity_id, quantity_name,
                            time_exponent, length_exponent, mass_exponent,
                            current_exponent, temperature_exponent,
                            amount_exponent )
    VALUES( ?, ?, ?, ?, ?, ?, ?, ? );
    """,
    (
        quantity_id,
        quantities[quantity_id].name,
        quantities[quantity_id].time_exponent,
        quantities[quantity_id].length_exponent,
        quantities[quantity_id].mass_exponent,
        quantities[quantity_id].current_exponent,
        quantities[quantity_id].temperature_exponent,
        quantities[quantity_id].amount_exponent,
    )
    )


# Latex codes for quantities
cursor.execute(
"""
CREATE TABLE quantity_latex_codes (
    quantity_id               TEXT NOT NULL,
    value_type_id             TEXT NOT NULL,
    quantity_latex_symbol     TEXT NOT NULL,
    quantity_latex_definition TEXT DEFAULT NULL,
    notes                     TEXT DEFAULT NULL,
    PRIMARY KEY(quantity_id, value_type_id),
    FOREIGN KEY(quantity_id) REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id)
);
"""
)

def define_quantity_symbol( quantity_id, value_type_id, quantity_latex_symbol,
                            quantity_latex_definition=None, notes=None ):
    cursor.execute(
    """
    INSERT INTO quantity_latex_codes( quantity_id, value_type_id,
                                      quantity_latex_symbol,
                                      quantity_latex_definition, notes )
    VALUES( ?, ?, ?, ?, ? );
    """,
    (
        quantity_id,
        value_type_id,
        quantity_latex_symbol,
        quantity_latex_definition,
        notes,
    )
    )

# Quantities for series
define_quantity_symbol( sd.Q_ANGLE_OF_ATTACK,                sd.VT_UNAVERAGED_VALUE, r"\alpha",                                            )
define_quantity_symbol( sd.Q_BODY_HEIGHT,                    sd.VT_UNAVERAGED_VALUE, r"h_b",                                               )
define_quantity_symbol( sd.Q_BODY_LENGTH,                    sd.VT_UNAVERAGED_VALUE, r"\ell_b",                                            )
define_quantity_symbol( sd.Q_BODY_REYNOLDS_NUMBER,           sd.VT_UNAVERAGED_VALUE, r"\mathrm{Re}_b",                                     )
define_quantity_symbol( sd.Q_BODY_STROUHAL_NUMBER,           sd.VT_UNAVERAGED_VALUE, r"\mathrm{Sr}_b",                                     )
define_quantity_symbol( sd.Q_BODY_WIDTH,                     sd.VT_UNAVERAGED_VALUE, r"w_b",                                               )
define_quantity_symbol( sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS, sd.VT_UNAVERAGED_VALUE, r"\ell_p",                                            )
define_quantity_symbol( sd.Q_DRAG_COEFFICIENT,               sd.VT_UNAVERAGED_VALUE, r"C_D",                                               )
define_quantity_symbol( sd.Q_DRAG_FORCE,                     sd.VT_UNAVERAGED_VALUE, r"F_D",                                               )
define_quantity_symbol( sd.Q_FREESTREAM_MACH_NUMBER,         sd.VT_UNAVERAGED_VALUE, r"\mathrm{Ma}_\infty",                                )
define_quantity_symbol( sd.Q_FREESTREAM_SPEED_OF_SOUND,      sd.VT_UNAVERAGED_VALUE, r"a_\infty",                                          )
define_quantity_symbol( sd.Q_FREESTREAM_TEMPERATURE,         sd.VT_UNAVERAGED_VALUE, r"T_\infty",                                          )
define_quantity_symbol( sd.Q_FREESTREAM_VELOCITY,            sd.VT_UNAVERAGED_VALUE, r"{:s}_\infty".format(sd.STREAMWISE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_LEADING_EDGE_LENGTH,            sd.VT_UNAVERAGED_VALUE, r"\ell_\mathrm{le}",                                  )
define_quantity_symbol( sd.Q_LEADING_EDGE_RADIUS,            sd.VT_UNAVERAGED_VALUE, r"r_\mathrm{le}",                                     )
define_quantity_symbol( sd.Q_LIFT_COEFFICIENT,               sd.VT_UNAVERAGED_VALUE, r"C_L",                                               )
define_quantity_symbol( sd.Q_LIFT_FORCE,                     sd.VT_UNAVERAGED_VALUE, r"F_L",                                               )
define_quantity_symbol( sd.Q_LIFT_TO_DRAG_RATIO,             sd.VT_UNAVERAGED_VALUE, r"(L/D)",                                             )
define_quantity_symbol( sd.Q_MASS_FLOW_RATE,                 sd.VT_UNAVERAGED_VALUE, r"\dot{m}",                                           )
define_quantity_symbol( sd.Q_SPANWISE_NUMBER_OF_POINTS,      sd.VT_UNAVERAGED_VALUE, r"n_{:s}".format(sd.SPANWISE_COORDINATE_SYMBOL),      )
define_quantity_symbol( sd.Q_STREAMWISE_NUMBER_OF_POINTS,    sd.VT_UNAVERAGED_VALUE, r"n_{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL),    )
define_quantity_symbol( sd.Q_TEST_LENGTH,                    sd.VT_UNAVERAGED_VALUE, r"\ell_t",                                            )
define_quantity_symbol( sd.Q_TRANSVERSE_NUMBER_OF_POINTS,    sd.VT_UNAVERAGED_VALUE, r"n_{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL),    )
define_quantity_symbol( sd.Q_VOLUMETRIC_FLOW_RATE,           sd.VT_UNAVERAGED_VALUE, r"Q",                                                 )


# Study types
cursor.execute(
"""
CREATE TABLE study_types (
    study_type_id   TEXT PRIMARY KEY UNIQUE,
    study_type_name TEXT NOT NULL
);
"""
)

study_types = {}
study_types[ sd.ST_DIRECT_NUMERICAL_SIMULATION ] = "direct numerical simulation"
study_types[ sd.ST_EXPERIMENT                  ] = "experiment"
study_types[ sd.ST_LARGE_EDDY_SIMULATION       ] = "large eddy simulation"

for study_type_id in study_types:
    cursor.execute(
    """
    INSERT INTO study_types( study_type_id, study_type_name )
    VALUES( ?, ? );
    """,
    ( study_type_id, study_types[study_type_id], )
    )

# Studies
cursor.execute(
"""
CREATE TABLE studies (
    study_id          TEXT PRIMARY KEY UNIQUE,
    flow_class_id     TEXT NOT NULL DEFAULT 'U',
    year              INTEGER NOT NULL CHECK (        year  >= 0 AND         year <= 9999 ),
    study_number      INTEGER NOT NULL CHECK ( study_number >  0 AND study_number <=  999 ),
    study_type_id     TEXT NOT NULL,
    outlier           INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    study_description TEXT DEFAULT NULL,
    study_provenance  TEXT DEFAULT NULL,
    FOREIGN KEY(flow_class_id) REFERENCES flow_classes(flow_class_id),
    FOREIGN KEY(study_type_id) REFERENCES study_types(study_type_id)
);
"""
)

# Series
cursor.execute(
"""
CREATE TABLE series (
    series_id            TEXT PRIMARY KEY UNIQUE,
    study_id             TEXT NOT NULL,
    series_number        INTEGER NOT NULL CHECK ( series_number > 0 AND series_number <= 999 ),
    number_of_dimensions INTEGER NOT NULL DEFAULT 2 CHECK ( number_of_dimensions > 0 AND number_of_dimensions <= 3 ),
    coordinate_system_id TEXT NOT NULL DEFAULT 'XYZ',
    geometry_id          TEXT DEFAULT NULL,
    outlier              INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    series_description   TEXT DEFAULT NULL,
    FOREIGN KEY(study_id)             REFERENCES studies(study_id),
    FOREIGN KEY(coordinate_system_id) REFERENCES coordinate_systems(coordinate_system_id),
    FOREIGN KEY(geometry_id)          REFERENCES geometries(geometry_id)
);
"""
)

# Stations
cursor.execute(
"""
CREATE TABLE stations (
    station_id                     TEXT PRIMARY KEY UNIQUE,
    series_id                      TEXT NOT NULL,
    study_id                       TEXT NOT NULL,
    station_number                 INTEGER NOT NULL CHECK ( station_number > 0 AND station_number <= 999 ),
    flow_regime_id                 TEXT DEFAULT NULL,
    previous_streamwise_station_id TEXT DEFAULT NULL,
    next_streamwise_station_id     TEXT DEFAULT NULL,
    previous_spanwise_station_id   TEXT DEFAULT NULL,
    next_spanwise_station_id       TEXT DEFAULT NULL,
    outlier                        INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    station_description            TEXT DEFAULT NULL,
    FOREIGN KEY(series_id)                      REFERENCES series(series_id),
    FOREIGN KEY(study_id)                       REFERENCES studies(study_id),
    FOREIGN KEY(flow_regime_id)                 REFERENCES flow_regimes(flow_regime_id),
    FOREIGN KEY(previous_streamwise_station_id) REFERENCES stations(station_id),
    FOREIGN KEY(next_streamwise_station_id)     REFERENCES stations(station_id),
    FOREIGN KEY(previous_spanwise_station_id)   REFERENCES stations(station_id),
    FOREIGN KEY(next_spanwise_station_id)       REFERENCES stations(station_id)
);
"""
)

# Points
cursor.execute(
"""
CREATE TABLE points (
    point_id          TEXT PRIMARY KEY UNIQUE,
    station_id        TEXT NOT NULL,
    series_id         TEXT NOT NULL,
    study_id          TEXT NOT NULL,
    point_number      INTEGER NOT NULL CHECK ( point_number > 0 AND point_number <= 9999 ),
    point_label_id    TEXT DEFAULT NULL,
    outlier           INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    point_description TEXT DEFAULT NULL,
    FOREIGN KEY(station_id)     REFERENCES stations(station_id),
    FOREIGN KEY(series_id)      REFERENCES series(series_id),
    FOREIGN KEY(study_id)       REFERENCES studies(study_id),
    FOREIGN KEY(point_label_id) REFERENCES point_labels(point_label_id)
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
CREATE TABLE study_sources (
    study_id              TEXT NOT NULL,
    citation_key          TEXT NOT NULL,
    source_classification INTEGER NOT NULL DEFAULT 1 CHECK ( source_classification = 1 OR source_classification = 2 ),
    PRIMARY KEY(study_id, citation_key),
    FOREIGN KEY(study_id) REFERENCES studies(study_id)
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
    series_id TEXT NOT NULL,
    fluid_id  TEXT DEFAULT NULL,
    name      TEXT DEFAULT NULL CHECK (
        fluid_id IS     NULL AND name IS NOT NULL
        OR
        fluid_id IS NOT NULL AND name IS NULL ),
    PRIMARY KEY(series_id, fluid_id),
    FOREIGN KEY(series_id) REFERENCES series(series_id),
    FOREIGN KEY(fluid_id)  REFERENCES fluids(fluid_id)
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
    study_id          TEXT NOT NULL,
    quantity_id       TEXT NOT NULL,
    value_type_id     TEXT NOT NULL,
    meastech_set      INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    study_value       REAL NOT NULL,
    study_uncertainty REAL DEFAULT NULL CHECK ( study_uncertainty >= 0.0 ),
    outlier           INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    PRIMARY KEY(study_id, quantity_id, value_type_id, meastech_set),
    FOREIGN KEY(study_id)      REFERENCES studies(study_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id)
);
"""
)

# Series values
cursor.execute(
"""
CREATE TABLE series_values (
    series_id          TEXT NOT NULL,
    quantity_id        TEXT NOT NULL,
    value_type_id      TEXT NOT NULL,
    meastech_set       INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    series_value       REAL NOT NULL,
    series_uncertainty REAL DEFAULT NULL CHECK ( series_uncertainty >= 0.0 ),
    outlier            INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    PRIMARY KEY(series_id, quantity_id, value_type_id, meastech_set),
    FOREIGN KEY(series_id)     REFERENCES series(series_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id)
);
"""
)

# Station values
cursor.execute(
"""
CREATE TABLE station_values (
    station_id          TEXT NOT NULL,
    quantity_id         TEXT NOT NULL,
    value_type_id       TEXT NOT NULL,
    meastech_set        INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    station_value       REAL NOT NULL,
    station_uncertainty REAL DEFAULT NULL CHECK ( station_uncertainty >= 0.0 ),
    outlier             INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    PRIMARY KEY(station_id, quantity_id, value_type_id, meastech_set),
    FOREIGN KEY(station_id)    REFERENCES stations(station_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id)
);
"""
)

# Point values
cursor.execute(
"""
CREATE TABLE point_values (
    point_id          TEXT NOT NULL,
    quantity_id       TEXT NOT NULL,
    value_type_id     TEXT NOT NULL,
    meastech_set      INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    point_value       REAL NOT NULL,
    point_uncertainty REAL DEFAULT NULL CHECK ( point_uncertainty >= 0.0 ),
    outlier           INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    PRIMARY KEY(point_id, quantity_id, value_type_id, meastech_set),
    FOREIGN KEY(point_id)      REFERENCES points(point_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id)
);
"""
)

# Measurement techniques for study values
cursor.execute(
"""
CREATE TABLE study_values_mt (
    study_id      TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    meastech_set  INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    meastech_id   TEXT NOT NULL,
    PRIMARY KEY(study_id, quantity_id, value_type_id, meastech_set, meastech_id),
    FOREIGN KEY(study_id)      REFERENCES studies(study_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(meastech_id)   REFERENCES measurement_techniques(meastech_id)
);
"""
)

# Measurement techniques for series values
cursor.execute(
"""
CREATE TABLE series_values_mt (
    series_Id     TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    meastech_set  INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    meastech_id   TEXT NOT NULL,
    PRIMARY KEY(series_id, quantity_id, value_type_id, meastech_set, meastech_id),
    FOREIGN KEY(series_id)     REFERENCES series(series_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(meastech_id)   REFERENCES measurement_techniques(meastech_id)
);
"""
)

# Measurement techniques for station values
cursor.execute(
"""
CREATE TABLE station_values_mt (
    station_id    TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    meastech_set  INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    meastech_id   TEXT NOT NULL,
    PRIMARY KEY(station_id, quantity_id, value_type_id, meastech_set, meastech_id),
    FOREIGN KEY(station_id)    REFERENCES stations(station_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(meastech_id)   REFERENCES measurement_techniques(meastech_id)
);
"""
)

# Measurement techniques for point values
cursor.execute(
"""
CREATE TABLE point_values_mt (
    point_id      TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    meastech_set  INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    meastech_id   TEXT NOT NULL,
    PRIMARY KEY(point_id, quantity_id, value_type_id, meastech_set, meastech_id),
    FOREIGN KEY(point_id)      REFERENCES points(point_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(meastech_id)   REFERENCES measurement_techniques(meastech_id)
);
"""
)

# Notes for studies
cursor.execute(
"""
CREATE TABLE study_notes (
    study_id TEXT NOT NULL,
    note_id  INTEGER NOT NULL CHECK ( note_id > 0 ),
    PRIMARY KEY(study_id, note_id),
    FOREIGN KEY(study_id) REFERENCES studies(study_id),
    FOREIGN KEY(note_id)  REFERENCES notes(note_id)
);
"""
)

# Notes for study values
cursor.execute(
"""
CREATE TABLE study_value_notes (
    study_id      TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    meastech_set  INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    note_id       INTEGER NOT NULL CHECK ( note_id > 0 ),
    PRIMARY KEY(study_id, quantity_id, value_type_id, meastech_set, note_id),
    FOREIGN KEY(study_id)      REFERENCES studies(study_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);
"""
)

# Notes for series
cursor.execute(
"""
CREATE TABLE series_notes (
    series_id TEXT NOT NULL,
    note_id   INTEGER NOT NULL CHECK ( note_id > 0 ),
    PRIMARY KEY(series_id, note_id),
    FOREIGN KEY(series_id) REFERENCES series(series_id),
    FOREIGN KEY(note_id)   REFERENCES notes(note_id)
);
"""
)

# Notes for series values
cursor.execute(
"""
CREATE TABLE series_value_notes (
    series_id     TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    meastech_set  INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    note_id       INTEGER NOT NULL CHECK ( note_id > 0 ),
    PRIMARY KEY(series_id, quantity_id, value_type_id, meastech_set, note_id),
    FOREIGN KEY(series_id)     REFERENCES series(series_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);
"""
)

# Notes for stations
cursor.execute(
"""
CREATE TABLE station_notes (
    station_id TEXT NOT NULL,
    note_id    INTEGER NOT NULL CHECK ( note_id > 0 ),
    PRIMARY KEY(station_id, note_id),
    FOREIGN KEY(station_id) REFERENCES stations(station_id),
    FOREIGN KEY(note_id)    REFERENCES notes(note_id)
);
"""
)

# Notes for station values
cursor.execute(
"""
CREATE TABLE station_value_notes (
    station_id    TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    meastech_set  INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    note_id       INTEGER NOT NULL CHECK ( note_id > 0 ),
    PRIMARY KEY(station_id, quantity_id, value_type_id, meastech_set, note_id),
    FOREIGN KEY(station_id)    REFERENCES stations(station_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);
"""
)

# Notes for points
cursor.execute(
"""
CREATE TABLE point_notes (
    point_id TEXT NOT NULL,
    note_id  INTEGER NOT NULL CHECK ( note_id > 0 ),
    PRIMARY KEY(point_id, note_id),
    FOREIGN KEY(point_id) REFERENCES points(point_id),
    FOREIGN KEY(note_id)  REFERENCES notes(note_id)
);
"""
)

# Notes for point values
cursor.execute(
"""
CREATE TABLE point_value_notes (
    point_id      TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    meastech_set  INTEGER NOT NULL DEFAULT 1 CHECK ( meastech_set > 0 ),
    note_id       INTEGER NOT NULL CHECK ( note_id > 0 ),
    PRIMARY KEY(point_id, quantity_id, value_type_id, meastech_set, note_id),
    FOREIGN KEY(point_id)      REFERENCES points(point_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
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
compilations[ sd.C_SELF         ] = "Originator"
compilations[ sd.C_CH_1969      ] = "Coles and Hirst"
compilations[ sd.C_BE_1973      ] = "Birch and Eggers"
compilations[ sd.C_FF_1977      ] = "Fernholz and Finley"
compilations[ sd.C_ERCOFTAC     ] = "ERCOFTAC Classic Collection"
compilations[ sd.C_AGARD_AR_345 ] = "AGARD-AR-345"

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
    compilation_id INTEGER NOT NULL,
    citation_key   TEXT NOT NULL,
    PRIMARY KEY(compilation_id, citation_key),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);
"""
)

compilation_sources = {}
compilation_sources[ sd.C_CH_1969      ] = [ "ColesDE+1969+eng+BOOK" ]
compilation_sources[ sd.C_BE_1973      ] = [ "BirchSF+1973+eng+BOOK" ]
compilation_sources[ sd.C_FF_1977      ] = [ "FernholzFF+1977+eng+RPRT",
                                             "FernholzFF+1980+eng+RPRT",
                                             "FernholzFF+1981+eng+RPRT",
                                             "FernholzFF+1989+eng+RPRT" ]
compilation_sources[ sd.C_ERCOFTAC     ] = [ "ERCOFTAC+DBASE" ]
compilation_sources[ sd.C_AGARD_AR_345 ] = [ "AGARD+1998+eng+RPRT" ]

for compilation_id in compilation_sources:
    for citation_key in compilation_sources[compilation_id]:
        cursor.execute(
        """
        INSERT INTO compilation_sources( compilation_id, citation_key )
        VALUES( ?, ? );
        """,
        ( compilation_id, citation_key, )
        )

# Study external identifiers
cursor.execute(
"""
CREATE TABLE study_external_ids (
    study_id          TEXT NOT NULL,
    compilation_id    INTEGER NOT NULL,
    study_external_id TEXT NOT NULL,
    PRIMARY KEY(study_id, compilation_id),
    FOREIGN KEY(study_id)       REFERENCES studies(study_id),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);
"""
)

# Series external identifiers
cursor.execute(
"""
CREATE TABLE series_external_ids (
    series_id          TEXT NOT NULL,
    compilation_id     INTEGER NOT NULL,
    series_external_id TEXT NOT NULL,
    PRIMARY KEY(series_id, compilation_id),
    FOREIGN KEY(series_id)      REFERENCES series(series_id),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);
"""
)

# Station external identifiers
cursor.execute(
"""
CREATE TABLE station_external_ids (
    station_id          TEXT NOT NULL,
    compilation_id      INTEGER NOT NULL,
    station_external_id TEXT NOT NULL,
    PRIMARY KEY(station_id, compilation_id),
    FOREIGN KEY(station_id)     REFERENCES stations(station_id),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);
"""
)

# Point external identifiers
cursor.execute(
"""
CREATE TABLE point_external_ids (
    point_id          TEXT NOT NULL,
    compilation_id    INTEGER NOT NULL,
    point_external_id TEXT NOT NULL,
    PRIMARY KEY(point_id, compilation_id),
    FOREIGN KEY(point_id)       REFERENCES points(point_id),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);
"""
)

conn.commit()
conn.close()
