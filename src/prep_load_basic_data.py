#!/usr/bin/env python3

# Copyright (C) 2020-2022 Andrew Trettel
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
value_types = {}
value_types[ sd.VT_DENSITY_WEIGHTED_AVERAGE ] = "density-weighted averaging"
value_types[ sd.VT_MAXIMUM_VALUE            ] = "maximum value"
value_types[ sd.VT_MINIMUM_VALUE            ] = "minimum value"
value_types[ sd.VT_UNAVERAGED_VALUE         ] = "unaveraged value"
value_types[ sd.VT_UNWEIGHTED_AVERAGE       ] = "unweighted averaging"

for value_type_id in value_types:
    cursor.execute(
    """
    INSERT INTO value_types( value_type_id, value_type_name )
    VALUES( ?, ? );
    """,
    ( value_type_id, value_types[value_type_id], )
    )

# Coordinate systems
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

# Source classifications
source_classifications = {}
source_classifications[   sd.PRIMARY_SOURCE ] =   "primary source"
source_classifications[ sd.SECONDARY_SOURCE ] = "secondary source"
source_classifications[  sd.TERTIARY_SOURCE ] =  "tertiary source"

for source_classification_id in source_classifications:
    cursor.execute(
    """
    INSERT INTO source_classifications( source_classification_id,
                                        source_classification_name )
    VALUES( ?, ? );
    """,
    (
        source_classification_id,
        source_classifications[source_classification_id],
    )
    )

# Facility classes
def add_facility_class( cursor, facility_class_id, facility_class_name,
                    facility_class_parent_id=None ):
    cursor.execute(
    """
    INSERT INTO facility_classes( facility_class_id, facility_class_name )
    VALUES( ?, ? );
    """,
    (
        str(facility_class_id),
        str(facility_class_name),
    )
    )
    if ( facility_class_parent_id == None ):
        cursor.execute(
        """
        INSERT INTO facility_class_paths( facility_class_ancestor_id,
                                      facility_class_descendant_id,
                                      facility_class_path_length )
        VALUES( ?, ?, 0 );
        """,
        (
            str(facility_class_id),
            str(facility_class_id),
        )
        )
    else:
        cursor.execute(
        """
        INSERT INTO facility_class_paths( facility_class_ancestor_id,
                                      facility_class_descendant_id,
                                      facility_class_path_length )
        SELECT ?, ?, 0
        UNION ALL
        SELECT tmp.facility_class_ancestor_id, ?, tmp.facility_class_path_length+1
        FROM facility_class_paths as tmp
        WHERE tmp.facility_class_descendant_id = ?;
        """,
        (
            str(facility_class_id),
            str(facility_class_id),
            str(facility_class_id),
            str(facility_class_parent_id),
        )
        )

add_facility_class( cursor, sd.FT_FACILITY,                   "facility",                   None                        )
add_facility_class( cursor, sd.FT_EXPERIMENTAL_FACILITY,      "experimental facility",      sd.FT_FACILITY              )
add_facility_class( cursor, sd.FT_TUNNEL,                     "tunnel",                     sd.FT_EXPERIMENTAL_FACILITY )
add_facility_class( cursor, sd.FT_WIND_TUNNEL,                "wind tunnel",                sd.FT_TUNNEL                )
add_facility_class( cursor, sd.FT_OPEN_CIRCUIT_WIND_TUNNEL,   "open-circuit wind tunnel",   sd.FT_WIND_TUNNEL           )
add_facility_class( cursor, sd.FT_CLOSED_CIRCUIT_WIND_TUNNEL, "closed-circuit wind tunnel", sd.FT_WIND_TUNNEL           )
add_facility_class( cursor, sd.FT_BLOWDOWN_WIND_TUNNEL,       "blowdown wind tunnel",       sd.FT_WIND_TUNNEL           )
add_facility_class( cursor, sd.FT_LUDWIEG_TUBE,               "Ludwieg tube",               sd.FT_BLOWDOWN_WIND_TUNNEL  )
add_facility_class( cursor, sd.FT_SHOCK_TUBE,                 "shock tube",                 sd.FT_BLOWDOWN_WIND_TUNNEL  )
add_facility_class( cursor, sd.FT_WATER_TUNNEL,               "water tunnel",               sd.FT_TUNNEL                )
add_facility_class( cursor, sd.FT_RANGE,                      "range",                      sd.FT_EXPERIMENTAL_FACILITY )
add_facility_class( cursor, sd.FT_TOWING_TANK,                "towing tank",                sd.FT_EXPERIMENTAL_FACILITY )
add_facility_class( cursor, sd.FT_NUMERICAL_FACILITY,         "numerical facility",         sd.FT_FACILITY              )
add_facility_class( cursor, sd.FT_FINITE_DIFFERENCE_METHOD,   "finite-difference method",   sd.FT_NUMERICAL_FACILITY    )
add_facility_class( cursor, sd.FT_FINITE_ELEMENT_METHOD,      "finite-element method",      sd.FT_NUMERICAL_FACILITY    )
add_facility_class( cursor, sd.FT_FINITE_VOLUME_METHOD,       "finite-volume method",       sd.FT_NUMERICAL_FACILITY    )
add_facility_class( cursor, sd.FT_SPECTRAL_METHOD,            "spectral method",            sd.FT_NUMERICAL_FACILITY    )

# Flow classes
def add_flow_class( cursor, flow_class_id, flow_class_name,
                    flow_class_parent_id=None ):
    cursor.execute(
    """
    INSERT INTO flow_classes( flow_class_id, flow_class_name )
    VALUES( ?, ? );
    """,
    (
        str(flow_class_id),
        str(flow_class_name),
    )
    )
    if ( flow_class_parent_id == None ):
        cursor.execute(
        """
        INSERT INTO flow_class_paths( flow_class_ancestor_id,
                                      flow_class_descendant_id,
                                      flow_class_path_length )
        VALUES( ?, ?, 0 );
        """,
        (
            str(flow_class_id),
            str(flow_class_id),
        )
        )
    else:
        cursor.execute(
        """
        INSERT INTO flow_class_paths( flow_class_ancestor_id,
                                      flow_class_descendant_id,
                                      flow_class_path_length )
        SELECT ?, ?, 0
        UNION ALL
        SELECT tmp.flow_class_ancestor_id, ?, tmp.flow_class_path_length+1
        FROM flow_class_paths as tmp
        WHERE tmp.flow_class_descendant_id = ?;
        """,
        (
            str(flow_class_id),
            str(flow_class_id),
            str(flow_class_id),
            str(flow_class_parent_id),
        )
        )
        
add_flow_class( cursor, sd.FC_UNCLASSIFIED_FLOW,    "flow",                                     None )
add_flow_class( cursor, sd.FC_HOMOGENEOUS_FLOW,     "homogeneous flow",      sd.FC_UNCLASSIFIED_FLOW )
add_flow_class( cursor, sd.FC_ISOTROPIC_FLOW,       "isotropic flow",         sd.FC_HOMOGENEOUS_FLOW )
add_flow_class( cursor, sd.FC_INHOMOGENEOUS_FLOW,   "inhomogeneous flow",    sd.FC_UNCLASSIFIED_FLOW )
add_flow_class( cursor, sd.FC_SHEAR_FLOW,           "shear flow",           sd.FC_INHOMOGENEOUS_FLOW )
add_flow_class( cursor, sd.FC_FREE_SHEAR_FLOW,      "free shear flow",              sd.FC_SHEAR_FLOW )
add_flow_class( cursor, sd.FC_FREE_JET,             "free jet",                sd.FC_FREE_SHEAR_FLOW )
add_flow_class( cursor, sd.FC_MIXING_LAYER,         "mixing layer",            sd.FC_FREE_SHEAR_FLOW )
add_flow_class( cursor, sd.FC_WAKE,                 "wake",                    sd.FC_FREE_SHEAR_FLOW )
add_flow_class( cursor, sd.FC_WALL_BOUNDED_FLOW,    "wall-bounded flow",            sd.FC_SHEAR_FLOW )
add_flow_class( cursor, sd.FC_EXTERNAL_FLOW,        "external flow",         sd.FC_WALL_BOUNDED_FLOW )
add_flow_class( cursor, sd.FC_INTERNAL_FLOW,        "internal flow",         sd.FC_WALL_BOUNDED_FLOW )
add_flow_class( cursor, sd.FC_BOUNDARY_LAYER,       "boundary layer",            sd.FC_EXTERNAL_FLOW )
add_flow_class( cursor, sd.FC_WALL_JET,             "wall jet",                  sd.FC_EXTERNAL_FLOW )
add_flow_class( cursor, sd.FC_DUCT_FLOW,            "duct flow",                 sd.FC_INTERNAL_FLOW )
add_flow_class( cursor, sd.FC_BOUNDARY_DRIVEN_FLOW, "boundary-driven flow",      sd.FC_INTERNAL_FLOW )

# Flow regimes
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
phases = {}
phases[ sd.PH_GAS        ] = "gas"
phases[ sd.PH_LIQUID     ] = "liquid"
phases[ sd.PH_SOLID      ] = "solid"
phases[ sd.PH_MULTIPHASE ] = "multiphase"

for phase_id in phases:
    cursor.execute(
    """
    INSERT INTO phases( phase_id, phase_name )
    VALUES( ?, ? );
    """,
    ( phase_id, phases[phase_id], )
    )

# Elements
class Element:
    _atomic_number              = None
    _element_symbol             = None
    _element_name               = None
    _standard_atomic_weight_min = None
    _standard_atomic_weight_max = None
    _conventional_atomic_weight = None

    def atomic_number( self ):
        return self._atomic_number

    def element_symbol( self ):
        return self._element_symbol

    def element_name( self ):
        return self._element_name

    def minimum_standard_atomic_weight( self ):
        return None if self._standard_atomic_weight_min == 0.0 else self._standard_atomic_weight_min

    def maximum_standard_atomic_weight( self ):
        return None if self._standard_atomic_weight_max == 0.0 else self._standard_atomic_weight_max

    def conventional_atomic_weight( self ):
        return None if self._conventional_atomic_weight == 0.0 else self._conventional_atomic_weight

    def execute_query( self ):
        cursor.execute(
        """
        INSERT INTO elements VALUES( ?, ?, ?, ?, ?, ? );
        """,
        (
            self.atomic_number(),
            self.element_symbol(),
            self.element_name(),
            self.minimum_standard_atomic_weight(),
            self.maximum_standard_atomic_weight(),
            self.conventional_atomic_weight(),
        )
        )

    def __init__( self, atomic_number, element_symbol, element_name,
                  standard_atomic_weight_min=0.0,
                  standard_atomic_weight_max=0.0,
                  conventional_atomic_weight=0.0,
                   ):
        self._atomic_number              = atomic_number
        self._element_symbol             = element_symbol
        self._element_name               = element_name
        self._standard_atomic_weight_min = standard_atomic_weight_min
        self._standard_atomic_weight_max = standard_atomic_weight_max
        self._conventional_atomic_weight = conventional_atomic_weight

elements = []
elements_filename = "../data/elements.csv"
with open( elements_filename, "r" ) as elements_file:
    elements_reader = csv.reader( elements_file, delimiter=",", quotechar='"', \
        skipinitialspace=True )
    next(elements_reader)
    for elements_row in elements_reader:
        elements.append( Element(
            int(elements_row[0]),
            str(elements_row[1]),
            str(elements_row[2]),
            float(elements_row[3]),
            float(elements_row[4]),
            float(elements_row[5]),
        ) )

for element in elements:
    element.execute_query()

# Fluids
class Fluid:
    _fluid_id          = None
    _fluid_name        = None
    _phase_id          = None
    _molecular_formula = None

    def fluid_id( self ):
        return self._fluid_id

    def fluid_name( self ):
        return self._fluid_name

    def phase_id( self ):
        return self._phase_id

    def molecular_formula( self ):
        return self._molecular_formula

    def execute_query( self ):
        cursor.execute(
        """
        INSERT INTO fluids( fluid_id, fluid_name, phase_id, molecular_formula )
        VALUES( ?, ?, ?, ? );
        """,
        (
            self.fluid_id(),
            self.fluid_name(),
            self.phase_id(),
            self.molecular_formula(),
        )
        )

    def __init__( self, fluid_id, fluid_name, phase_id, molecular_formula=None ):
        self._fluid_id          = fluid_id
        self._fluid_name        = fluid_name
        self._phase_id          = phase_id
        self._molecular_formula = molecular_formula

fluids = []
fluids.append( Fluid( sd.F_MIXTURE,                   "mixture",                   sd.PH_MULTIPHASE,       ) )
fluids.append( Fluid( sd.F_GASEOUS_AIR,               "gaseous air",               sd.PH_MULTIPHASE,       ) )
fluids.append( Fluid( sd.F_LIQUID_AIR,                "liquid air",                sd.PH_MULTIPHASE,       ) )
fluids.append( Fluid( sd.F_GASEOUS_ARGON,             "gaseous argon",             sd.PH_GAS,        "Ar"  ) )
fluids.append( Fluid( sd.F_GASEOUS_CARBON_DIOXIDE,    "gaseous carbon dioxide",    sd.PH_GAS,        "CO2" ) )
fluids.append( Fluid( sd.F_GASEOUS_DIATOMIC_HYDROGEN, "gaseous diatomic hydrogen", sd.PH_GAS,        "H2"  ) )
fluids.append( Fluid( sd.F_GASEOUS_DIATOMIC_NITROGEN, "gaseous diatomic nitrogen", sd.PH_GAS,        "N2"  ) )
fluids.append( Fluid( sd.F_GASEOUS_DIATOMIC_OXYGEN,   "gaseous diatomic oxygen",   sd.PH_GAS,        "O2"  ) )
fluids.append( Fluid( sd.F_GASEOUS_HELIUM,            "gaseous helium",            sd.PH_GAS,        "He"  ) )
fluids.append( Fluid( sd.F_GASEOUS_KRYPTON,           "gaseous krypton",           sd.PH_GAS,        "Kr"  ) )
fluids.append( Fluid( sd.F_GASEOUS_METHANE,           "gaseous methane",           sd.PH_GAS,        "CH4" ) )
fluids.append( Fluid( sd.F_GASEOUS_NEON,              "gaseous neon",              sd.PH_GAS,        "Ne"  ) )
fluids.append( Fluid( sd.F_GASEOUS_NITROGEN_DIOXIDE,  "gaseous nitrogen dioxide",  sd.PH_GAS,        "NO2" ) )
fluids.append( Fluid( sd.F_GASEOUS_NITROUS_OXIDE,     "gaseous nitrous oxide",     sd.PH_GAS,        "N2O" ) )
fluids.append( Fluid( sd.F_GASEOUS_OZONE,             "gaseous ozone",             sd.PH_GAS,        "O3"  ) )
fluids.append( Fluid( sd.F_GASEOUS_WATER,             "gaseous water",             sd.PH_GAS,        "H2O" ) )
fluids.append( Fluid( sd.F_GASEOUS_XENON,             "gaseous xenon",             sd.PH_GAS,        "Xe"  ) )
fluids.append( Fluid( sd.F_LIQUID_WATER,              "liquid water",              sd.PH_LIQUID,     "H2O" ) )

for fluid in fluids:
    fluid.execute_query()

# Geometries
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

# Instrument classes
class InstrumentClass:
    _instrument_class_id        = None
    _instrument_class_name      = None
    _intrusive                  = None
    _instrument_class_parent_id = None

    def instrument_class_id( self ):
        return self._instrument_class_id

    def instrument_class_name( self ):
        return self._instrument_class_name

    def intrusive( self ):
        return self._intrusive

    def instrument_class_parent_id( self ):
        return self._instrument_class_parent_id

    def is_child( self ):
        return self.instrument_class_parent_id() != None

    def execute_query( self ):
        cursor.execute(
        """
        INSERT INTO instrument_classes( instrument_class_id, instrument_class_name, intrusive )
        VALUES( ?, ?, ? );
        """,
        (
            self.instrument_class_id(),
            self.instrument_class_name(),
            self.intrusive(),
        )
        )

    def __init__( self, instrument_class_id, instrument_class_name, instrument_class_parent_id, intrusive=False, ):
        self._instrument_class_id        = instrument_class_id
        self._instrument_class_name      = str(instrument_class_name)
        self._instrument_class_parent_id = instrument_class_parent_id
        self._intrusive                  = 1 if intrusive else 0

instrument_classes = []
instrument_classes.append( InstrumentClass( sd.IT_APPROXIMATION,                            "approximation",                            sd.IT_REASONING,                                    ) )
instrument_classes.append( InstrumentClass( sd.IT_ASSUMPTION,                               "assumption",                               sd.IT_REASONING,                                    ) )
instrument_classes.append( InstrumentClass( sd.IT_CALCULATION,                              "calculation",                              sd.IT_REASONING,                                    ) )
instrument_classes.append( InstrumentClass( sd.IT_CLAIM,                                    "claim",                                    sd.IT_REASONING,                                    ) )
instrument_classes.append( InstrumentClass( sd.IT_CLAUSER_METHOD,                           "Clauser method",                           sd.IT_VELOCITY_PROFILE_METHOD,                      ) )
instrument_classes.append( InstrumentClass( sd.IT_CONSTANT_CURRENT_HOT_WIRE_ANEMOMETER,     "constant-current hot-wire anemometer",     sd.IT_HOT_WIRE_ANEMOMETER,          intrusive=True, ) )
instrument_classes.append( InstrumentClass( sd.IT_CONSTANT_TEMPERATURE_HOT_WIRE_ANEMOMETER, "constant-temperature hot-wire anemometer", sd.IT_HOT_WIRE_ANEMOMETER,          intrusive=True, ) )
instrument_classes.append( InstrumentClass( sd.IT_DIFFERENTIAL_PRESSURE_METHOD,             "differential pressure method",             sd.IT_OBSERVATION,                                  ) )
instrument_classes.append( InstrumentClass( sd.IT_DIRECT_INJECTION_METHOD,                  "direct injection method",                  sd.IT_OPTICAL_SYSTEM,                               ) )
instrument_classes.append( InstrumentClass( sd.IT_FLOATING_ELEMENT_BALANCE,                 "floating element balance",                 sd.IT_WALL_SHEAR_STRESS_METHOD,                     ) )
instrument_classes.append( InstrumentClass( sd.IT_FLOWMETER,                                "flowmeter",                                sd.IT_OBSERVATION,                                  ) )
instrument_classes.append( InstrumentClass( sd.IT_HOT_WIRE_ANEMOMETER,                      "hot-wire anemometer",                      sd.IT_THERMAL_ANEMOMETER,           intrusive=True, ) )
instrument_classes.append( InstrumentClass( sd.IT_IMPACT_TUBE,                              "impact tube",                              sd.IT_DIFFERENTIAL_PRESSURE_METHOD, intrusive=True, ) )
instrument_classes.append( InstrumentClass( sd.IT_INDEX_OF_REFRACTION_METHOD,               "index-of-refraction method",               sd.IT_OPTICAL_SYSTEM,                               ) )
instrument_classes.append( InstrumentClass( sd.IT_LASER_DOPPLER_ANEMOMETER,                 "laser Doppler anemometer",                 sd.IT_OPTICAL_SYSTEM,                               ) )
instrument_classes.append( InstrumentClass( sd.IT_MACH_ZEHNDER_INTERFEROMETER,              "Mach-Zehnder interferometer",              sd.IT_INDEX_OF_REFRACTION_METHOD,                   ) )
instrument_classes.append( InstrumentClass( sd.IT_MOMENTUM_BALANCE,                         "momentum balance",                         sd.IT_WALL_SHEAR_STRESS_METHOD,                     ) )
instrument_classes.append( InstrumentClass( sd.IT_OBSERVATION,                              "observation",                              sd.IT_ROOT,                                         ) )
instrument_classes.append( InstrumentClass( sd.IT_OPTICAL_SYSTEM,                           "optical system",                           sd.IT_OBSERVATION,                                  ) )
instrument_classes.append( InstrumentClass( sd.IT_PARTICLE_IMAGE_VELOCIMETER,               "particle image velocimeter",               sd.IT_OPTICAL_SYSTEM,                               ) )
instrument_classes.append( InstrumentClass( sd.IT_PITOT_STATIC_TUBE,                        "Pitot-static tube",                        sd.IT_DIFFERENTIAL_PRESSURE_METHOD, intrusive=True, ) )
instrument_classes.append( InstrumentClass( sd.IT_PRESTON_TUBE,                             "Preston tube",                             sd.IT_WALL_SHEAR_STRESS_METHOD,     intrusive=True, ) )
instrument_classes.append( InstrumentClass( sd.IT_REASONING,                                "reasoning",                                sd.IT_ROOT,                                         ) )
instrument_classes.append( InstrumentClass( sd.IT_ROOT,                                     "knowledge source",                         None,                                               ) )
instrument_classes.append( InstrumentClass( sd.IT_SCHLIEREN_SYSTEM,                         "schlieren system",                         sd.IT_INDEX_OF_REFRACTION_METHOD,                   ) )
instrument_classes.append( InstrumentClass( sd.IT_SHADOWGRAPH_SYSTEM,                       "shadowgraph system",                       sd.IT_INDEX_OF_REFRACTION_METHOD,                   ) )
instrument_classes.append( InstrumentClass( sd.IT_SIMULATION,                               "simulation",                               sd.IT_REASONING,                                    ) )
instrument_classes.append( InstrumentClass( sd.IT_STANTON_TUBE,                             "Stanton tube",                             sd.IT_WALL_SHEAR_STRESS_METHOD,     intrusive=True, ) )
instrument_classes.append( InstrumentClass( sd.IT_THERMAL_ANEMOMETER,                       "thermal anemometer",                       sd.IT_OBSERVATION,                                  ) )
instrument_classes.append( InstrumentClass( sd.IT_VELOCITY_PROFILE_METHOD,                  "velocity profile method",                  sd.IT_WALL_SHEAR_STRESS_METHOD,                     ) )
instrument_classes.append( InstrumentClass( sd.IT_VISCOUS_SUBLAYER_SLOPE_METHOD,            "viscous sublayer slope method",            sd.IT_VELOCITY_PROFILE_METHOD,                      ) )
instrument_classes.append( InstrumentClass( sd.IT_WALL_SHEAR_STRESS_METHOD,                 "wall shear stress method",                 sd.IT_OBSERVATION,                                  ) )
instrument_classes.append( InstrumentClass( sd.IT_WEIGHING_METHOD,                          "weighing method",                          sd.IT_FLOWMETER,                                    ) )

for instrument_class in instrument_classes:
    instrument_class.execute_query()

# Two separate loops MUST occur due to foreign key constraints.
for instrument_class in instrument_classes:
    if ( instrument_class.is_child() ):
        cursor.execute(
        """
        UPDATE instrument_classes
        SET instrument_class_parent_id=?
        WHERE instrument_class_id=?;
        """,
        (
            instrument_class.instrument_class_parent_id(),
            instrument_class.instrument_class_id(),
        )
        )

# Point labels
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
class Quantity:
    _quantity_id          = None
    _quantity_name        = None
    _time_exponent        = None
    _length_exponent      = None
    _mass_exponent        = None
    _current_exponent     = None
    _temperature_exponent = None
    _amount_exponent      = None
    _minimum_value        = None
    _maximum_value        = None

    def quantity_id( self ):
        return self._quantity_id

    def quantity_name( self ):
        return self._quantity_name

    def time_exponent( self ):
        return self._time_exponent

    def length_exponent( self ):
        return self._length_exponent

    def mass_exponent( self ):
        return self._mass_exponent

    def current_exponent( self ):
        return self._current_exponent

    def temperature_exponent( self ):
        return self._temperature_exponent

    def amount_exponent( self ):
        return self._amount_exponent

    def minimum_value( self ):
        return self._minimum_value

    def maximum_value( self ):
        return self._maximum_value

    def execute_query( self ):
        cursor.execute(
        """
        INSERT INTO quantities( quantity_id, quantity_name,
                                time_exponent, length_exponent, mass_exponent,
                                current_exponent, temperature_exponent,
                                amount_exponent, minimum_value, maximum_value )
        VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ? );
        """,
        (
            self.quantity_id(),
            self.quantity_name(),
            self.time_exponent(),
            self.length_exponent(),
            self.mass_exponent(),
            self.current_exponent(),
            self.temperature_exponent(),
            self.amount_exponent(),
            self.minimum_value(),
            self.maximum_value(),
        )
        )

    def __init__( self, quantity_id, quantity_name,
                  time_exponent=0.0,
                  length_exponent=0.0,
                  mass_exponent=0.0,
                  current_exponent=0.0,
                  temperature_exponent=0.0,
                  amount_exponent=0.0,
                  minimum_value=float("-inf"),
                  maximum_value=float("+inf"), ):
        self._quantity_id          = str(quantity_id)
        self._quantity_name        = str(quantity_name)
        self._time_exponent        = time_exponent
        self._length_exponent      = length_exponent
        self._mass_exponent        = mass_exponent
        self._current_exponent     = current_exponent
        self._temperature_exponent = temperature_exponent
        self._amount_exponent      = amount_exponent
        self._minimum_value        = minimum_value
        self._maximum_value        = maximum_value

quantities = []

# Quantities, series
quantities.append( Quantity( sd.Q_ANGLE_OF_ATTACK,                "angle of attack",                                                                                                                                 ) )
quantities.append( Quantity( sd.Q_BODY_REYNOLDS_NUMBER,           "body Reynolds number",                                                                                                         minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_BODY_STROUHAL_NUMBER,           "body Strouhal number",                                                                                                         minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_DRAG_COEFFICIENT,               "drag coefficient",                                                                                                                                ) )
quantities.append( Quantity( sd.Q_DRAG_FORCE,                     "drag force",                          time_exponent=-2.0, length_exponent=+1.0, mass_exponent=+1.0,                                               ) )
quantities.append( Quantity( sd.Q_FREESTREAM_MACH_NUMBER,         "freestream Mach number",                                                                                                       minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_FREESTREAM_SPEED_OF_SOUND,      "freestream speed of sound",           time_exponent=-1.0, length_exponent=+1.0,                                                minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_FREESTREAM_TEMPERATURE,         "freestream temperature",                                                                            temperature_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_FREESTREAM_VELOCITY,            "freestream velocity",                 time_exponent=-1.0, length_exponent=+1.0,                                                                   ) )
quantities.append( Quantity( sd.Q_LIFT_COEFFICIENT,               "lift coefficient",                                                                                                                                ) )
quantities.append( Quantity( sd.Q_LIFT_FORCE,                     "lift force",                          time_exponent=-2.0, length_exponent=+1.0, mass_exponent=+1.0,                                               ) )
quantities.append( Quantity( sd.Q_LIFT_TO_DRAG_RATIO,             "lift-to-drag ratio",                                                                                                                              ) )
quantities.append( Quantity( sd.Q_MASS_FLOW_RATE,                 "mass flow rate",                      time_exponent=-1.0,                       mass_exponent=+1.0,                            minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_SPANWISE_NUMBER_OF_POINTS,      "spanwise number of points",                                                                                                    minimum_value=1.0, ) )
quantities.append( Quantity( sd.Q_STREAMWISE_NUMBER_OF_POINTS,    "streamwise number of points",                                                                                                  minimum_value=1.0, ) )
quantities.append( Quantity( sd.Q_TEST_LENGTH,                    "test length",                                             length_exponent=+1.0,                                                minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_TRANSVERSE_NUMBER_OF_POINTS,    "transverse number of points",                                                                                                  minimum_value=1.0, ) )
quantities.append( Quantity( sd.Q_VOLUMETRIC_FLOW_RATE,           "volumetric flow rate",                time_exponent=-1.0, length_exponent=+3.0,                                                minimum_value=0.0, ) )

# Quantities, station
quantities.append( Quantity( sd.Q_BULK_DYNAMIC_VISCOSITY,                 "bulk dynamic viscosity",                 time_exponent=-1.0, length_exponent=-1.0, mass_exponent=+1.0, minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_BULK_KINEMATIC_VISCOSITY,               "bulk kinematic viscosity",               time_exponent=-1.0, length_exponent=+2.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_BULK_MACH_NUMBER,                       "bulk Mach number",                                                                                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_BULK_MASS_DENSITY,                      "bulk mass density",                                          length_exponent=-3.0, mass_exponent=+1.0, minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_BULK_REYNOLDS_NUMBER,                   "bulk Reynolds number",                                                                                 minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_BULK_SPEED_OF_SOUND,                    "bulk speed of sound",                    time_exponent=-1.0, length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_BULK_VELOCITY,                          "bulk velocity",                          time_exponent=-1.0, length_exponent=+1.0,                                                           ) )
quantities.append( Quantity( sd.Q_CLAUSER_THICKNESS,                      "Clauser thickness",                                          length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_CROSS_SECTIONAL_AREA,                   "cross-sectional area",                                       length_exponent=+2.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_CROSS_SECTIONAL_ASPECT_RATIO,           "cross-sectional aspect ratio",                                                                         minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_CROSS_SECTIONAL_HALF_HEIGHT,            "cross-sectional half height",                                length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_CROSS_SECTIONAL_HEIGHT,                 "cross-sectional height",                                     length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_CROSS_SECTIONAL_WIDTH,                  "cross-sectional width",                                      length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_DEVELOPMENT_LENGTH,                     "development length",                                         length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_DISPLACEMENT_THICKNESS,                 "displacement thickness",                                     length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_DISPLACEMENT_THICKNESS_REYNOLDS_NUMBER, "displacement thickness Reynolds number",                                                               minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_ENERGY_THICKNESS,                       "energy thickness",                                           length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_EQUILIBRIUM_PARAMETER,                  "equilibrium parameter",                                                                                                                      ) )
quantities.append( Quantity( sd.Q_HYDRAULIC_DIAMETER,                     "hydraulic diameter",                                         length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_INNER_DIAMETER,                         "inner diameter",                                             length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_MOMENTUM_INTEGRAL_LHS,                  "momentum integral left-hand side",                                                                                                           ) )
quantities.append( Quantity( sd.Q_MOMENTUM_INTEGRAL_RHS,                  "momentum integral right-hand side",                                                                                                          ) )
quantities.append( Quantity( sd.Q_MOMENTUM_THICKNESS,                     "momentum thickness",                                         length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_MOMENTUM_THICKNESS_REYNOLDS_NUMBER,     "momentum thickness Reynolds number",                                                                   minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_OUTER_DIAMETER,                         "outer diameter",                                             length_exponent=+1.0,                     minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH,         "outer-layer development length",                                                                       minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_RECOVERY_FACTOR,                        "recovery factor",                                                                                      minimum_value=0.0, maximum_value=1.0, ) )
quantities.append( Quantity( sd.Q_SHAPE_FACTOR_1_TO_2,                    "shape factor 1-to-2",                                                                                  minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_SHAPE_FACTOR_3_TO_2,                    "shape factor 3-to-2",                                                                                  minimum_value=0.0,                    ) )
quantities.append( Quantity( sd.Q_SPANWISE_PRESSURE_GRADIENT,             "spanwise pressure gradient",             time_exponent=-2.0, length_exponent=-2.0, mass_exponent=+1.0,                                       ) )
quantities.append( Quantity( sd.Q_STREAMWISE_COORDINATE_REYNOLDS_NUMBER,  "streamwise coordinate Reynolds number",                                                                                                      ) )
quantities.append( Quantity( sd.Q_STREAMWISE_PRESSURE_GRADIENT,           "streamwise pressure gradient",           time_exponent=-2.0, length_exponent=-2.0, mass_exponent=+1.0,                                       ) )
quantities.append( Quantity( sd.Q_TRANSVERSE_PRESSURE_GRADIENT,           "transverse pressure gradient",           time_exponent=-2.0, length_exponent=-2.0, mass_exponent=+1.0,                                       ) )
quantities.append( Quantity( sd.Q_WETTED_PERIMETER,                       "wetted perimeter",                                           length_exponent=+2.0,                     minimum_value=0.0,                    ) )

# Quantities, wall point
#
# Note that some of these quantities, like the friction velocity and viscous
# length scale, can also be defined as point variable (away from the wall)
# using local variables.  But for both, the shear stress at the wall remains.
# For that reason I leave these variables here, even though they can be defined
# as point variables too.
quantities.append( Quantity( sd.Q_AVERAGE_SKIN_FRICTION_COEFFICIENT,    "average skin friction coefficient",                                                                        minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_DARCY_FRICTION_FACTOR,                "Darcy friction factor",                                                                                    minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_FANNING_FRICTION_FACTOR,              "Fanning friction factor",                                                                                  minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_FRICTION_MACH_NUMBER,                 "friction Mach number",                                                                                     minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_FRICTION_REYNOLDS_NUMBER,             "friction Reynolds number",                                                                                 minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_FRICTION_TEMPERATURE,                 "friction temperature",                                                          temperature_exponent=+1.0,                    ) )
quantities.append( Quantity( sd.Q_FRICTION_VELOCITY,                    "friction velocity",                   time_exponent=-1.0, length_exponent=+1.0,                            minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_HEAT_TRANSFER_COEFFICIENT,            "heat transfer coefficient",                                                                                                   ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_HEAT_FLUX,                "inner-layer heat flux",                                                                                                       ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,         "inner-layer roughness height",                                                                             minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_SKIN_FRICTION_COEFFICIENT,      "local skin friction coefficient",                                                                          minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT,         "outer-layer roughness height",                                                                             minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_PRESSURE_COEFFICIENT,                 "pressure coefficient",                                                                                                        ) )
quantities.append( Quantity( sd.Q_ROUGHNESS_HEIGHT,                     "roughness height",                                        length_exponent=+1.0,                            minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER,  "semi-local friction Reynolds number",                                                                      minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_SPANWISE_WALL_CURVATURE,              "spanwise wall curvature",                                 length_exponent=-1.0,                            minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_STREAMWISE_WALL_CURVATURE,            "streamwise wall curvature",                               length_exponent=-1.0,                            minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_VISCOUS_LENGTH_SCALE,                 "viscous length scale",                                    length_exponent=+1.0,                            minimum_value=0.0, ) )

# Quantities, point
quantities.append( Quantity( sd.Q_AMOUNT_DENSITY,                                     "amount density",                                                           length_exponent=-3.0,                     amount_exponent=+1.0,                            minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_AMOUNT_FRACTION,                                    "amount fraction",                                                                                                                                                     minimum_value=0.0, maximum_value=1.0,     ) )
quantities.append( Quantity( sd.Q_DILATATION_RATE,                                    "dilatation rate",                                      time_exponent=-1.0,                                                                                                                                      ) )
quantities.append( Quantity( sd.Q_DISTANCE_FROM_WALL,                                 "distance from wall",                                                       length_exponent=+1.0,                                                                      minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_DYNAMIC_VISCOSITY,                                  "dynamic viscosity",                                    time_exponent=-1.0, length_exponent=-1.0, mass_exponent=+1.0,                                                  minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_HEAT_CAPACITY_RATIO,                                "gamma",                                                                                                                                                               minimum_value=1.0, maximum_value=5.0/3.0, ) )
quantities.append( Quantity( sd.Q_HEAT_FLUX,                                          "heat flux",                                            time_exponent=-3.0,                       mass_exponent=+1.0,                                                                                            ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_COORDINATE,                             "inner-layer coordinate",                                                                                                                                              minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_TEMPERATURE,                            "inner-layer temperature",                                                                                                                                                                                       ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_VELOCITY,                               "inner-layer velocity",                                                                                                                                                minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_VELOCITY_DEFECT,                        "inner-layer velocity defect",                                                                                                                                                                                   ) )
quantities.append( Quantity( sd.Q_KINEMATIC_VISCOSITY,                                "kinematic viscosity",                                  time_exponent=-1.0, length_exponent=+2.0,                                                                      minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_MACH_NUMBER,                                        "Mach number",                                                                                                                                                         minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_MASS_DENSITY,                                       "mass density",                                                             length_exponent=-3.0, mass_exponent=+1.0,                                                  minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_MASS_FRACTION,                                      "mass fraction",                                                                                                                                                       minimum_value=0.0, maximum_value=1.0,     ) )
quantities.append( Quantity( sd.Q_OUTER_LAYER_COORDINATE,                             "outer-layer coordinate",                                                                                                                                              minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_OUTER_LAYER_TEMPERATURE,                            "outer-layer temperature",                                                                                                                                                                                       ) )
quantities.append( Quantity( sd.Q_OUTER_LAYER_VELOCITY,                               "outer-layer velocity",                                                                                                                                                minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_OUTER_LAYER_VELOCITY_DEFECT,                        "outer-layer velocity defect",                                                                                                                                                                                   ) )
quantities.append( Quantity( sd.Q_PRANDTL_NUMBER,                                     "Prandtl number",                                                                                                                                                      minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_PRESSURE,                                           "pressure",                                             time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                                                  minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_SEMI_LOCAL_COORDINATE,                              "semi-local inner-layer coordinate",                                                                                                                                   minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_SPANWISE_COORDINATE,                                "spanwise coordinate",                                                      length_exponent=+1.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_SPANWISE_VELOCITY,                                  "spanwise velocity",                                    time_exponent=-1.0, length_exponent=+1.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_SPECIFIC_ENTHALPY,                                  "specific enthalpy",                                    time_exponent=-2.0, length_exponent=+2.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_SPECIFIC_GAS_CONSTANT,                              "specific gas constant",                                time_exponent=-2.0, length_exponent=+2.0,                                           temperature_exponent=-1.0, minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_SPECIFIC_INTERNAL_ENERGY,                           "specific internal energy",                             time_exponent=-2.0, length_exponent=+2.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_SPECIFIC_ISOBARIC_HEAT_CAPACITY,                    "specific isobaric heat capacity",                      time_exponent=-2.0, length_exponent=+2.0,                                           temperature_exponent=-1.0,                                           ) )
quantities.append( Quantity( sd.Q_SPECIFIC_ISOCHORIC_HEAT_CAPACITY,                   "specific isochoric heat capacity",                     time_exponent=-2.0, length_exponent=+2.0,                                           temperature_exponent=-1.0,                                           ) )
quantities.append( Quantity( sd.Q_SPECIFIC_TOTAL_ENTHALPY,                            "specific total enthalpy",                              time_exponent=-2.0, length_exponent=+2.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_SPECIFIC_TOTAL_INTERNAL_ENERGY,                     "specific total internal energy",                       time_exponent=-2.0, length_exponent=+2.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_SPECIFIC_VOLUME,                                    "specific volume",                                                          length_exponent=+3.0, mass_exponent=-1.0,                                                  minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_SPEED,                                              "speed",                                                time_exponent=-1.0, length_exponent=+1.0,                                                                      minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_SPEED_OF_SOUND,                                     "speed of sound",                                       time_exponent=-1.0, length_exponent=+1.0,                                                                      minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_STREAMWISE_COORDINATE,                              "streamwise coordinate",                                                    length_exponent=+1.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_STREAMWISE_VELOCITY,                                "streamwise velocity",                                  time_exponent=-1.0, length_exponent=+1.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_STRESS[sd.D_STREAMWISE,sd.D_STREAMWISE],                      "streamwise normal stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                                                                                            ) )
quantities.append( Quantity( sd.Q_STRESS[sd.D_STREAMWISE,sd.D_TRANSVERSE],            "streamwise-transverse shear stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                                                                                            ) )
quantities.append( Quantity( sd.Q_STRESS[sd.D_STREAMWISE,sd.D_SPANWISE  ],              "streamwise-spanwise shear stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                                                                                            ) )
quantities.append( Quantity( sd.Q_STRESS[sd.D_TRANSVERSE,sd.D_TRANSVERSE],                      "transverse normal stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                                                                                            ) )
quantities.append( Quantity( sd.Q_STRESS[sd.D_TRANSVERSE,sd.D_SPANWISE  ],              "transverse-spanwise shear stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                                                                                            ) )
quantities.append( Quantity( sd.Q_STRESS[sd.D_SPANWISE,  sd.D_SPANWISE  ],                        "spanwise normal stress",                   time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                                                                                            ) )
quantities.append( Quantity( sd.Q_TEMPERATURE,                                        "temperature",                                                                                                                              temperature_exponent=+1.0, minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_THERMAL_CONDUCTIVITY,                               "thermal conductivity",                                 time_exponent=-3.0, length_exponent=+1.0, mass_exponent=+1.0,                       temperature_exponent=-1.0, minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_THERMAL_DIFFUSIVITY,                                "thermal diffusivity",                                  time_exponent=-1.0, length_exponent=+2.0,                                                                      minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_TOTAL_PRESSURE,                                     "total pressure",                                       time_exponent=-2.0, length_exponent=-1.0, mass_exponent=+1.0,                                                  minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_TOTAL_TEMPERATURE,                                  "total temperature",                                                                                                                        temperature_exponent=+1.0, minimum_value=0.0,                        ) )
quantities.append( Quantity( sd.Q_TRANSVERSE_COORDINATE,                              "transverse coordinate",                                                    length_exponent=+1.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_TRANSVERSE_VELOCITY,                                "transverse velocity",                                  time_exponent=-1.0, length_exponent=+1.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_VELOCITY_DEFECT,                                    "velocity defect",                                      time_exponent=-1.0, length_exponent=+1.0,                                                                                                                ) )
quantities.append( Quantity( sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_STREAMWISE], "streamwise velocity gradient in streamwise direction", time_exponent=-1.0,                                                                                                                                      ) )
quantities.append( Quantity( sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_TRANSVERSE], "streamwise velocity gradient in transverse direction", time_exponent=-1.0,                                                                                                                                      ) )
quantities.append( Quantity( sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_SPANWISE  ], "streamwise velocity gradient in spanwise direction",   time_exponent=-1.0,                                                                                                                                      ) )
quantities.append( Quantity( sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_STREAMWISE], "transverse velocity gradient in streamwise direction", time_exponent=-1.0,                                                                                                                                      ) )
quantities.append( Quantity( sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_TRANSVERSE], "transverse velocity gradient in transverse direction", time_exponent=-1.0,                                                                                                                                      ) )
quantities.append( Quantity( sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_SPANWISE  ], "transverse velocity gradient in spanwise direction",   time_exponent=-1.0,                                                                                                                                      ) )
quantities.append( Quantity( sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_STREAMWISE],   "spanwise velocity gradient in streamwise direction", time_exponent=-1.0,                                                                                                                                      ) )
quantities.append( Quantity( sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_TRANSVERSE],   "spanwise velocity gradient in transverse direction", time_exponent=-1.0,                                                                                                                                      ) )
quantities.append( Quantity( sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_SPANWISE  ],   "spanwise velocity gradient in spanwise direction",   time_exponent=-1.0,                                                                                                                                      ) )

# Quantities, point, turbulence
quantities.append( Quantity( sd.Q_MASS_DENSITY_AUTOCOVARIANCE,                       "mass density autocovariance",                                  length_exponent=-6.0, mass_exponent=+2.0,                            minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_NORMALIZED_MASS_DENSITY_AUTOCOVARIANCE,            "normalized mass density autocovariance",                                                                                            minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_NORMALIZED_PRESSURE_AUTOCOVARIANCE,                "normalized pressure autocovariance",                                                                                                minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_NORMALIZED_TEMPERATURE_AUTOCOVARIANCE,             "normalized temperature autocovariance",                                                                                             minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_PRESSURE_AUTOCOVARIANCE,                           "pressure autocovariance",                  time_exponent=-4.0, length_exponent=-2.0, mass_exponent=+2.0,                            minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_SPECIFIC_TURBULENT_KINETIC_ENERGY,     "inner-layer turbulent kinetic energy",                                                                                              minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_MORKOVIN_SCALED_SPECIFIC_TURBULENT_KINETIC_ENERGY, "Morkovin-scaled turbulent kinetic energy",                                                                                          minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_SPECIFIC_TURBULENT_KINETIC_ENERGY,                 "specific turbulent kinetic energy",        time_exponent=-2.0, length_exponent=+2.0,                                                minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_TEMPERATURE_AUTOCOVARIANCE,                        "temperature autocovariance",                                                                             temperature_exponent=+2.0, minimum_value=0.0, ) )

quantities.append( Quantity( sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE],              "streamwise velocity autocovariance", time_exponent=-2.0, length_exponent=+2.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE], "streamwise-transverse velocity cross covariance", time_exponent=-2.0, length_exponent=+2.0,                    ) )
quantities.append( Quantity( sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ],   "streamwise-spanwise velocity cross covariance", time_exponent=-2.0, length_exponent=+2.0,                    ) )
quantities.append( Quantity( sd.Q_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE],              "transverse velocity autocovariance", time_exponent=-2.0, length_exponent=+2.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ],   "transverse-spanwise velocity cross covariance", time_exponent=-2.0, length_exponent=+2.0,                    ) )
quantities.append( Quantity( sd.Q_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ],                "spanwise velocity autocovariance", time_exponent=-2.0, length_exponent=+2.0, minimum_value=0.0, ) )

quantities.append( Quantity( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE],              "inner-layer streamwise velocity autocovariance", minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE], "inner-layer streamwise-transverse velocity cross covariance",                    ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ],   "inner-layer streamwise-spanwise velocity cross covariance",                    ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE],              "inner-layer transverse velocity autocovariance", minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ],   "inner-layer transverse-spanwise velocity cross covariance",                    ) )
quantities.append( Quantity( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ],                "inner-layer spanwise velocity autocovariance", minimum_value=0.0, ) )

quantities.append( Quantity( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE],              "Morkovin-scaled streamwise velocity autocovariance", minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE], "Morkovin-scaled streamwise-transverse velocity cross covariance",                    ) )
quantities.append( Quantity( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ],   "Morkovin-scaled streamwise-spanwise velocity cross covariance",                    ) )
quantities.append( Quantity( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE],              "Morkovin-scaled transverse velocity autocovariance", minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ],   "Morkovin-scaled transverse-spanwise velocity cross covariance",                    ) )
quantities.append( Quantity( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ],                "Morkovin-scaled spanwise velocity autocovariance", minimum_value=0.0, ) )

# Quantities, point, ratios
quantities.append( Quantity( sd.Q_LOCAL_TO_BULK_STREAMWISE_VELOCITY_RATIO,        "local-to-bulk streamwise velocity ratio",        minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_BULK_TEMPERATURE_RATIO,                "local-to-bulk temperature ratio",                minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_CENTER_LINE_DYNAMIC_VISCOSITY_RATIO,   "local-to-center-line dynamic viscosity ratio",   minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_CENTER_LINE_MASS_DENSITY_RATIO,        "local-to-center-line density ratio",             minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_CENTER_LINE_STREAMWISE_VELOCITY_RATIO, "local-to-center-line streamwise velocity ratio", minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_CENTER_LINE_TEMPERATURE_RATIO,         "local-to-center-line temperature ratio",         minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_EDGE_DYNAMIC_VISCOSITY_RATIO,          "local-to-edge dynamic viscosity ratio",          minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_EDGE_MASS_DENSITY_RATIO,               "local-to-edge density ratio",                    minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_EDGE_STREAMWISE_VELOCITY_RATIO,        "local-to-edge streamwise velocity ratio",        minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_EDGE_TEMPERATURE_RATIO,                "local-to-edge temperature ratio",                minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_RECOVERY_TEMPERATURE_RATIO,            "local-to-recovery temperature ratio",            minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_WALL_DYNAMIC_VISCOSITY_RATIO,          "local-to-wall dynamic viscosity ratio",          minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_WALL_MASS_DENSITY_RATIO,               "local-to-wall density ratio",                    minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_WALL_STREAMWISE_VELOCITY_RATIO,        "local-to-wall streamwise velocity ratio",        minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LOCAL_TO_WALL_TEMPERATURE_RATIO,                "local-to-wall temperature ratio",                minimum_value=0.0, ) )

# Quantities, facility
# - Mach number range (use point quantity)
# - Reynolds number range (TODO)
# - static and stagnation temperature ranges (TODO)
# - static and stagnation pressure ranges (TODO)
#
# Note that I may add a separate table for facility components that then
# specifies the order of the different components (and whether they form a
# closed loop).  The test-section dimensions would then be better defined in
# that context to prevent duplication, but for the moment these are here.
quantities.append( Quantity( sd.Q_RUN_TIME,                   "run time",                     time_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_SPATIAL_ORDER_OF_ACCURACY,  "spatial order of accuracy",                        minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_TEMPORAL_ORDER_OF_ACCURACY, "temporal order of accuracy",                       minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_TEST_SECTION_HEIGHT,        "test-section height",        length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_TEST_SECTION_LENGTH,        "test-section length",        length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_TEST_SECTION_WIDTH,         "test-section width",         length_exponent=+1.0, minimum_value=0.0, ) )

# Quantities, instrument
#
# TODO: Come up with more, or just create them as needed incrementally.
quantities.append( Quantity( sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS, "distance between pressure taps", length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_ORDER_OF_APPROXIMATION,         "order of approximation",                               minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_PROBE_INNER_DIAMETER,           "probe inner diameter",           length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_PROBE_OUTER_DIAMETER,           "probe outer diameter",           length_exponent=+1.0, minimum_value=0.0, ) )

# Quantities, model
quantities.append( Quantity( sd.Q_BODY_HEIGHT,                    "body height",                 length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_BODY_LENGTH,                    "body length",                 length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_BODY_PROJECTED_FRONTAL_AREA,    "body projected frontal area", length_exponent=+2.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_BODY_VOLUME,                    "body volume",                 length_exponent=+3.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_BODY_WETTED_SURFACE_AREA,       "body wetted surface area",    length_exponent=+2.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_BODY_WIDTH,                     "body width",                  length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_CHORD_LENGTH,                   "chord length",                length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LEADING_EDGE_LENGTH,            "leading edge length",         length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_LEADING_EDGE_RADIUS,            "leading edge radius",         length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_TRAILING_EDGE_LENGTH,           "trailing edge length",        length_exponent=+1.0, minimum_value=0.0, ) )
quantities.append( Quantity( sd.Q_TRAILING_EDGE_RADIUS,           "trailing edge radius",        length_exponent=+1.0, minimum_value=0.0, ) )

for quantity in quantities:
    quantity.execute_query()


# Latex codes for quantities
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

# Quantities, series
define_quantity_symbol( sd.Q_ANGLE_OF_ATTACK,                sd.VT_UNAVERAGED_VALUE, r"\alpha",                                            )
define_quantity_symbol( sd.Q_BODY_HEIGHT,                    sd.VT_UNAVERAGED_VALUE, r"h_b",                                               )
define_quantity_symbol( sd.Q_BODY_LENGTH,                    sd.VT_UNAVERAGED_VALUE, r"\ell_b",                                            )
define_quantity_symbol( sd.Q_BODY_PROJECTED_FRONTAL_AREA,    sd.VT_UNAVERAGED_VALUE, r"A_f",                                               )
define_quantity_symbol( sd.Q_BODY_REYNOLDS_NUMBER,           sd.VT_UNAVERAGED_VALUE, r"\mathrm{Re}_\infty",                                )
define_quantity_symbol( sd.Q_BODY_STROUHAL_NUMBER,           sd.VT_UNAVERAGED_VALUE, r"\mathrm{Sr}_b",                                     )
define_quantity_symbol( sd.Q_BODY_VOLUME,                    sd.VT_UNAVERAGED_VALUE, r"V_b",                                               )
define_quantity_symbol( sd.Q_BODY_WETTED_SURFACE_AREA,       sd.VT_UNAVERAGED_VALUE, r"A_s",                                               )
define_quantity_symbol( sd.Q_BODY_WIDTH,                     sd.VT_UNAVERAGED_VALUE, r"w_b",                                               )
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

# Quantities, station
define_quantity_symbol( sd.Q_BULK_DYNAMIC_VISCOSITY,                 sd.VT_UNAVERAGED_VALUE, r"\mu_b",                                                                       )
define_quantity_symbol( sd.Q_BULK_KINEMATIC_VISCOSITY,               sd.VT_UNAVERAGED_VALUE, r"\nu_b",                                                                       )
define_quantity_symbol( sd.Q_BULK_MACH_NUMBER,                       sd.VT_UNAVERAGED_VALUE, r"\mathrm{Ma}_b",                                                               )
define_quantity_symbol( sd.Q_BULK_MASS_DENSITY,                      sd.VT_UNAVERAGED_VALUE, r"\rho_b",                                                                      )
define_quantity_symbol( sd.Q_BULK_REYNOLDS_NUMBER,                   sd.VT_UNAVERAGED_VALUE, r"\mathrm{Re}_b",                                                               )
define_quantity_symbol( sd.Q_BULK_SPEED_OF_SOUND,                    sd.VT_UNAVERAGED_VALUE, r"a_b",                                                                         )
define_quantity_symbol( sd.Q_BULK_VELOCITY,                          sd.VT_UNAVERAGED_VALUE, r"{:s}_b".format(sd.STREAMWISE_VELOCITY_SYMBOL),                                )
define_quantity_symbol( sd.Q_CLAUSER_THICKNESS,                      sd.VT_UNAVERAGED_VALUE, r"\Delta_C",                                                                    )
define_quantity_symbol( sd.Q_CROSS_SECTIONAL_AREA,                   sd.VT_UNAVERAGED_VALUE, r"A_\mathrm{cs}",                                                               )
define_quantity_symbol( sd.Q_CROSS_SECTIONAL_ASPECT_RATIO,           sd.VT_UNAVERAGED_VALUE, r"\mathrm{AR}_\mathrm{cs}",                                                     )
define_quantity_symbol( sd.Q_CROSS_SECTIONAL_HALF_HEIGHT,            sd.VT_UNAVERAGED_VALUE, r"b_\mathrm{cs}",                                                               )
define_quantity_symbol( sd.Q_CROSS_SECTIONAL_HEIGHT,                 sd.VT_UNAVERAGED_VALUE, r"h_\mathrm{cs}",                                                               )
define_quantity_symbol( sd.Q_CROSS_SECTIONAL_WIDTH,                  sd.VT_UNAVERAGED_VALUE, r"w_\mathrm{cs}",                                                               )
define_quantity_symbol( sd.Q_DEVELOPMENT_LENGTH,                     sd.VT_UNAVERAGED_VALUE, r"\ell_d",                                                                      )
define_quantity_symbol( sd.Q_DISPLACEMENT_THICKNESS,                 sd.VT_UNAVERAGED_VALUE, r"\delta_1",                                                                    )
define_quantity_symbol( sd.Q_DISPLACEMENT_THICKNESS_REYNOLDS_NUMBER, sd.VT_UNAVERAGED_VALUE, r"\mathrm{Re}_{\delta_1}",                                                      )
define_quantity_symbol( sd.Q_ENERGY_THICKNESS,                       sd.VT_UNAVERAGED_VALUE, r"\delta_3",                                                                    )
define_quantity_symbol( sd.Q_EQUILIBRIUM_PARAMETER,                  sd.VT_UNAVERAGED_VALUE, r"\Pi_2",                                                                       )
define_quantity_symbol( sd.Q_HYDRAULIC_DIAMETER,                     sd.VT_UNAVERAGED_VALUE, r"D_H",                                                                         )
define_quantity_symbol( sd.Q_INNER_DIAMETER,                         sd.VT_UNAVERAGED_VALUE, r"D_i",                                                                         )
define_quantity_symbol( sd.Q_MOMENTUM_INTEGRAL_LHS,                  sd.VT_UNAVERAGED_VALUE, r"P_l",                                                                         )
define_quantity_symbol( sd.Q_MOMENTUM_INTEGRAL_RHS,                  sd.VT_UNAVERAGED_VALUE, r"P_r",                                                                         )
define_quantity_symbol( sd.Q_MOMENTUM_THICKNESS,                     sd.VT_UNAVERAGED_VALUE, r"\delta_2",                                                                    )
define_quantity_symbol( sd.Q_MOMENTUM_THICKNESS_REYNOLDS_NUMBER,     sd.VT_UNAVERAGED_VALUE, r"\mathrm{Re}_{\delta_2}",                                                      )
define_quantity_symbol( sd.Q_OUTER_DIAMETER,                         sd.VT_UNAVERAGED_VALUE, r"D_o",                                                                         )
define_quantity_symbol( sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH,         sd.VT_UNAVERAGED_VALUE, r"(\ell_d/D_H)",                                                                )
define_quantity_symbol( sd.Q_RECOVERY_FACTOR,                        sd.VT_UNAVERAGED_VALUE, r"r",                                                                           )
define_quantity_symbol( sd.Q_SHAPE_FACTOR_1_TO_2,                    sd.VT_UNAVERAGED_VALUE, r"H_{12}",                                                                      )
define_quantity_symbol( sd.Q_SHAPE_FACTOR_3_TO_2,                    sd.VT_UNAVERAGED_VALUE, r"H_{23}",                                                                      )
define_quantity_symbol( sd.Q_SPANWISE_PRESSURE_GRADIENT,             sd.VT_UNAVERAGED_VALUE, r"(\mathrm{d} p / \mathrm{d} "+"{:s})".format(sd.SPANWISE_COORDINATE_SYMBOL),   )
define_quantity_symbol( sd.Q_STREAMWISE_COORDINATE_REYNOLDS_NUMBER,  sd.VT_UNAVERAGED_VALUE, r"\mathrm{Re}_"+"{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL),                 )
define_quantity_symbol( sd.Q_STREAMWISE_PRESSURE_GRADIENT,           sd.VT_UNAVERAGED_VALUE, r"(\mathrm{d} p / \mathrm{d} "+"{:s})".format(sd.STREAMWISE_COORDINATE_SYMBOL), )
define_quantity_symbol( sd.Q_TRANSVERSE_PRESSURE_GRADIENT,           sd.VT_UNAVERAGED_VALUE, r"(\mathrm{d} p / \mathrm{d} "+"{:s})".format(sd.TRANSVERSE_COORDINATE_SYMBOL), )
define_quantity_symbol( sd.Q_WETTED_PERIMETER,                       sd.VT_UNAVERAGED_VALUE, r"P",                                                                           )

# Quantities, wall point
define_quantity_symbol( sd.Q_AVERAGE_SKIN_FRICTION_COEFFICIENT,   sd.VT_UNAVERAGED_VALUE, r"C_f",                                                 )
define_quantity_symbol( sd.Q_DARCY_FRICTION_FACTOR,               sd.VT_UNAVERAGED_VALUE, r"f_D",                                                 )
define_quantity_symbol( sd.Q_FANNING_FRICTION_FACTOR,             sd.VT_UNAVERAGED_VALUE, r"f",                                                   )
define_quantity_symbol( sd.Q_FRICTION_MACH_NUMBER,                sd.VT_UNAVERAGED_VALUE, r"\mathrm{Ma}_\tau",                                    )
define_quantity_symbol( sd.Q_FRICTION_REYNOLDS_NUMBER,            sd.VT_UNAVERAGED_VALUE, r"\mathrm{Re}_\tau",                                    )
define_quantity_symbol( sd.Q_FRICTION_TEMPERATURE,                sd.VT_UNAVERAGED_VALUE, r"T_\tau",                                              )
define_quantity_symbol( sd.Q_FRICTION_VELOCITY,                   sd.VT_UNAVERAGED_VALUE, r"{:s}_\tau".format(sd.STREAMWISE_VELOCITY_SYMBOL),     )
define_quantity_symbol( sd.Q_HEAT_TRANSFER_COEFFICIENT,           sd.VT_UNAVERAGED_VALUE, r"c_q",                                                 )
define_quantity_symbol( sd.Q_INNER_LAYER_HEAT_FLUX,               sd.VT_UNAVERAGED_VALUE, r"B_q",                                                 )
define_quantity_symbol( sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,        sd.VT_UNAVERAGED_VALUE, r"\epsilon^+",                                          )
define_quantity_symbol( sd.Q_LOCAL_SKIN_FRICTION_COEFFICIENT,     sd.VT_UNAVERAGED_VALUE, r"c_f",                                                 )
define_quantity_symbol( sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT,        sd.VT_UNAVERAGED_VALUE, r"(\epsilon/D_H)",                                      )
define_quantity_symbol( sd.Q_PRESSURE_COEFFICIENT,                sd.VT_UNAVERAGED_VALUE, r"C_p",                                                 )
define_quantity_symbol( sd.Q_ROUGHNESS_HEIGHT,                    sd.VT_UNAVERAGED_VALUE, r"\epsilon",                                            )
define_quantity_symbol( sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER, sd.VT_UNAVERAGED_VALUE, r"\mathrm{Re}_\tau^*",                                  )
define_quantity_symbol( sd.Q_SPANWISE_WALL_CURVATURE,             sd.VT_UNAVERAGED_VALUE, r"\kappa_{:s}".format(sd.SPANWISE_COORDINATE_SYMBOL),   )
define_quantity_symbol( sd.Q_STREAMWISE_WALL_CURVATURE,           sd.VT_UNAVERAGED_VALUE, r"\kappa_{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL), )
define_quantity_symbol( sd.Q_VISCOUS_LENGTH_SCALE,                sd.VT_UNAVERAGED_VALUE, r"\ell_\nu",                                            )

# Quantities, point
define_quantity_symbol( sd.Q_DILATATION_RATE,                                    sd.VT_UNAVERAGED_VALUE, r"\Theta",                                              )
define_quantity_symbol( sd.Q_DISTANCE_FROM_WALL,                                 sd.VT_UNAVERAGED_VALUE, r"{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL),        )
define_quantity_symbol( sd.Q_DYNAMIC_VISCOSITY,                                  sd.VT_UNAVERAGED_VALUE, r"\mu",                                                 )
define_quantity_symbol( sd.Q_HEAT_CAPACITY_RATIO,                                sd.VT_UNAVERAGED_VALUE, r"\gamma",                                              )
define_quantity_symbol( sd.Q_HEAT_FLUX,                                          sd.VT_UNAVERAGED_VALUE, r"q",                                                   )
define_quantity_symbol( sd.Q_INNER_LAYER_COORDINATE,                             sd.VT_UNAVERAGED_VALUE, r"{:s}^+".format(sd.TRANSVERSE_COORDINATE_SYMBOL),      )
define_quantity_symbol( sd.Q_INNER_LAYER_TEMPERATURE,                            sd.VT_UNAVERAGED_VALUE, r"T^+",                                                 )
define_quantity_symbol( sd.Q_INNER_LAYER_VELOCITY,                               sd.VT_UNAVERAGED_VALUE, r"{:s}^+".format(sd.STREAMWISE_VELOCITY_SYMBOL),        )
define_quantity_symbol( sd.Q_INNER_LAYER_VELOCITY_DEFECT,                        sd.VT_UNAVERAGED_VALUE, r"\Delta {:s}^+".format(sd.STREAMWISE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_KINEMATIC_VISCOSITY,                                sd.VT_UNAVERAGED_VALUE, r"\nu",         )
define_quantity_symbol( sd.Q_MACH_NUMBER,                                        sd.VT_UNAVERAGED_VALUE, r"\mathrm{Ma}", )
define_quantity_symbol( sd.Q_MASS_DENSITY,                                       sd.VT_UNAVERAGED_VALUE, r"\rho",        )
define_quantity_symbol( sd.Q_OUTER_LAYER_COORDINATE,                             sd.VT_UNAVERAGED_VALUE, r"\eta", )
define_quantity_symbol( sd.Q_OUTER_LAYER_TEMPERATURE,                            sd.VT_UNAVERAGED_VALUE, r"\Theta", )
define_quantity_symbol( sd.Q_OUTER_LAYER_VELOCITY,                               sd.VT_UNAVERAGED_VALUE, r"F", )
define_quantity_symbol( sd.Q_OUTER_LAYER_VELOCITY_DEFECT,                        sd.VT_UNAVERAGED_VALUE, r"\Delta {:s}", )
define_quantity_symbol( sd.Q_PRANDTL_NUMBER,                                     sd.VT_UNAVERAGED_VALUE, r"\mathrm{Pr}", )
define_quantity_symbol( sd.Q_PRESSURE,                                           sd.VT_UNAVERAGED_VALUE, r"p", )
define_quantity_symbol( sd.Q_SEMI_LOCAL_COORDINATE,                              sd.VT_UNAVERAGED_VALUE, r"{:s}^*".format(sd.TRANSVERSE_COORDINATE_SYMBOL), )
define_quantity_symbol( sd.Q_SPANWISE_COORDINATE,                                sd.VT_UNAVERAGED_VALUE, r"{:s}".format(sd.SPANWISE_COORDINATE_SYMBOL), )
define_quantity_symbol( sd.Q_SPANWISE_VELOCITY,                                  sd.VT_UNAVERAGED_VALUE, r"{:s}".format(sd.SPANWISE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_SPECIFIC_ENTHALPY,                                  sd.VT_UNAVERAGED_VALUE, r"h", )
define_quantity_symbol( sd.Q_SPECIFIC_GAS_CONSTANT,                              sd.VT_UNAVERAGED_VALUE, r"R", )
define_quantity_symbol( sd.Q_SPECIFIC_INTERNAL_ENERGY,                           sd.VT_UNAVERAGED_VALUE, r"e", )
define_quantity_symbol( sd.Q_SPECIFIC_ISOBARIC_HEAT_CAPACITY,                    sd.VT_UNAVERAGED_VALUE, r"c_p", )
define_quantity_symbol( sd.Q_SPECIFIC_ISOCHORIC_HEAT_CAPACITY,                   sd.VT_UNAVERAGED_VALUE, r"c_v", )
define_quantity_symbol( sd.Q_SPECIFIC_TOTAL_ENTHALPY,                            sd.VT_UNAVERAGED_VALUE, r"h_0", )
define_quantity_symbol( sd.Q_SPECIFIC_TOTAL_INTERNAL_ENERGY,                     sd.VT_UNAVERAGED_VALUE, r"e_0", )
define_quantity_symbol( sd.Q_SPECIFIC_VOLUME,                                    sd.VT_UNAVERAGED_VALUE, r"v", )
define_quantity_symbol( sd.Q_SPEED,                                              sd.VT_UNAVERAGED_VALUE, r"V", )
define_quantity_symbol( sd.Q_SPEED_OF_SOUND,                                     sd.VT_UNAVERAGED_VALUE, r"a", )
define_quantity_symbol( sd.Q_STREAMWISE_COORDINATE,                              sd.VT_UNAVERAGED_VALUE, r"{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL), )
define_quantity_symbol( sd.Q_STREAMWISE_VELOCITY,                                sd.VT_UNAVERAGED_VALUE, r"{:s}".format(sd.STREAMWISE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_STRESS[sd.D_STREAMWISE,sd.D_STREAMWISE],            sd.VT_UNAVERAGED_VALUE, r"\sigma_{"+"{:s}{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL,sd.STREAMWISE_COORDINATE_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_STRESS[sd.D_STREAMWISE,sd.D_TRANSVERSE],            sd.VT_UNAVERAGED_VALUE, r"\tau_{"+"{:s}{:s}".format(  sd.STREAMWISE_COORDINATE_SYMBOL,sd.TRANSVERSE_COORDINATE_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_STRESS[sd.D_STREAMWISE,sd.D_SPANWISE  ],            sd.VT_UNAVERAGED_VALUE, r"\tau_{"+"{:s}{:s}".format(  sd.STREAMWISE_COORDINATE_SYMBOL,  sd.SPANWISE_COORDINATE_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_STRESS[sd.D_TRANSVERSE,sd.D_TRANSVERSE],            sd.VT_UNAVERAGED_VALUE, r"\sigma_{"+"{:s}{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL,sd.TRANSVERSE_COORDINATE_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_STRESS[sd.D_TRANSVERSE,sd.D_SPANWISE  ],            sd.VT_UNAVERAGED_VALUE, r"\tau_{"+"{:s}{:s}".format(  sd.TRANSVERSE_COORDINATE_SYMBOL,  sd.SPANWISE_COORDINATE_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_STRESS[sd.D_SPANWISE,  sd.D_SPANWISE  ],            sd.VT_UNAVERAGED_VALUE, r"\sigma_{"+"{:s}{:s}".format(  sd.SPANWISE_COORDINATE_SYMBOL,  sd.SPANWISE_COORDINATE_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_TEMPERATURE,                                        sd.VT_UNAVERAGED_VALUE, r"T", )
define_quantity_symbol( sd.Q_THERMAL_CONDUCTIVITY,                               sd.VT_UNAVERAGED_VALUE, r"\lambda", )
define_quantity_symbol( sd.Q_THERMAL_DIFFUSIVITY,                                sd.VT_UNAVERAGED_VALUE, r"\alpha", )
define_quantity_symbol( sd.Q_TOTAL_PRESSURE,                                     sd.VT_UNAVERAGED_VALUE, r"p_0", )
define_quantity_symbol( sd.Q_TOTAL_TEMPERATURE,                                  sd.VT_UNAVERAGED_VALUE, r"T_0", )
define_quantity_symbol( sd.Q_TRANSVERSE_COORDINATE,                              sd.VT_UNAVERAGED_VALUE, r"{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL), )
define_quantity_symbol( sd.Q_TRANSVERSE_VELOCITY,                                sd.VT_UNAVERAGED_VALUE, r"{:s}".format(sd.TRANSVERSE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_VELOCITY_DEFECT,                                    sd.VT_UNAVERAGED_VALUE, r"{:s}".format(sd.STREAMWISE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_STREAMWISE], sd.VT_UNAVERAGED_VALUE, r"\mathrm{d} "+"{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL)+" / "+r"\mathrm{d} "+"{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL)+")", )
define_quantity_symbol( sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_TRANSVERSE], sd.VT_UNAVERAGED_VALUE, r"\mathrm{d} "+"{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL)+" / "+r"\mathrm{d} "+"{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL)+")", )
define_quantity_symbol( sd.Q_VELOCITY_GRADIENT[sd.D_STREAMWISE,sd.D_SPANWISE  ], sd.VT_UNAVERAGED_VALUE, r"\mathrm{d} "+"{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL)+" / "+r"\mathrm{d} "+"{:s}".format(  sd.SPANWISE_COORDINATE_SYMBOL)+")", )
define_quantity_symbol( sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_STREAMWISE], sd.VT_UNAVERAGED_VALUE, r"\mathrm{d} "+"{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL)+" / "+r"\mathrm{d} "+"{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL)+")", )
define_quantity_symbol( sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_TRANSVERSE], sd.VT_UNAVERAGED_VALUE, r"\mathrm{d} "+"{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL)+" / "+r"\mathrm{d} "+"{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL)+")", )
define_quantity_symbol( sd.Q_VELOCITY_GRADIENT[sd.D_TRANSVERSE,sd.D_SPANWISE  ], sd.VT_UNAVERAGED_VALUE, r"\mathrm{d} "+"{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL)+" / "+r"\mathrm{d} "+"{:s}".format(  sd.SPANWISE_COORDINATE_SYMBOL)+")", )
define_quantity_symbol( sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_STREAMWISE], sd.VT_UNAVERAGED_VALUE, r"\mathrm{d} "+"{:s}".format(  sd.SPANWISE_COORDINATE_SYMBOL)+" / "+r"\mathrm{d} "+"{:s}".format(sd.STREAMWISE_COORDINATE_SYMBOL)+")", )
define_quantity_symbol( sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_TRANSVERSE], sd.VT_UNAVERAGED_VALUE, r"\mathrm{d} "+"{:s}".format(  sd.SPANWISE_COORDINATE_SYMBOL)+" / "+r"\mathrm{d} "+"{:s}".format(sd.TRANSVERSE_COORDINATE_SYMBOL)+")", )
define_quantity_symbol( sd.Q_VELOCITY_GRADIENT[sd.D_SPANWISE,  sd.D_SPANWISE  ], sd.VT_UNAVERAGED_VALUE, r"\mathrm{d} "+"{:s}".format(  sd.SPANWISE_COORDINATE_SYMBOL)+" / "+r"\mathrm{d} "+"{:s}".format(  sd.SPANWISE_COORDINATE_SYMBOL)+")", )

# Quantities, point, turbulence
define_quantity_symbol( sd.Q_MASS_DENSITY_AUTOCOVARIANCE,                       sd.VT_UNWEIGHTED_AVERAGE, r"\overline{\rho'\rho'}", )
define_quantity_symbol( sd.Q_NORMALIZED_MASS_DENSITY_AUTOCOVARIANCE,            sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{\rho'\rho'}/\overline{\rho}^2)", )
define_quantity_symbol( sd.Q_NORMALIZED_PRESSURE_AUTOCOVARIANCE,                sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{p'p'}/\overline{p}^2)", )
define_quantity_symbol( sd.Q_NORMALIZED_TEMPERATURE_AUTOCOVARIANCE,             sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{T'T'}/\overline{T}^2)", )
define_quantity_symbol( sd.Q_PRESSURE_AUTOCOVARIANCE,                           sd.VT_UNWEIGHTED_AVERAGE, r"\overline{p'p'}", )
define_quantity_symbol( sd.Q_INNER_LAYER_SPECIFIC_TURBULENT_KINETIC_ENERGY,     sd.VT_UNWEIGHTED_AVERAGE, r"k^+", )
define_quantity_symbol( sd.Q_MORKOVIN_SCALED_SPECIFIC_TURBULENT_KINETIC_ENERGY, sd.VT_UNWEIGHTED_AVERAGE, r"k^*", )
define_quantity_symbol( sd.Q_SPECIFIC_TURBULENT_KINETIC_ENERGY,                 sd.VT_UNWEIGHTED_AVERAGE, r"k", )
define_quantity_symbol( sd.Q_TEMPERATURE_AUTOCOVARIANCE,                        sd.VT_UNWEIGHTED_AVERAGE, r"\overline{T'T'}", )

define_quantity_symbol( sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE], sd.VT_UNWEIGHTED_AVERAGE, r"\overline{"+"{:s}'{:s}'".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.STREAMWISE_VELOCITY_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE], sd.VT_UNWEIGHTED_AVERAGE, r"\overline{"+"{:s}'{:s}'".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.TRANSVERSE_VELOCITY_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ], sd.VT_UNWEIGHTED_AVERAGE, r"\overline{"+"{:s}'{:s}'".format(sd.STREAMWISE_VELOCITY_SYMBOL,  sd.SPANWISE_VELOCITY_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE], sd.VT_UNWEIGHTED_AVERAGE, r"\overline{"+"{:s}'{:s}'".format(sd.TRANSVERSE_VELOCITY_SYMBOL,sd.TRANSVERSE_VELOCITY_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ], sd.VT_UNWEIGHTED_AVERAGE, r"\overline{"+"{:s}'{:s}'".format(sd.TRANSVERSE_VELOCITY_SYMBOL,  sd.SPANWISE_VELOCITY_SYMBOL)+"}", )
define_quantity_symbol( sd.Q_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ], sd.VT_UNWEIGHTED_AVERAGE, r"\overline{"+"{:s}'{:s}'".format(  sd.SPANWISE_VELOCITY_SYMBOL,  sd.SPANWISE_VELOCITY_SYMBOL)+"}", )

define_quantity_symbol( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.STREAMWISE_VELOCITY_SYMBOL)+"})^+", )
define_quantity_symbol( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.TRANSVERSE_VELOCITY_SYMBOL)+"})^+", )
define_quantity_symbol( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.STREAMWISE_VELOCITY_SYMBOL,  sd.SPANWISE_VELOCITY_SYMBOL)+"})^+", )
define_quantity_symbol( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.TRANSVERSE_VELOCITY_SYMBOL,sd.TRANSVERSE_VELOCITY_SYMBOL)+"})^+", )
define_quantity_symbol( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.TRANSVERSE_VELOCITY_SYMBOL,  sd.SPANWISE_VELOCITY_SYMBOL)+"})^+", )
define_quantity_symbol( sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(  sd.SPANWISE_VELOCITY_SYMBOL,  sd.SPANWISE_VELOCITY_SYMBOL)+"})^+", )

define_quantity_symbol( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_STREAMWISE], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.STREAMWISE_VELOCITY_SYMBOL)+"})^*", )
define_quantity_symbol( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_TRANSVERSE], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.TRANSVERSE_VELOCITY_SYMBOL)+"})^*", )
define_quantity_symbol( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_STREAMWISE,sd.D_SPANWISE  ], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.STREAMWISE_VELOCITY_SYMBOL,  sd.SPANWISE_VELOCITY_SYMBOL)+"})^*", )
define_quantity_symbol( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_TRANSVERSE], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.TRANSVERSE_VELOCITY_SYMBOL,sd.TRANSVERSE_VELOCITY_SYMBOL)+"})^*", )
define_quantity_symbol( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_TRANSVERSE,sd.D_SPANWISE  ], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(sd.TRANSVERSE_VELOCITY_SYMBOL,  sd.SPANWISE_VELOCITY_SYMBOL)+"})^*", )
define_quantity_symbol( sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[sd.D_SPANWISE,  sd.D_SPANWISE  ], sd.VT_UNWEIGHTED_AVERAGE, r"(\overline{"+"{:s}'{:s}'".format(  sd.SPANWISE_VELOCITY_SYMBOL,  sd.SPANWISE_VELOCITY_SYMBOL)+"})^*", )

# Quantities, point, ratios
define_quantity_symbol( sd.Q_LOCAL_TO_BULK_STREAMWISE_VELOCITY_RATIO,        sd.VT_UNAVERAGED_VALUE, r"({:s}/{:s}_b)".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.STREAMWISE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_LOCAL_TO_BULK_TEMPERATURE_RATIO,                sd.VT_UNAVERAGED_VALUE, r"(T/T_b)",                                                                           )
define_quantity_symbol( sd.Q_LOCAL_TO_CENTER_LINE_DYNAMIC_VISCOSITY_RATIO,   sd.VT_UNAVERAGED_VALUE, r"(\mu/\mu_c)",                                                                       )
define_quantity_symbol( sd.Q_LOCAL_TO_CENTER_LINE_MASS_DENSITY_RATIO,        sd.VT_UNAVERAGED_VALUE, r"(\rho/\rho_c)",                                                                     )
define_quantity_symbol( sd.Q_LOCAL_TO_CENTER_LINE_STREAMWISE_VELOCITY_RATIO, sd.VT_UNAVERAGED_VALUE, r"({:s}/{:s}_c)".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.STREAMWISE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_LOCAL_TO_CENTER_LINE_TEMPERATURE_RATIO,         sd.VT_UNAVERAGED_VALUE, r"(T/T_c)",                                                                           )
define_quantity_symbol( sd.Q_LOCAL_TO_EDGE_DYNAMIC_VISCOSITY_RATIO,          sd.VT_UNAVERAGED_VALUE, r"(\mu/\mu_e)",                                                                       )
define_quantity_symbol( sd.Q_LOCAL_TO_EDGE_MASS_DENSITY_RATIO,               sd.VT_UNAVERAGED_VALUE, r"(\rho/\rho_e)",                                                                     )
define_quantity_symbol( sd.Q_LOCAL_TO_EDGE_STREAMWISE_VELOCITY_RATIO,        sd.VT_UNAVERAGED_VALUE, r"({:s}/{:s}_e)".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.STREAMWISE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_LOCAL_TO_EDGE_TEMPERATURE_RATIO,                sd.VT_UNAVERAGED_VALUE, r"(T/T_e)",                                                                           )
define_quantity_symbol( sd.Q_LOCAL_TO_RECOVERY_TEMPERATURE_RATIO,            sd.VT_UNAVERAGED_VALUE, r"(T/T_r)",                                                                           )
define_quantity_symbol( sd.Q_LOCAL_TO_WALL_DYNAMIC_VISCOSITY_RATIO,          sd.VT_UNAVERAGED_VALUE, r"(\mu/\mu_w)",                                                                       )
define_quantity_symbol( sd.Q_LOCAL_TO_WALL_MASS_DENSITY_RATIO,               sd.VT_UNAVERAGED_VALUE, r"(\rho/\rho_w)",                                                                     )
define_quantity_symbol( sd.Q_LOCAL_TO_WALL_STREAMWISE_VELOCITY_RATIO,        sd.VT_UNAVERAGED_VALUE, r"({:s}/{:s}_w)".format(sd.STREAMWISE_VELOCITY_SYMBOL,sd.STREAMWISE_VELOCITY_SYMBOL), )
define_quantity_symbol( sd.Q_LOCAL_TO_WALL_TEMPERATURE_RATIO,                sd.VT_UNAVERAGED_VALUE, r"(T/T_w)",                                                                           )

# Quantities, facility
define_quantity_symbol( sd.Q_RUN_TIME,                   sd.VT_UNAVERAGED_VALUE, r"t_\mathrm{rt}",    )
define_quantity_symbol( sd.Q_SPATIAL_ORDER_OF_ACCURACY,  sd.VT_UNAVERAGED_VALUE, r"O_s",              )
define_quantity_symbol( sd.Q_TEMPORAL_ORDER_OF_ACCURACY, sd.VT_UNAVERAGED_VALUE, r"O_t",              )
define_quantity_symbol( sd.Q_TEST_SECTION_HEIGHT,        sd.VT_UNAVERAGED_VALUE, r"h_\mathrm{ts}",    )
define_quantity_symbol( sd.Q_TEST_SECTION_LENGTH,        sd.VT_UNAVERAGED_VALUE, r"\ell_\mathrm{ts}", )
define_quantity_symbol( sd.Q_TEST_SECTION_WIDTH,         sd.VT_UNAVERAGED_VALUE, r"w_\mathrm{ts}",    )

# Quantities, instrument
define_quantity_symbol( sd.Q_DISTANCE_BETWEEN_PRESSURE_TAPS, sd.VT_UNAVERAGED_VALUE, r"\ell_p",         )
define_quantity_symbol( sd.Q_ORDER_OF_APPROXIMATION,         sd.VT_UNAVERAGED_VALUE, r"O_a",            )
define_quantity_symbol( sd.Q_PROBE_INNER_DIAMETER,        sd.VT_UNAVERAGED_VALUE, r"d_\mathrm{p,i}", )
define_quantity_symbol( sd.Q_PROBE_OUTER_DIAMETER,        sd.VT_UNAVERAGED_VALUE, r"d_\mathrm{p,i}", )


# Study types
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


# Compilations
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

conn.commit()
conn.close()
