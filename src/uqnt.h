/*
 * Copyright (C) 2023 Andrew Trettel
 *
 * SPDX-License-Identifier: MIT
 */

/*
 * Rational number data type
 *
 * integer:  numerator, denominator
 */
typedef struct {
    int num, den;
} ratnum;

int gcd( int a, int b );
int lcm( int a, int b );
ratnum ratnum_frac( int num, int den );
ratnum ratnum_str( char str[] );
int ratnum_num( ratnum a );
int ratnum_den( ratnum a );
double ratnum_to_double( ratnum a );
ratnum ratnum_add( ratnum a, ratnum b );
ratnum ratnum_subt( ratnum a, ratnum b );
ratnum ratnum_mult( ratnum a, ratnum b );
ratnum ratnum_div( ratnum a, ratnum b );
void ratnum_print( ratnum a );
_Bool ratnum_eq( ratnum a, ratnum b );
_Bool ratnum_ne( ratnum a, ratnum b );

/*
 * Uncertainty quantity data type
 *
 * double:          mean value, standard uncertainty
 * Boolean:         propagate uncertainties or not?
 * rational number: length dimension, mass dimension, time dimension,
 *                  temperature_dimension
 */
typedef struct {
    double val, unc;
    _Bool prop_unc;
    ratnum len_d, mass_d, time_d, temp_d;
} uqnt;

double uqnt_val( uqnt a );
double uqnt_unc( uqnt a );
_Bool uqnt_prop_unc( uqnt a );
ratnum uqnt_len_d( uqnt a );
ratnum uqnt_mass_d( uqnt a );
ratnum uqnt_time_d( uqnt a );
ratnum uqnt_temp_d( uqnt a );
uqnt uqnt_norm( double val, double unc, uqnt units );
uqnt uqnt_unifb( double min_val, double max_val, uqnt units );
uqnt uqnt_unif( double val, double half_width, uqnt units );
uqnt uqnt_blk( double val, uqnt units );
uqnt uqnt_num( double val );
_Bool uqnt_same_dim( uqnt a, uqnt b );
uqnt uqnt_add( uqnt a, uqnt b );
uqnt uqnt_subt( uqnt a, uqnt b );
uqnt uqnt_mult( uqnt a, uqnt b );
uqnt uqnt_div( uqnt a, uqnt b );
uqnt uqnt_pow( uqnt a, uqnt b );
uqnt uqnt_rpow( uqnt a, ratnum b );
uqnt uqnt_rpow_int( uqnt a, int b );
uqnt uqnt_rpow_str( uqnt a, char str[] );
uqnt uqnt_sqrt( uqnt a );
void uqnt_print( uqnt a );
_Bool uqnt_eq( uqnt a, uqnt b );
_Bool uqnt_ne( uqnt a, uqnt b );
_Bool uqnt_lt( uqnt a, uqnt b );
_Bool uqnt_gt( uqnt a, uqnt b );
_Bool uqnt_le( uqnt a, uqnt b );
_Bool uqnt_ge( uqnt a, uqnt b );

uqnt unit_one(void);

uqnt unit_tera(void);
uqnt unit_giga(void);
uqnt unit_mega(void);
uqnt unit_kilo(void);
uqnt unit_hecto(void);
uqnt unit_deca(void);
uqnt unit_deci(void);
uqnt unit_centi(void);
uqnt unit_milli(void);
uqnt unit_micro(void);
uqnt unit_nano(void);
uqnt unit_pico(void);

uqnt unit_meter(void);
uqnt unit_kilogram(void);
uqnt unit_second(void);
uqnt unit_kelvin(void);

uqnt unit_foot(void);
uqnt unit_inch(void);
uqnt unit_yard(void);

uqnt unit_gram(void);
uqnt unit_pound_mass(void);
uqnt unit_avoirdupois_ounce(void);

uqnt unit_minute(void);
uqnt unit_hour(void);
uqnt unit_day(void);

uqnt unit_rankine(void);

uqnt unit_hertz(void);

uqnt unit_radian(void);
uqnt unit_steradian(void);
uqnt unit_degree(void);

uqnt unit_liter(void);
uqnt unit_imperial_gallon(void);
uqnt unit_us_gallon(void);
uqnt unit_imperial_fluid_ounce(void);
uqnt unit_us_fluid_ounce(void);

uqnt unit_newton(void);
uqnt unit_pound_force(void);

uqnt unit_atmosphere(void);
uqnt unit_bar(void);
uqnt unit_millimeter_of_mercury(void);
uqnt unit_inch_of_mercury(void);
uqnt unit_inch_of_water(void);
uqnt unit_pascal(void);
uqnt unit_pound_per_square_inch(void);
uqnt unit_torr(void);

uqnt unit_joule(void);
uqnt unit_gram_calorie(void);
uqnt unit_kilogram_calorie(void);
uqnt unit_british_thermal_unit(void);

uqnt unit_watt(void);

uqnt u_km(void);
uqnt u_m(void);
uqnt u_cm(void);
uqnt u_mm(void);
uqnt u_um(void);
uqnt u_nm(void);
uqnt u_kg(void);
uqnt u_g(void);
uqnt u_s(void);
uqnt u_ms(void);
uqnt u_us(void);
uqnt u_ns(void);
uqnt u_K(void);
uqnt u_lbm(void);
uqnt u_GHz(void);
uqnt u_MHz(void);
uqnt u_kHz(void);
uqnt u_Hz(void);
uqnt u_rad(void);
uqnt u_sr(void);
uqnt u_L(void);
uqnt u_mL(void);
uqnt u_N(void);
uqnt u_lbf(void);
uqnt u_atm(void);
uqnt u_kbar(void);
uqnt u_bar(void);
uqnt u_mbar(void);
uqnt u_GPa(void);
uqnt u_MPa(void);
uqnt u_kPa(void);
uqnt u_hPa(void);
uqnt u_Pa(void);
uqnt u_J(void);
uqnt u_Btu(void);
uqnt u_W(void);

uqnt absolute_zero(void);
uqnt standard_atmospheric_pressure(void);
uqnt standard_gravitational_acceleration(void);

uqnt celsius_norm( double val, double unc );
uqnt celsius_unif( double val, double half_width );
uqnt celsius_blk( double val );
uqnt fahrenheit_norm( double val, double unc );
uqnt fahrenheit_unif( double val, double half_width );
uqnt fahrenheit_blk( double val );
