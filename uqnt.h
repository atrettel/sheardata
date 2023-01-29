// Copyright (C) 2023 Andrew Trettel

typedef struct {
    double value, uncertainty;
    double length_d, mass_d, time_d, temperature_d;
} uqnt;


uqnt one;
uqnt meter;
uqnt gram;
uqnt second;
uqnt deg_kelvin;

double uqnt_value( uqnt a );
double uqnt_uncertainty( uqnt a );
double uqnt_length_d( uqnt a );
double uqnt_mass_d( uqnt a );
double uqnt_time_d( uqnt a );
double uqnt_temperature_d( uqnt a );
uqnt uqnt_norm( double value, double uncertainty, uqnt units );
uqnt uqnt_unif( double min_value, double max_value, uqnt units );
uqnt uqnt_num( double value );
_Bool uqnt_same_dim( uqnt a, uqnt b );
uqnt uqnt_add( uqnt a, uqnt b );
uqnt uqnt_subt( uqnt a, uqnt b );
uqnt uqnt_mult( uqnt a, uqnt b );
uqnt uqnt_div( uqnt a, uqnt b );
void uqnt_print( uqnt a );

