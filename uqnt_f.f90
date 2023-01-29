! Copyright (C) 2023 Andrew Trettel
module uqnt_f
   use, intrinsic :: iso_c_binding

   implicit none

   type, bind(c) :: uqnt
      real(c_double) :: value, uncertainty
      real(c_double) :: length_d, mass_d, time_d, temperature_d
   end type uqnt

   type(uqnt), bind(c) :: one, meter, gram, second, degree_Kelvin

   interface
      function uqnt_norm(a, b, units) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_norm
         real(c_double), value :: a, b
         type(uqnt), value :: units
      end function uqnt_norm
   end interface

   interface
      function uqnt_unif(a, b, units) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_unif
         real(c_double), value :: a, b
         type(uqnt), value :: units
      end function uqnt_unif
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
end module uqnt_f
