! Copyright (C) 2023 Andrew Trettel
!
! SPDX-License-Identifier: MIT
module uqnt_f
   use, intrinsic :: iso_c_binding

   implicit none

   type, bind(c) :: ratnum
      integer(c_int) :: num, den
   end type ratnum

   interface
      function ratnum_frac(num, den) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         type(ratnum) :: ratnum_frac
         integer(c_int), value :: num, den
      end function ratnum_frac
   end interface

   interface
      function ratnum_str(str) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         type(ratnum) :: ratnum_str
         character(kind=c_char), dimension(*) :: str
      end function ratnum_str
   end interface

   interface
      function ratnum_num(a) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         integer(c_int) :: ratnum_num
         type(ratnum), value :: a
      end function ratnum_num
   end interface

   interface
      function ratnum_den(a) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         integer(c_int) :: ratnum_den
         type(ratnum), value :: a
      end function ratnum_den
   end interface

   interface
      function ratnum_to_double(a) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         real(c_double) :: ratnum_to_double
         type(ratnum), value :: a
      end function ratnum_to_double
   end interface

   interface
      function ratnum_add(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         type(ratnum) :: ratnum_add
         type(ratnum), intent(in), value :: a, b
      end function ratnum_add
   end interface

   interface
      function ratnum_subt(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         type(ratnum) :: ratnum_subt
         type(ratnum), intent(in), value :: a, b
      end function ratnum_subt
   end interface

   interface
      function ratnum_mult(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         type(ratnum) :: ratnum_mult
         type(ratnum), intent(in), value :: a, b
      end function ratnum_mult
   end interface

   interface
      function ratnum_div(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         type(ratnum) :: ratnum_div
         type(ratnum), intent(in), value :: a, b
      end function ratnum_div
   end interface

   interface
      subroutine ratnum_print(a) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         type(ratnum), value :: a
      end subroutine ratnum_print
   end interface

   interface
      function ratnum_eq(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         logical(c_bool) :: ratnum_eq
         type(ratnum), intent(in), value :: a, b
      end function ratnum_eq
   end interface

   interface
      function ratnum_ne(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum
         logical(c_bool) :: ratnum_ne
         type(ratnum), intent(in), value :: a, b
      end function ratnum_ne
   end interface

   type, bind(c) :: uqnt
      real(c_double)  :: val, unc
      logical(c_bool) :: prop_unc
      type(ratnum)    :: len_d, mass_d, time_d, temp_d
   end type uqnt

   interface
      function uqnt_val(a) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         real(c_double) :: uqnt_val
         type(uqnt), value :: a
      end function uqnt_val
   end interface

   interface
      function uqnt_unc(a) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         real(c_double) :: uqnt_unc
         type(uqnt), value :: a
      end function uqnt_unc
   end interface

   interface
      function uqnt_prop_unc(a) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         logical(c_bool) :: uqnt_prop_unc
         type(uqnt), value :: a
      end function uqnt_prop_unc
   end interface

   interface
      function uqnt_norm(val, unc, units) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_norm
         real(c_double), value :: val, unc
         type(uqnt), value :: units
      end function uqnt_norm
   end interface

   interface
      function uqnt_unifb(min_val, max_val, units) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_unifb
         real(c_double), value :: min_val, max_val
         type(uqnt), value :: units
      end function uqnt_unifb
   end interface

   interface
      function uqnt_unif(val, half_width, units) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_unif
         real(c_double), value :: val, half_width
         type(uqnt), value :: units
      end function uqnt_unif
   end interface

   interface
      function uqnt_blk(val, units) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_blk
         real(c_double), value :: val
         type(uqnt), value :: units
      end function uqnt_blk
   end interface

   interface
      function uqnt_num(val) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_num
         real(c_double), value :: val
      end function uqnt_num
   end interface

   interface
      function uqnt_same_dim(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         logical(c_bool) :: uqnt_same_dim
         type(uqnt), value :: a, b
      end function uqnt_same_dim
   end interface

   interface
      function uqnt_add(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_add
         type(uqnt), intent(in), value :: a, b
      end function uqnt_add
   end interface

   interface
      function uqnt_subt(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_subt
         type(uqnt), intent(in), value :: a, b
      end function uqnt_subt
   end interface

   interface
      function uqnt_mult(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_mult
         type(uqnt), intent(in), value :: a, b
      end function uqnt_mult
   end interface

   interface
      function uqnt_div(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_div
         type(uqnt), intent(in), value :: a, b
      end function uqnt_div
   end interface

   interface
      function uqnt_pow(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_pow
         type(uqnt), intent(in), value :: a, b
      end function uqnt_pow
   end interface

   interface
      function uqnt_rpow(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum, uqnt
         type(uqnt) :: uqnt_rpow
         type(uqnt), intent(in), value :: a
         type(ratnum), intent(in), value :: b
      end function uqnt_rpow
   end interface

   interface
      function uqnt_rpow_int(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import ratnum, uqnt
         type(uqnt) :: uqnt_rpow_int
         type(uqnt), intent(in), value :: a
         integer(c_int), intent(in), value :: b
      end function uqnt_rpow_int
   end interface

   interface
      function uqnt_rpow_str(a, str) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_rpow_str
         type(uqnt), intent(in), value :: a
         character(kind=c_char), intent(in), dimension(*) :: str
      end function uqnt_rpow_str
   end interface

   interface
      function uqnt_sqrt(a) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_sqrt
         type(uqnt), intent(in), value :: a
      end function uqnt_sqrt
   end interface

   interface
      subroutine uqnt_print(a) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt), value :: a
      end subroutine uqnt_print
   end interface

   interface
      function uqnt_eq(a,b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         logical(c_bool) :: uqnt_eq
         type(uqnt), intent(in), value :: a, b
      end function uqnt_eq
   end interface

   interface
      function uqnt_ne(a,b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         logical(c_bool) :: uqnt_ne
         type(uqnt), intent(in), value :: a, b
      end function uqnt_ne
   end interface

   interface
      function uqnt_lt(a,b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         logical(c_bool) :: uqnt_lt
         type(uqnt), intent(in), value :: a, b
      end function uqnt_lt
   end interface

   interface
      function uqnt_gt(a,b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         logical(c_bool) :: uqnt_gt
         type(uqnt), intent(in), value :: a, b
      end function uqnt_gt
   end interface

   interface
      function uqnt_le(a,b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         logical(c_bool) :: uqnt_le
         type(uqnt), intent(in), value :: a, b
      end function uqnt_le
   end interface

   interface
      function uqnt_ge(a,b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         logical(c_bool) :: uqnt_ge
         type(uqnt), intent(in), value :: a, b
      end function uqnt_ge
   end interface

   interface
      function unit_one() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_one
      end function unit_one
   end interface

   interface
      function unit_tera() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_tera
      end function unit_tera
   end interface

   interface
      function unit_giga() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_giga
      end function unit_giga
   end interface

   interface
      function unit_mega() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_mega
      end function unit_mega
   end interface

   interface
      function unit_kilo() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_kilo
      end function unit_kilo
   end interface

   interface
      function unit_hecto() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_hecto
      end function unit_hecto
   end interface

   interface
      function unit_deca() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_deca
      end function unit_deca
   end interface

   interface
      function unit_deci() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_deci
      end function unit_deci
   end interface

   interface
      function unit_centi() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_centi
      end function unit_centi
   end interface

   interface
      function unit_milli() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_milli
      end function unit_milli
   end interface

   interface
      function unit_micro() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_micro
      end function unit_micro
   end interface

   interface
      function unit_nano() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_nano
      end function unit_nano
   end interface

   interface
      function unit_pico() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_pico
      end function unit_pico
   end interface

   interface
      function unit_meter() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_meter
      end function unit_meter
   end interface

   interface
      function unit_kilogram() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_kilogram
      end function unit_kilogram
   end interface

   interface
      function unit_second() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_second
      end function unit_second
   end interface

   interface
      function unit_kelvin() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_kelvin
      end function unit_kelvin
   end interface

   interface
      function unit_foot() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_foot
      end function unit_foot
   end interface

   interface
      function unit_inch() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_inch
      end function unit_inch
   end interface

   interface
      function unit_yard() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_yard
      end function unit_yard
   end interface

   interface
      function unit_gram() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_gram
      end function unit_gram
   end interface

   interface
      function unit_pound_mass() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_pound_mass
      end function unit_pound_mass
   end interface

   interface
      function unit_avoirdupois_ounce() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_avoirdupois_ounce
      end function unit_avoirdupois_ounce
   end interface

   interface
      function unit_minute() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_minute
      end function unit_minute
   end interface

   interface
      function unit_hour() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_hour
      end function unit_hour
   end interface

   interface
      function unit_day() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_day
      end function unit_day
   end interface

   interface
      function unit_rankine() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_rankine
      end function unit_rankine
   end interface

   interface
      function unit_hertz() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_hertz
      end function unit_hertz
   end interface

   interface
      function unit_radian() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_radian
      end function unit_radian
   end interface

   interface
      function unit_steradian() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_steradian
      end function unit_steradian
   end interface

   interface
      function unit_degree() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_degree
      end function unit_degree
   end interface

   interface
      function unit_liter() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_liter
      end function unit_liter
   end interface

   interface
      function unit_imperial_gallon() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_imperial_gallon
      end function unit_imperial_gallon
   end interface

   interface
      function unit_us_gallon() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_us_gallon
      end function unit_us_gallon
   end interface

   interface
      function unit_imperial_fluid_ounce() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_imperial_fluid_ounce
      end function unit_imperial_fluid_ounce
   end interface

   interface
      function unit_us_fluid_ounce() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_us_fluid_ounce
      end function unit_us_fluid_ounce
   end interface

   interface
      function unit_newton() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_newton
      end function unit_newton
   end interface

   interface
      function unit_pound_force() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_pound_force
      end function unit_pound_force
   end interface

   interface
      function unit_atmosphere() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_atmosphere
      end function unit_atmosphere
   end interface

   interface
      function unit_bar() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_bar
      end function unit_bar
   end interface

   interface
      function unit_millimeter_of_mercury() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_millimeter_of_mercury
      end function unit_millimeter_of_mercury
   end interface

   interface
      function unit_inch_of_mercury() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_inch_of_mercury
      end function unit_inch_of_mercury
   end interface

   interface
      function unit_inch_of_water() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_inch_of_water
      end function unit_inch_of_water
   end interface

   interface
      function unit_pascal() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_pascal
      end function unit_pascal
   end interface

   interface
      function unit_pound_per_square_inch() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_pound_per_square_inch
      end function unit_pound_per_square_inch
   end interface

   interface
      function unit_torr() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_torr
      end function unit_torr
   end interface

   interface
      function unit_joule() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_joule
      end function unit_joule
   end interface

   interface
      function unit_gram_calorie() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_gram_calorie
      end function unit_gram_calorie
   end interface

   interface
      function unit_kilogram_calorie() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_kilogram_calorie
      end function unit_kilogram_calorie
   end interface

   interface
      function unit_british_thermal_unit() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_british_thermal_unit
      end function unit_british_thermal_unit
   end interface

   interface
      function unit_watt() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_watt
      end function unit_watt
   end interface

   interface
      function u_km() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_km
      end function u_km
   end interface

   interface
      function u_m() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_m
      end function u_m
   end interface

   interface
      function u_cm() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_cm
      end function u_cm
   end interface

   interface
      function u_mm() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_mm
      end function u_mm
   end interface

   interface
      function u_um() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_um
      end function u_um
   end interface

   interface
      function u_nm() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_nm
      end function u_nm
   end interface

   interface
      function u_kg() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_kg
      end function u_kg
   end interface

   interface
      function u_g() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_g
      end function u_g
   end interface

   interface
      function u_s() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_s
      end function u_s
   end interface

   interface
      function u_ms() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_ms
      end function u_ms
   end interface

   interface
      function u_us() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_us
      end function u_us
   end interface

   interface
      function u_ns() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_ns
      end function u_ns
   end interface

   interface
      function u_K() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_K
      end function u_K
   end interface

   interface
      function u_lbm() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_lbm
      end function u_lbm
   end interface

   interface
      function u_GHz() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_GHz
      end function u_GHz
   end interface

   interface
      function u_MHz() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_MHz
      end function u_MHz
   end interface

   interface
      function u_kHz() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_kHz
      end function u_kHz
   end interface

   interface
      function u_Hz() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_Hz
      end function u_Hz
   end interface

   interface
      function u_rad() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_rad
      end function u_rad
   end interface

   interface
      function u_sr() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_sr
      end function u_sr
   end interface

   interface
      function u_L() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_L
      end function u_L
   end interface

   interface
      function u_mL() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_mL
      end function u_mL
   end interface

   interface
      function u_N() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_N
      end function u_N
   end interface

   interface
      function u_lbf() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_lbf
      end function u_lbf
   end interface

   interface
      function u_atm() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_atm
      end function u_atm
   end interface

   interface
      function u_kbar() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_kbar
      end function u_kbar
   end interface

   interface
      function u_bar() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_bar
      end function u_bar
   end interface

   interface
      function u_mbar() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_mbar
      end function u_mbar
   end interface

   interface
      function u_GPa() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_GPa
      end function u_GPa
   end interface

   interface
      function u_MPa() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_MPa
      end function u_MPa
   end interface

   interface
      function u_kPa() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_kPa
      end function u_kPa
   end interface

   interface
      function u_hPa() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_hPa
      end function u_hPa
   end interface

   interface
      function u_Pa() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_Pa
      end function u_Pa
   end interface

   interface
      function u_J() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_J
      end function u_J
   end interface

   interface
      function u_Btu() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_Btu
      end function u_Btu
   end interface

   interface
      function u_W() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: u_W
      end function u_W
   end interface

   interface
      function absolute_zero() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: absolute_zero
      end function absolute_zero
   end interface

   interface
      function standard_atmospheric_pressure() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: standard_atmospheric_pressure
      end function standard_atmospheric_pressure
   end interface

   interface
      function standard_gravitational_acceleration() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: standard_gravitational_acceleration
      end function standard_gravitational_acceleration
   end interface

   interface
      function celsius_norm(val, unc) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: celsius_norm
         real(c_double), value :: val, unc
      end function celsius_norm
   end interface

   interface
      function celsius_unif(val, half_width) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: celsius_unif
         real(c_double), value :: val, half_width
      end function celsius_unif
   end interface

   interface
      function celsius_blk(val) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: celsius_blk
         real(c_double), value :: val
      end function celsius_blk
   end interface

   interface
      function fahrenheit_norm(val, unc) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: fahrenheit_norm
         real(c_double), value :: val, unc
      end function fahrenheit_norm
   end interface

   interface
      function fahrenheit_unif(val, half_width) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: fahrenheit_unif
         real(c_double), value :: val, half_width
      end function fahrenheit_unif
   end interface

   interface
      function fahrenheit_blk(val) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: fahrenheit_blk
         real(c_double), value :: val
      end function fahrenheit_blk
   end interface

   interface operator (+)
      module procedure ratnum_add, uqnt_add_f
   end interface operator (+)

   interface operator (-)
      module procedure ratnum_subt, uqnt_subt_f
   end interface operator (-)

   interface operator (*)
      module procedure ratnum_mult, uqnt_mult_f
   end interface operator (*)

   interface operator (/)
      module procedure ratnum_div, uqnt_div_f
   end interface operator (/)

   interface operator (**)
      module procedure uqnt_pow_f, uqnt_rpow_f, uqnt_rpow_int_f
   end interface operator (**)

   interface sqrt
      procedure uqnt_sqrt_f
   end interface sqrt

   interface operator (==)
      module procedure ratnum_eq, uqnt_eq
   end interface operator (==)

   interface operator (/=)
      module procedure ratnum_ne, uqnt_ne
   end interface operator (/=)

   interface operator (<)
      module procedure uqnt_lt
   end interface operator (<)

   interface operator (>)
      module procedure uqnt_gt
   end interface operator (>)

   interface operator (<=)
      module procedure uqnt_le
   end interface operator (<=)

   interface operator (>=)
      module procedure uqnt_ge
   end interface operator (>=)
contains
   impure elemental function uqnt_add_f(a, b) result(c)
      type(uqnt), intent(in) :: a, b
      type(uqnt) :: c
      c = uqnt_add(a,b)
   end function uqnt_add_f

   impure elemental function uqnt_subt_f(a, b) result(c)
      type(uqnt), intent(in) :: a, b
      type(uqnt) :: c
      c = uqnt_subt(a,b)
   end function uqnt_subt_f

   impure elemental function uqnt_mult_f(a, b) result(c)
      type(uqnt), intent(in) :: a, b
      type(uqnt) :: c
      c = uqnt_mult(a,b)
   end function uqnt_mult_f

   impure elemental function uqnt_div_f(a, b) result(c)
      type(uqnt), intent(in) :: a, b
      type(uqnt) :: c
      c = uqnt_div(a,b)
   end function uqnt_div_f

   impure elemental function uqnt_pow_f(a, b) result(c)
      type(uqnt), intent(in) :: a, b
      type(uqnt) :: c
      c = uqnt_pow(a,b)
   end function uqnt_pow_f

   impure elemental function uqnt_rpow_f(a, b) result(c)
      type(uqnt), intent(in) :: a
      type(ratnum), intent(in) :: b
      type(uqnt) :: c
      c = uqnt_rpow(a,b)
   end function uqnt_rpow_f

   impure elemental function uqnt_rpow_int_f(a, b) result(c)
      type(uqnt), intent(in) :: a
      integer(c_int), intent(in) :: b
      type(uqnt) :: c
      c = uqnt_rpow_int(a,b)
   end function uqnt_rpow_int_f

   impure elemental function uqnt_sqrt_f(a) result(b)
      type(uqnt), intent(in) :: a
      type(uqnt) :: b
      b = uqnt_sqrt(a)
   end function uqnt_sqrt_f
end module uqnt_f
