! Copyright (C) 2023 Andrew Trettel
module uqnt_f
   use, intrinsic :: iso_c_binding

   implicit none

   type, bind(c) :: uqnt
      real(c_double) :: value, uncertainty
      real(c_double) :: len_d, mass_d, time_d, temp_d
   end type uqnt

   type(uqnt), bind(c) :: one, meter, gram, second, deg_kelvin

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
      function uqnt_unif(min_val, max_val, units) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_unif
         real(c_double), value :: min_val, max_val
         type(uqnt), value :: units
      end function uqnt_unif
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
         type(uqnt), value :: a, b
      end function uqnt_add
   end interface

   interface
      function uqnt_subt(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_subt
         type(uqnt), value :: a, b
      end function uqnt_subt
   end interface

   interface
      function uqnt_mult(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_mult
         type(uqnt), value :: a, b
      end function uqnt_mult
   end interface

   interface
      function uqnt_div(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_div
         type(uqnt), value :: a, b
      end function uqnt_div
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
         type(uqnt), value :: a, b
      end function uqnt_eq
   end interface
end module uqnt_f
