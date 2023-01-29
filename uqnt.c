// Copyright (C) 2023 Andrew Trettel
#include <assert.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include "uqnt.h"

uqnt one           = { .value = 1.0, .uncertainty = 0.0, .length_d = 0.0, .mass_d = 0.0, .time_d = 0.0, .temperature_d = 0.0 };
uqnt meter         = { .value = 1.0, .uncertainty = 0.0, .length_d = 1.0, .mass_d = 0.0, .time_d = 0.0, .temperature_d = 0.0 };
uqnt gram          = { .value = 1.0, .uncertainty = 0.0, .length_d = 0.0, .mass_d = 1.0, .time_d = 0.0, .temperature_d = 0.0 };
uqnt second        = { .value = 1.0, .uncertainty = 0.0, .length_d = 0.0, .mass_d = 0.0, .time_d = 1.0, .temperature_d = 0.0 };
uqnt degree_Kelvin = { .value = 1.0, .uncertainty = 0.0, .length_d = 0.0, .mass_d = 0.0, .time_d = 0.0, .temperature_d = 1.0 };

double uqnt_value( uqnt a )
{
    return a.value;
}

double uqnt_uncertainty( uqnt a )
{
    return a.uncertainty;
}

double uqnt_length_d( uqnt a )
{
    return a.length_d;
}

double uqnt_mass_d( uqnt a )
{
    return a.mass_d;
}

double uqnt_time_d( uqnt a )
{
    return a.time_d;
}

double uqnt_temperature_d( uqnt a )
{
    return a.temperature_d;
}

uqnt uqnt_norm( double value, double uncertainty, uqnt units )
{
    uqnt a =
    {
        .value         =       value * uqnt_value(units),
        .uncertainty   = uncertainty * uqnt_value(units),
        .length_d      =            uqnt_length_d(units),
        .mass_d        =              uqnt_mass_d(units),
        .time_d        =              uqnt_time_d(units), 
        .temperature_d =       uqnt_temperature_d(units)
    };
    return a;
}

_Bool uqnt_same_dimensions( uqnt a, uqnt b )
{
    if ( uqnt_length_d(a) != uqnt_length_d(b) )
    {
        return false;
    }
    else if ( uqnt_mass_d(a) != uqnt_mass_d(b) )
    {
        return false;
    }
    else if ( uqnt_time_d(a) != uqnt_time_d(b) )
    {
        return false;
    }
    else if ( uqnt_temperature_d(a) != uqnt_temperature_d(b) )
    {
        return false;
    }
    else
    {
        return true;
    }
}

uqnt uqnt_add( uqnt a, uqnt b )
{
    assert( uqnt_same_dimensions(a,b) );

    double a_u = uqnt_uncertainty(a);
    double b_u = uqnt_uncertainty(b);
    uqnt c =
    {
        .value         = uqnt_value(a) + uqnt_value(b),
        .uncertainty   = sqrt( a_u * a_u + b_u * b_u ),
        .length_d      =      uqnt_length_d(a),
        .mass_d        =        uqnt_mass_d(a),
        .time_d        =        uqnt_time_d(a), 
        .temperature_d = uqnt_temperature_d(a)
    };
    return c;
}

uqnt uqnt_subtract( uqnt a, uqnt b )
{
    assert( uqnt_same_dimensions(a,b) );

    double a_u = uqnt_uncertainty(a);
    double b_u = uqnt_uncertainty(b);
    uqnt c =
    {
        .value         = uqnt_value(a) - uqnt_value(b),
        .uncertainty   = sqrt( a_u * a_u + b_u * b_u ),
        .length_d      =      uqnt_length_d(a),
        .mass_d        =        uqnt_mass_d(a),
        .time_d        =        uqnt_time_d(a), 
        .temperature_d = uqnt_temperature_d(a)
    };
    return c;
}

uqnt uqnt_multiply( uqnt a, uqnt b )
{
    double a_v = uqnt_value(a);
    double b_v = uqnt_value(b);
    double c_v = a_v * b_v;
    double a_u = uqnt_uncertainty(a);
    double b_u = uqnt_uncertainty(b);
    uqnt c =
    {
        .value         = c_v,
        .uncertainty   = fabs(c_v) * sqrt( a_u * a_u / ( a_v * a_v )
                                         + b_u * b_u / ( b_v * b_v ) ),
        .length_d      =      uqnt_length_d(a) +      uqnt_length_d(b),
        .mass_d        =        uqnt_mass_d(a) +        uqnt_mass_d(b),
        .time_d        =        uqnt_time_d(a) +        uqnt_time_d(b), 
        .temperature_d = uqnt_temperature_d(a) + uqnt_temperature_d(b)
    };
    return c;
}

uqnt uqnt_divide( uqnt a, uqnt b )
{
    double a_v = uqnt_value(a);
    double b_v = uqnt_value(b);
    double c_v = a_v / b_v;
    double a_u = uqnt_uncertainty(a);
    double b_u = uqnt_uncertainty(b);
    uqnt c =
    {
        .value         = c_v,
        .uncertainty   = fabs(c_v) * sqrt( a_u * a_u / ( a_v * a_v )
                                         + b_u * b_u / ( b_v * b_v ) ),
        .length_d      =      uqnt_length_d(a) -      uqnt_length_d(b),
        .mass_d        =        uqnt_mass_d(a) -        uqnt_mass_d(b),
        .time_d        =        uqnt_time_d(a) -        uqnt_time_d(b), 
        .temperature_d = uqnt_temperature_d(a) - uqnt_temperature_d(b)
    };
    return c;
}

void uqnt_print( uqnt a )
{
    printf( "( %+8.5e +/- %+8.5e )", uqnt_value(a), uqnt_uncertainty(a) );

    if ( uqnt_length_d(a) != 0.0 )
    {
        printf( " m^%+g", uqnt_length_d(a) );
    }
    if ( uqnt_mass_d(a) != 0.0 )
    {
        printf( " m^%+g", uqnt_mass_d(a) );
    }
    if ( uqnt_time_d(a) != 0.0 )
    {
        printf( " m^%+g", uqnt_time_d(a) );
    }
    if ( uqnt_temperature_d(a) != 0.0 )
    {
        printf( " m^%+g", uqnt_temperature_d(a) );
    }
}
