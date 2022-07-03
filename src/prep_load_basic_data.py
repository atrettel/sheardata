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

# Instrument classes
def add_instrument_class( cursor, instrument_class_id, instrument_class_name,
                          instrument_class_parent_id=None, intrusive=False, ):
    cursor.execute(
    """
    INSERT INTO instrument_classes( instrument_class_id, instrument_class_name,
                                    intrusive )
    VALUES( ?, ?, ? );
    """,
    (
        str(instrument_class_id),
        str(instrument_class_name),
        int(intrusive),
    )
    )
    if ( instrument_class_parent_id == None ):
        cursor.execute(
        """
        INSERT INTO instrument_class_paths( instrument_class_ancestor_id,
                                      instrument_class_descendant_id,
                                      instrument_class_path_length )
        VALUES( ?, ?, 0 );
        """,
        (
            str(instrument_class_id),
            str(instrument_class_id),
        )
        )
    else:
        cursor.execute(
        """
        INSERT INTO instrument_class_paths( instrument_class_ancestor_id,
                                      instrument_class_descendant_id,
                                      instrument_class_path_length )
        SELECT ?, ?, 0
        UNION ALL
        SELECT tmp.instrument_class_ancestor_id, ?, tmp.instrument_class_path_length+1
        FROM instrument_class_paths as tmp
        WHERE tmp.instrument_class_descendant_id = ?;
        """,
        (
            str(instrument_class_id),
            str(instrument_class_id),
            str(instrument_class_id),
            str(instrument_class_parent_id),
        )
        )

add_instrument_class( cursor, sd.IC_INSTRUMENT,                               "instrument",                               None,                                               )
add_instrument_class( cursor, sd.IC_OBSERVATION,                              "observation",                              sd.IC_INSTRUMENT,                                   )
add_instrument_class( cursor, sd.IC_DIFFERENTIAL_PRESSURE_METHOD,             "differential pressure method",             sd.IC_OBSERVATION,                                  )
add_instrument_class( cursor, sd.IC_IMPACT_TUBE,                              "impact tube",                              sd.IC_DIFFERENTIAL_PRESSURE_METHOD, intrusive=True, )
add_instrument_class( cursor, sd.IC_PITOT_STATIC_TUBE,                        "Pitot-static tube",                        sd.IC_DIFFERENTIAL_PRESSURE_METHOD, intrusive=True, )
add_instrument_class( cursor, sd.IC_FLOWMETER,                                "flowmeter",                                sd.IC_OBSERVATION,                                  )
add_instrument_class( cursor, sd.IC_WEIGHING_METHOD,                          "weighing method",                          sd.IC_FLOWMETER,                                    )
add_instrument_class( cursor, sd.IC_OPTICAL_SYSTEM,                           "optical system",                           sd.IC_OBSERVATION,                                  )
add_instrument_class( cursor, sd.IC_DIRECT_INJECTION_METHOD,                  "direct injection method",                  sd.IC_OPTICAL_SYSTEM,                               )
add_instrument_class( cursor, sd.IC_INDEX_OF_REFRACTION_METHOD,               "index-of-refraction method",               sd.IC_OPTICAL_SYSTEM,                               )
add_instrument_class( cursor, sd.IC_MACH_ZEHNDER_INTERFEROMETER,              "Mach-Zehnder interferometer",              sd.IC_INDEX_OF_REFRACTION_METHOD,                   )
add_instrument_class( cursor, sd.IC_SCHLIEREN_SYSTEM,                         "schlieren system",                         sd.IC_INDEX_OF_REFRACTION_METHOD,                   )
add_instrument_class( cursor, sd.IC_SHADOWGRAPH_SYSTEM,                       "shadowgraph system",                       sd.IC_INDEX_OF_REFRACTION_METHOD,                   )
add_instrument_class( cursor, sd.IC_LASER_DOPPLER_ANEMOMETER,                 "laser Doppler anemometer",                 sd.IC_OPTICAL_SYSTEM,                               )
add_instrument_class( cursor, sd.IC_PARTICLE_IMAGE_VELOCIMETER,               "particle image velocimeter",               sd.IC_OPTICAL_SYSTEM,                               )
add_instrument_class( cursor, sd.IC_THERMAL_ANEMOMETER,                       "thermal anemometer",                       sd.IC_OBSERVATION,                                  )
add_instrument_class( cursor, sd.IC_HOT_WIRE_ANEMOMETER,                      "hot-wire anemometer",                      sd.IC_THERMAL_ANEMOMETER,           intrusive=True, )
add_instrument_class( cursor, sd.IC_CONSTANT_CURRENT_HOT_WIRE_ANEMOMETER,     "constant-current hot-wire anemometer",     sd.IC_HOT_WIRE_ANEMOMETER,          intrusive=True, )
add_instrument_class( cursor, sd.IC_CONSTANT_TEMPERATURE_HOT_WIRE_ANEMOMETER, "constant-temperature hot-wire anemometer", sd.IC_HOT_WIRE_ANEMOMETER,          intrusive=True, )
add_instrument_class( cursor, sd.IC_WALL_SHEAR_STRESS_METHOD,                 "wall shear stress method",                 sd.IC_OBSERVATION,                                  )
add_instrument_class( cursor, sd.IC_FLOATING_ELEMENT_BALANCE,                 "floating element balance",                 sd.IC_WALL_SHEAR_STRESS_METHOD,                     )
add_instrument_class( cursor, sd.IC_MOMENTUM_BALANCE,                         "momentum balance",                         sd.IC_WALL_SHEAR_STRESS_METHOD,                     )
add_instrument_class( cursor, sd.IC_PRESTON_TUBE,                             "Preston tube",                             sd.IC_WALL_SHEAR_STRESS_METHOD,     intrusive=True, )
add_instrument_class( cursor, sd.IC_STANTON_TUBE,                             "Stanton tube",                             sd.IC_WALL_SHEAR_STRESS_METHOD,     intrusive=True, )
add_instrument_class( cursor, sd.IC_VELOCITY_PROFILE_METHOD,                  "velocity profile method",                  sd.IC_WALL_SHEAR_STRESS_METHOD,                     )
add_instrument_class( cursor, sd.IC_CLAUSER_METHOD,                           "Clauser method",                           sd.IC_VELOCITY_PROFILE_METHOD,                      )
add_instrument_class( cursor, sd.IC_VISCOUS_SUBLAYER_SLOPE_METHOD,            "viscous sublayer slope method",            sd.IC_VELOCITY_PROFILE_METHOD,                      )
add_instrument_class( cursor, sd.IC_REASONING,                                "reasoning",                                sd.IC_INSTRUMENT,                                   )
add_instrument_class( cursor, sd.IC_APPROXIMATION,                            "approximation",                            sd.IC_REASONING,                                    )
add_instrument_class( cursor, sd.IC_ASSUMPTION,                               "assumption",                               sd.IC_REASONING,                                    )
add_instrument_class( cursor, sd.IC_CALCULATION,                              "calculation",                              sd.IC_REASONING,                                    )
add_instrument_class( cursor, sd.IC_CLAIM,                                    "claim",                                    sd.IC_REASONING,                                    )
add_instrument_class( cursor, sd.IC_SIMULATION,                               "simulation",                               sd.IC_REASONING,                                    )


# Model classes
def add_model_class( cursor, model_class_id, model_class_name,
                          model_class_parent_id=None, intrusive=False, ):
    cursor.execute(
    """
    INSERT INTO model_classes( model_class_id, model_class_name )
    VALUES( ?, ? );
    """,
    (
        str(model_class_id),
        str(model_class_name),
    )
    )
    if ( model_class_parent_id == None ):
        cursor.execute(
        """
        INSERT INTO model_class_paths( model_class_ancestor_id,
                                       model_class_descendant_id,
                                       model_class_path_length )
        VALUES( ?, ?, 0 );
        """,
        (
            str(model_class_id),
            str(model_class_id),
        )
        )
    else:
        cursor.execute(
        """
        INSERT INTO model_class_paths( model_class_ancestor_id,
                                       model_class_descendant_id,
                                       model_class_path_length )
        SELECT ?, ?, 0
        UNION ALL
        SELECT tmp.model_class_ancestor_id, ?, tmp.model_class_path_length+1
        FROM model_class_paths as tmp
        WHERE tmp.model_class_descendant_id = ?;
        """,
        (
            str(model_class_id),
            str(model_class_id),
            str(model_class_id),
            str(model_class_parent_id),
        )
        )

add_model_class( cursor, sd.MC_MODEL,                                "model",                                     None,                                       )
add_model_class( cursor, sd.MC_INTERIOR_MODEL,                       "interior model",                            sd.MC_MODEL,                                )
add_model_class( cursor, sd.MC_INTERIOR_CONSTANT_CROSS_SECTION,      "constant cross-section interior model",     sd.MC_INTERIOR_MODEL,                       )
add_model_class( cursor, sd.MC_INTERIOR_POLYGONAL_CROSS_SECTION,     "polygonal cross-section interior model",    sd.MC_INTERIOR_CONSTANT_CROSS_SECTION,      )
add_model_class( cursor, sd.MC_INTERIOR_RECTANGULAR_CROSS_SECTION,   "rectangular cross-section interior model",  sd.MC_INTERIOR_POLYGONAL_CROSS_SECTION,     )
add_model_class( cursor, sd.MC_INTERIOR_ELLIPTICAL_CROSS_SECTION,    "elliptical cross-section interior model",   sd.MC_INTERIOR_CONSTANT_CROSS_SECTION,      )
add_model_class( cursor, sd.MC_INTERIOR_VARIABLE_CROSS_SECTION,      "variable cross-section interior model",     sd.MC_INTERIOR_MODEL,                       )
add_model_class( cursor, sd.MC_EXTERIOR_MODEL,                       "exterior model",                            sd.MC_MODEL,                                )
add_model_class( cursor, sd.MC_EXTERIOR_BODY,                        "body",                                      sd.MC_EXTERIOR_MODEL,                       )
add_model_class( cursor, sd.MC_EXTERIOR_ELLIPSOID,                   "ellipsoid",                                 sd.MC_EXTERIOR_ELLIPSOID,                   )
add_model_class( cursor, sd.MC_EXTERIOR_ELLIPTIC_CONE,               "elliptic cone",                             sd.MC_EXTERIOR_ELLIPTIC_CONE,               )
add_model_class( cursor, sd.MC_EXTERIOR_WING,                        "wing",                                      sd.MC_EXTERIOR_MODEL,                       )
add_model_class( cursor, sd.MC_EXTERIOR_CONSTANT_CROSS_SECTION_WING, "constant cross-section wing",               sd.MC_EXTERIOR_WING,                        )
add_model_class( cursor, sd.MC_EXTERIOR_PLATE,                       "plate",                                     sd.MC_EXTERIOR_CONSTANT_CROSS_SECTION_WING, )
add_model_class( cursor, sd.MC_EXTERIOR_WEDGE,                       "wedge",                                     sd.MC_EXTERIOR_CONSTANT_CROSS_SECTION_WING, )
add_model_class( cursor, sd.MC_EXTERIOR_CYLINDER,                    "cylinder",                                  sd.MC_EXTERIOR_CONSTANT_CROSS_SECTION_WING, )
add_model_class( cursor, sd.MC_EXTERIOR_DIAMOND_WING,                "diamond wing",                              sd.MC_EXTERIOR_CONSTANT_CROSS_SECTION_WING, )
add_model_class( cursor, sd.MC_EXTERIOR_VARIABLE_CROSS_SECTION_WING, "variable cross-section wing",               sd.MC_EXTERIOR_WING,                        )


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
