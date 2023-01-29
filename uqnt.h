// Copyright (C) 2023 Andrew Trettel

typedef struct {
    double value, uncertainty;
    double length_d, mass_d, time_d, temperature_d;
} uqnt;


uqnt one;
uqnt meter;
uqnt gram;
uqnt second;
uqnt degree_kelvin;

double uqnt_value( uqnt a );
double uqnt_uncertainty( uqnt a );
double uqnt_length_d( uqnt a );
double uqnt_mass_d( uqnt a );
double uqnt_time_d( uqnt a );
double uqnt_temperature_d( uqnt a );
uqnt uqnt_norm( double value, double uncertainty, uqnt units );
_Bool uqnt_same_dimensions( uqnt a, uqnt b );
uqnt uqnt_add( uqnt a, uqnt b );
uqnt uqnt_subtract( uqnt a, uqnt b );
uqnt uqnt_multiply( uqnt a, uqnt b );
uqnt uqnt_divide( uqnt a, uqnt b );
void uqnt_print( uqnt a );

