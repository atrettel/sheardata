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
import math
import sqlite3
import sheardata as sd
import sys
from uncertainties import ufloat
from uncertainties import unumpy as unp

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

flow_class   = sd.DUCT_FLOW_CLASS
year         = 1928
study_number = 2

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "CornishRJ+1928+eng+JOUR", 1 )
sd.add_source( cursor, study_identifier, "JonesOC+1976+eng+JOUR",   2 )
sd.add_source( cursor, study_identifier, "ObotNT+1988+eng+JOUR",    2 )

# p. 691
#
# \begin{quote}
# The object of the research was to investigate the flow of water in a pipe of
# rectangular cross-section.
# \end{quote}

# p. 692
#
# \begin{quote}
# The width of the channel ($2 a$) was 1.178 cms., and the depth ($2 b$) was
# 0.404 cm.  The maximum variation from these average figures was less than 0.5
# per cent. in both cases.
# \end{quote}
#
# Assume a uniform distribution.
width_value        = 1.178e-2
height_value       = 0.404e-2
width_uncertainty  = 0.005 * width_value / 3.0**0.5
height_uncertainty = 0.005 * height_value / 3.0**0.5

width  = ufloat( width_value, width_uncertainty )
height = ufloat( height_value, height_uncertainty )

half_height        = 0.5 * height
aspect_ratio       = width / height
hydraulic_diameter = 2.0 * width * height / ( width + height )

# p. 692
#
# \begin{quote}
# The pressure differences were measured in three ways, according to the
# magnitude---
#
# \begin{enumerate}
#
# \item Very small differences, up to about 12 cms. of water, were found by
# observing a differential water gauge with a cathetometer, which could be read
# to 0.001 cm. by a verneier.
#
# \item Up to about 30 inches water a differential water gauge, read directly,
# was used.
#
# \item For all higher pressures two mercury gauges were used.
# \end{enumerate}
#
# A calibrated mercury thermometer was used for temperature, and the quantity
# of water was found by measuring with a stop watch (calibrated every day) the
# time to fill vessels whose volume was known within 0.1 per cent.
# \end{quote}
mt_wall_shear_stress = sd.MT_MOMENTUM_BALANCE
mt_flow_rate         = sd.MT_WEIGHING_METHOD

# p. 692
#
# \begin{quote}
# Fig. 1 shows a cross section through the pipe.  The two main components were
# two brass casting about 120 cms. long.  In the lower casting a channel was
# cut and finished smooth with emery paper.  The upper casting was a plate,
# planed flat and smoothed with emery paper.  Three gauge holes, $\alpha$,
# $\beta$, $\gamma$, each 1/16 inch in diameter, were drilled in it.  The
# distance from the entrance to $\alpha$ was 30.2 cms., from $\alpha$ to
# $\beta$ 30.50 cms., from $\beta$ to $\gamma$ 36.43 cms., and from $\gamma$ to
# the exit 22.8 cms.
# \end{quote}
#
# p. 693
#
# \begin{quote}
# The results have been divided into two series, and are detailed in Appendix
# I.  Series 1 includes readings taken at gauge holes $\alpha$ and $\gamma$ and
# the readings of series 2 were taken at $\beta$ and $\gamma$.
# \end{quote}
#
# Use the term "set" instead of "series" to prevent confusion.  These
# paragraphs provide detailed information about the development length and
# distance between pressure taps.
point_alpha =               30.20e-2
point_beta  = point_alpha + 30.50e-2
point_gamma = point_beta  + 36.43e-2

development_lengths = {}
development_lengths[1] = point_alpha
development_lengths[2] = point_beta

distance_between_pressure_taps = {}
distance_between_pressure_taps[1] = point_gamma - point_alpha
distance_between_pressure_taps[2] = point_gamma - point_beta

# p. 693
mass_density = 1000.0


conn.commit()
conn.close()
