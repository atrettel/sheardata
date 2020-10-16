/* Copyright (C) 2020 Andrew Trettel
 * 
 * This file is licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.  You may
 * obtain a copy of the License at
 * <http://www.apache.org/licenses/LICENSE-2.0>.
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */
.mode column
.headers on
PRAGMA foreign_keys = ON;

CREATE TABLE averaging_systems (
    identifier TEXT PRIMARY KEY UNIQUE,
    name       TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO averaging_systems( identifier, name ) VALUES( "UW",       "Unweighted averaging" );
INSERT INTO averaging_systems( identifier, name ) VALUES( "DW", "Density-weighted averaging" );

CREATE TABLE coordinate_systems (
    identifier TEXT PRIMARY KEY UNIQUE,
    name       TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO coordinate_systems( identifier, name ) VALUES( "XYZ", "Rectangular coordinates" );
INSERT INTO coordinate_systems( identifier, name ) VALUES( "XRT", "Cylindrical coordinates" );

CREATE TABLE flow_classes (
    identifier TEXT PRIMARY KEY UNIQUE CHECK ( length(identifier) = 1 ),
    name       TEXT NOT NULL,
    parent     TEXT DEFAULT NULL,
    notes      TEXT DEFAULT NULL,
    FOREIGN KEY(parent) REFERENCES flow_classes(identifier)
);

INSERT INTO flow_classes( identifier, name ) VALUES( "B", "boundary layer"                              );
INSERT INTO flow_classes( identifier, name ) VALUES( "C", "wall-bounded flow"                           );
INSERT INTO flow_classes( identifier, name ) VALUES( "D", "duct flow"                                   );
INSERT INTO flow_classes( identifier, name ) VALUES( "E", "external flow"                               );
INSERT INTO flow_classes( identifier, name ) VALUES( "F", "free shear flow"                             );
INSERT INTO flow_classes( identifier, name ) VALUES( "G", "isotropic flow"                              );
INSERT INTO flow_classes( identifier, name ) VALUES( "H", "homogeneous flow"                            );
INSERT INTO flow_classes( identifier, name ) VALUES( "I", "internal flow"                               );
INSERT INTO flow_classes( identifier, name ) VALUES( "J", "free jet"                                    );
INSERT INTO flow_classes( identifier, name ) VALUES( "K", "wall jet"                                    );
INSERT INTO flow_classes( identifier, name ) VALUES( "M", "mixing layer"                                );
INSERT INTO flow_classes( identifier, name ) VALUES( "N", "inhomogeneous flow"                          );
INSERT INTO flow_classes( identifier, name ) VALUES( "R", "flow with relative motion of the boundaries" );
INSERT INTO flow_classes( identifier, name ) VALUES( "S", "shear layer"                                 );
INSERT INTO flow_classes( identifier, name ) VALUES( "U", "flow"                                        );
INSERT INTO flow_classes( identifier, name ) VALUES( "W", "wake"                                        );

UPDATE flow_classes SET parent="U" WHERE identifier="H";
UPDATE flow_classes SET parent="U" WHERE identifier="N";

UPDATE flow_classes SET parent="H" WHERE identifier="G";

UPDATE flow_classes SET parent="N" WHERE identifier="S";

UPDATE flow_classes SET parent="S" WHERE identifier="C";
UPDATE flow_classes SET parent="S" WHERE identifier="F";

UPDATE flow_classes SET parent="F" WHERE identifier="J";
UPDATE flow_classes SET parent="F" WHERE identifier="M";
UPDATE flow_classes SET parent="F" WHERE identifier="W";

UPDATE flow_classes SET parent="C" WHERE identifier="E";
UPDATE flow_classes SET parent="C" WHERE identifier="I";

UPDATE flow_classes SET parent="E" WHERE identifier="B";
UPDATE flow_classes SET parent="E" WHERE identifier="K";

UPDATE flow_classes SET parent="I" WHERE identifier="D";
UPDATE flow_classes SET parent="I" WHERE identifier="R";

CREATE TABLE flow_regimes (
    identifier TEXT PRIMARY KEY UNIQUE CHECK ( length(identifier) = 2 ),
    name       TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO flow_regimes( identifier, name ) VALUES( "LA",      "Laminar flow" );
INSERT INTO flow_regimes( identifier, name ) VALUES( "TR", "Transitional flow" );
INSERT INTO flow_regimes( identifier, name ) VALUES( "TU",    "Turbulent flow" );

CREATE TABLE fluids (
    identifier TEXT PRIMARY KEY UNIQUE,
    name       TEXT NOT NULL,
    phase      TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO fluids( identifier, name, phase ) VALUES( "dry_air",   "Dry air",             "G" );
INSERT INTO fluids( identifier, name, phase ) VALUES( "moist_air", "Moist air",           "M" );
INSERT INTO fluids( identifier, name, phase ) VALUES( "water",     "Water",               "L" );
INSERT INTO fluids( identifier, name, phase ) VALUES( "steam",     "Steam",               "G" );
INSERT INTO fluids( identifier, name, phase ) VALUES( "thick_oil", "Thick oil (generic)", "L" );

CREATE TABLE geometries (
    identifier TEXT PRIMARY KEY UNIQUE,
    name       TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO geometries( identifier, name ) VALUES( "E",  "Elliptical geometry" );
INSERT INTO geometries( identifier, name ) VALUES( "R", "Rectangular geometry" );

CREATE TABLE measurement_techniques (
    identifier TEXT PRIMARY KEY UNIQUE,
    name       TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO measurement_techniques( identifier, name ) VALUES( "FEB", "Floating element balance" );
INSERT INTO measurement_techniques( identifier, name ) VALUES( "IT",  "Impact tube"              );
INSERT INTO measurement_techniques( identifier, name ) VALUES( "PST", "Pitot-static tube"        );
INSERT INTO measurement_techniques( identifier, name ) VALUES( "SPT", "Static pressure tap"      );

CREATE TABLE point_labels (
    identifier TEXT PRIMARY KEY UNIQUE,
    name       TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO point_labels( identifier, name ) VALUES( "C", "Center-line" );
INSERT INTO point_labels( identifier, name ) VALUES( "E", "Edge"        );
INSERT INTO point_labels( identifier, name ) VALUES( "W", "Wall"        );

CREATE TABLE quantities (
    identifier           TEXT PRIMARY KEY UNIQUE,
    name                 TEXT NOT NULL,
    length_exponent      REAL NOT NULL DEFAULT 0.0,
    mass_exponent        REAL NOT NULL DEFAULT 0.0,
    time_exponent        REAL NOT NULL DEFAULT 0.0,
    temperature_exponent REAL NOT NULL DEFAULT 0.0,
    note                 TEXT DEFAULT NULL
);

-- Profile quantities
INSERT INTO quantities( identifier, name                                                ) VALUES( "AR",      "Aspect ratio"                                     );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                ) VALUES( "u_b",     "Bulk velocity",                  +1.0, -1.0       );
INSERT INTO quantities( identifier, name, length_exponent                               ) VALUES( "DELTA",   "Clauser thickness",              +1.0             );
INSERT INTO quantities( identifier, name, length_exponent                               ) VALUES( "A",       "Cross-sectional area",           +2.0             );
INSERT INTO quantities( identifier, name                                                ) VALUES( "PI",      "Equilibrium parameter"                            );
INSERT INTO quantities( identifier, name, length_exponent                               ) VALUES( "d_h",     "Hydraulic diameter",             +1.0             );
INSERT INTO quantities( identifier, name, mass_exponent, time_exponent                  ) VALUES( "mdot",    "Mass flow rate",                 +1.0, -1.0       );
INSERT INTO quantities( identifier, name, length_exponent, mass_exponent, time_exponent ) VALUES( "dp/dx",   "Pressure gradient",              -2.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, name                                                ) VALUES( "RF",      "Recovery factor"                                  );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                ) VALUES( "Vdot",    "Volume flow rate",               +3.0, -1.0       );

/* Wall point quantities
 *
 * Arguably these quantities are profile quantities, but there could be
 * multiple of them, one for each wall.  For the sake of simplicity, treat
 * these as point quantities, since that is what they are.  They should only
 * occur at walls, though.
 */
INSERT INTO quantities( identifier, name                                 ) VALUES( "f_D",     "Darcy friction factor"                            );
INSERT INTO quantities( identifier, name                                 ) VALUES( "f",       "Fanning friction factor"                          );
INSERT INTO quantities( identifier, name, temperature_exponent           ) VALUES( "T_tau",   "Friction temperature",           +1.0             );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent ) VALUES( "u_tau",   "Friction velocity",              +1.0, -1.0       );
INSERT INTO quantities( identifier, name                                 ) VALUES( "Ma_tau",  "Friction Mach number"                             );
INSERT INTO quantities( identifier, name                                 ) VALUES( "Re_tau",  "Friction Reynolds number"                         );
INSERT INTO quantities( identifier, name                                 ) VALUES( "c_f",     "Local skin friction coefficient"                  );
INSERT INTO quantities( identifier, name, length_exponent                ) VALUES( "k",       "Roughness height",               +1.0             );
INSERT INTO quantities( identifier, name, length_exponent, note          ) VALUES( "kappa_z", "Spanwise wall curvature",        -1.0,
                                                                                   "Positive for external flows and negative for internal flows" );
INSERT INTO quantities( identifier, name, length_exponent                ) VALUES( "kappa_x", "Streamwise wall curvature",      -1.0             );
INSERT INTO quantities( identifier, name, length_exponent                ) VALUES( "l_nu",    "Viscous length scale",           +1.0             );


-- Point quantities
INSERT INTO quantities( identifier, name, length_exponent, mass_exponent, time_exponent        ) VALUES( "mu",    "Dynamic viscosity",                -1.0, +1.0, -1.0 );
INSERT INTO quantities( identifier, name                                                       ) VALUES( "gamma", "Heat capacity ratio"                                );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "nu",    "Kinematic viscosity",              +2.0, -1.0       );
INSERT INTO quantities( identifier, name                                                       ) VALUES( "Ma",    "Mach number"                                        );
INSERT INTO quantities( identifier, name, length_exponent, mass_exponent                       ) VALUES( "rho",   "Mass density",                     -3.0, +1.0       );
INSERT INTO quantities( identifier, name                                                       ) VALUES( "Pr",    "Prandtl number"                                     );
INSERT INTO quantities( identifier, name, length_exponent, mass_exponent, time_exponent        ) VALUES( "p",     "Pressure",                         -1.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, name, length_exponent, mass_exponent, time_exponent        ) VALUES( "tau",   "Shear stress",                     -1.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, name, length_exponent                                      ) VALUES( "z",     "Spanwise coordinate",              +1.0             );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "w",     "Spanwise velocity",                +1.0, -1.0       );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "h",     "Specific enthalpy",                +2.0, -2.0       );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "e",     "Specific internal energy",         +2.0, -2.0       );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent, temperature_exponent ) VALUES( "c_p",   "Specific isobaric heat capacity",  +2.0, -2.0, -1.0 );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent, temperature_exponent ) VALUES( "c_v",   "Specific isochoric heat capacity", +2.0, -2.0, -1.0 );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "h_0",   "Specific total enthalpy",          +2.0, -2.0       );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "e_0",   "Specific total internal energy",   +2.0, -2.0       );
INSERT INTO quantities( identifier, name, length_exponent, mass_exponent                       ) VALUES( "vbar",  "Specific volume",                  +3.0, -1.0       );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "V",     "Speed",                            +1.0, -1.0       );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "a",     "Speed of sound",                   +1.0, -1.0       );
INSERT INTO quantities( identifier, name, length_exponent                                      ) VALUES( "x",     "Streamwise coordinate",            +1.0             );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "u",     "Streamwise velocity",              +1.0, -1.0       );
INSERT INTO quantities( identifier, name, temperature_exponent                                 ) VALUES( "T",     "Temperature",                      +1.0             );
INSERT INTO quantities( identifier, name, length_exponent, mass_exponent, time_exponent        ) VALUES( "p_0",   "Total pressure",                   -1.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, name, temperature_exponent                                 ) VALUES( "T_0",   "Total temperature",                +1.0             );
INSERT INTO quantities( identifier, name, length_exponent                                      ) VALUES( "y",     "Transverse coordinate",            +1.0             );
INSERT INTO quantities( identifier, name, length_exponent, time_exponent                       ) VALUES( "v",     "Transverse velocity",              +1.0, -1.0       );

CREATE TABLE study_types (
    identifier TEXT PRIMARY KEY UNIQUE CHECK ( length(identifier) = 1 ),
    name       TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO study_types( identifier, name ) VALUES( "E", "Experimental study" );
INSERT INTO study_types( identifier, name ) VALUES( "N",    "Numerical study" );

CREATE TABLE studies (
    identifier            TEXT PRIMARY KEY UNIQUE,
    flow_class            TEXT NOT NULL DEFAULT "U",
    year                  INTEGER NOT NULL CHECK (        year  >= 0 AND         year <= 9999 ),
    study_number          INTEGER NOT NULL CHECK ( study_number >  0 AND study_number <=  999 ),
    study_type            TEXT NOT NULL,
    description           TEXT DEFAULT NULL,
    provenance            TEXT DEFAULT NULL,
    primary_reference     TEXT DEFAULT NULL,
    additional_references TEXT DEFAULT NULL,
    notes                 TEXT DEFAULT NULL,
    FOREIGN KEY(flow_class) REFERENCES flow_classes(identifier),
    FOREIGN KEY(study_type) REFERENCES  study_types(identifier)
);

CREATE TABLE series (
    identifier           TEXT PRIMARY KEY UNIQUE,
    series_number        INTEGER NOT NULL CHECK ( series_number > 0 AND series_number <=  999 ),
    number_of_dimensions INTEGER NOT NULL DEFAULT 2 CHECK ( number_of_dimensions > 0 AND number_of_dimensions <= 3 ),
    coordinate_system    TEXT NOT NULL DEFAULT "XYZ",
    working_fluid        TEXT NOT NULL,
    geometry             TEXT DEFAULT NULL,
    number_of_sides      TEXT DEFAULT NULL CHECK ( number_of_sides > 1 ),
    description          TEXT DEFAULT NULL,
    notes                TEXT DEFAULT NULL,
    FOREIGN KEY(working_fluid)     REFERENCES             fluids(identifier),
    FOREIGN KEY(coordinate_system) REFERENCES coordinate_systems(identifier),
    FOREIGN KEY(geometry)          REFERENCES         geometries(identifier)
);

CREATE TABLE profiles (
    identifier                   TEXT PRIMARY KEY UNIQUE,
    profile_number               INTEGER NOT NULL CHECK ( profile_number > 0 AND profile_number <=  999 ),
    originators_identifier       TEXT UNIQUE DEFAULT NULL,
    flow_regime                  TEXT DEFAULT NULL,
    previous_streamwise_station  TEXT DEFAULT NULL,
    next_streamwise_station      TEXT DEFAULT NULL,
    previous_spanwise_station    TEXT DEFAULT NULL,
    next_spanwise_station        TEXT DEFAULT NULL,
    outlier                      INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    description                  TEXT DEFAULT NULL,
    notes                        TEXT DEFAULT NULL,
    FOREIGN KEY(flow_regime)                 REFERENCES flow_regimes(identifier),
    FOREIGN KEY(previous_streamwise_station) REFERENCES     profiles(identifier),
    FOREIGN KEY(next_streamwise_station)     REFERENCES     profiles(identifier),
    FOREIGN KEY(previous_spanwise_station)   REFERENCES     profiles(identifier),
    FOREIGN KEY(next_spanwise_station)       REFERENCES     profiles(identifier)
);

CREATE TABLE points (
    identifier           TEXT PRIMARY KEY UNIQUE,
    point_number         INTEGER NOT NULL CHECK ( point_number > 0 AND point_number <= 9999 ),
    point_label          TEXT DEFAULT NULL,
    outlier              INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    description          TEXT DEFAULT NULL,
    notes                TEXT DEFAULT NULL,
    FOREIGN KEY(point_label) REFERENCES point_labels(identifier)
);

CREATE TABLE study_values (
    study                 TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    value                 REAL NOT NULL,
    uncertainty           REAL DEFAULT NULL CHECK ( uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(study, quantity),
    FOREIGN KEY(study)                 REFERENCES                studies(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);

CREATE TABLE series_values (
    series                TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    value                 REAL NOT NULL,
    uncertainty           REAL DEFAULT NULL CHECK ( uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(series, quantity),
    FOREIGN KEY(series)                REFERENCES                 series(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);

CREATE TABLE profile_values (
    profile               TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    value                 REAL NOT NULL,
    uncertainty           REAL DEFAULT NULL CHECK ( uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(profile, quantity),
    FOREIGN KEY(profile)               REFERENCES               profiles(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);

CREATE TABLE point_values (
    point                 TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    value                 REAL NOT NULL,
    uncertainty           REAL DEFAULT NULL CHECK ( uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(point, quantity),
    FOREIGN KEY(point)                 REFERENCES                 points(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);
