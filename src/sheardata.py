#!/usr/bin/env python3

# Copyright (C) 2020 Andrew Trettel
# 
# This file is licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import sqlite3

EXPERIMENTAL_DATA_TYPE = "E"
NUMERICAL_DATA_TYPE    = "N"

BOUNDARY_LAYER_CLASS     = "B"
WALL_BOUNDED_FLOW_CLASS  = "C"
DUCT_FLOW_CLASS          = "D"
EXTERNAL_FLOW_CLASS      = "E"
FREE_SHEAR_FLOW_CLASS    = "F"
ISOTROPIC_FLOW_CLASS     = "G"
HOMOGENEOUS_FLOW_CLASS   = "H"
INTERNAL_FLOW_CLASS      = "I"
FREE_JET_CLASS           = "J"
WALL_JET_CLASS           = "K"
MIXING_LAYER_CLASS       = "M"
INHOMOGENEOUS_FLOW_CLASS = "N"
RELATIVE_MOTION_CLASS    = "R"
SHEAR_LAYER_CLASS        = "S"
FLOW_CLASS               = "U"
WAKE_CLASS               = "W"

SOLID_PHASE  = "S"
LIQUID_PHASE = "L"
GAS_PHASE    = "G"
PLASMA_PHASE = "P"
MULTIPHASE   = "M"

DEFAULT_PROFILE_IDENTIFIER = "S9999001001001"

DISCRETE_GLOBALS_TABLE = "globals_d"

def identify_case( flow_class, year, case_number, readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:1s}{:s}{:4d}{:s}{:3d}".format(
        str(flow_class),
        str(separator),
        int(year),
        str(separator),
        int(case_number),
    ).replace(" ","0")

def identify_series( flow_class, year, case_number, series_number, \
                     readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:s}{:s}{:3d}".format(
        identify_case( flow_class, year, case_number, readable=readable, ),
        str(separator),
        int(series_number),
    ).replace(" ","0")

def identify_profile( flow_class, year, case_number, series_number, \
                      profile_number, readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:s}{:s}{:3d}".format(
        identify_series(
            flow_class, year, case_number, series_number, readable=readable,
        ),
        str(separator),
        int(profile_number),
    ).replace(" ","0")

def identify_point( flow_class, year, case_number, series_number, \
                    profile_number, point_number, readable=False ):
    separator = ""
    if ( readable ):
        separator = "-"

    return "{:s}{:s}{:4d}".format(
        identify_profile(
            flow_class, year, case_number, series_number, profile_number, \
            readable=readable,
        ),
        str(separator),
        int(point_number),
    ).replace(" ","0")

class ShearLayer:
    _cursor             = None
    _profile_identifier = None

    # TODO: This is unsafe at the moment.  Later I will add in checks on the
    # table and variable.
    def _set_integer( self, table, variable, value ):
        self._cursor.execute(
            "UPDATE "+table+" SET "+variable+"=? WHERE profile_identifier=?",
            ( int(value), self.profile_identifier(), ),
        )

    # TODO: This is unsafe at the moment.  Later I will add in checks on the
    # table and variable.
    def _set_string( self, table, variable, value ):
        self._cursor.execute(
            "UPDATE "+table+" SET "+variable+"=? WHERE profile_identifier=?",
            ( str(value), self.profile_identifier(), ),
        )

    def case_identifier( self, readable=False ):
        if ( readable ):
            return identify_case(
                self.flow_class(),
                self.year(),
                self.case_number(),
                readable=True,
            )
        else:
            self._cursor.execute(
                "SELECT case_identifier FROM globals_d WHERE profile_identifier=?",
                ( self.profile_identifier(), ),
            )
            return str(self._cursor.fetchone()[0])

    def set_case_identifier( self, case_identifier ):
        self._set_string(
            DISCRETE_GLOBALS_TABLE,
            "case_identifier",
            case_identifier,
        )

    def case_number( self ):
        self._cursor.execute(
            "SELECT case_number FROM globals_d WHERE profile_identifier=?",
            ( self.profile_identifier(), ),
        )
        return int(self._cursor.fetchone()[0])

    def set_case_number( self, case_number ):
        self._set_integer(
            DISCRETE_GLOBALS_TABLE,
            "case_number",
            case_number,
        )

    def flow_class( self ):
        self._cursor.execute(
            "SELECT flow_class FROM globals_d WHERE profile_identifier=?",
            ( self.profile_identifier(), ),
        )
        return str(self._cursor.fetchone()[0])

    def set_flow_class( self, flow_class ):
        self._set_string(
            DISCRETE_GLOBALS_TABLE,
            "flow_class",
            flow_class,
        )

    def profile_identifier( self, readable=False ):
        if ( readable ):
            return identify_profile(
                self.flow_class(),
                self.year(),
                self.case_number(),
                self.series_number(),
                self.profile_number(),
                readable=True,
            )
        else:
            return self._profile_identifier

    def profile_number( self ):
        self._cursor.execute(
            "SELECT profile_number FROM globals_d WHERE profile_identifier=?",
            ( self.profile_identifier(), ),
        )
        return int(self._cursor.fetchone()[0])

    def set_profile_number( self, profile_number ):
        self._set_integer(
            DISCRETE_GLOBALS_TABLE,
            "profile_number",
            profile_number,
        )

    def series_identifier( self, readable=False ):
        if ( readable ):
            return identify_series(
                self.flow_class(),
                self.year(),
                self.case_number(),
                self.series_number(),
                readable=True,
            )
        else:
            self._cursor.execute(
                "SELECT series_identifier FROM globals_d WHERE profile_identifier=?",
                ( self.profile_identifier(), ),
            )
            return str(self._cursor.fetchone()[0])

    def set_series_identifier( self, series_identifier ):
        self._set_string(
            DISCRETE_GLOBALS_TABLE,
            "series_identifier",
            series_identifier,
        )

    def series_number( self ):
        self._cursor.execute(
            "SELECT series_number FROM globals_d WHERE profile_identifier=?",
            ( self.profile_identifier(), ),
        )
        return int(self._cursor.fetchone()[0])

    def set_series_number( self, series_number ):
        self._set_integer(
            DISCRETE_GLOBALS_TABLE,
            "series_number",
            series_number,
        )

    def year( self ):
        self._cursor.execute(
            "SELECT year FROM globals_d WHERE profile_identifier=?",
            ( self.profile_identifier(), ),
        )
        return int(self._cursor.fetchone()[0])

    def set_year( self, year ):
        self._set_integer(
            DISCRETE_GLOBALS_TABLE,
            "year",
            year,
        )

    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=SHEAR_LAYER_CLASS,     \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        self._cursor = cursor
        if ( profile_identifier == None and case_number != None ):
            self._profile_identifier = identify_profile(
                flow_class,
                year,
                case_number, 
                series_number,
                profile_number,
                readable=False,
            )

            cursor.execute(
            """
            SELECT profile_identifier FROM globals_d WHERE profile_identifier=?
            LIMIT 1
            """,
            ( self._profile_identifier, ) )

            if ( cursor.fetchone() == None ):
                cursor.execute( "INSERT INTO globals_d DEFAULT VALUES" )

                cursor.execute(
                """
                UPDATE globals_d SET profile_identifier=?
                WHERE profile_identifier=?
                """,
                (
                    self._profile_identifier,
                    DEFAULT_PROFILE_IDENTIFIER,
                )
                )

                self.set_flow_class( flow_class )
                self.set_year( year )
                self.set_case_number( case_number )
                self.set_series_number( series_number )
                self.set_profile_number( profile_number )

                self.set_case_identifier(
                    identify_case(
                        self.flow_class(),
                        self.year(),
                        self.case_number(),
                        readable=False,
                    ),
                )
                self.set_series_identifier(
                    identify_series(
                        self.flow_class(),
                        self.year(),
                        self.case_number(),
                        self.series_number(),
                        readable=False,
                    ),
                )
        elif ( profile_identifier != None ):
            self._profile_identifier = profile_identifier.replace("-","")

class FreeShearFlow(ShearLayer):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=FREE_SHEAR_FLOW_CLASS, \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )

class WallBoundedFlow(ShearLayer):
    def __init__( self,                               \
                  cursor,                             \
                  profile_identifier=None,            \
                  flow_class=WALL_BOUNDED_FLOW_CLASS, \
                  year=None,                          \
                  case_number=None,                   \
                  series_number=None,                 \
                  profile_number=None,                \
                  data_type=EXPERIMENTAL_DATA_TYPE,   \
                  number_of_points=0,                 \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )

class FreeJet(FreeShearFlow):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=FREE_JET_CLASS,        \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )

class MixingLayer(FreeShearFlow):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=MIXING_LAYER_CLASS,    \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )

class Wake(FreeShearFlow):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=WAKE_CLASS,            \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )

class ExternalFlow(WallBoundedFlow):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=EXTERNAL_FLOW_CLASS,   \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )

class InternalFlow(WallBoundedFlow):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=INTERNAL_FLOW_CLASS,   \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )


class BoundaryLayer(ExternalFlow):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=BOUNDARY_LAYER_CLASS,  \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )

class WallJet(ExternalFlow):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=WALL_JET_CLASS,        \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )

class DuctFlow(InternalFlow):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=DUCT_FLOW_CLASS,       \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )

class FlowWithRelativeMotion(InternalFlow):
    def __init__( self,                             \
                  cursor,                           \
                  profile_identifier=None,          \
                  flow_class=RELATIVE_MOTION_CLASS, \
                  year=None,                        \
                  case_number=None,                 \
                  series_number=None,               \
                  profile_number=None,              \
                  data_type=EXPERIMENTAL_DATA_TYPE, \
                  number_of_points=0,               \
                  number_of_dimensions=2, ):
        super().__init__( cursor,
                          profile_identifier=profile_identifier,     \
                          flow_class=flow_class,                     \
                          year=year,                                 \
                          case_number=case_number,                   \
                          series_number=series_number,               \
                          profile_number=profile_number,             \
                          data_type=data_type,                       \
                          number_of_points=number_of_points,         \
                          number_of_dimensions=number_of_dimensions, )
