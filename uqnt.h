// Copyright (C) 2023 Andrew Trettel

typedef struct {
    int num, den;
} rat;

int gcd( int a, int b );
int lcm( int a, int b );
rat rat_frac( int num, int den );
rat rat_str( char str[] );
int rat_num( rat a );
int rat_den( rat a );
double rat_to_double( rat a );
rat rat_add( rat a, rat b );
rat rat_subt( rat a, rat b );
rat rat_mult( rat a, rat b );
rat rat_div( rat a, rat b );
void rat_print( rat a );

typedef struct {
    double val, unc;
    _Bool prop_unc;
    double len_d, mass_d, time_d, temp_d;
} uqnt;

extern const uqnt one;
extern const uqnt meter;
extern const uqnt gram;
extern const uqnt second;
extern const uqnt deg_kelvin;

double uqnt_val( uqnt a );
double uqnt_unc( uqnt a );
_Bool uqnt_prop_unc( uqnt a );
double uqnt_len_d( uqnt a );
double uqnt_mass_d( uqnt a );
double uqnt_time_d( uqnt a );
double uqnt_temp_d( uqnt a );
uqnt uqnt_norm( double val, double unc, uqnt units );
uqnt uqnt_unifb( double min_val, double max_val, uqnt units );
uqnt uqnt_unif( double val, double half_width, uqnt units );
uqnt uqnt_num( double val );
_Bool uqnt_same_dim( uqnt a, uqnt b );
uqnt uqnt_add( uqnt a, uqnt b );
uqnt uqnt_subt( uqnt a, uqnt b );
uqnt uqnt_mult( uqnt a, uqnt b );
uqnt uqnt_div( uqnt a, uqnt b );
uqnt uqnt_pow( uqnt a, uqnt b );
uqnt uqnt_dpow( uqnt a, double b );
uqnt uqnt_sqrt( uqnt a );
void uqnt_print( uqnt a );
_Bool uqnt_eq( uqnt a, uqnt b );
_Bool uqnt_ne( uqnt a, uqnt b );
_Bool uqnt_lt( uqnt a, uqnt b );
_Bool uqnt_gt( uqnt a, uqnt b );
_Bool uqnt_le( uqnt a, uqnt b );
_Bool uqnt_ge( uqnt a, uqnt b );

