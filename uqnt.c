// Copyright (C) 2023 Andrew Trettel
#include <assert.h>
#include <float.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "uqnt.h"

int gcd( int a, int b )
{
    if ( b == 0 )
    {
        return a;
    }
    else
    {
        return gcd( b, a % b );
    }
}

int lcm( int a, int b )
{
    int c = gcd(a,b);
    if ( c == 0 )
    {
        return 0;
    }
    else
    {
        return abs(a) * abs(b) / c;
    }
}

rat rat_frac( int num, int den )
{
    assert( den != 0 );
    int c = abs(gcd(num,den));
    if ( den > 0 )
    {
        rat a =
        {
            .num = num / c,
            .den = den / c
        };
        return a;
    }
    else
    {
        rat a =
        {
            .num = -num / c,
            .den = -den / c
        };
        return a;
    }
}

rat rat_str( char str[] )
{
    int num, den;
    if ( strchr( str, '/' ) == NULL )
    {
        sscanf( str, "%d", &num );
        den = 1;
    }
    else
    {
        sscanf( str, "%d/%d", &num, &den );
    }
    return rat_frac(num,den);
}

int rat_num( rat a )
{
    return a.num;
}

int rat_den( rat a )
{
    return a.den;
}

double rat_to_double( rat a )
{
    return ( (double) rat_num(a) ) / ( (double) rat_den(a) );
}

rat rat_add( rat a, rat b )
{
    return rat_frac(
        rat_num(a) * rat_den(b) + rat_num(b) * rat_den(a),
        rat_den(a) * rat_den(b)
    );
}

rat rat_subt( rat a, rat b )
{
    return rat_frac(
        rat_num(a) * rat_den(b) - rat_num(b) * rat_den(a),
        rat_den(a) * rat_den(b)
    );
}

rat rat_mult( rat a, rat b )
{
    return rat_frac(
        rat_num(a) * rat_num(b),
        rat_den(a) * rat_den(b)
    );
}

rat rat_div( rat a, rat b )
{
    return rat_frac(
        rat_num(a) * rat_den(b),
        rat_den(a) * rat_num(b)
    );
}

void rat_print( rat a )
{
    if ( rat_den(a) == 1 )
    {
        printf( "%+d", rat_num(a) );
    }
    else
    {
        printf( "%+d/%d", rat_num(a), rat_den(a) );
    }
}

_Bool rat_eq( rat a, rat b )
{
    return ( rat_num(a) == rat_num(b) ) && ( rat_den(a) == rat_den(b) );
}

_Bool rat_ne( rat a, rat b )
{
    return ! rat_eq(a,b);
}

double uqnt_val( uqnt a )
{
    return a.val;
}

double uqnt_unc( uqnt a )
{
    return a.unc;
}

_Bool uqnt_prop_unc( uqnt a )
{
    return a.prop_unc;
}

rat uqnt_len_d( uqnt a )
{
    return a.len_d;
}

rat uqnt_mass_d( uqnt a )
{
    return a.mass_d;
}

rat uqnt_time_d( uqnt a )
{
    return a.time_d;
}

rat uqnt_temp_d( uqnt a )
{
    return a.temp_d;
}

uqnt uqnt_norm( double val, double unc, uqnt units )
{
    assert( unc >= 0.0 );
    double u_v = uqnt_val(units);
    uqnt a =
    {
        .val      = val *      u_v,
        .unc      = unc * fabs(u_v),
        .prop_unc = true,
        .len_d    =  uqnt_len_d(units),
        .mass_d   = uqnt_mass_d(units),
        .time_d   = uqnt_time_d(units),
        .temp_d   = uqnt_temp_d(units)
    };
    return a;
}

uqnt uqnt_unifb( double min_val, double max_val, uqnt units )
{
    double val = 0.5 * ( min_val + max_val );
    double unc = ( max_val - min_val ) / sqrt(12.0);
    return uqnt_norm( val, unc, units );
}

uqnt uqnt_unif( double val, double half_width, uqnt units )
{
    return uqnt_unifb( val-half_width, val+half_width, units );
}

// Blocks uncertainty propagation.
uqnt uqnt_blk( double val, uqnt units )
{
    uqnt a =
    {
        .val      = val * uqnt_val(units),
        .unc      = 0.0,
        .prop_unc = false,
        .len_d    =  uqnt_len_d(units),
        .mass_d   = uqnt_mass_d(units),
        .time_d   = uqnt_time_d(units),
        .temp_d   = uqnt_temp_d(units)
    };
    return a;
}

uqnt uqnt_num( double val )
{
    return uqnt_norm( val, 0.0, unit_one() );
}

_Bool uqnt_same_dim( uqnt a, uqnt b )
{
    if ( rat_ne( uqnt_len_d(a), uqnt_len_d(b) ) )
    {
        return false;
    }
    else if ( rat_ne( uqnt_mass_d(a), uqnt_mass_d(b) ) )
    {
        return false;
    }
    else if ( rat_ne( uqnt_time_d(a), uqnt_time_d(b) ) )
    {
        return false;
    }
    else if ( rat_ne( uqnt_temp_d(a), uqnt_temp_d(b) ) )
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
    _Bool prop_unc = uqnt_prop_unc(a) && uqnt_prop_unc(b);
    double c_u = 0.0;
    if ( prop_unc )
    {
        c_u = sqrt( a_u * a_u + b_u * b_u );
    }
    uqnt c =
    {
        .val      = uqnt_val(a) + uqnt_val(b),
        .unc      = c_u,
        .prop_unc = prop_unc,
        .len_d    =  uqnt_len_d(a),
        .mass_d   = uqnt_mass_d(a),
        .time_d   = uqnt_time_d(a),
        .temp_d   = uqnt_temp_d(a)
    };
    return c;
}

uqnt uqnt_subt( uqnt a, uqnt b )
{
    assert( uqnt_same_dim(a,b) );

    double a_u = uqnt_unc(a);
    double b_u = uqnt_unc(b);
    _Bool prop_unc = uqnt_prop_unc(a) && uqnt_prop_unc(b);
    double c_u = 0.0;
    if ( prop_unc )
    {
        c_u = sqrt( a_u * a_u + b_u * b_u );
    }
    uqnt c =
    {
        .val      = uqnt_val(a) - uqnt_val(b),
        .unc      = c_u,
        .prop_unc = prop_unc,
        .len_d    =  uqnt_len_d(a),
        .mass_d   = uqnt_mass_d(a),
        .time_d   = uqnt_time_d(a),
        .temp_d   = uqnt_temp_d(a)
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
    _Bool prop_unc = uqnt_prop_unc(a) && uqnt_prop_unc(b);
    double c_u = 0.0;
    if ( prop_unc )
    {
        c_u = fabs(c_v) * sqrt( a_u * a_u / ( a_v * a_v )
                              + b_u * b_u / ( b_v * b_v ) );
    }
    uqnt c =
    {
        .val      = c_v,
        .unc      = c_u,
        .prop_unc = prop_unc,
        .len_d    = rat_add(  uqnt_len_d(a),  uqnt_len_d(b) ),
        .mass_d   = rat_add( uqnt_mass_d(a), uqnt_mass_d(b) ),
        .time_d   = rat_add( uqnt_time_d(a), uqnt_time_d(b) ),
        .temp_d   = rat_add( uqnt_temp_d(a), uqnt_temp_d(b) )
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
    _Bool prop_unc = uqnt_prop_unc(a) && uqnt_prop_unc(b);
    double c_u = 0.0;
    if ( prop_unc )
    {
        c_u = fabs(c_v) * sqrt( a_u * a_u / ( a_v * a_v )
                              + b_u * b_u / ( b_v * b_v ) );
    }
    uqnt c =
    {
        .val      = c_v,
        .unc      = c_u,
        .prop_unc = prop_unc,
        .len_d    = rat_subt(  uqnt_len_d(a),  uqnt_len_d(b) ),
        .mass_d   = rat_subt( uqnt_mass_d(a), uqnt_mass_d(b) ),
        .time_d   = rat_subt( uqnt_time_d(a), uqnt_time_d(b) ),
        .temp_d   = rat_subt( uqnt_temp_d(a), uqnt_temp_d(b) )
    };
    return c;
}

/*
Exponentation presents an issue when considering uncertainty quantities with
dimensions.  For exponents with uncertainty, the dimensions of the result
become uncertain.  This issue emerges even with the assumption that the
exponent is always dimensionless.  For now, to avoid this issue, I assume that
the arguments for this function are dimensionless.
*/
uqnt uqnt_pow( uqnt a, uqnt b )
{
    assert( uqnt_same_dim( a, unit_one() ) );
    assert( uqnt_same_dim( b, unit_one() ) );
    double a_v = uqnt_val(a);
    double b_v = uqnt_val(b);
    double c_v = pow(a_v,b_v);
    double a_u = uqnt_unc(a);
    double b_u = uqnt_unc(b);
    _Bool prop_unc = uqnt_prop_unc(a) && uqnt_prop_unc(b);
    double c_u = 0.0;
    if ( prop_unc )
    {
        c_u = sqrt( pow( b_v * pow(a_v,b_v-1.0) * a_u, 2.0 )
                  + pow( log(a_v) * c_v * b_u,         2.0 ) );
    }
    uqnt c =
    {
        .val      = c_v,
        .unc      = c_u,
        .prop_unc = prop_unc,
        .len_d    = rat_frac( 0, 1 ),
        .mass_d   = rat_frac( 0, 1 ),
        .time_d   = rat_frac( 0, 1 ),
        .temp_d   = rat_frac( 0, 1 )
    };
    return c;
}

/*
This function avoids the issues with the dimensions entirely, since the
exponent is always a certain, dimensionless number.
*/
uqnt uqnt_rpow( uqnt a, rat b )
{
    double a_v = uqnt_val(a);
    double b_v = rat_to_double(b);
    double c_v = pow(a_v,b_v);
    double a_u = uqnt_unc(a);
    _Bool prop_unc = uqnt_prop_unc(a);
    double c_u = 0.0;
    if ( prop_unc )
    {
        c_u = c_v * fabs(b_v) * a_u / a_v;
    }
    uqnt c =
    {
        .val      = c_v,
        .unc      = c_u,
        .prop_unc = prop_unc,
        .len_d    = rat_mult( b,  uqnt_len_d(a) ),
        .mass_d   = rat_mult( b, uqnt_mass_d(a) ),
        .time_d   = rat_mult( b, uqnt_time_d(a) ),
        .temp_d   = rat_mult( b, uqnt_temp_d(a) )
    };
    return c;
}

uqnt uqnt_sqrt( uqnt a )
{
    return uqnt_rpow( a, rat_frac( 1, 2 ) );
}

void uqnt_print( uqnt a )
{
    if ( uqnt_prop_unc(a) )
    {
        printf( "( %+8.5e +/- %+8.5e )", uqnt_val(a), uqnt_unc(a) );
    }
    else
    {
        printf( "%+8.5e", uqnt_val(a) );
    }

    if ( rat_ne( uqnt_len_d(a), rat_frac( 0, 1 ) ) )
    {
        printf( " m^" );
        rat_print( uqnt_len_d(a) );
    }
    if ( rat_ne( uqnt_mass_d(a), rat_frac( 0, 1 ) ) )
    {
        printf( " kg^" );
        rat_print( rat_div( uqnt_mass_d(a), rat_frac( 1000, 1 ) ) );
    }
    if ( rat_ne( uqnt_time_d(a), rat_frac( 0, 1 ) ) )
    {
        printf( " s^" );
        rat_print( uqnt_time_d(a) );
    }
    if ( rat_ne( uqnt_temp_d(a), rat_frac( 0, 1 ) ) )
    {
        printf( " K^" );
        rat_print( uqnt_temp_d(a) );
    }
}

_Bool uqnt_eq( uqnt a, uqnt b )
{
    if ( fabs( uqnt_val(a) - uqnt_val(b) ) < DBL_EPSILON )
    {
        return true;
    }
    else
    {
        return false;
    }
}

_Bool uqnt_ne( uqnt a, uqnt b )
{
    return ! uqnt_eq(a,b);
}

_Bool uqnt_lt( uqnt a, uqnt b )
{
    if ( uqnt_eq(a,b) )
    {
        return false;
    }
    else if ( uqnt_val(a) < uqnt_val(b) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

_Bool uqnt_gt( uqnt a, uqnt b )
{
    if ( uqnt_eq(a,b) )
    {
        return false;
    }
    else if ( uqnt_lt(a,b) )
    {
        return false;
    }
    else
    {
        return true;
    }
}

_Bool uqnt_le( uqnt a, uqnt b )
{
    return ! uqnt_gt(a,b);
}

_Bool uqnt_ge( uqnt a, uqnt b )
{
    return ! uqnt_lt(a,b);
}

uqnt unit_one(void)
{
    uqnt a =
    {
        .val      = 1.0,
        .unc      = 0.0,
        .prop_unc = true,
        .len_d    = rat_frac( 0, 1 ),
        .mass_d   = rat_frac( 0, 1 ),
        .time_d   = rat_frac( 0, 1 ),
        .temp_d   = rat_frac( 0, 1 )
    };
    return a;
}

uqnt unit_meter(void)
{
    uqnt a =
    {
        .val      = 1.0,
        .unc      = 0.0,
        .prop_unc = true,
        .len_d    = rat_frac( 1, 1 ),
        .mass_d   = rat_frac( 0, 1 ),
        .time_d   = rat_frac( 0, 1 ),
        .temp_d   = rat_frac( 0, 1 )
    };
    return a;
}

uqnt unit_gram(void)
{
    uqnt a =
    {
        .val      = 1.0,
        .unc      = 0.0,
        .prop_unc = true,
        .len_d    = rat_frac( 0, 1 ),
        .mass_d   = rat_frac( 1, 1 ),
        .time_d   = rat_frac( 0, 1 ),
        .temp_d   = rat_frac( 0, 1 )
    };
    return a;
}

uqnt unit_second(void)
{
    uqnt a =
    {
        .val      = 1.0,
        .unc      = 0.0,
        .prop_unc = true,
        .len_d    = rat_frac( 0, 1 ),
        .mass_d   = rat_frac( 0, 1 ),
        .time_d   = rat_frac( 1, 1 ),
        .temp_d   = rat_frac( 0, 1 )
    };
    return a;
}

uqnt unit_kelvin(void)
{
    uqnt a =
    {
        .val      = 1.0,
        .unc      = 0.0,
        .prop_unc = true,
        .len_d    = rat_frac( 0, 1 ),
        .mass_d   = rat_frac( 0, 1 ),
        .time_d   = rat_frac( 0, 1 ),
        .temp_d   = rat_frac( 1, 1 )
    };
    return a;
}

uqnt unit_kilogram(void)
{
    return uqnt_mult( uqnt_num(1000.0), unit_gram() );
}
