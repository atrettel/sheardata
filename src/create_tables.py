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

import csv
import sqlite3
import sheardata as sd
import sys

conn = sqlite3.connect( sys.argv[1] )
cursor =  conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

# Averaging systems
cursor.execute(
"""
CREATE TABLE averaging_systems (
    identifier  TEXT PRIMARY KEY UNIQUE,
    system_name TEXT NOT NULL,
    notes       TEXT DEFAULT NULL
);
"""
)

averaging_systems = {}
averaging_systems[       sd.UNWEIGHTED_AVERAGING_SYSTEM ]       = "unweighted averaging"
averaging_systems[ sd.DENSITY_WEIGHTED_AVERAGING_SYSTEM ] = "density-weighted averaging"

for identifier in averaging_systems:
    cursor.execute(
    """
    INSERT INTO averaging_systems( identifier, system_name )
    VALUES( ?, ? );
    """,
    ( identifier, averaging_systems[identifier], )
    )

# Coordinate systems
cursor.execute(
"""
CREATE TABLE coordinate_systems (
    identifier  TEXT PRIMARY KEY UNIQUE,
    system_name TEXT NOT NULL,
    notes       TEXT DEFAULT NULL
);
"""
)

coordinate_systems = {}
coordinate_systems[ sd.RECTANGULAR_COORDINATE_SYSTEM ] = "rectangular coordinates"
coordinate_systems[ sd.CYLINDRICAL_COORDINATE_SYSTEM ] = "cylindrical coordinates"

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
    notes      TEXT DEFAULT NULL,
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
flow_classes[ sd.BOUNDARY_LAYER_FLOW_CLASS  ] = flow_class( "boundary layer",            sd.EXTERNAL_FLOW_CLASS )
flow_classes[ sd.DUCT_FLOW_CLASS            ] = flow_class( "duct flow",                 sd.INTERNAL_FLOW_CLASS )
flow_classes[ sd.EXTERNAL_FLOW_CLASS        ] = flow_class( "external flow",         sd.WALL_BOUNDED_FLOW_CLASS )
flow_classes[ sd.FREE_JET_FLOW_CLASS        ] = flow_class( "free jet",                sd.FREE_SHEAR_FLOW_CLASS )
flow_classes[ sd.FREE_SHEAR_FLOW_CLASS      ] = flow_class( "free shear flow",              sd.SHEAR_FLOW_CLASS )
flow_classes[ sd.HOMOGENEOUS_FLOW_CLASS     ] = flow_class( "homogeneous flow",      sd.UNCLASSIFIED_FLOW_CLASS )
flow_classes[ sd.INHOMOGENEOUS_FLOW_CLASS   ] = flow_class( "inhomogeneous flow",    sd.UNCLASSIFIED_FLOW_CLASS )
flow_classes[ sd.INTERNAL_FLOW_CLASS        ] = flow_class( "internal flow",         sd.WALL_BOUNDED_FLOW_CLASS )
flow_classes[ sd.ISOTROPIC_FLOW_CLASS       ] = flow_class( "isotropic flow",         sd.HOMOGENEOUS_FLOW_CLASS )
flow_classes[ sd.MIXING_LAYER_FLOW_CLASS    ] = flow_class( "mixing layer",            sd.FREE_SHEAR_FLOW_CLASS )
flow_classes[ sd.BOUNDARY_DRIVEN_FLOW_CLASS ] = flow_class( "boundary-driven flow",      sd.INTERNAL_FLOW_CLASS )
flow_classes[ sd.SHEAR_FLOW_CLASS           ] = flow_class( "shear flow",           sd.INHOMOGENEOUS_FLOW_CLASS )
flow_classes[ sd.UNCLASSIFIED_FLOW_CLASS    ] = flow_class( "flow",                                        None )
flow_classes[ sd.WAKE_FLOW_CLASS            ] = flow_class( "wake",                    sd.FREE_SHEAR_FLOW_CLASS )
flow_classes[ sd.WALL_BOUNDED_FLOW_CLASS    ] = flow_class( "wall-bounded flow",            sd.SHEAR_FLOW_CLASS )
flow_classes[ sd.WALL_JET_FLOW_CLASS        ] = flow_class( "wall jet",                  sd.EXTERNAL_FLOW_CLASS )

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
    identifier  TEXT PRIMARY KEY UNIQUE CHECK ( length(identifier) = 2 ),
    regime_name TEXT NOT NULL,
    notes       TEXT DEFAULT NULL
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
    phase_name TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
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
cursor.execute(
"""
CREATE TABLE fluids (
    identifier TEXT PRIMARY KEY UNIQUE,
    fluid_name TEXT NOT NULL,
    phase      TEXT NOT NULL,
    notes      TEXT DEFAULT NULL,
    FOREIGN KEY(phase) REFERENCES phases(identifier)
);
"""
)

class fluid:
    name       = None
    phase      = None

    def __init__( self, name, phase ):
        self.name       = name
        self.phase      = phase

fluids = {}
fluids[ sd.ARGON_GAS          ] = fluid( "argon",          "g" )
fluids[ sd.CARBON_DIOXIDE_GAS ] = fluid( "carbon dioxide", "g" )
fluids[ sd.HELIUM_GAS         ] = fluid( "helium",         "g" )
fluids[ sd.HYDROGEN_GAS       ] = fluid( "hydrogen",       "g" )
fluids[ sd.NITROGEN_GAS       ] = fluid( "nitrogen",       "g" )
fluids[ sd.OXYGEN_GAS         ] = fluid( "oxygen",         "g" )
fluids[ sd.WATER_LIQUID       ] = fluid( "water",          "l" )
fluids[ sd.WATER_VAPOR        ] = fluid( "water",          "g" )

for identifier in fluids:
    cursor.execute(
    """
    INSERT INTO fluids( identifier, fluid_name, phase )
    VALUES( ?, ?, ? );
    """,
    ( identifier, fluids[identifier].name, fluids[identifier].phase, )
    )

# Geometries
cursor.execute(
"""
CREATE TABLE geometries (
    identifier    TEXT PRIMARY KEY UNIQUE,
    geometry_name TEXT NOT NULL,
    notes         TEXT DEFAULT NULL
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
    notes          TEXT DEFAULT NULL,
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
measurement_techniques[ sd.MT_ASSUMPTION                               ] = MeasTech( "assumption",                               sd.MT_REASONING,                                    )
measurement_techniques[ sd.MT_CALCULATION                              ] = MeasTech( "calculation",                              sd.MT_REASONING,                                    )
measurement_techniques[ sd.MT_EMPIRICISM                               ] = MeasTech( "empiricism",                               sd.MT_ROOT,                                         )
measurement_techniques[ sd.MT_DIFFERENTIAL_PRESSURE_METHOD             ] = MeasTech( "differential pressure method",             sd.MT_EMPIRICISM,                                   )
measurement_techniques[ sd.MT_IMPACT_TUBE                              ] = MeasTech( "impact tube",                              sd.MT_DIFFERENTIAL_PRESSURE_METHOD, intrusive=True, )
measurement_techniques[ sd.MT_PITOT_STATIC_TUBE                        ] = MeasTech( "Pitot-static tube",                        sd.MT_DIFFERENTIAL_PRESSURE_METHOD, intrusive=True, )
measurement_techniques[ sd.MT_FLOW_RATE_MEASUREMENT                    ] = MeasTech( "flow rate measurement",                    sd.MT_EMPIRICISM,                                   )
measurement_techniques[ sd.MT_WEIGHING_METHOD                          ] = MeasTech( "weighing method",                          sd.MT_FLOW_RATE_MEASUREMENT,                        )
measurement_techniques[ sd.MT_OPTICAL_METHOD                           ] = MeasTech( "optical method",                           sd.MT_EMPIRICISM,                                   )
measurement_techniques[ sd.MT_DIRECT_INJECTION_METHOD                  ] = MeasTech( "direct injection method",                  sd.MT_OPTICAL_METHOD,                               )
measurement_techniques[ sd.MT_INDEX_OF_REFRACTION_METHOD               ] = MeasTech( "index-of-refraction method",               sd.MT_OPTICAL_METHOD,                               )
measurement_techniques[ sd.MT_MACH_ZEHNDER_INTERFEROMETRY              ] = MeasTech( "Mach-Zehnder interferometry",              sd.MT_INDEX_OF_REFRACTION_METHOD,                   )
measurement_techniques[ sd.MT_SCHLIEREN_PHOTOGRAPHY                    ] = MeasTech( "schlieren photography",                    sd.MT_INDEX_OF_REFRACTION_METHOD,                   )
measurement_techniques[ sd.MT_SHADOWGRAPH_PHOTOGRAPHY                  ] = MeasTech( "shadowgraph photography",                  sd.MT_INDEX_OF_REFRACTION_METHOD,                   )
measurement_techniques[ sd.MT_LASER_DOPPLER_ANEMOMETRY                 ] = MeasTech( "laser Doppler anemometry",                 sd.MT_OPTICAL_METHOD,                               )
measurement_techniques[ sd.MT_PARTICLE_IMAGE_VELOCIMETRY               ] = MeasTech( "particle image velocimetry",               sd.MT_OPTICAL_METHOD,                               )
measurement_techniques[ sd.MT_THERMAL_ANEMOMETRY                       ] = MeasTech( "thermal anemometry",                       sd.MT_EMPIRICISM,                                   )
measurement_techniques[ sd.MT_HOT_WIRE_ANEMOMETRY                      ] = MeasTech( "hot-wire anemometry",                      sd.MT_THERMAL_ANEMOMETRY,           intrusive=True, )
measurement_techniques[ sd.MT_CONSTANT_CURRENT_HOT_WIRE_ANEMOMETRY     ] = MeasTech( "constant-current hot-wire anemometry",     sd.MT_HOT_WIRE_ANEMOMETRY,          intrusive=True, )
measurement_techniques[ sd.MT_CONSTANT_TEMPERATURE_HOT_WIRE_ANEMOMETRY ] = MeasTech( "constant-temperature hot-wire anemometry", sd.MT_HOT_WIRE_ANEMOMETRY,          intrusive=True, )
measurement_techniques[ sd.MT_WALL_SHEAR_STRESS_METHOD                 ] = MeasTech( "wall shear stress method",                 sd.MT_EMPIRICISM,                                   )
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

# Point labels
cursor.execute(
"""
CREATE TABLE point_labels (
    identifier TEXT PRIMARY KEY UNIQUE,
    label_name TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);
"""
)

point_labels = {}
point_labels[ sd.CENTER_LINE_POINT_LABEL ] = "center-line"
point_labels[ sd.EDGE_POINT_LABEL        ] = "edge"
point_labels[ sd.WALL_POINT_LABEL        ] = "wall"

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
    temperature_exponent REAL NOT NULL DEFAULT 0.0,
    notes                TEXT DEFAULT NULL
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
quantities[ sd.Q_BODY_REYNOLDS_NUMBER           ] = quantity( "body Reynolds number",                                                                              )
quantities[ sd.Q_BODY_STROUHAL_NUMBER           ] = quantity( "body Strouhal number",                                                                              )
quantities[ sd.Q_DEVELOPMENT_LENGTH             ] = quantity( "development length",                                                                                )
quantities[ sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS ] = quantity( "distance between pressure taps",      length_exponent=+1.0,                                         )
quantities[ sd.Q_DRAG_COEFFICIENT               ] = quantity( "drag coefficient",                                                                                  )
quantities[ sd.Q_DRAG_FORCE                     ] = quantity( "drag force",                          length_exponent=+1.0, mass_exponent=+1.0, time_exponent=-2.0, )
quantities[ sd.Q_FREESTREAM_MACH_NUMBER         ] = quantity( "freestream Mach number",                                                                            )
quantities[ sd.Q_FREESTREAM_SPEED_OF_SOUND      ] = quantity( "freestream speed of sound",           length_exponent=+1.0, time_exponent=-1.0,                     )
quantities[ sd.Q_FREESTREAM_TEMPERATURE         ] = quantity( "freestream temperature",         temperature_exponent=+1.0,                                         )
quantities[ sd.Q_FREESTREAM_VELOCITY            ] = quantity( "freestream velocity",                 length_exponent=+1.0, time_exponent=-1.0,                     )
quantities[ sd.Q_LIFT_COEFFICIENT               ] = quantity( "lift coefficient",                                                                                  )
quantities[ sd.Q_LIFT_FORCE                     ] = quantity( "lift force",                          length_exponent=+1.0, mass_exponent=+1.0, time_exponent=-2.0, )
quantities[ sd.Q_LIFT_TO_DRAG_RATIO             ] = quantity( "lift-to-drag ratio",                                                                                )
quantities[ sd.Q_MASS_FLOW_RATE                 ] = quantity( "mass flow rate",                        mass_exponent=+1.0, time_exponent=-1.0,                     )
quantities[ sd.Q_TEST_LENGTH                    ] = quantity( "test length",                         length_exponent=+1.0,                                         )
quantities[ sd.Q_VOLUMETRIC_FLOW_RATE           ] = quantity( "volumetric flow rate",                length_exponent=+3.0, time_exponent=-1.0,                     )

# Quantities, station
quantities[ sd.Q_ASPECT_RATIO                           ] = quantity( "aspect ratio",                                                                                           )
quantities[ sd.Q_BULK_MACH_NUMBER                       ] = quantity( "bulk Mach number",                                                                                       )
quantities[ sd.Q_BULK_REYNOLDS_NUMBER                   ] = quantity( "bulk Reynolds number",                                                                                   )
quantities[ sd.Q_BULK_TO_CENTER_LINE_VELOCITY_RATIO     ] = quantity( "bulk-to-center-line velocity ratio",                                                                     )
quantities[ sd.Q_BULK_VELOCITY                          ] = quantity( "bulk velocity",                          length_exponent=+1.0,   time_exponent=-1.0,                     )
quantities[ sd.Q_CLAUSER_THICKNESS                      ] = quantity( "Clauser thickness",                      length_exponent=+1.0,                                           )
quantities[ sd.Q_CROSS_SECTIONAL_AREA                   ] = quantity( "cross-sectional area",                   length_exponent=+2.0,                                           )
quantities[ sd.Q_DISPLACEMENT_THICKNESS                 ] = quantity( "displacement thickness",                 length_exponent=+1.0,                                           )
quantities[ sd.Q_DISPLACEMENT_THICKNESS_REYNOLDS_NUMBER ] = quantity( "displacement thickness Reynolds number",                                                                 )
quantities[ sd.Q_ENERGY_THICKNESS                       ] = quantity( "energy thickness",                       length_exponent=+1.0,                                           )
quantities[ sd.Q_EQUILIBRIUM_PARAMETER                  ] = quantity( "equilibrium parameter",                                                                                  )
quantities[ sd.Q_HEIGHT                                 ] = quantity( "height",                                 length_exponent=+1.0,                                           )
quantities[ sd.Q_HYDRAULIC_DIAMETER                     ] = quantity( "hydraulic diameter",                     length_exponent=+1.0,                                           )
quantities[ sd.Q_INNER_DIAMETER                         ] = quantity( "inner diameter",                         length_exponent=+1.0,                                           )
quantities[ sd.Q_MOMENTUM_THICKNESS                     ] = quantity( "momentum thickness",                     length_exponent=+1.0,                                           )
quantities[ sd.Q_MOMENTUM_THICKNESS_REYNOLDS_NUMBER     ] = quantity( "momentum thickness Reynolds number",                                                                     )
quantities[ sd.Q_OUTER_DIAMETER                         ] = quantity( "outer diameter",                         length_exponent=+1.0,                                           )
quantities[ sd.Q_RECOVERY_FACTOR                        ] = quantity( "recovery factor",                                                                                        )
quantities[ sd.Q_SHAPE_FACTOR_1_TO_2                    ] = quantity( "shape factor 1-to-2",                                                                                    )
quantities[ sd.Q_SHAPE_FACTOR_3_TO_2                    ] = quantity( "shape factor 3-to-2",                                                                                    )
quantities[ sd.Q_SPANWISE_PRESSURE_GRADIENT             ] = quantity( "spanwise pressure gradient",               mass_exponent=+1.0, length_exponent=-2.0, time_exponent=-2.0, )
quantities[ sd.Q_STREAMWISE_COORDINATE_REYNOLDS_NUMBER  ] = quantity( "streamwise coordinate Reynolds number",                                                                  )
quantities[ sd.Q_STREAMWISE_PRESSURE_GRADIENT           ] = quantity( "streamwise pressure gradient",             mass_exponent=+1.0, length_exponent=-2.0, time_exponent=-2.0, )
quantities[ sd.Q_WETTED_PERIMETER                       ] = quantity( "wetted perimeter",                       length_exponent=+2.0,                                           )
quantities[ sd.Q_WIDTH                                  ] = quantity( "width",                                  length_exponent=+1.0,                                           )

# Quantities, wall point
quantities[ sd.Q_DARCY_FRICTION_FACTOR               ] = quantity( "Darcy friction factor",                                                              )
quantities[ sd.Q_FANNING_FRICTION_FACTOR             ] = quantity( "Fanning friction factor",                                                            )
quantities[ sd.Q_FRICTION_MACH_NUMBER                ] = quantity( "friction Mach number",                                                               )
quantities[ sd.Q_FRICTION_REYNOLDS_NUMBER            ] = quantity( "friction Reynolds number",                                                           )
quantities[ sd.Q_FRICTION_TEMPERATURE                ] = quantity( "friction temperature",                temperature_exponent=+1.0,                     )
quantities[ sd.Q_FRICTION_VELOCITY                   ] = quantity( "friction velocity",                        length_exponent=+1.0, time_exponent=-1.0, )
quantities[ sd.Q_HEAT_TRANSFER_COEFFICIENT           ] = quantity( "heat transfer coefficient",                                                          )
quantities[ sd.Q_INNER_LAYER_HEAT_FLUX               ] = quantity( "inner-layer heat flux",                                                              )
quantities[ sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT        ] = quantity( "inner-layer roughness height",                                                       )
quantities[ sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT        ] = quantity( "outer-layer roughness height",                                                       )
quantities[ sd.Q_PRESSURE_COEFFICIENT                ] = quantity( "pressure coefficient",                                                               )
quantities[ sd.Q_ROUGHNESS_HEIGHT                    ] = quantity( "roughness height",                         length_exponent=+1.0,                     )
quantities[ sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER ] = quantity( "semi-local friction Reynolds number",                                                )
quantities[ sd.Q_SKIN_FRICTION_COEFFICIENT           ] = quantity( "skin friction coefficient",                                                          )
quantities[ sd.Q_SPANWISE_WALL_CURVATURE             ] = quantity( "spanwise wall curvature",                  length_exponent=-1.0,                     )
quantities[ sd.Q_STREAMWISE_WALL_CURVATURE           ] = quantity( "streamwise wall curvature",                length_exponent=-1.0,                     )
quantities[ sd.Q_VISCOUS_LENGTH_SCALE                ] = quantity( "viscous length scale",                     length_exponent=+1.0                      )
quantities[ sd.Q_WALL_TO_EDGE_TEMPERATURE_RATIO      ] = quantity( "wall-to-edge temperature ratio",                                                     )
quantities[ sd.Q_WALL_TO_RECOVERY_TEMPERATURE_RATIO  ] = quantity( "wall-to-recovery temperature ratio",                                                 )

# Quantities, point
quantities[ sd.Q_DISTANCE_FROM_WALL               ] = quantity( "distance from wall",                    length_exponent=+1.0,                                                  )
quantities[ sd.Q_DYNAMIC_VISCOSITY                ] = quantity( "dynamic viscosity",                       mass_exponent=+1.0, length_exponent=-1.0,        time_exponent=-1.0, )
quantities[ sd.Q_HEAT_CAPACITY_RATIO              ] = quantity( "gamma",                                                                                                        )
quantities[ sd.Q_HEAT_FLUX                        ] = quantity( "heat flux",                               mass_exponent=+1.0,   time_exponent=-3.0,                            )
quantities[ sd.Q_INNER_LAYER_COORDINATE           ] = quantity( "inner-layer coordinate",                                                                                       )
quantities[ sd.Q_INNER_LAYER_TEMPERATURE          ] = quantity( "inner-layer temperature",                                                                                      )
quantities[ sd.Q_INNER_LAYER_VELOCITY             ] = quantity( "inner-layer velocity",                                                                                         )
quantities[ sd.Q_KINEMATIC_VISCOSITY              ] = quantity( "kinematic viscosity",                   length_exponent=+2.0,   time_exponent=-1.0,                            )
quantities[ sd.Q_MACH_NUMBER                      ] = quantity( "Mach number",                                                                                                  )
quantities[ sd.Q_MASS_DENSITY                     ] = quantity( "mass density",                            mass_exponent=+1.0, length_exponent=-1.0,                            )
quantities[ sd.Q_OUTER_LAYER_COORDINATE           ] = quantity( "outer-layer coordinate",                                                                                       )
quantities[ sd.Q_OUTER_LAYER_TEMPERATURE          ] = quantity( "outer-layer temperature",                                                                                      )
quantities[ sd.Q_OUTER_LAYER_VELOCITY             ] = quantity( "outer-layer velocity",                                                                                         )
quantities[ sd.Q_PRANDTL_NUMBER                   ] = quantity( "Prandtl number",                                                                                               )
quantities[ sd.Q_PRESSURE                         ] = quantity( "pressure",                                mass_exponent=+1.0, length_exponent=-1.0,        time_exponent=-2.0, )
quantities[ sd.Q_SEMI_LOCAL_COORDINATE            ] = quantity( "semi-local inner-layer coordinate",                                                                            )
quantities[ sd.Q_SHEAR_STRESS                     ] = quantity( "shear stress",                            mass_exponent=+1.0, length_exponent=-1.0,        time_exponent=-2.0, )
quantities[ sd.Q_SPANWISE_COORDINATE              ] = quantity( "spanwise coordinate",                   length_exponent=+1.0,                                                  )
quantities[ sd.Q_SPANWISE_VELOCITY                ] = quantity( "spanwise velocity",                     length_exponent=+1.0,   time_exponent=-1.0,                            )
quantities[ sd.Q_SPECIFIC_ENTHALPY                ] = quantity( "specific enthalpy",                     length_exponent=+2.0,   time_exponent=-2.0,                            )
quantities[ sd.Q_SPECIFIC_GAS_CONSTANT            ] = quantity( "specific gas constant",                 length_exponent=+2.0,   time_exponent=-2.0, temperature_exponent=-1.0, )
quantities[ sd.Q_SPECIFIC_INTERNAL_ENERGY         ] = quantity( "specific internal energy",              length_exponent=+2.0,   time_exponent=-2.0,                            )
quantities[ sd.Q_SPECIFIC_ISOBARIC_HEAT_CAPACITY  ] = quantity( "specific isobaric heat capacity",       length_exponent=+2.0,   time_exponent=-2.0, temperature_exponent=-1.0, )
quantities[ sd.Q_SPECIFIC_ISOCHORIC_HEAT_CAPACITY ] = quantity( "specific isochoric heat capacity",      length_exponent=+2.0,   time_exponent=-2.0, temperature_exponent=-1.0, )
quantities[ sd.Q_SPECIFIC_TOTAL_ENTHALPY          ] = quantity( "specific total enthalpy",               length_exponent=+2.0,   time_exponent=-2.0,                            )
quantities[ sd.Q_SPECIFIC_TOTAL_INTERNAL_ENERGY   ] = quantity( "specific total internal energy",        length_exponent=+2.0,   time_exponent=-2.0,                            )
quantities[ sd.Q_SPECIFIC_VOLUME                  ] = quantity( "specific volume",                       length_exponent=+3.0,   mass_exponent=-1.0,                            )
quantities[ sd.Q_SPEED                            ] = quantity( "speed",                                 length_exponent=+1.0,   time_exponent=-1.0,                            )
quantities[ sd.Q_SPEED_OF_SOUND                   ] = quantity( "speed of sound",                        length_exponent=+1.0,   time_exponent=-1.0,                            )
quantities[ sd.Q_STREAMWISE_COORDINATE            ] = quantity( "streamwise coordinate",                 length_exponent=+1.0,                                                  )
quantities[ sd.Q_STREAMWISE_VELOCITY              ] = quantity( "streamwise velocity",                   length_exponent=+1.0,   time_exponent=-1.0,                            )
quantities[ sd.Q_TEMPERATURE                      ] = quantity( "temperature",                      temperature_exponent=+1.0,                                                  )
quantities[ sd.Q_TOTAL_PRESSURE                   ] = quantity( "total pressure",                          mass_exponent=+1.0, length_exponent=-1.0,        time_exponent=-2.0, )
quantities[ sd.Q_TOTAL_TEMPERATURE                ] = quantity( "total temperature",                temperature_exponent=+1.0,                                                  )
quantities[ sd.Q_TRANSVERSE_COORDINATE            ] = quantity( "transverse coordinate",                 length_exponent=+1.0,                                                  )
quantities[ sd.Q_TRANSVERSE_VELOCITY              ] = quantity( "transverse velocity",                   length_exponent=+1.0,   time_exponent=-1.0,                            )

# Quantities, point, component-based
for prefix in [ sd.AMOUNT_FRACTION_PREFIX,
                sd.MASS_FRACTION_PREFIX, ]:
    for fluid in fluids:
        name = "unknown quantity"
        if ( prefix == sd.AMOUNT_FRACTION_PREFIX ):
            name = "amount fraction for "
        elif ( prefix == sd.MASS_FRACTION_PREFIX ):
            name = "mass fraction for "
        quantities[ prefix+fluid ] = quantity( name+fluids[fluid].name+" ("+fluids[fluid].phase+")" )

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
    type_name  TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
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
    description           TEXT DEFAULT NULL,
    provenance            TEXT DEFAULT NULL,
    notes                 TEXT DEFAULT NULL,
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
    description          TEXT DEFAULT NULL,
    notes                TEXT DEFAULT NULL,
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
    originators_identifier       TEXT DEFAULT NULL,
    flow_regime                  TEXT DEFAULT NULL,
    previous_streamwise_station  TEXT DEFAULT NULL,
    next_streamwise_station      TEXT DEFAULT NULL,
    previous_spanwise_station    TEXT DEFAULT NULL,
    next_spanwise_station        TEXT DEFAULT NULL,
    outlier                      INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    description                  TEXT DEFAULT NULL,
    notes                        TEXT DEFAULT NULL,
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
    notes                TEXT DEFAULT NULL,
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
    study                 TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    study_value           REAL NOT NULL,
    study_uncertainty     REAL DEFAULT NULL CHECK ( study_uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(study, quantity, averaging_system, measurement_technique),
    FOREIGN KEY(study)                 REFERENCES                studies(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);
"""
)

# Series values
cursor.execute(
"""
CREATE TABLE series_values (
    series                TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    series_value          REAL NOT NULL,
    series_uncertainty    REAL DEFAULT NULL CHECK ( series_uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(series, quantity, averaging_system, measurement_technique),
    FOREIGN KEY(series)                REFERENCES                 series(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);
"""
)

# Station values
cursor.execute(
"""
CREATE TABLE station_values (
    station               TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    station_value         REAL NOT NULL,
    station_uncertainty   REAL DEFAULT NULL CHECK ( station_uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(station, quantity, averaging_system, measurement_technique),
    FOREIGN KEY(station)               REFERENCES               stations(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);
"""
)

# Point values
cursor.execute(
"""
CREATE TABLE point_values (
    point                 TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    point_value           REAL NOT NULL,
    point_uncertainty     REAL DEFAULT NULL CHECK ( point_uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(point, quantity, averaging_system, measurement_technique),
    FOREIGN KEY(point)                 REFERENCES                 points(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
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
