// Copyright (C) 2023 Andrew Trettel

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
uqnt unit_meter(void);
uqnt unit_kilogram(void);
uqnt unit_second(void);
uqnt unit_kelvin(void);

uqnt unit_foot(void);
uqnt unit_inch(void);
uqnt unit_yard(void);

uqnt unit_gram(void);
uqnt unit_pound_mass(void);

uqnt unit_minute(void);
uqnt unit_hour(void);
uqnt unit_day(void);

uqnt unit_hertz(void);

uqnt unit_radian(void);
uqnt unit_steradian(void);
uqnt unit_degree(void);

uqnt unit_liter(void);

uqnt unit_newton(void);
uqnt unit_pound_force(void);

uqnt unit_atmosphere(void);
uqnt unit_bar(void);
uqnt unit_inch_of_mercury(void);
uqnt unit_pascal(void);
uqnt unit_pound_per_square_inch(void);
uqnt unit_torr(void);

uqnt unit_joule(void);
uqnt unit_calorie(void);

uqnt unit_watt(void);

uqnt absolute_zero(void);
uqnt standard_atmospheric_pressure(void);
uqnt standard_gravitational_acceleration(void);
