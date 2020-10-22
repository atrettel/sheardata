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
    identifier  TEXT PRIMARY KEY UNIQUE,
    system_name TEXT NOT NULL,
    notes       TEXT DEFAULT NULL
);

INSERT INTO averaging_systems( identifier, system_name ) VALUES( 'UW',       'unweighted averaging' );
INSERT INTO averaging_systems( identifier, system_name ) VALUES( 'DW', 'density-weighted averaging' );

CREATE TABLE coordinate_systems (
    identifier  TEXT PRIMARY KEY UNIQUE,
    system_name TEXT NOT NULL,
    notes       TEXT DEFAULT NULL
);

INSERT INTO coordinate_systems( identifier, system_name ) VALUES( 'XYZ', 'rectangular coordinates' );
INSERT INTO coordinate_systems( identifier, system_name ) VALUES( 'XRT', 'cylindrical coordinates' );

-- Facilities?

CREATE TABLE flow_classes (
    identifier TEXT PRIMARY KEY UNIQUE CHECK ( length(identifier) = 1 ),
    class_name TEXT NOT NULL,
    parent     TEXT DEFAULT NULL,
    notes      TEXT DEFAULT NULL,
    FOREIGN KEY(parent) REFERENCES flow_classes(identifier)
);

INSERT INTO flow_classes( identifier, class_name ) VALUES( 'B', 'boundary layer'                              );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'C', 'wall-bounded flow'                           );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'D', 'duct flow'                                   );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'E', 'external flow'                               );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'F', 'free shear flow'                             );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'G', 'isotropic flow'                              );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'H', 'homogeneous flow'                            );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'I', 'internal flow'                               );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'J', 'free jet'                                    );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'K', 'wall jet'                                    );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'M', 'mixing layer'                                );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'N', 'inhomogeneous flow'                          );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'R', 'flow with relative motion of the boundaries' );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'S', 'shear layer'                                 );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'U', 'flow'                                        );
INSERT INTO flow_classes( identifier, class_name ) VALUES( 'W', 'wake'                                        );

UPDATE flow_classes SET parent='U' WHERE identifier='H';
UPDATE flow_classes SET parent='U' WHERE identifier='N';

UPDATE flow_classes SET parent='H' WHERE identifier='G';

UPDATE flow_classes SET parent='N' WHERE identifier='S';

UPDATE flow_classes SET parent='S' WHERE identifier='C';
UPDATE flow_classes SET parent='S' WHERE identifier='F';

UPDATE flow_classes SET parent='F' WHERE identifier='J';
UPDATE flow_classes SET parent='F' WHERE identifier='M';
UPDATE flow_classes SET parent='F' WHERE identifier='W';

UPDATE flow_classes SET parent='C' WHERE identifier='E';
UPDATE flow_classes SET parent='C' WHERE identifier='I';

UPDATE flow_classes SET parent='E' WHERE identifier='B';
UPDATE flow_classes SET parent='E' WHERE identifier='K';

UPDATE flow_classes SET parent='I' WHERE identifier='D';
UPDATE flow_classes SET parent='I' WHERE identifier='R';

CREATE TABLE flow_regimes (
    identifier  TEXT PRIMARY KEY UNIQUE CHECK ( length(identifier) = 2 ),
    regime_name TEXT NOT NULL,
    notes       TEXT DEFAULT NULL
);

INSERT INTO flow_regimes( identifier, regime_name ) VALUES( 'LA',      'laminar flow' );
INSERT INTO flow_regimes( identifier, regime_name ) VALUES( 'TR', 'transitional flow' );
INSERT INTO flow_regimes( identifier, regime_name ) VALUES( 'TU',    'turbulent flow' );

CREATE TABLE fluids (
    identifier TEXT PRIMARY KEY UNIQUE,
    fluid_name TEXT NOT NULL,
    phase      TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO fluids( identifier, fluid_name, phase ) VALUES( 'dry_air',   'dry air',             'G' );
INSERT INTO fluids( identifier, fluid_name, phase ) VALUES( 'moist_air', 'moist air',           'M' );
INSERT INTO fluids( identifier, fluid_name, phase ) VALUES( 'water',     'water',               'L' );
INSERT INTO fluids( identifier, fluid_name, phase ) VALUES( 'steam',     'steam',               'G' );
INSERT INTO fluids( identifier, fluid_name, phase ) VALUES( 'thick_oil', 'thick oil (generic)', 'L' );

CREATE TABLE geometries (
    identifier    TEXT PRIMARY KEY UNIQUE,
    geometry_name TEXT NOT NULL,
    notes         TEXT DEFAULT NULL
);

INSERT INTO geometries( identifier, geometry_name ) VALUES( 'E',  'elliptical geometry' );
INSERT INTO geometries( identifier, geometry_name ) VALUES( 'R', 'rectangular geometry' );

CREATE TABLE measurement_techniques (
    identifier     TEXT PRIMARY KEY UNIQUE,
    technique_name TEXT NOT NULL,
    notes          TEXT DEFAULT NULL
);

INSERT INTO measurement_techniques( identifier, technique_name ) VALUES( 'FEB', 'floating element balance' );
INSERT INTO measurement_techniques( identifier, technique_name ) VALUES( 'IT',  'impact tube'              );
INSERT INTO measurement_techniques( identifier, technique_name ) VALUES( 'PST', 'Pitot-static tube'        );
INSERT INTO measurement_techniques( identifier, technique_name ) VALUES( 'SPT', 'static pressure tap'      );

CREATE TABLE point_labels (
    identifier TEXT PRIMARY KEY UNIQUE,
    label_name TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO point_labels( identifier, label_name ) VALUES( 'C', 'center-line' );
INSERT INTO point_labels( identifier, label_name ) VALUES( 'E', 'edge'        );
INSERT INTO point_labels( identifier, label_name ) VALUES( 'W', 'wall'        );

CREATE TABLE quantities (
    identifier           TEXT PRIMARY KEY UNIQUE,
    quantity_name        TEXT NOT NULL,
    length_exponent      REAL NOT NULL DEFAULT 0.0,
    mass_exponent        REAL NOT NULL DEFAULT 0.0,
    time_exponent        REAL NOT NULL DEFAULT 0.0,
    temperature_exponent REAL NOT NULL DEFAULT 0.0,
    note                 TEXT DEFAULT NULL
);

-- Series quantities
INSERT INTO quantities( identifier, quantity_name                                                ) VALUES( 'Re_inf',  'body Reynolds number'                     );
INSERT INTO quantities( identifier, quantity_name                                                ) VALUES( 'Sr',      'body Strouhal number'                     );
INSERT INTO quantities( identifier, quantity_name                                                ) VALUES( 'c_D',     'drag coefficient'                         );
INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent, time_exponent ) VALUES( 'F_D',     'drag force',             +1.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, quantity_name                                                ) VALUES( 'Ma_inf',  'freestream Mach number'                   );
INSERT INTO quantities( identifier, quantity_name, temperature_exponent                          ) VALUES( 'T_inf',   'freestream temperature', +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                ) VALUES( 'u_inf',   'freestream velocity',    +1.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent, time_exponent ) VALUES( 'F_L',     'lift force',             +1.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, quantity_name                                                ) VALUES( 'c_L',     'lift coefficient'                         );
INSERT INTO quantities( identifier, quantity_name, mass_exponent, time_exponent                  ) VALUES( 'mdot',    'mass flow rate',         +1.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                ) VALUES( 'Vdot',    'volume flow rate',       +3.0, -1.0       );

-- Station quantities
INSERT INTO quantities( identifier, quantity_name                                                ) VALUES( 'AR',      'aspect ratio'                                     );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                ) VALUES( 'u_b',     'bulk velocity',                  +1.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent                               ) VALUES( 'DELTA',   'Clauser thickness',              +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent                               ) VALUES( 'A',       'cross-sectional area',           +2.0             );
INSERT INTO quantities( identifier, quantity_name                                                ) VALUES( 'PI',      'equilibrium parameter'                            );
INSERT INTO quantities( identifier, quantity_name, length_exponent                               ) VALUES( 'd_h',     'hydraulic diameter',             +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent, time_exponent ) VALUES( 'dp/dx',   'pressure gradient',              -2.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, quantity_name                                                ) VALUES( 'RF',      'recovery factor'                                  );

/* Wall point quantities
 *
 * Arguably these quantities are station quantities, but there could be
 * multiple of them, one for each wall.  For the sake of simplicity, treat
 * these as point quantities, since that is what they are.  They should only
 * occur at walls, though.
 */
INSERT INTO quantities( identifier, quantity_name                                 ) VALUES( 'f_D',     'Darcy friction factor'                            );
INSERT INTO quantities( identifier, quantity_name                                 ) VALUES( 'f',       'Fanning friction factor'                          );
INSERT INTO quantities( identifier, quantity_name, temperature_exponent           ) VALUES( 'T_tau',   'Friction temperature',           +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent ) VALUES( 'u_tau',   'friction velocity',              +1.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name                                 ) VALUES( 'Ma_tau',  'friction Mach number'                             );
INSERT INTO quantities( identifier, quantity_name                                 ) VALUES( 'Re_tau',  'friction Reynolds number'                         );
INSERT INTO quantities( identifier, quantity_name                                 ) VALUES( 'c_f',     'local skin friction coefficient'                  );
INSERT INTO quantities( identifier, quantity_name, length_exponent                ) VALUES( 'k',       'roughness height',               +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent, note          ) VALUES( 'kappa_z', 'spanwise wall curvature',        -1.0,
                                                                                   'positive for external flows and negative for internal flows' );
INSERT INTO quantities( identifier, quantity_name, length_exponent                ) VALUES( 'kappa_x', 'streamwise wall curvature',      -1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent                ) VALUES( 'l_nu',    'viscous length scale',           +1.0             );

-- Point quantities
INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent, time_exponent        ) VALUES( 'mu',    'dynamic viscosity',                -1.0, +1.0, -1.0 );
INSERT INTO quantities( identifier, quantity_name                                                       ) VALUES( 'gamma', 'heat capacity ratio'                                );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'nu',    'kinematic viscosity',              +2.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name                                                       ) VALUES( 'Ma',    'Mach number'                                        );
INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent                       ) VALUES( 'rho',   'mass density',                     -3.0, +1.0       );
INSERT INTO quantities( identifier, quantity_name                                                       ) VALUES( 'Pr',    'Prandtl number'                                     );
INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent, time_exponent        ) VALUES( 'p',     'pressure',                         -1.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent, time_exponent        ) VALUES( 'tau',   'shear stress',                     -1.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, quantity_name, length_exponent                                      ) VALUES( 'z',     'spanwise coordinate',              +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'w',     'spanwise velocity',                +1.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'h',     'specific enthalpy',                +2.0, -2.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'e',     'specific internal energy',         +2.0, -2.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent, temperature_exponent ) VALUES( 'c_p',   'specific isobaric heat capacity',  +2.0, -2.0, -1.0 );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent, temperature_exponent ) VALUES( 'c_v',   'specific isochoric heat capacity', +2.0, -2.0, -1.0 );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'h_0',   'specific total enthalpy',          +2.0, -2.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'e_0',   'specific total internal energy',   +2.0, -2.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent                       ) VALUES( 'vbar',  'specific volume',                  +3.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'V',     'speed',                            +1.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'a',     'speed of sound',                   +1.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name, length_exponent                                      ) VALUES( 'x',     'streamwise coordinate',            +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'u',     'streamwise velocity',              +1.0, -1.0       );
INSERT INTO quantities( identifier, quantity_name, temperature_exponent                                 ) VALUES( 'T',     'temperature',                      +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent, mass_exponent, time_exponent        ) VALUES( 'p_0',   'total pressure',                   -1.0, +1.0, -2.0 );
INSERT INTO quantities( identifier, quantity_name, temperature_exponent                                 ) VALUES( 'T_0',   'total temperature',                +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent                                      ) VALUES( 'y',     'transverse coordinate',            +1.0             );
INSERT INTO quantities( identifier, quantity_name, length_exponent, time_exponent                       ) VALUES( 'v',     'transverse velocity',              +1.0, -1.0       );

CREATE TABLE study_types (
    identifier TEXT PRIMARY KEY UNIQUE CHECK ( length(identifier) = 1 ),
    type_name  TEXT NOT NULL,
    notes      TEXT DEFAULT NULL
);

INSERT INTO study_types( identifier, type_name ) VALUES( 'E', 'experimental study' );
INSERT INTO study_types( identifier, type_name ) VALUES( 'N',    'numerical study' );

CREATE TABLE studies (
    identifier            TEXT PRIMARY KEY UNIQUE,
    flow_class            TEXT NOT NULL DEFAULT 'U',
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
    coordinate_system    TEXT NOT NULL DEFAULT 'XYZ',
    working_fluid        TEXT NOT NULL,
    geometry             TEXT DEFAULT NULL,
    number_of_sides      TEXT DEFAULT NULL CHECK ( number_of_sides > 1 ),
    description          TEXT DEFAULT NULL,
    notes                TEXT DEFAULT NULL,
    FOREIGN KEY(working_fluid)     REFERENCES             fluids(identifier),
    FOREIGN KEY(coordinate_system) REFERENCES coordinate_systems(identifier),
    FOREIGN KEY(geometry)          REFERENCES         geometries(identifier)
);

CREATE TABLE stations (
    identifier                   TEXT PRIMARY KEY UNIQUE,
    station_number               INTEGER NOT NULL CHECK ( station_number > 0 AND station_number <=  999 ),
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
    FOREIGN KEY(previous_streamwise_station) REFERENCES     stations(identifier),
    FOREIGN KEY(next_streamwise_station)     REFERENCES     stations(identifier),
    FOREIGN KEY(previous_spanwise_station)   REFERENCES     stations(identifier),
    FOREIGN KEY(next_spanwise_station)       REFERENCES     stations(identifier)
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
    study_value           REAL NOT NULL,
    study_uncertainty     REAL DEFAULT NULL CHECK ( study_uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(study, quantity, measurement_technique),
    FOREIGN KEY(study)                 REFERENCES                studies(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);

CREATE TABLE series_values (
    series                TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    series_value          REAL NOT NULL,
    series_uncertainty    REAL DEFAULT NULL CHECK ( series_uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(series, quantity, measurement_technique),
    FOREIGN KEY(series)                REFERENCES                 series(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);

CREATE TABLE station_values (
    station               TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    station_value         REAL NOT NULL,
    station_uncertainty   REAL DEFAULT NULL CHECK ( station_uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(station, quantity, measurement_technique),
    FOREIGN KEY(station)               REFERENCES               stations(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);

CREATE TABLE point_values (
    point                 TEXT NOT NULL,
    quantity              TEXT NOT NULL,
    point_value           REAL NOT NULL,
    point_uncertainty     REAL DEFAULT NULL CHECK ( point_uncertainty >= 0.0 ),
    averaging_system      TEXT DEFAULT NULL,
    measurement_technique TEXT DEFAULT NULL,
    outlier               INTEGER NOT NULL DEFAULT 0 CHECK ( outlier = 0 OR outlier = 1 ),
    notes                 TEXT DEFAULT NULL,
    PRIMARY KEY(point, quantity, measurement_technique),
    FOREIGN KEY(point)                 REFERENCES                 points(identifier),
    FOREIGN KEY(quantity)              REFERENCES             quantities(identifier),
    FOREIGN KEY(averaging_system)      REFERENCES      averaging_systems(identifier),
    FOREIGN KEY(measurement_technique) REFERENCES measurement_techniques(identifier)
);
