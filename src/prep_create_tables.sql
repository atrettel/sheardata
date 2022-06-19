/*
Copyright (C) 2020-2022 Andrew Trettel

SPDX-License-Identifier: MIT
*/

PRAGMA foreign_keys = ON;

CREATE TABLE booleans (
    boolean_id   INTEGER PRIMARY KEY CHECK ( boolean_id IN (0,1) ),
    boolean_name TEXT UNIQUE NOT NULL
);

INSERT INTO booleans VALUES( TRUE,  "true"  );
INSERT INTO booleans VALUES( FALSE, "false" );

CREATE TABLE value_types (
    value_type_id   TEXT PRIMARY KEY,
    value_type_name TEXT UNIQUE NOT NULL
);

CREATE TABLE coordinate_systems (
    coordinate_system_id   TEXT PRIMARY KEY,
    coordinate_system_name TEXT UNIQUE NOT NULL
);

CREATE TABLE facility_classes (
    facility_class_id        TEXT PRIMARY KEY CHECK ( length(facility_class_id) = 1 ),
    facility_class_name      TEXT UNIQUE NOT NULL
);

CREATE TABLE facility_class_paths (
    facility_class_ancestor_id   TEXT NOT NULL,
    facility_class_descendant_id TEXT NOT NULL,
    facility_class_path_length   INTEGER NOT NULL CHECK ( facility_class_path_length >= 0 ),
    PRIMARY KEY(facility_class_ancestor_id, facility_class_descendant_id),
    FOREIGN KEY(facility_class_ancestor_id)   REFERENCES facility_classes(facility_class_id),
    FOREIGN KEY(facility_class_descendant_id) REFERENCES facility_classes(facility_class_id)
);

CREATE TABLE flow_classes (
    flow_class_id   TEXT PRIMARY KEY CHECK ( length(flow_class_id) = 1 ),
    flow_class_name TEXT UNIQUE NOT NULL
);

CREATE TABLE flow_class_paths (
    flow_class_ancestor_id   TEXT NOT NULL,
    flow_class_descendant_id TEXT NOT NULL,
    flow_class_path_length   INTEGER NOT NULL CHECK ( flow_class_path_length >= 0 ),
    PRIMARY KEY(flow_class_ancestor_id, flow_class_descendant_id),
    FOREIGN KEY(flow_class_ancestor_id)   REFERENCES flow_classes(flow_class_id),
    FOREIGN KEY(flow_class_descendant_id) REFERENCES flow_classes(flow_class_id)
);

CREATE TABLE flow_regimes (
    flow_regime_id   TEXT PRIMARY KEY,
    flow_regime_name TEXT UNIQUE NOT NULL
);

CREATE TABLE phases (
    phase_id   TEXT PRIMARY KEY,
    phase_name TEXT NOT NULL
);

CREATE TABLE elements (
    atomic_number              INTEGER PRIMARY KEY CHECK ( atomic_number > 0 ),
    element_symbol             TEXT UNIQUE NOT NULL CHECK ( length(element_symbol) IN (1,2) ),
    element_name               TEXT UNIQUE NOT NULL,
    standard_atomic_weight_min REAL CHECK ( standard_atomic_weight_min > 0.0 ),
    standard_atomic_weight_max REAL CHECK ( standard_atomic_weight_max > 0.0 ),
    conventional_atomic_weight REAL CHECK ( conventional_atomic_weight > 0.0 )
);

CREATE TABLE fluids (
    fluid_id          TEXT PRIMARY KEY,
    fluid_name        TEXT UNIQUE NOT NULL,
    phase_id          TEXT NOT NULL,
    molecular_formula TEXT DEFAULT NULL,
    FOREIGN KEY(phase_id) REFERENCES phases(phase_id)
);

/*
TODO: consider creating a hierarchy of geometries organized by the number of
sides an object has.  For example, rectangles are a particular form of
quadrilaterals, and circles are a particular form of ellipses, etc.  The point
of this is to be able to select different duct flow cross sections or airfoil
sections in a useful manner.  I still need to think about this more.
cursor.execute(
*/
CREATE TABLE geometries (
    geometry_id   TEXT PRIMARY KEY,
    geometry_name TEXT UNIQUE NOT NULL
);

CREATE TABLE instrument_classes (
    instrument_class_id        TEXT PRIMARY KEY,
    instrument_class_name      TEXT UNIQUE NOT NULL,
    intrusive                  INTEGER NOT NULL DEFAULT FALSE,
    FOREIGN KEY(intrusive) REFERENCES booleans(boolean_id)
);

CREATE TABLE instrument_class_paths (
    instrument_class_ancestor_id   TEXT NOT NULL,
    instrument_class_descendant_id TEXT NOT NULL,
    instrument_class_path_length   INTEGER NOT NULL CHECK ( instrument_class_path_length >= 0 ),
    PRIMARY KEY(instrument_class_ancestor_id, instrument_class_descendant_id),
    FOREIGN KEY(instrument_class_ancestor_id)   REFERENCES instrument_classes(instrument_class_id),
    FOREIGN KEY(instrument_class_descendant_id) REFERENCES instrument_classes(instrument_class_id)
);

CREATE TABLE notes (
    note_id       INTEGER PRIMARY KEY CHECK ( note_id > 0 ),
    note_contents TEXT UNIQUE NOT NULL
);

CREATE TABLE point_labels (
    point_label_id   TEXT PRIMARY KEY,
    point_label_name TEXT UNIQUE NOT NULL
);

/*
I have implemented all quantities in the same table, though I divide them up
into categories based on whether they apply to a study, series, station, point,
or facilities.  Separate tables may be a better design choice in the long run
because it enforces the division, but for the moment I am leaving it with only
one table for simplicity.

The advantage of a single table is that it grants the ability to apply some
quantities to both a point and a station, for example.  Coordinates are
nominally point quantities, but it may also be a good idea to specify the x and
z coordinates at the station level too if those coordinates are in fact
constant for an entire station (they most likely will be).  That would allow
for `SELECT` statements at the station level while also retaining the relevant
data at another level.  The problem is that this duplication violates the idea
that data should only be in one particular place in the database, and for that
reason I have only implemented coordinates as point quantities so far.

Now that I have added quantities for the facilities too, it seems like having a
single table for quantities is better, since I can use point quantities as
corresponding facility quantities without having to add them a second time.
This benefit seems to favor a single table.
*/
CREATE TABLE quantities (
    quantity_id          TEXT PRIMARY KEY,
    quantity_name        TEXT UNIQUE NOT NULL,
    time_exponent        REAL NOT NULL DEFAULT 0.0,
    length_exponent      REAL NOT NULL DEFAULT 0.0,
    mass_exponent        REAL NOT NULL DEFAULT 0.0,
    current_exponent     REAL NOT NULL DEFAULT 0.0,
    temperature_exponent REAL NOT NULL DEFAULT 0.0,
    amount_exponent      REAL NOT NULL DEFAULT 0.0,
    minimum_value        REAL NOT NULL,
    maximum_value        REAL NOT NULL
);

CREATE TABLE quantity_latex_codes (
    quantity_id               TEXT NOT NULL,
    value_type_id             TEXT NOT NULL,
    quantity_latex_symbol     TEXT NOT NULL,
    quantity_latex_definition TEXT DEFAULT NULL,
    notes                     TEXT DEFAULT NULL,
    PRIMARY KEY(quantity_id, value_type_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id)
);

/*
TODO: Right now I use the citation key as part of the primary key.  That makes
it possible to have multiple sets of data for a given pressure and temperature
and fluid, and I am torn at the moment as to whether or not I want to allow
that.  For the moment, I will allow it, but I am writing this note so that I
think about it more later.
*/
CREATE TABLE fluid_property_values (
    pressure                   REAL NOT NULL CHECK (    pressure > 0.0 ),
    temperature                REAL NOT NULL CHECK ( temperature > 0.0 ),
    fluid_id                   TEXT NOT NULL,
    citation_key               TEXT NOT NULL,
    quantity_id                TEXT NOT NULL,
    fluid_property_value       REAL NOT NULL,
    fluid_property_uncertainty REAL DEFAULT NULL CHECK ( fluid_property_uncertainty >= 0.0 ),
    preferred                  INTEGER NOT NULL DEFAULT FALSE,
    PRIMARY KEY(pressure, temperature, fluid_id, citation_key, quantity_id),
    FOREIGN KEY(quantity_id) REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)    REFERENCES fluids(fluid_id),
    FOREIGN KEY(preferred)   REFERENCES booleans(boolean_id)
);

CREATE TABLE study_types (
    study_type_id   TEXT PRIMARY KEY,
    study_type_name TEXT NOT NULL
);

/*
TODO: Certains fields should only be allowed if the facility is an experimental
facility, etc.  I need to add triggers or more advanced checks for these.

TODO: Columns to add later:
- operational status
- open test section: yes or no?  This would be easier to manage if the sequence
  of parts of a facility is specified, at which point there would be two kinds
  of test sections (open and closed).
*/
CREATE TABLE facilities (
    facility_id             INTEGER PRIMARY KEY AUTOINCREMENT CHECK ( facility_id > 0 ),
    facility_class_id       TEXT NOT NULL,
    facility_name           TEXT UNIQUE NOT NULL,
    iso_country_code        TEXT NOT NULL CHECK ( length(iso_country_code) = 3 ),
    organization_name       TEXT DEFAULT NULL,
    start_year              INTEGER DEFAULT NULL,
    end_year                INTEGER DEFAULT NULL,
    predecessor_facility_id INTEGER DEFAULT NULL,
    successor_facility_id   INTEGER DEFAULT NULL,
    FOREIGN KEY(facility_class_id)       REFERENCES facility_classes(facility_class_id),
    FOREIGN KEY(predecessor_facility_id) REFERENCES facilities(facility_id),
    FOREIGN KEY(successor_facility_id)   REFERENCES facilities(facility_id)
);

CREATE TABLE instruments (
    instrument_id       INTEGER PRIMARY KEY AUTOINCREMENT CHECK ( instrument_id > 0 ),
    instrument_class_id TEXT NOT NULL,
    instrument_name     TEXT DEFAULT NULL,
    FOREIGN KEY(instrument_class_id) REFERENCES instrument_classes(instrument_class_id)
);

CREATE TABLE models (
    model_id   INTEGER PRIMARY KEY AUTOINCREMENT CHECK ( model_id > 0 ),
    model_name TEXT DEFAULT NULL
);

CREATE TABLE studies (
    study_id          TEXT PRIMARY KEY,
    flow_class_id     TEXT NOT NULL DEFAULT 'U',
    year              INTEGER NOT NULL CHECK (        year  >= 0 AND         year <= 9999 ),
    study_number      INTEGER NOT NULL CHECK ( study_number >  0 AND study_number <=  999 ),
    study_type_id     TEXT NOT NULL,
    outlier           INTEGER NOT NULL DEFAULT FALSE,
    study_description TEXT DEFAULT NULL,
    study_provenance  TEXT DEFAULT NULL,
    FOREIGN KEY(flow_class_id) REFERENCES flow_classes(flow_class_id),
    FOREIGN KEY(study_type_id) REFERENCES study_types(study_type_id),
    FOREIGN KEY(outlier)       REFERENCES booleans(boolean_id)
);

CREATE TABLE series (
    series_id            TEXT PRIMARY KEY,
    study_id             TEXT NOT NULL,
    series_number        INTEGER NOT NULL CHECK ( series_number > 0 AND series_number <= 999 ),
    number_of_dimensions INTEGER NOT NULL DEFAULT 2 CHECK ( number_of_dimensions > 0 AND number_of_dimensions <= 3 ),
    coordinate_system_id TEXT NOT NULL DEFAULT 'XYZ',
    geometry_id          TEXT DEFAULT NULL,
    facility_id          INTEGER DEFAULT NULL,
    model_id             INTEGER DEFAULT NULL,
    outlier              INTEGER NOT NULL DEFAULT FALSE,
    series_description   TEXT DEFAULT NULL,
    FOREIGN KEY(study_id)             REFERENCES studies(study_id),
    FOREIGN KEY(coordinate_system_id) REFERENCES coordinate_systems(coordinate_system_id),
    FOREIGN KEY(geometry_id)          REFERENCES geometries(geometry_id),
    FOREIGN KEY(facility_id)          REFERENCES facilities(facility_id),
    FOREIGN KEY(model_id)             REFERENCES models(model_id),
    FOREIGN KEY(outlier)              REFERENCES booleans(boolean_id)
);

CREATE TABLE stations (
    station_id                     TEXT PRIMARY KEY,
    series_id                      TEXT NOT NULL,
    station_number                 INTEGER NOT NULL CHECK ( station_number > 0 AND station_number <= 999 ),
    flow_regime_id                 TEXT DEFAULT NULL,
    previous_streamwise_station_id TEXT DEFAULT NULL,
    next_streamwise_station_id     TEXT DEFAULT NULL,
    previous_spanwise_station_id   TEXT DEFAULT NULL,
    next_spanwise_station_id       TEXT DEFAULT NULL,
    outlier                        INTEGER NOT NULL DEFAULT FALSE,
    station_description            TEXT DEFAULT NULL,
    FOREIGN KEY(series_id)                      REFERENCES series(series_id),
    FOREIGN KEY(flow_regime_id)                 REFERENCES flow_regimes(flow_regime_id),
    FOREIGN KEY(previous_streamwise_station_id) REFERENCES stations(station_id),
    FOREIGN KEY(next_streamwise_station_id)     REFERENCES stations(station_id),
    FOREIGN KEY(previous_spanwise_station_id)   REFERENCES stations(station_id),
    FOREIGN KEY(next_spanwise_station_id)       REFERENCES stations(station_id),
    FOREIGN KEY(outlier)                        REFERENCES booleans(boolean_id)
);

CREATE TABLE points (
    point_id          TEXT PRIMARY KEY,
    station_id        TEXT NOT NULL,
    point_number      INTEGER NOT NULL CHECK ( point_number > 0 AND point_number <= 9999 ),
    point_label_id    TEXT DEFAULT NULL,
    outlier           INTEGER NOT NULL DEFAULT FALSE,
    point_description TEXT DEFAULT NULL,
    FOREIGN KEY(station_id)     REFERENCES stations(station_id),
    FOREIGN KEY(point_label_id) REFERENCES point_labels(point_label_id),
    FOREIGN KEY(outlier)        REFERENCES booleans(boolean_id)
);

/*
Sources (literature references)
*/
CREATE TABLE source_classifications (
    source_classification_id   INTEGER PRIMARY KEY CHECK ( source_classification_id IN (1,2,3) ),
    source_classification_name TEXT NOT NULL
);

CREATE TABLE study_sources (
    study_id                 TEXT NOT NULL,
    citation_key             TEXT NOT NULL,
    source_classification_id INTEGER NOT NULL,
    PRIMARY KEY(study_id, citation_key),
    FOREIGN KEY(study_id)                 REFERENCES studies(study_id),
    FOREIGN KEY(source_classification_id) REFERENCES source_classifications(source_classification_id)
);

CREATE TABLE facility_sources (
    facility_id              TEXT NOT NULL,
    citation_key             TEXT NOT NULL,
    source_classification_id INTEGER NOT NULL,
    PRIMARY KEY(facility_id, citation_key),
    FOREIGN KEY(facility_id) REFERENCES facilities(facility_id),
    FOREIGN KEY(source_classification_id) REFERENCES source_classifications(source_classification_id)
);

CREATE TABLE instrument_sources (
    instrument_id            TEXT NOT NULL,
    citation_key             TEXT NOT NULL,
    source_classification_id INTEGER NOT NULL,
    PRIMARY KEY(instrument_id, citation_key),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id),
    FOREIGN KEY(source_classification_id) REFERENCES source_classifications(source_classification_id)
);

CREATE TABLE model_sources (
    model_id                 TEXT NOT NULL,
    citation_key             TEXT NOT NULL,
    source_classification_id INTEGER NOT NULL,
    PRIMARY KEY(model_id, citation_key),
    FOREIGN KEY(model_id) REFERENCES models(model_id),
    FOREIGN KEY(source_classification_id) REFERENCES source_classifications(source_classification_id)
);

CREATE TABLE series_components (
    series_id TEXT NOT NULL,
    fluid_id  TEXT NOT NULL,
    PRIMARY KEY(series_id, fluid_id),
    FOREIGN KEY(series_id) REFERENCES series(series_id),
    FOREIGN KEY(fluid_id)  REFERENCES fluids(fluid_id)
);

CREATE TABLE study_values (
    study_id          TEXT NOT NULL,
    quantity_id       TEXT NOT NULL,
    fluid_id          TEXT NOT NULL,
    value_type_id     TEXT NOT NULL,
    instrument_set    INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    study_value       REAL NOT NULL,
    study_uncertainty REAL DEFAULT NULL CHECK ( study_uncertainty >= 0.0 ),
    corrected         INTEGER NOT NULL DEFAULT FALSE,
    outlier           INTEGER NOT NULL DEFAULT FALSE,
    PRIMARY KEY(study_id, quantity_id, fluid_id, value_type_id, instrument_set),
    FOREIGN KEY(study_id)      REFERENCES studies(study_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(corrected)     REFERENCES booleans(boolean_id),
    FOREIGN KEY(outlier)       REFERENCES booleans(boolean_id)
);

CREATE TRIGGER study_values_within_quantity_bounds
AFTER INSERT ON study_values
WHEN EXISTS (
    SELECT ( minimum_value <= NEW.study_value AND NEW.study_value <= maximum_value ) AS study_value_in_bounds
    FROM quantities
    WHERE ( NEW.quantity_id = quantities.quantity_id AND study_value_in_bounds = 0 )
)
BEGIN
    SELECT RAISE( FAIL, "study value is not within the allowed bounds for the quantity" );
END;

CREATE TABLE series_values (
    series_id          TEXT NOT NULL,
    quantity_id        TEXT NOT NULL,
    fluid_id           TEXT NOT NULL,
    value_type_id      TEXT NOT NULL,
    instrument_set     INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    series_value       REAL NOT NULL,
    series_uncertainty REAL DEFAULT NULL CHECK ( series_uncertainty >= 0.0 ),
    corrected          INTEGER NOT NULL DEFAULT FALSE,
    outlier            INTEGER NOT NULL DEFAULT FALSE,
    PRIMARY KEY(series_id, quantity_id, fluid_id, value_type_id, instrument_set),
    FOREIGN KEY(series_id)     REFERENCES series(series_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(corrected)     REFERENCES booleans(boolean_id),
    FOREIGN KEY(outlier)       REFERENCES booleans(boolean_id)
);

CREATE TRIGGER series_values_within_quantity_bounds
AFTER INSERT ON series_values
WHEN EXISTS (
    SELECT ( minimum_value <= NEW.series_value AND NEW.series_value <= maximum_value ) AS series_value_in_bounds
    FROM quantities
    WHERE ( NEW.quantity_id = quantities.quantity_id AND series_value_in_bounds = 0 )
)
BEGIN
    SELECT RAISE( FAIL, "series value is not within the allowed bounds for the quantity" );
END;

CREATE TABLE station_values (
    station_id          TEXT NOT NULL,
    quantity_id         TEXT NOT NULL,
    fluid_id            TEXT NOT NULL,
    value_type_id       TEXT NOT NULL,
    instrument_set      INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    station_value       REAL NOT NULL,
    station_uncertainty REAL DEFAULT NULL CHECK ( station_uncertainty >= 0.0 ),
    corrected           INTEGER NOT NULL DEFAULT FALSE,
    outlier             INTEGER NOT NULL DEFAULT FALSE,
    PRIMARY KEY(station_id, quantity_id, fluid_id, value_type_id, instrument_set),
    FOREIGN KEY(station_id)    REFERENCES stations(station_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(corrected)     REFERENCES booleans(boolean_id),
    FOREIGN KEY(outlier)       REFERENCES booleans(boolean_id)
);

CREATE TRIGGER station_values_within_quantity_bounds
AFTER INSERT ON station_values
WHEN EXISTS (
    SELECT ( minimum_value <= NEW.station_value AND NEW.station_value <= maximum_value ) AS station_value_in_bounds
    FROM quantities
    WHERE ( NEW.quantity_id = quantities.quantity_id AND station_value_in_bounds = 0 )
)
BEGIN
    SELECT RAISE( FAIL, "station value is not within the allowed bounds for the quantity" );
END;

CREATE TABLE point_values (
    point_id          TEXT NOT NULL,
    quantity_id       TEXT NOT NULL,
    fluid_id          TEXT NOT NULL,
    value_type_id     TEXT NOT NULL,
    instrument_set    INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    point_value       REAL NOT NULL,
    point_uncertainty REAL DEFAULT NULL CHECK ( point_uncertainty >= 0.0 ),
    corrected         INTEGER NOT NULL DEFAULT FALSE,
    outlier           INTEGER NOT NULL DEFAULT FALSE,
    PRIMARY KEY(point_id, quantity_id, fluid_id, value_type_id, instrument_set),
    FOREIGN KEY(point_id)      REFERENCES points(point_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(corrected)     REFERENCES booleans(boolean_id),
    FOREIGN KEY(outlier)       REFERENCES booleans(boolean_id)
);

CREATE TRIGGER point_values_within_quantity_bounds
AFTER INSERT ON point_values
WHEN EXISTS (
    SELECT ( minimum_value <= NEW.point_value AND NEW.point_value <= maximum_value ) AS point_value_in_bounds
    FROM quantities
    WHERE ( NEW.quantity_id = quantities.quantity_id AND point_value_in_bounds = 0 )
)
BEGIN
    SELECT RAISE( FAIL, "point value is not within the allowed bounds for the quantity" );
END;

CREATE TABLE facility_values (
    facility_id          TEXT NOT NULL,
    quantity_id          TEXT NOT NULL,
    value_type_id        TEXT NOT NULL,
    facility_value       REAL NOT NULL,
    facility_uncertainty REAL DEFAULT NULL CHECK ( facility_uncertainty >= 0.0 ),
    PRIMARY KEY(facility_id, quantity_id, value_type_id),
    FOREIGN KEY(facility_id)   REFERENCES facilities(facility_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id)
);

CREATE TRIGGER facility_values_within_quantity_bounds
AFTER INSERT ON facility_values
WHEN EXISTS (
    SELECT ( minimum_value <= NEW.facility_value AND NEW.facility_value <= maximum_value ) AS facility_value_in_bounds
    FROM quantities
    WHERE ( NEW.quantity_id = quantities.quantity_id AND facility_value_in_bounds = 0 )
)
BEGIN
    SELECT RAISE( FAIL, "facility value is not within the allowed bounds for the quantity" );
END;

CREATE TABLE instrument_values (
    instrument_id          TEXT NOT NULL,
    quantity_id            TEXT NOT NULL,
    value_type_id          TEXT NOT NULL,
    instrument_value       REAL NOT NULL,
    instrument_uncertainty REAL DEFAULT NULL CHECK ( instrument_uncertainty >= 0.0 ),
    PRIMARY KEY(instrument_id, quantity_id, value_type_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id)
);

CREATE TRIGGER instrument_values_within_quantity_bounds
AFTER INSERT ON instrument_values
WHEN EXISTS (
    SELECT ( minimum_value <= NEW.instrument_value AND NEW.instrument_value <= maximum_value ) AS instrument_value_in_bounds
    FROM quantities
    WHERE ( NEW.quantity_id = quantities.quantity_id AND instrument_value_in_bounds = 0 )
)
BEGIN
    SELECT RAISE( FAIL, "instrument value is not within the allowed bounds for the quantity" );
END;

CREATE TABLE model_values (
    model_id          TEXT NOT NULL,
    quantity_id       TEXT NOT NULL,
    value_type_id     TEXT NOT NULL,
    model_value       REAL NOT NULL,
    model_uncertainty REAL DEFAULT NULL CHECK ( model_uncertainty >= 0.0 ),
    PRIMARY KEY(model_id, quantity_id, value_type_id),
    FOREIGN KEY(model_id) REFERENCES models(model_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id)
);

CREATE TRIGGER model_values_within_quantity_bounds
AFTER INSERT ON model_values
WHEN EXISTS (
    SELECT ( minimum_value <= NEW.model_value AND NEW.model_value <= maximum_value ) AS model_value_in_bounds
    FROM quantities
    WHERE ( NEW.quantity_id = quantities.quantity_id AND model_value_in_bounds = 0 )
)
BEGIN
    SELECT RAISE( FAIL, "model value is not within the allowed bounds for the quantity" );
END;

CREATE TABLE study_values_it (
    study_id       TEXT NOT NULL,
    quantity_id    TEXT NOT NULL,
    fluid_id       TEXT NOT NULL,
    value_type_id  TEXT NOT NULL,
    instrument_set INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    instrument_id  INTEGER NOT NULL,
    PRIMARY KEY(study_id, quantity_id, fluid_id, value_type_id, instrument_set, instrument_id),
    FOREIGN KEY(study_id)      REFERENCES studies(study_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id)
);

CREATE TABLE series_values_it (
    series_id      TEXT NOT NULL,
    quantity_id    TEXT NOT NULL,
    fluid_id       TEXT NOT NULL,
    value_type_id  TEXT NOT NULL,
    instrument_set INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    instrument_id  TEXT NOT NULL,
    PRIMARY KEY(series_id, quantity_id, fluid_id, value_type_id, instrument_set, instrument_id),
    FOREIGN KEY(series_id)     REFERENCES series(series_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id)
);

CREATE TABLE station_values_it (
    station_id     TEXT NOT NULL,
    quantity_id    TEXT NOT NULL,
    fluid_id       TEXT NOT NULL,
    value_type_id  TEXT NOT NULL,
    instrument_set INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    instrument_id  TEXT NOT NULL,
    PRIMARY KEY(station_id, quantity_id, fluid_id, value_type_id, instrument_set, instrument_id),
    FOREIGN KEY(station_id)    REFERENCES stations(station_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id)
);

CREATE TABLE point_values_it (
    point_id       TEXT NOT NULL,
    quantity_id    TEXT NOT NULL,
    fluid_id       TEXT NOT NULL,
    value_type_id  TEXT NOT NULL,
    instrument_set INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    instrument_id  TEXT NOT NULL,
    PRIMARY KEY(point_id, quantity_id, fluid_id, value_type_id, instrument_set, instrument_id),
    FOREIGN KEY(point_id)      REFERENCES points(point_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id)
);

CREATE TABLE study_notes (
    study_id TEXT NOT NULL,
    note_id  INTEGER NOT NULL,
    PRIMARY KEY(study_id, note_id),
    FOREIGN KEY(study_id) REFERENCES studies(study_id),
    FOREIGN KEY(note_id)  REFERENCES notes(note_id)
);

CREATE TABLE study_value_notes (
    study_id       TEXT NOT NULL,
    quantity_id    TEXT NOT NULL,
    fluid_id       TEXT NOT NULL,
    value_type_id  TEXT NOT NULL,
    instrument_set INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    note_id        INTEGER NOT NULL,
    PRIMARY KEY(study_id, quantity_id, fluid_id, value_type_id, instrument_set, note_id),
    FOREIGN KEY(study_id)      REFERENCES studies(study_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE series_notes (
    series_id TEXT NOT NULL,
    note_id   INTEGER NOT NULL,
    PRIMARY KEY(series_id, note_id),
    FOREIGN KEY(series_id) REFERENCES series(series_id),
    FOREIGN KEY(note_id)   REFERENCES notes(note_id)
);

CREATE TABLE series_value_notes (
    series_id      TEXT NOT NULL,
    quantity_id    TEXT NOT NULL,
    fluid_id       TEXT NOT NULL,
    value_type_id  TEXT NOT NULL,
    instrument_set INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    note_id        INTEGER NOT NULL,
    PRIMARY KEY(series_id, quantity_id, fluid_id, value_type_id, instrument_set, note_id),
    FOREIGN KEY(series_id)     REFERENCES series(series_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE station_notes (
    station_id TEXT NOT NULL,
    note_id    INTEGER NOT NULL,
    PRIMARY KEY(station_id, note_id),
    FOREIGN KEY(station_id) REFERENCES stations(station_id),
    FOREIGN KEY(note_id)    REFERENCES notes(note_id)
);

CREATE TABLE station_value_notes (
    station_id     TEXT NOT NULL,
    quantity_id    TEXT NOT NULL,
    fluid_id       TEXT NOT NULL,
    value_type_id  TEXT NOT NULL,
    instrument_set INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    note_id        INTEGER NOT NULL,
    PRIMARY KEY(station_id, quantity_id, fluid_id, value_type_id, instrument_set, note_id),
    FOREIGN KEY(station_id)    REFERENCES stations(station_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE point_notes (
    point_id TEXT NOT NULL,
    note_id  INTEGER NOT NULL,
    PRIMARY KEY(point_id, note_id),
    FOREIGN KEY(point_id) REFERENCES points(point_id),
    FOREIGN KEY(note_id)  REFERENCES notes(note_id)
);

CREATE TABLE point_value_notes (
    point_id       TEXT NOT NULL,
    quantity_id    TEXT NOT NULL,
    fluid_id       TEXT NOT NULL,
    value_type_id  TEXT NOT NULL,
    instrument_set INTEGER NOT NULL DEFAULT 1 CHECK ( instrument_set > 0 ),
    note_id        INTEGER NOT NULL,
    PRIMARY KEY(point_id, quantity_id, fluid_id, value_type_id, instrument_set, note_id),
    FOREIGN KEY(point_id)      REFERENCES points(point_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(fluid_id)      REFERENCES fluids(fluid_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE facility_notes (
    facility_id TEXT NOT NULL,
    note_id     INTEGER NOT NULL,
    PRIMARY KEY(facility_id, note_id),
    FOREIGN KEY(facility_id) REFERENCES facilities(facility_id),
    FOREIGN KEY(note_id)     REFERENCES notes(note_id)
);

CREATE TABLE facility_value_notes (
    facility_id   TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    note_id       INTEGER NOT NULL,
    PRIMARY KEY(facility_id, quantity_id, value_type_id, note_id),
    FOREIGN KEY(facility_id)   REFERENCES facilities(facility_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE instrument_notes (
    instrument_id TEXT NOT NULL,
    note_id       INTEGER NOT NULL,
    PRIMARY KEY(instrument_id, note_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE instrument_value_notes (
    instrument_id TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    note_id       INTEGER NOT NULL,
    PRIMARY KEY(instrument_id, quantity_id, value_type_id, note_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE model_notes (
    model_id TEXT NOT NULL,
    note_id  INTEGER NOT NULL,
    PRIMARY KEY(model_id, note_id),
    FOREIGN KEY(model_id) REFERENCES models(model_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE model_value_notes (
    model_id TEXT NOT NULL,
    quantity_id   TEXT NOT NULL,
    value_type_id TEXT NOT NULL,
    note_id       INTEGER NOT NULL,
    PRIMARY KEY(model_id, quantity_id, value_type_id, note_id),
    FOREIGN KEY(model_id)      REFERENCES models(model_id),
    FOREIGN KEY(quantity_id)   REFERENCES quantities(quantity_id),
    FOREIGN KEY(value_type_id) REFERENCES value_types(value_type_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE compilations (
    compilation_id   INTEGER PRIMARY KEY CHECK ( compilation_id >= 0 ),
    compilation_name TEXT UNIQUE NOT NULL
);

CREATE TABLE compilation_sources (
    compilation_id INTEGER NOT NULL,
    citation_key   TEXT NOT NULL,
    PRIMARY KEY(compilation_id, citation_key),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);

CREATE TABLE study_external_ids (
    study_id          TEXT NOT NULL,
    compilation_id    INTEGER NOT NULL,
    study_external_id TEXT NOT NULL,
    PRIMARY KEY(study_id, compilation_id),
    FOREIGN KEY(study_id)       REFERENCES studies(study_id),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);

CREATE TABLE series_external_ids (
    series_id          TEXT NOT NULL,
    compilation_id     INTEGER NOT NULL,
    series_external_id TEXT NOT NULL,
    PRIMARY KEY(series_id, compilation_id),
    FOREIGN KEY(series_id)      REFERENCES series(series_id),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);

CREATE TABLE station_external_ids (
    station_id          TEXT NOT NULL,
    compilation_id      INTEGER NOT NULL,
    station_external_id TEXT NOT NULL,
    PRIMARY KEY(station_id, compilation_id),
    FOREIGN KEY(station_id)     REFERENCES stations(station_id),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);

CREATE TABLE point_external_ids (
    point_id          TEXT NOT NULL,
    compilation_id    INTEGER NOT NULL,
    point_external_id TEXT NOT NULL,
    PRIMARY KEY(point_id, compilation_id),
    FOREIGN KEY(point_id)       REFERENCES points(point_id),
    FOREIGN KEY(compilation_id) REFERENCES compilations(compilation_id)
);

