! Copyright (C) 2023 Andrew Trettel
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
      function uqnt_sqrt(a) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_sqrt
         type(uqnt), intent(in), value :: a
      end function uqnt_sqrt
   end interface

   interface sqrt
      procedure uqnt_sqrt
   end interface sqrt

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
      function unit_meter() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_meter
      end function unit_meter
   end interface

   interface
      function unit_gram() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_gram
      end function unit_gram
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
      function unit_kilogram() bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: unit_kilogram
      end function unit_kilogram
   end interface

   interface operator (+)
      module procedure ratnum_add, uqnt_add
   end interface operator (+)

   interface operator (-)
      module procedure ratnum_subt, uqnt_subt
   end interface operator (-)

   interface operator (*)
      module procedure ratnum_mult, uqnt_mult
   end interface operator (*)

   interface operator (/)
      module procedure ratnum_div, uqnt_div
   end interface operator (/)

   interface operator (**)
      module procedure uqnt_pow, uqnt_rpow
   end interface operator (**)

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
end module uqnt_f
