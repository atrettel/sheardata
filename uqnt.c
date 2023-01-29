// Copyright (C) 2023 Andrew Trettel
#include <assert.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include "uqnt.h"

const uqnt one        = { .val = 1.0, .unc = 0.0, .len_d = 0.0, .mass_d = 0.0, .time_d = 0.0, .temp_d = 0.0 };
const uqnt meter      = { .val = 1.0, .unc = 0.0, .len_d = 1.0, .mass_d = 0.0, .time_d = 0.0, .temp_d = 0.0 };
const uqnt gram       = { .val = 1.0, .unc = 0.0, .len_d = 0.0, .mass_d = 1.0, .time_d = 0.0, .temp_d = 0.0 };
const uqnt second     = { .val = 1.0, .unc = 0.0, .len_d = 0.0, .mass_d = 0.0, .time_d = 1.0, .temp_d = 0.0 };
const uqnt deg_kelvin = { .val = 1.0, .unc = 0.0, .len_d = 0.0, .mass_d = 0.0, .time_d = 0.0, .temp_d = 1.0 };

double uqnt_val( uqnt a )
{
    return a.val;
}

double uqnt_unc( uqnt a )
{
    return a.unc;
}

double uqnt_len_d( uqnt a )
{
    return a.len_d;
}

double uqnt_mass_d( uqnt a )
{
    return a.mass_d;
}

double uqnt_time_d( uqnt a )
{
    return a.time_d;
}

double uqnt_temp_d( uqnt a )
{
    return a.temp_d;
}

uqnt uqnt_norm( double val, double unc, uqnt units )
{
    uqnt a =
    {
        .val    = val * uqnt_val(units),
        .unc    = unc * uqnt_val(units),
        .len_d  =  uqnt_len_d(units),
        .mass_d = uqnt_mass_d(units),
        .time_d = uqnt_time_d(units),
        .temp_d = uqnt_temp_d(units)
    };
    return a;
}

uqnt uqnt_unif( double min_val, double max_val, uqnt units )
{
    double val = 0.5 * ( min_val + max_val );
    double unc = ( max_val - min_val ) / sqrt(12.0);
    return uqnt_norm( val, unc, units );
}

uqnt uqnt_num( double val )
{
    return uqnt_norm( val, 0.0, one );
}

_Bool uqnt_same_dim( uqnt a, uqnt b )
{
    if ( uqnt_len_d(a) != uqnt_len_d(b) )
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
    else if ( uqnt_temp_d(a) != uqnt_temp_d(b) )
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
    assert( uqnt_same_dim(a,b) );

    double a_u = uqnt_unc(a);
    double b_u = uqnt_unc(b);
    uqnt c =
    {
        .val    = uqnt_val(a) + uqnt_val(b),
        .unc    = sqrt( a_u * a_u + b_u * b_u ),
        .len_d  =  uqnt_len_d(a),
        .mass_d = uqnt_mass_d(a),
        .time_d = uqnt_time_d(a),
        .temp_d = uqnt_temp_d(a)
    };
    return c;
}

uqnt uqnt_subt( uqnt a, uqnt b )
{
    assert( uqnt_same_dim(a,b) );

    double a_u = uqnt_unc(a);
    double b_u = uqnt_unc(b);
    uqnt c =
    {
        .val    = uqnt_val(a) - uqnt_val(b),
        .unc    = sqrt( a_u * a_u + b_u * b_u ),
        .len_d  =  uqnt_len_d(a),
        .mass_d = uqnt_mass_d(a),
        .time_d = uqnt_time_d(a),
        .temp_d = uqnt_temp_d(a)
    };
    return c;
}

uqnt uqnt_mult( uqnt a, uqnt b )
{
    double a_v = uqnt_val(a);
    double b_v = uqnt_val(b);
    double c_v = a_v * b_v;
    double a_u = uqnt_unc(a);
    double b_u = uqnt_unc(b);
    uqnt c =
    {
        .val    = c_v,
        .unc    = fabs(c_v) * sqrt( a_u * a_u / ( a_v * a_v )
                                  + b_u * b_u / ( b_v * b_v ) ),
        .len_d  =  uqnt_len_d(a) +  uqnt_len_d(b),
        .mass_d = uqnt_mass_d(a) + uqnt_mass_d(b),
        .time_d = uqnt_time_d(a) + uqnt_time_d(b),
        .temp_d = uqnt_temp_d(a) + uqnt_temp_d(b)
    };
    return c;
}

uqnt uqnt_div( uqnt a, uqnt b )
{
    double a_v = uqnt_val(a);
    double b_v = uqnt_val(b);
    double c_v = a_v / b_v;
    double a_u = uqnt_unc(a);
    double b_u = uqnt_unc(b);
    uqnt c =
    {
        .val    = c_v,
        .unc    = fabs(c_v) * sqrt( a_u * a_u / ( a_v * a_v )
                                  + b_u * b_u / ( b_v * b_v ) ),
        .len_d  =  uqnt_len_d(a) -  uqnt_len_d(b),
        .mass_d = uqnt_mass_d(a) - uqnt_mass_d(b),
        .time_d = uqnt_time_d(a) - uqnt_time_d(b),
        .temp_d = uqnt_temp_d(a) - uqnt_temp_d(b)
    };
    return c;
}

void uqnt_print( uqnt a )
{
    printf( "( %+8.5e +/- %+8.5e )", uqnt_val(a), uqnt_unc(a) );

    if ( uqnt_len_d(a) != 0.0 )
    {
        printf( " m^%+g", uqnt_len_d(a) );
    }
    if ( uqnt_mass_d(a) != 0.0 )
    {
        printf( " m^%+g", uqnt_mass_d(a) );
    }
    if ( uqnt_time_d(a) != 0.0 )
    {
        printf( " m^%+g", uqnt_time_d(a) );
    }
    if ( uqnt_temp_d(a) != 0.0 )
    {
        printf( " m^%+g", uqnt_temp_d(a) );
    }
}
