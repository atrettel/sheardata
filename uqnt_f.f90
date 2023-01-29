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
      function uqnt_init(a, b, units) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_init
         real(c_double), value :: a, b
         type(uqnt), value :: units
      end function uqnt_init
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
      function uqnt_subtract(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_subtract
         type(uqnt), value :: a, b
      end function uqnt_subtract
   end interface

   interface
      function uqnt_multiply(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_multiply
         type(uqnt), value :: a, b
      end function uqnt_multiply
   end interface

   interface
      function uqnt_divide(a, b) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt) :: uqnt_divide
         type(uqnt), value :: a, b
      end function uqnt_divide
   end interface

   interface
      subroutine uqnt_print(a) bind(c)
         use, intrinsic :: iso_c_binding
         import uqnt
         type(uqnt), value :: a
      end subroutine uqnt_print
   end interface
end module uqnt_f
