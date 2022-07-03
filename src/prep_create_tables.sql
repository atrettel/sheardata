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
    flow_class_id   TEXT PRIMARY KEY CHECK ( length(flow_class_id) = 1 AND flow_class_id != 'O' ),
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

CREATE TABLE model_classes (
    model_class_id   TEXT PRIMARY KEY,
    model_class_name TEXT UNIQUE NOT NULL
);

CREATE TABLE model_class_paths (
    model_class_ancestor_id   TEXT NOT NULL,
    model_class_descendant_id TEXT NOT NULL,
    model_class_path_length   INTEGER NOT NULL CHECK ( model_class_path_length >= 0 ),
    PRIMARY KEY(model_class_ancestor_id, model_class_descendant_id),
    FOREIGN KEY(model_class_ancestor_id)   REFERENCES model_classes(model_class_id),
    FOREIGN KEY(model_class_descendant_id) REFERENCES model_classes(model_class_id)
);

CREATE TABLE notes (
    note_id       INTEGER PRIMARY KEY CHECK ( note_id > 0 ),
    note_contents TEXT UNIQUE NOT NULL
);

CREATE TABLE point_labels (
    point_label_id   TEXT PRIMARY KEY,
    point_label_name TEXT UNIQUE NOT NULL
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

TODO: Create a closure table for the predecessor and successor facilities.
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
    model_id       INTEGER PRIMARY KEY AUTOINCREMENT CHECK ( model_id > 0 ),
    model_class_id TEXT NOT NULL,
    model_name     TEXT DEFAULT NULL,
    FOREIGN KEY(model_class_id) REFERENCES model_classes(model_class_id)
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

/*
TODO: Consider removing the number of dimensions and moving the specification
of periodicity from the stations table to the series table.
*/
CREATE TABLE series (
    series_id            TEXT PRIMARY KEY,
    study_id             TEXT NOT NULL,
    series_number        INTEGER NOT NULL CHECK ( series_number > 0 AND series_number <= 999 ),
    number_of_dimensions INTEGER NOT NULL DEFAULT 2 CHECK ( number_of_dimensions > 0 AND number_of_dimensions <= 3 ),
    facility_id          INTEGER DEFAULT NULL,
    model_id             INTEGER DEFAULT NULL,
    outlier              INTEGER NOT NULL DEFAULT FALSE,
    series_description   TEXT DEFAULT NULL,
    FOREIGN KEY(study_id)             REFERENCES studies(study_id),
    FOREIGN KEY(facility_id)          REFERENCES facilities(facility_id),
    FOREIGN KEY(model_id)             REFERENCES models(model_id),
    FOREIGN KEY(outlier)              REFERENCES booleans(boolean_id)
);

CREATE TABLE stations (
    station_id                     TEXT PRIMARY KEY,
    series_id                      TEXT NOT NULL,
    station_number                 INTEGER NOT NULL CHECK ( station_number > 0 AND station_number <= 999 ),
    flow_regime_id                 TEXT DEFAULT NULL,
    streamwise_periodic            INTEGER NOT NULL DEFAULT FALSE,
    spanwise_periodic              INTEGER NOT NULL DEFAULT TRUE,
    outlier                        INTEGER NOT NULL DEFAULT FALSE,
    station_description            TEXT DEFAULT NULL,
    FOREIGN KEY(series_id)           REFERENCES series(series_id),
    FOREIGN KEY(flow_regime_id)      REFERENCES flow_regimes(flow_regime_id),
    FOREIGN KEY(streamwise_periodic) REFERENCES booleans(boolean_id),
    FOREIGN KEY(spanwise_periodic)   REFERENCES booleans(boolean_id),
    FOREIGN KEY(outlier)             REFERENCES booleans(boolean_id)
);

/*
TODO: Come up with a better way to represent this.  I currently have
implemented this using a closure table approach, but I want to ensure that the
stations can be marked as periodic too.  As a kludge, I added a column the
stations table to mark it as periodic in that particular direct.

TODO: At the moment I have implemented this as a single table for both
streamwise and spanwise variations in the station locations.  At the moment,
this appears to be more general, but I am unsure about this as a design choice.
*/
CREATE TABLE station_paths (
    station_ancestor_id   TEXT NOT NULL,
    station_descendant_id TEXT NOT NULL,
    station_path_length   INTEGER NOT NULL CHECK ( station_path_length >= 0 ),
    PRIMARY KEY(station_ancestor_id, station_descendant_id),
    FOREIGN KEY(station_ancestor_id)   REFERENCES stations(station_id),
    FOREIGN KEY(station_descendant_id) REFERENCES stations(station_id)
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

CREATE TABLE study_notes (
    study_id TEXT NOT NULL,
    note_id  INTEGER NOT NULL,
    PRIMARY KEY(study_id, note_id),
    FOREIGN KEY(study_id) REFERENCES studies(study_id),
    FOREIGN KEY(note_id)  REFERENCES notes(note_id)
);

CREATE TABLE series_notes (
    series_id TEXT NOT NULL,
    note_id   INTEGER NOT NULL,
    PRIMARY KEY(series_id, note_id),
    FOREIGN KEY(series_id) REFERENCES series(series_id),
    FOREIGN KEY(note_id)   REFERENCES notes(note_id)
);

CREATE TABLE station_notes (
    station_id TEXT NOT NULL,
    note_id    INTEGER NOT NULL,
    PRIMARY KEY(station_id, note_id),
    FOREIGN KEY(station_id) REFERENCES stations(station_id),
    FOREIGN KEY(note_id)    REFERENCES notes(note_id)
);

CREATE TABLE point_notes (
    point_id TEXT NOT NULL,
    note_id  INTEGER NOT NULL,
    PRIMARY KEY(point_id, note_id),
    FOREIGN KEY(point_id) REFERENCES points(point_id),
    FOREIGN KEY(note_id)  REFERENCES notes(note_id)
);

CREATE TABLE facility_notes (
    facility_id TEXT NOT NULL,
    note_id     INTEGER NOT NULL,
    PRIMARY KEY(facility_id, note_id),
    FOREIGN KEY(facility_id) REFERENCES facilities(facility_id),
    FOREIGN KEY(note_id)     REFERENCES notes(note_id)
);

CREATE TABLE instrument_notes (
    instrument_id TEXT NOT NULL,
    note_id       INTEGER NOT NULL,
    PRIMARY KEY(instrument_id, note_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id),
    FOREIGN KEY(note_id)       REFERENCES notes(note_id)
);

CREATE TABLE model_notes (
    model_id TEXT NOT NULL,
    note_id  INTEGER NOT NULL,
    PRIMARY KEY(model_id, note_id),
    FOREIGN KEY(model_id) REFERENCES models(model_id),
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

-- AKA time instances
CREATE TABLE times (
    time_id       INTEGER PRIMARY KEY AUTOINCREMENT CHECK ( time_id > 0 ),
    series_id     TEXT NOT NULL,
    instrument_id INTEGER DEFAULT NULL,
    value         REAL DEFAULT NULL,
    uncertainty   REAL DEFAULT NULL CHECK ( uncertainty >= 0.0 ),
    outlier       INTEGER NOT NULL DEFAULT FALSE,
    FOREIGN KEY(series_id)     REFERENCES series(series_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id),
    FOREIGN KEY(outlier)       REFERENCES booleans(boolean_id)
);

CREATE TABLE streamwise_coordinate (
    point_id      TEXT NOT NULL,
    time_id       INTEGER NOT NULL,
    instrument_id INTEGER DEFAULT NULL,
    value         REAL NOT NULL,
    uncertainty   REAL DEFAULT NULL CHECK ( uncertainty >= 0.0 ),
    outlier       INTEGER NOT NULL DEFAULT FALSE,
    PRIMARY KEY(point_id, time_id, instrument_id),
    FOREIGN KEY(point_id)      REFERENCES points(point_id),
    FOREIGN KEY(time_id)       REFERENCES times(time_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id),
    FOREIGN KEY(outlier)       REFERENCES booleans(boolean_id)
);

CREATE TABLE transverse_coordinate (
    point_id      TEXT NOT NULL,
    time_id       INTEGER NOT NULL,
    instrument_id INTEGER DEFAULT NULL,
    value         REAL NOT NULL,
    uncertainty   REAL DEFAULT NULL CHECK ( uncertainty >= 0.0 ),
    outlier       INTEGER NOT NULL DEFAULT FALSE,
    PRIMARY KEY(point_id, time_id, instrument_id),
    FOREIGN KEY(point_id)      REFERENCES points(point_id),
    FOREIGN KEY(time_id)       REFERENCES times(time_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id),
    FOREIGN KEY(outlier)       REFERENCES booleans(boolean_id)
);

CREATE TABLE spanwise_coordinate (
    point_id      TEXT NOT NULL,
    time_id       INTEGER NOT NULL,
    instrument_id INTEGER DEFAULT NULL,
    value         REAL NOT NULL,
    uncertainty   REAL DEFAULT NULL CHECK ( uncertainty >= 0.0 ),
    outlier       INTEGER NOT NULL DEFAULT FALSE,
    PRIMARY KEY(point_id, time_id, instrument_id),
    FOREIGN KEY(point_id)      REFERENCES points(point_id),
    FOREIGN KEY(time_id)       REFERENCES times(time_id),
    FOREIGN KEY(instrument_id) REFERENCES instruments(instrument_id),
    FOREIGN KEY(outlier)       REFERENCES booleans(boolean_id)
);

CREATE VIEW wall_streamwise_coordinate AS
     SELECT                points.station_id    AS station_id,
                           points.point_id      AS point_id,
            streamwise_coordinate.time_id       AS time_id,
            streamwise_coordinate.instrument_id AS instrument_id,
            streamwise_coordinate.value         AS value,
            streamwise_coordinate.uncertainty   AS uncertainty,
            streamwise_coordinate.outlier       AS outlier
       FROM streamwise_coordinate
 INNER JOIN points
         ON points.point_id   = streamwise_coordinate.point_id
        AND points.point_type = 'W';

CREATE VIEW wall_transverse_coordinate AS
     SELECT                points.station_id    AS station_id,
                           points.point_id      AS point_id,
            transverse_coordinate.time_id       AS time_id,
            transverse_coordinate.instrument_id AS instrument_id,
            transverse_coordinate.value         AS value,
            transverse_coordinate.uncertainty   AS uncertainty,
            transverse_coordinate.outlier       AS outlier
       FROM transverse_coordinate
 INNER JOIN points
         ON points.point_id   = transverse_coordinate.point_id
        AND points.point_type = 'W';

CREATE VIEW wall_spanwise_coordinate AS
     SELECT              points.station_id    AS station_id,
                         points.point_id      AS point_id,
            spanwise_coordinate.time_id       AS time_id,
            spanwise_coordinate.instrument_id AS instrument_id,
            spanwise_coordinate.value         AS value,
            spanwise_coordinate.uncertainty   AS uncertainty,
            spanwise_coordinate.outlier       AS outlier
       FROM spanwise_coordinate
 INNER JOIN points
         ON points.point_id   = spanwise_coordinate.point_id
        AND points.point_type = 'W';

