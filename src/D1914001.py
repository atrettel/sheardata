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

conn = sqlite3.connect( sys.argv[1] )
cursor =  conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

flow_class   = sd.DUCT_FLOW_CLASS
year         = 1914
study_number = 1

study_identifier = sd.add_study(
    cursor,
    flow_class=flow_class,
    year=year,
    study_number=study_number,
    study_type=sd.EXPERIMENTAL_STUDY_TYPE,
)

sd.add_source( cursor, study_identifier, "StantonTE+1914+eng+JOUR", 1 )

conn.commit()
conn.close()


# p. 202
#
# \begin{quote}
# For very accurate comparison the surfaces of the tubes should have been
# precisely geometrically similar, as regards roughness, but as this condition
# could not be fulfilled, the experiments were all made on commercially
# smooth-drawn brass pipes.
# \end{quote}
#
# However, this only appears to be the case for most of the experiments.  Some
# were conducted using steel pipes.  One experiment using air and all of the
# experiments with thick oil are using steel pipes.
#
# p. 209
#
# \begin{quote}
# As a matter of interest the results of a series of observations of the
# surface fraction of this oil, when flowing through a steel pipe 10.1 cm.
# diameter at speeds varying from 5 to 60 cm. per second, are given in Table
# IV. and are also plotted in fig. 3.
# \end{quote}
#
# Pipe 12A on p. 224 is not in the table on p. 207.  It is possible that this
# pipe is a brass pipe, but unfortunately the test length is not specified.

# p. 203
#
# \begin{quote}
# To measure the velocity of the current, one of two methods was used according
# to convenience.  By one method the total quantity of fluid passing through
# the pipe in a given time was either weighed directly, or passed through a
# water-meter or a gas-holder, which had been designed for the purpose of the
# experiments and carefully calibrated.  By the other method the velocity at
# the axis of the pipe was estimated by measuring the difference of pressure
# between that in a small Pitot tube facing the current and placed in the axis
# of the pipe and that in a small hole in the wall of the pipe.
# \end{quote}
velocity_measurement_technique = "PT"

# p. 203
#
# \begin{quote}
# To determine the amount of the surface friction two small holes were made
# in the walls of the experimental portion of the pipe, one at each extremity,
# at a known distance apart, and connected to a tilting manometer.  \ldots  In
# this way the fall of pressure along a given length of the pipe was
# determined, and from the known diameter of the pipe the surface friction per
# unit area was calculated.
# \end{quote}
wall_shear_stress_measurement_technique = "PD"

# p. 203
#
# \begin{quote}
# The form of the tilting manometer used for the estimation of both the surface
# friction and the axial velocity, is that devised by Dr. A. P. Chattock and
# has been previously described.†  For the purpose of the present paper it is
# sufficient to state that in this manometer a pressure difference of the order
# of 0.003 mm. of water can be detected, which is well within the limits of
# sensitivity required in these experiments.  As the fall of pressure in these
# pipes varied from 0.5 to 150,000 mm. of water, other manometers were required
# for the higher pressures, and for this purpose water or mercury U-tubes were
# used for the intermediate pressures, and the Bourdon pressure gauges for the
# highest pressures.
# \end{quote}
#
# The footnote lists two papers that should contain more information about the
# manometers used.

# p. 207
#
# This contains a table of global parameters listing the measurement techniques
# for different series of measurements.
#
# However, even knowing how the flow rate was measured does not provide enough
# information to quantify the uncertainty on that measurement, since the paper
# does not appear to give any information on that subject.

# p. 209
#
# \begin{quote}
# The particular oil on which these observations were made had a value of the
# kinematical viscosity at 15.5° C. of 36.2, or 3230 times that of water at the
# same temperature.  By heating this to 50° C. the kinematical viscosity could
# be reduced to 2.1, but even at this temperature the critical velocity in the
# 10 cm. pipe used for the experiments would have been 525 cm. per second.
# \end{quote}

# The velocity ratio experiments do not give the test conditions like the
# temperature.  Graphical extraction from figure 1 reveals that the kinematic
# viscosity used there is consistent with the value around 15°C.
nu_water = 9.186e-7
nu_air   = 1.468e-5
