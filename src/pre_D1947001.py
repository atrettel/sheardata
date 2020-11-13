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

import sqlite3
import sheardata as sd
import sys

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

flow_class   = sd.DUCT_FLOW_CLASS
year         = 1947
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "HuebscherRG+1947+eng+JOUR", 1 )

conn.commit()
conn.close()

# Duct dimensions
#
# p. 128
#
# \begin{quote}
# The first part of the paper gives the results of an experimental
# investigation using three ducts of different forms but each of 8 in.
# equivalent diameter.  The duct sizes were 8 in. ID round, 8 in. square and
# 4.5 in. by 36 in. rectangular (8:1 aspect ratio).  Air velocities used ranged
# from 300 to 9310 fpm.
# \end{quote}

# Duct material
#
# p. 128
#
# \begin{quote}
# The three ducts were fabricated from 16 gage galvanized sheet metal to
# provide the necessary rigidity against deflection.
# \end{quote}
#
# p. 129
#
# \begin{quote}
# The internal roughness of all three ducts was typical of galvanized iron,
# very little roughness was contributed by the joints.  The hydraulic roughness
# magnitude cannot be measured geometrically but can be deduced from the test
# results.
# \end{quote}

# p. 128
#
# \begin{quote}
# The mean air velocity was determined from the measurement of the air quantity
# and the duct area.  \ldots  Air quantity was measured by the use of five cast
# aluminum nozzles made approximately to ASME log-radius, low-ratio proportions
# and equiped with throat static taps.  \ldots  The nozzles were calibrated in
# place by impact tube traverses at the throat over the full flow range.
# \end{quote}
volume_flow_rate_measurement_technique = sd.IMPACT_TUBE_MEASUREMENT_TECHNIQUE

# Uncertainty of flow rate measurements
#
# p. 128
#
# \begin{quote}
# The estimated error in any flow measurement due to all sources, including the
# assumption of constant nozzle coefficient, did not exceed $\pm 2$ percent.
# \end{quote}

# p. 129
wall_shear_stress_measurement_technique = sd.PRESSURE_DROP_MEASUREMENT_TECHNIQUE

# Uncertainty of wall shear stress measurements
#
# p. 129
#
# \begin{quote}
# The maximum sensitivity of the five gages was $\pm 0.02$ in. of water, with
# an accuracy within this value over the entire range.
# \edn{quote}

# p. 132
#
# \begin{quote}
# Two traverses at opposite ends of the round duct indicated different velocity
# profiles, the centerline velocity at the downstream end was 6.6 percent
# higher than at the upstream end for a mean velocity of 9310 fpm.
# \end{quote}
