// Copyright (C) 2023 Andrew Trettel

typedef struct {
    double val, unc;
    double len_d, mass_d, time_d, temp_d;
} uqnt;


extern const uqnt one;
extern const uqnt meter;
extern const uqnt gram;
extern const uqnt second;
extern const uqnt deg_kelvin;

double uqnt_val( uqnt a );
double uqnt_unc( uqnt a );
double uqnt_len_d( uqnt a );
double uqnt_mass_d( uqnt a );
double uqnt_time_d( uqnt a );
double uqnt_temp_d( uqnt a );
uqnt uqnt_norm( double val, double unc, uqnt units );
uqnt uqnt_unif( double min_val, double max_val, uqnt units );
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

