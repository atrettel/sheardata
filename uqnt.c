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

ratnum ratnum_frac( int num, int den )
{
    assert( den != 0 );
    int c = abs(gcd(num,den));
    if ( den > 0 )
    {
        ratnum a =
        {
            .num = num / c,
            .den = den / c
        };
        return a;
    }
    else
    {
        ratnum a =
        {
            .num = -num / c,
            .den = -den / c
        };
        return a;
    }
}

ratnum ratnum_str( char str[] )
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
    return ratnum_frac(num,den);
}

int ratnum_num( ratnum a )
{
    return a.num;
}

int ratnum_den( ratnum a )
{
    return a.den;
}

double ratnum_to_double( ratnum a )
{
    return ( (double) ratnum_num(a) ) / ( (double) ratnum_den(a) );
}

ratnum ratnum_add( ratnum a, ratnum b )
{
    return ratnum_frac(
        ratnum_num(a) * ratnum_den(b) + ratnum_num(b) * ratnum_den(a),
        ratnum_den(a) * ratnum_den(b)
    );
}

ratnum ratnum_subt( ratnum a, ratnum b )
{
    return ratnum_frac(
        ratnum_num(a) * ratnum_den(b) - ratnum_num(b) * ratnum_den(a),
        ratnum_den(a) * ratnum_den(b)
    );
}

ratnum ratnum_mult( ratnum a, ratnum b )
{
    return ratnum_frac(
        ratnum_num(a) * ratnum_num(b),
        ratnum_den(a) * ratnum_den(b)
    );
}

ratnum ratnum_div( ratnum a, ratnum b )
{
    return ratnum_frac(
        ratnum_num(a) * ratnum_den(b),
        ratnum_den(a) * ratnum_num(b)
    );
}

void ratnum_print( ratnum a )
{
    if ( ratnum_den(a) == 1 )
    {
        printf( "%+d", ratnum_num(a) );
    }
    else
    {
        printf( "%+d/%d", ratnum_num(a), ratnum_den(a) );
    }
}

_Bool ratnum_eq( ratnum a, ratnum b )
{
    return ( ratnum_num(a) == ratnum_num(b) ) && ( ratnum_den(a) == ratnum_den(b) );
}

_Bool ratnum_ne( ratnum a, ratnum b )
{
    return ! ratnum_eq(a,b);
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

ratnum uqnt_len_d( uqnt a )
{
    return a.len_d;
}

ratnum uqnt_mass_d( uqnt a )
{
    return a.mass_d;
}

ratnum uqnt_time_d( uqnt a )
{
    return a.time_d;
}

ratnum uqnt_temp_d( uqnt a )
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
    if ( ratnum_ne( uqnt_len_d(a), uqnt_len_d(b) ) )
    {
        return false;
    }
    else if ( ratnum_ne( uqnt_mass_d(a), uqnt_mass_d(b) ) )
    {
        return false;
    }
    else if ( ratnum_ne( uqnt_time_d(a), uqnt_time_d(b) ) )
    {
        return false;
    }
    else if ( ratnum_ne( uqnt_temp_d(a), uqnt_temp_d(b) ) )
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
        .len_d    = ratnum_add(  uqnt_len_d(a),  uqnt_len_d(b) ),
        .mass_d   = ratnum_add( uqnt_mass_d(a), uqnt_mass_d(b) ),
        .time_d   = ratnum_add( uqnt_time_d(a), uqnt_time_d(b) ),
        .temp_d   = ratnum_add( uqnt_temp_d(a), uqnt_temp_d(b) )
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
        .len_d    = ratnum_subt(  uqnt_len_d(a),  uqnt_len_d(b) ),
        .mass_d   = ratnum_subt( uqnt_mass_d(a), uqnt_mass_d(b) ),
        .time_d   = ratnum_subt( uqnt_time_d(a), uqnt_time_d(b) ),
        .temp_d   = ratnum_subt( uqnt_temp_d(a), uqnt_temp_d(b) )
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
        .len_d    = ratnum_frac( 0, 1 ),
        .mass_d   = ratnum_frac( 0, 1 ),
        .time_d   = ratnum_frac( 0, 1 ),
        .temp_d   = ratnum_frac( 0, 1 )
    };
    return c;
}

/*
This function avoids the issues with the dimensions entirely, since the
exponent is always a certain, dimensionless number.
*/
uqnt uqnt_rpow( uqnt a, ratnum b )
{
    double a_v = uqnt_val(a);
    double b_v = ratnum_to_double(b);
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
        .len_d    = ratnum_mult( b,  uqnt_len_d(a) ),
        .mass_d   = ratnum_mult( b, uqnt_mass_d(a) ),
        .time_d   = ratnum_mult( b, uqnt_time_d(a) ),
        .temp_d   = ratnum_mult( b, uqnt_temp_d(a) )
    };
    return c;
}

uqnt uqnt_sqrt( uqnt a )
{
    return uqnt_rpow( a, ratnum_frac( 1, 2 ) );
}

uqnt uqnt_rpow_int( uqnt a, int b )
{
    return uqnt_rpow( a, ratnum_frac( b, 1 ) );
}

uqnt uqnt_rpow_str( uqnt a, char str[] )
{
    return uqnt_rpow( a, ratnum_str(str) );
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

    if ( ratnum_ne( uqnt_len_d(a), ratnum_frac( 0, 1 ) ) )
    {
        printf( " m^" );
        ratnum_print( uqnt_len_d(a) );
    }
    if ( ratnum_ne( uqnt_mass_d(a), ratnum_frac( 0, 1 ) ) )
    {
        printf( " kg^" );
        ratnum_print( uqnt_mass_d(a) );
    }
    if ( ratnum_ne( uqnt_time_d(a), ratnum_frac( 0, 1 ) ) )
    {
        printf( " s^" );
        ratnum_print( uqnt_time_d(a) );
    }
    if ( ratnum_ne( uqnt_temp_d(a), ratnum_frac( 0, 1 ) ) )
    {
        printf( " K^" );
        ratnum_print( uqnt_temp_d(a) );
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
        .len_d    = ratnum_frac( 0, 1 ),
        .mass_d   = ratnum_frac( 0, 1 ),
        .time_d   = ratnum_frac( 0, 1 ),
        .temp_d   = ratnum_frac( 0, 1 )
    };
    return a;
}

uqnt unit_tera(void)
{
    return uqnt_num(1.0e+12);
}

uqnt unit_giga(void)
{
    return uqnt_num(1.0e+9);
}

uqnt unit_mega(void)
{
    return uqnt_num(1.0e+6);
}

uqnt unit_kilo(void)
{
    return uqnt_num(1.0e+3);
}

uqnt unit_hecto(void)
{
    return uqnt_num(1.0e+2);
}

uqnt unit_deca(void)
{
    return uqnt_num(1.0e+1);
}

uqnt unit_deci(void)
{
    return uqnt_num(1.0e-1);
}

uqnt unit_centi(void)
{
    return uqnt_num(1.0e-2);
}

uqnt unit_milli(void)
{
    return uqnt_num(1.0e-3);
}

uqnt unit_micro(void)
{
    return uqnt_num(1.0e-6);
}

uqnt unit_nano(void)
{
    return uqnt_num(1.0e-9);
}

uqnt unit_pico(void)
{
    return uqnt_num(1.0e-12);
}

uqnt unit_meter(void)
{
    uqnt a =
    {
        .val      = 1.0,
        .unc      = 0.0,
        .prop_unc = true,
        .len_d    = ratnum_frac( 1, 1 ),
        .mass_d   = ratnum_frac( 0, 1 ),
        .time_d   = ratnum_frac( 0, 1 ),
        .temp_d   = ratnum_frac( 0, 1 )
    };
    return a;
}

uqnt unit_kilogram(void)
{
    uqnt a =
    {
        .val      = 1.0,
        .unc      = 0.0,
        .prop_unc = true,
        .len_d    = ratnum_frac( 0, 1 ),
        .mass_d   = ratnum_frac( 1, 1 ),
        .time_d   = ratnum_frac( 0, 1 ),
        .temp_d   = ratnum_frac( 0, 1 )
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
        .len_d    = ratnum_frac( 0, 1 ),
        .mass_d   = ratnum_frac( 0, 1 ),
        .time_d   = ratnum_frac( 1, 1 ),
        .temp_d   = ratnum_frac( 0, 1 )
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
        .len_d    = ratnum_frac( 0, 1 ),
        .mass_d   = ratnum_frac( 0, 1 ),
        .time_d   = ratnum_frac( 0, 1 ),
        .temp_d   = ratnum_frac( 1, 1 )
    };
    return a;
}

uqnt unit_foot(void)
{
    return uqnt_div( unit_yard(), uqnt_num(3.0) );
}

uqnt unit_inch(void)
{
    return uqnt_div( unit_foot(), uqnt_num(12.0) );
}

uqnt unit_yard(void)
{
    return uqnt_mult( uqnt_num(0.9144), unit_meter() );
}

uqnt unit_gram(void)
{
    return uqnt_div( unit_kilogram(), uqnt_num(1000.0) );
}

uqnt unit_pound_mass(void)
{
    return uqnt_mult( uqnt_num(0.45359237), unit_kilogram() );
}

uqnt unit_avoirdupois_ounce(void)
{
    return uqnt_div( unit_pound_mass(), uqnt_num(16.0) );
}

uqnt unit_minute(void)
{
    return uqnt_mult( uqnt_num(60.0), unit_second() );
}

uqnt unit_hour(void)
{
    return uqnt_mult( uqnt_num(60.0), unit_minute() );
}

uqnt unit_day(void)
{
    return uqnt_mult( uqnt_num(24.0), unit_hour() );
}

uqnt unit_rankine(void)
{
    return uqnt_mult( uqnt_num(5.0/9.0), unit_kelvin() );
}

uqnt unit_hertz(void)
{
    return uqnt_div( unit_one(), unit_second() );
}

uqnt unit_radian(void)
{
    return uqnt_div( unit_meter(), unit_meter() );
}

uqnt unit_steradian(void)
{
    return uqnt_div(
        uqnt_mult( unit_meter(), unit_meter() ),
        uqnt_mult( unit_meter(), unit_meter() )
    );
}

uqnt unit_degree(void)
{
    return uqnt_mult( uqnt_num(atan(1.0)/45.0), unit_radian() );
}

uqnt unit_liter(void)
{
    return uqnt_mult(
        uqnt_num(0.001),
        uqnt_rpow( unit_meter(), ratnum_frac(3,1) )
    );
}

uqnt unit_imperial_gallon(void)
{
    return uqnt_mult( uqnt_num(4.54609), unit_liter() );
}

uqnt unit_us_gallon(void)
{
    return uqnt_mult(
        uqnt_num(231.0),
        uqnt_rpow( unit_inch(), ratnum_frac(3,1) )
    );
}

uqnt unit_imperial_fluid_ounce(void)
{
    return uqnt_div( unit_imperial_gallon(), uqnt_num(160.0) );
}

uqnt unit_us_fluid_ounce(void)
{
    return uqnt_div( unit_us_gallon(), uqnt_num(160.0) );
}

uqnt unit_newton(void)
{
    return uqnt_div(
        uqnt_mult( unit_kilogram(), unit_meter() ),
        uqnt_mult( unit_second(), unit_second() )
    );
}

uqnt unit_pound_force(void)
{
    return uqnt_mult(
        unit_pound_mass(),
        standard_gravitational_acceleration()
    );
}

uqnt unit_atmosphere(void)
{
    return standard_atmospheric_pressure();
}

uqnt unit_bar(void)
{
    return uqnt_mult( uqnt_num(100000.0), unit_pascal() );
}

uqnt unit_millimeter_of_mercury(void)
{
    return uqnt_mult( uqnt_num(133.322387415), unit_pascal() );
}

uqnt unit_inch_of_mercury(void)
{
    return uqnt_mult(
        uqnt_div(
            unit_inch(),
            uqnt_div(
                unit_meter(),
                uqnt_num(1000.0)
            )
        ),
        unit_millimeter_of_mercury()
    );
}

uqnt unit_inch_of_water(void)
{
    return uqnt_mult( uqnt_num(249.0889), unit_pascal() );
}

uqnt unit_pascal(void)
{
    return uqnt_div(
        unit_newton(),
        uqnt_mult( unit_meter(), unit_meter() )
    );
}

uqnt unit_pound_per_square_inch(void)
{
    return uqnt_div(
        unit_pound_force(),
        uqnt_mult( unit_inch(), unit_inch() )
    );
}

uqnt unit_torr(void)
{
    return uqnt_div( standard_atmospheric_pressure(), uqnt_num(760.0) );
}

uqnt unit_joule(void)
{
    return uqnt_mult( unit_newton(), unit_meter() );
}

uqnt unit_gram_calorie(void)
{
    return uqnt_mult( uqnt_num(4.184), unit_joule() );
}

uqnt unit_kilogram_calorie(void)
{
    return uqnt_mult( uqnt_num(1000.0), unit_gram_calorie() );
}

uqnt unit_british_thermal_unit(void)
{
    return uqnt_div(
        uqnt_mult(
            unit_kilogram_calorie(),
            uqnt_div( unit_pound_mass(), unit_kilogram() )
        ),
        uqnt_div( unit_rankine(), unit_kelvin() )
    );
}

uqnt unit_watt(void)
{
    return uqnt_div( unit_joule(), unit_second() );
}

uqnt absolute_zero(void)
{
    return uqnt_mult( uqnt_num(273.15), unit_kelvin() );
}

uqnt standard_atmospheric_pressure(void)
{
    return uqnt_mult( uqnt_num(101325.0), unit_pascal() );
}

uqnt standard_gravitational_acceleration(void)
{
    return uqnt_mult(
        uqnt_num(9.80665),
        uqnt_div(
            unit_meter(),
            uqnt_mult( unit_second(), unit_second() )
        )
    );
}

// Convert Celsius to Kelvin.
uqnt celsius_norm( double val, double unc )
{
    return uqnt_add(
        uqnt_norm( val, unc, unit_kelvin() ),
        absolute_zero()
    );
}

uqnt celsius_unif( double val, double half_width )
{
    uqnt tmp = uqnt_unif( val, half_width, unit_one() );
    return celsius_norm( uqnt_val(tmp), uqnt_unc(tmp) );
}

uqnt celsius_blk( double val )
{
    uqnt tmp = celsius_norm( val, 0.0 );
    return uqnt_blk( uqnt_val(tmp), unit_kelvin() );
}

// Convert Fahrenheit to Kelvin.
uqnt fahrenheit_norm( double val, double unc )
{
    return uqnt_add(
        uqnt_subt(
            uqnt_norm(  val, unc, unit_rankine() ),
            uqnt_norm( 32.0, 0.0, unit_rankine() )
        ),
        absolute_zero()
    );
}

uqnt fahrenheit_unif( double val, double half_width )
{
    uqnt tmp = uqnt_unif( val, half_width, unit_one() );
    return fahrenheit_norm( uqnt_val(tmp), uqnt_unc(tmp) );
}

uqnt fahrenheit_blk( double val )
{
    uqnt tmp = fahrenheit_norm( val, 0.0 );
    return uqnt_blk( uqnt_val(tmp), unit_kelvin() );
}
