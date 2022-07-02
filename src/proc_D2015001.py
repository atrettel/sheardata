#!/usr/bin/env python3

# Copyright (C) 2020-2022 Andrew Trettel
#
# SPDX-License-Identifier: MIT

import csv
import math
import sqlite3
import sheardata as sd
import sys

conn   = sqlite3.connect( sys.argv[1] )
cursor = conn.cursor()
cursor.execute( "PRAGMA foreign_keys = ON;" )

flow_class   = sd.FC_DUCT_FLOW
year         = 2015
study_number = 1

floating_point_precision_note = sd.add_note(
    cursor,
    "../data/{:s}/note_floating_point_precision.tex".format(
        sd.identify_study(
            flow_class,
            year,
            study_number,
        )
    ),
)

study_id = sd.add_study(
    cursor,
    flow_class_id=flow_class,
    year=year,
    study_number=study_number,
    study_type_id=sd.ST_DIRECT_NUMERICAL_SIMULATION,
    note_ids=[floating_point_precision_note],
)

sd.add_study_source( cursor, study_id, "TrettelA+2015+eng+THES", sd.PRIMARY_SOURCE )
sd.add_study_source( cursor, study_id, "TrettelA+2016+eng+JOUR", sd.PRIMARY_SOURCE )

model_id = sd.add_model(
    cursor,
    sd.MC_INTERIOR_RECTANGULAR_CROSS_SECTION,
)

# TODO: Add model values.

zeroth_order_approximation_id = sd.add_instrument(
    cursor,
    sd.IC_APPROXIMATION,
)
sd.set_instrument_value(
    cursor,
    zeroth_order_approximation_id,
    sd.Q_ORDER_OF_APPROXIMATION,
    sd.sdfloat( 0.0, 0.0 ),
)

dynamic_viscosity_note = sd.add_note(
    cursor,
    "../data/{:s}/note_dynamic_viscosity.tex".format( study_id ),
)

series_number = 0
globals_filename = "../data/{:s}/globals.csv".format( study_id, )
with open( globals_filename, "r" ) as globals_file:
    globals_reader = csv.reader(
        globals_file,
        delimiter=",",
        quotechar='"', \
        skipinitialspace=True,
    )
    next(globals_reader)
    for globals_row in globals_reader:
        series_number += 1

        originators_identifier              = str(globals_row[0])
        prandtl_number                      = sd.sdfloat(globals_row[3],0.0)
        heat_capacity_ratio                 = sd.sdfloat(globals_row[4],0.0)
        specific_gas_constant               = sd.sdfloat(globals_row[5],0.0)
        omega                               = sd.sdfloat(globals_row[6],0.0)
        nx                                  = int(globals_row[7])
        ny                                  = int(globals_row[8])
        nz                                  = int(globals_row[9])
        wall_temperature                    = sd.sdfloat(globals_row[10],0.0)
        wall_dynamic_viscosity              = sd.sdfloat(globals_row[12])
        wall_shear_stress                   = sd.sdfloat(globals_row[13])
        friction_velocity                   = sd.sdfloat(globals_row[18])
        viscous_length_scale                = sd.sdfloat(globals_row[19])
        friction_temperature                = sd.sdfloat(globals_row[20])
        B_q                                 = sd.sdfloat(globals_row[21])
        wall_heat_flux                      = sd.sdfloat(globals_row[22])
        friction_reynolds_number            = sd.sdfloat(globals_row[23])
        semi_local_friction_reynolds_number = sd.sdfloat(globals_row[24])
        friction_mach_number                = sd.sdfloat(globals_row[25])

        # In Hybrid simulations, the number of points in the y-direction
        # exclude the center-line and the wall, so these are added back in the
        # previous post-processing.
        number_of_points = ny // 2 + 2

        # TODO: calculate the bulk velocity from the data.
        bulk_velocity      = sd.sdfloat(   1.0, 0.0 )
        height             = sd.sdfloat(   2.0, 0.0 )
        aspect_ratio       = sd.sdfloat( "inf", 0.0 )
        development_length = sd.sdfloat( "inf", 0.0 )

        half_height                    = 0.5 * height
        hydraulic_diameter             = 2.0 * height
        outer_layer_development_length = development_length / hydraulic_diameter

        specific_isochoric_heat_capacity = specific_gas_constant / ( heat_capacity_ratio - 1.0 )
        specific_isobaric_heat_capacity  = heat_capacity_ratio * specific_isochoric_heat_capacity

        series_id = sd.add_series(
            cursor,
            flow_class_id=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            number_of_dimensions=2,
            coordinate_system_id=sd.CS_RECTANGULAR,
            model_id=model_id,
            series_external_ids={ sd.C_SELF : originators_identifier },
        )

        station_number = 1
        station_id = sd.add_station(
            cursor,
            flow_class_id=flow_class,
            year=year,
            study_number=study_number,
            series_number=series_number,
            station_number=station_number,
            streamwise_periodic=True,
            spanwise_periodic=True,
            station_external_ids={ sd.C_SELF : originators_identifier },
        )

        sd.set_station_value( cursor, station_id, sd.Q_HYDRAULIC_DIAMETER,                 hydraulic_diameter,             )
        sd.set_station_value( cursor, station_id, sd.Q_DEVELOPMENT_LENGTH,                 development_length,             )
        sd.set_station_value( cursor, station_id, sd.Q_OUTER_LAYER_DEVELOPMENT_LENGTH,     outer_layer_development_length, )
        sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_ASPECT_RATIO,                       aspect_ratio,                   )
        sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_HEIGHT,                             height,                         )
        sd.set_station_value( cursor, station_id, sd.Q_CROSS_SECTIONAL_HALF_HEIGHT,                        half_height,                    )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_VELOCITY,                      bulk_velocity,                      value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )

        point_number = 0
        series_filename = "../data/{:s}/{:s}_profiles.csv".format(
            study_id,
            originators_identifier,
        )
        with open( series_filename, "r" ) as series_file:
            series_reader = csv.reader(
                series_file,
                delimiter=",",
                quotechar='"', \
                skipinitialspace=True,
            )
            next(series_reader)
            for series_row in series_reader:
                point_number += 1

                point_label = None
                if ( point_number == 1 ):
                    point_label = sd.PL_WALL
                elif ( point_number == number_of_points ):
                    point_label = sd.PL_CENTER_LINE

                point_id = sd.add_point(
                    cursor,
                    flow_class_id=flow_class,
                    year=year,
                    study_number=study_number,
                    series_number=series_number,
                    station_number=station_number,
                    point_number=point_number,
                    point_label_id=point_label,
                )

                distance_from_wall             = sd.sdfloat(series_row[0])
                inner_layer_coordinate         = sd.sdfloat(series_row[1])
                streamwise_velocity_uw         = sd.sdfloat(series_row[5])
                streamwise_velocity_dw         = sd.sdfloat(series_row[6])
                mass_density                   = sd.sdfloat(series_row[11])
                pressure                       = sd.sdfloat(series_row[12])
                temperature_uw                 = sd.sdfloat(series_row[13])
                temperature_dw                 = sd.sdfloat(series_row[14])
                dynamic_viscosity              = sd.sdfloat(series_row[15])
                R_uu_dw                        = sd.sdfloat(series_row[16])
                R_vv_dw                        = sd.sdfloat(series_row[17])
                R_ww_dw                        = sd.sdfloat(series_row[18])
                R_uv_dw                        = sd.sdfloat(series_row[19])
                mass_density_autocovariance_uw = sd.sdfloat(series_row[24])
                pressure_autocovariance_uw     = sd.sdfloat(series_row[25])
                temperature_autocovariance_dw  = sd.sdfloat(series_row[26])

                outer_layer_coordinate =  distance_from_wall / half_height
                kinematic_viscosity    =   dynamic_viscosity / mass_density
                thermal_diffusivity    = kinematic_viscosity / prandtl_number
                thermal_conductivity   = thermal_diffusivity * mass_density * specific_isobaric_heat_capacity
                speed_of_sound_uw      = ( heat_capacity_ratio * specific_gas_constant * temperature_uw )**0.5
                speed_of_sound_dw      = ( heat_capacity_ratio * specific_gas_constant * temperature_dw )**0.5

                R_uu_plus_dw = R_uu_dw / friction_velocity**2.0
                R_vv_plus_dw = R_vv_dw / friction_velocity**2.0
                R_ww_plus_dw = R_ww_dw / friction_velocity**2.0
                R_uv_plus_dw = R_uv_dw / friction_velocity**2.0

                R_uu_star_dw = mass_density * R_uu_dw / wall_shear_stress
                R_vv_star_dw = mass_density * R_vv_dw / wall_shear_stress
                R_ww_star_dw = mass_density * R_ww_dw / wall_shear_stress
                R_uv_star_dw = mass_density * R_uv_dw / wall_shear_stress

                TKE_dw      = 0.5 * ( R_uu_dw + R_vv_dw + R_ww_dw )
                TKE_plus_dw = TKE_dw / friction_velocity**2.0
                TKE_star_dw = mass_density * TKE_dw / wall_shear_stress

                normalized_mass_density_autocovariance_uw = mass_density_autocovariance_uw / mass_density
                normalized_pressure_autocovariance_uw     =     pressure_autocovariance_uw / pressure
                normalized_temperature_autocovariance_dw  =  temperature_autocovariance_dw / temperature_dw

                sd.set_point_value( cursor, point_id, sd.Q_DISTANCE_FROM_WALL,               distance_from_wall,                                                                                                                                                )
                sd.set_point_value( cursor, point_id, sd.Q_INNER_LAYER_COORDINATE,           inner_layer_coordinate,           value_type_id=sd.VT_BOTH_AVERAGES,                                                                                               )
                sd.set_point_value( cursor, point_id, sd.Q_OUTER_LAYER_COORDINATE,           outer_layer_coordinate,                                                                                                                                            )
                sd.set_point_value( cursor, point_id, sd.Q_STREAMWISE_VELOCITY,              streamwise_velocity_uw,           value_type_id=sd.VT_UNWEIGHTED_AVERAGE,                                                                                          )
                sd.set_point_value( cursor, point_id, sd.Q_STREAMWISE_VELOCITY,              streamwise_velocity_dw,           value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE,                                                                                    )
                sd.set_point_value( cursor, point_id, sd.Q_MASS_DENSITY,                     mass_density,                     value_type_id=sd.VT_UNWEIGHTED_AVERAGE,                                                                                          )
                sd.set_point_value( cursor, point_id, sd.Q_PRESSURE,                         pressure,                         value_type_id=sd.VT_UNWEIGHTED_AVERAGE,                                                                                          )
                sd.set_point_value( cursor, point_id, sd.Q_TEMPERATURE,                      temperature_uw,                   value_type_id=sd.VT_UNWEIGHTED_AVERAGE,                                                                                          )
                sd.set_point_value( cursor, point_id, sd.Q_TEMPERATURE,                      temperature_dw,                   value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE,                                                                                    )
                sd.set_point_value( cursor, point_id, sd.Q_DYNAMIC_VISCOSITY,                dynamic_viscosity,                value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       instrument_ids=[zeroth_order_approximation_id], note_ids=[dynamic_viscosity_note], )
                sd.set_point_value( cursor, point_id, sd.Q_KINEMATIC_VISCOSITY,              kinematic_viscosity,              value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       instrument_ids=[zeroth_order_approximation_id], note_ids=[dynamic_viscosity_note], )
                sd.set_point_value( cursor, point_id, sd.Q_PRANDTL_NUMBER,                   prandtl_number,                   value_type_id=sd.VT_BOTH_AVERAGES,                                                                                               )
                sd.set_point_value( cursor, point_id, sd.Q_HEAT_CAPACITY_RATIO,              heat_capacity_ratio,              value_type_id=sd.VT_BOTH_AVERAGES,                                                                                               )
                sd.set_point_value( cursor, point_id, sd.Q_SPECIFIC_GAS_CONSTANT,            specific_gas_constant,            value_type_id=sd.VT_BOTH_AVERAGES,                                                                                               )
                sd.set_point_value( cursor, point_id, sd.Q_SPECIFIC_ISOBARIC_HEAT_CAPACITY,  specific_isobaric_heat_capacity,  value_type_id=sd.VT_BOTH_AVERAGES,                                                                                               )
                sd.set_point_value( cursor, point_id, sd.Q_SPECIFIC_ISOCHORIC_HEAT_CAPACITY, specific_isochoric_heat_capacity, value_type_id=sd.VT_BOTH_AVERAGES,                                                                                               )
                sd.set_point_value( cursor, point_id, sd.Q_THERMAL_CONDUCTIVITY,             thermal_conductivity,             value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       instrument_ids=[zeroth_order_approximation_id], note_ids=[dynamic_viscosity_note], )
                sd.set_point_value( cursor, point_id, sd.Q_THERMAL_DIFFUSIVITY,              thermal_diffusivity,              value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       instrument_ids=[zeroth_order_approximation_id], note_ids=[dynamic_viscosity_note], )
                sd.set_point_value( cursor, point_id, sd.Q_SPEED_OF_SOUND,                   speed_of_sound_uw,                value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       instrument_ids=[zeroth_order_approximation_id], note_ids=[dynamic_viscosity_note], )
                sd.set_point_value( cursor, point_id, sd.Q_SPEED_OF_SOUND,                   speed_of_sound_dw,                value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, instrument_ids=[zeroth_order_approximation_id], note_ids=[dynamic_viscosity_note], )

                sd.set_point_value( cursor, point_id, sd.Q_LOCAL_TO_WALL_DYNAMIC_VISCOSITY_RATIO, dynamic_viscosity / wall_dynamic_viscosity, value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       )
                sd.set_point_value( cursor, point_id, sd.Q_LOCAL_TO_WALL_TEMPERATURE_RATIO,       temperature_dw    / wall_temperature,       value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_LOCAL_TO_WALL_TEMPERATURE_RATIO,       temperature_uw    / wall_temperature,       value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       )

                sd.set_point_value( cursor, point_id, sd.Q_VELOCITY_COVARIANCE[1,1],                          R_uu_dw,                                   value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_VELOCITY_COVARIANCE[2,2],                          R_vv_dw,                                   value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_VELOCITY_COVARIANCE[3,3],                          R_ww_dw,                                   value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_VELOCITY_COVARIANCE[1,2],                          R_uv_dw,                                   value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[1,1],              R_uu_plus_dw,                              value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[2,2],              R_vv_plus_dw,                              value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[3,3],              R_ww_plus_dw,                              value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_INNER_LAYER_VELOCITY_COVARIANCE[1,2],              R_uv_plus_dw,                              value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[1,1],          R_uu_star_dw,                              value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[2,2],          R_vv_star_dw,                              value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[3,3],          R_ww_star_dw,                              value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_MORKOVIN_SCALED_VELOCITY_COVARIANCE[1,2],          R_uv_star_dw,                              value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_SPECIFIC_TURBULENT_KINETIC_ENERGY,                 TKE_dw,                                    value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_INNER_LAYER_SPECIFIC_TURBULENT_KINETIC_ENERGY,     TKE_plus_dw,                               value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_MORKOVIN_SCALED_SPECIFIC_TURBULENT_KINETIC_ENERGY, TKE_star_dw,                               value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_MASS_DENSITY_AUTOCOVARIANCE,                       mass_density_autocovariance_uw,            value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       )
                sd.set_point_value( cursor, point_id, sd.Q_PRESSURE_AUTOCOVARIANCE,                           pressure_autocovariance_uw,                value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       )
                sd.set_point_value( cursor, point_id, sd.Q_TEMPERATURE_AUTOCOVARIANCE,                        temperature_autocovariance_dw,             value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )
                sd.set_point_value( cursor, point_id, sd.Q_NORMALIZED_MASS_DENSITY_AUTOCOVARIANCE,            normalized_mass_density_autocovariance_uw, value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       )
                sd.set_point_value( cursor, point_id, sd.Q_NORMALIZED_PRESSURE_AUTOCOVARIANCE,                normalized_pressure_autocovariance_uw,     value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       )
                sd.set_point_value( cursor, point_id, sd.Q_NORMALIZED_TEMPERATURE_AUTOCOVARIANCE,             normalized_temperature_autocovariance_dw,  value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )

        bulk_quantities = {}
        for quantity_id in [ sd.Q_MASS_DENSITY,
                             sd.Q_DYNAMIC_VISCOSITY,
                             sd.Q_SPEED_OF_SOUND, ]:
            outer_layer_coordinate_profile, quantity_profile = sd.get_intersecting_profiles(
                cursor,
                station_id,
                [
                    sd.Q_DISTANCE_FROM_WALL,
                    quantity_id,
                ],
                value_type_ids=[None,sd.VT_UNWEIGHTED_AVERAGE],
            )
            bulk_quantities[quantity_id] = sd.integrate_using_trapezoid_rule( outer_layer_coordinate_profile, quantity_profile )

        bulk_mass_density      = bulk_quantities[sd.Q_MASS_DENSITY]
        bulk_dynamic_viscosity = bulk_quantities[sd.Q_DYNAMIC_VISCOSITY]
        bulk_speed_of_sound    = bulk_quantities[sd.Q_SPEED_OF_SOUND]

        bulk_reynolds_number = bulk_mass_density * bulk_velocity * hydraulic_diameter / bulk_dynamic_viscosity
        bulk_mach_number     = bulk_velocity / bulk_speed_of_sound

        fanning_friction_factor = 2.0 * wall_shear_stress / ( bulk_mass_density * bulk_velocity**2.0 )

        center_line_velocity       = sd.get_labeled_value( cursor, station_id, sd.Q_STREAMWISE_VELOCITY, sd.PL_CENTER_LINE, value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       )
        center_line_temperature_uw = sd.get_labeled_value( cursor, station_id, sd.Q_TEMPERATURE,         sd.PL_WALL,        value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       )
        center_line_temperature_dw = sd.get_labeled_value( cursor, station_id, sd.Q_TEMPERATURE,         sd.PL_WALL,        value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )

        bulk_to_center_line_velocity_ratio = bulk_velocity / center_line_velocity

        sd.set_station_value( cursor, station_id, sd.Q_BULK_REYNOLDS_NUMBER, bulk_reynolds_number, value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_station_value( cursor, station_id, sd.Q_BULK_MACH_NUMBER,     bulk_mach_number,     value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )

        for quantity_id in [ sd.Q_ROUGHNESS_HEIGHT,
                             sd.Q_INNER_LAYER_ROUGHNESS_HEIGHT,
                             sd.Q_OUTER_LAYER_ROUGHNESS_HEIGHT, ]:
            sd.set_labeled_value(
                cursor,
                station_id,
                quantity_id,
                sd.PL_WALL,
                sd.sdfloat( 0.0, 0.0 ),
            )

        sd.set_labeled_value( cursor, station_id, sd.Q_SHEAR_STRESS,                        sd.PL_WALL, wall_shear_stress,                   value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_VELOCITY,                   sd.PL_WALL, friction_velocity,                   value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_labeled_value( cursor, station_id, sd.Q_VISCOUS_LENGTH_SCALE,                sd.PL_WALL, viscous_length_scale,                value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_TEMPERATURE,                sd.PL_WALL, friction_temperature,                value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_labeled_value( cursor, station_id, sd.Q_INNER_LAYER_HEAT_FLUX,               sd.PL_WALL, B_q,                                 value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_labeled_value( cursor, station_id, sd.Q_HEAT_FLUX,                           sd.PL_WALL, wall_heat_flux,                      value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_REYNOLDS_NUMBER,            sd.PL_WALL, friction_reynolds_number,            value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_labeled_value( cursor, station_id, sd.Q_SEMI_LOCAL_FRICTION_REYNOLDS_NUMBER, sd.PL_WALL, semi_local_friction_reynolds_number, value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_labeled_value( cursor, station_id, sd.Q_FRICTION_MACH_NUMBER,                sd.PL_WALL, friction_mach_number,                value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )
        sd.set_labeled_value( cursor, station_id, sd.Q_FANNING_FRICTION_FACTOR,             sd.PL_WALL, fanning_friction_factor,             value_type_id=sd.VT_UNWEIGHTED_AVERAGE, )

        # TODO: create profiles for these quantities.
        sd.set_labeled_value( cursor, station_id, sd.Q_LOCAL_TO_CENTER_LINE_TEMPERATURE_RATIO, sd.PL_WALL, wall_temperature / center_line_temperature_uw, value_type_id=sd.VT_UNWEIGHTED_AVERAGE,       )
        sd.set_labeled_value( cursor, station_id, sd.Q_LOCAL_TO_CENTER_LINE_TEMPERATURE_RATIO, sd.PL_WALL, wall_temperature / center_line_temperature_dw, value_type_id=sd.VT_DENSITY_WEIGHTED_AVERAGE, )

        for point_id in sd.get_points_at_station( cursor, station_id ):
            streamwise_velocity = sd.get_point_value( cursor, point_id, sd.Q_STREAMWISE_VELOCITY )
            sd.set_point_value( cursor, point_id,        sd.Q_LOCAL_TO_BULK_STREAMWISE_VELOCITY_RATIO, streamwise_velocity /        bulk_velocity, value_type_id=sd.VT_BOTH_AVERAGES, )
            sd.set_point_value( cursor, point_id, sd.Q_LOCAL_TO_CENTER_LINE_STREAMWISE_VELOCITY_RATIO, streamwise_velocity / center_line_velocity, value_type_id=sd.VT_BOTH_AVERAGES, )

conn.commit()
conn.close()
