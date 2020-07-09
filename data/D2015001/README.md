# 2015, Andrew Trettel and Johan Larsson of the University of Maryland, College Park, channel flow simulation

- The direct numerical simulations are described in `TrettelA+2015+eng+THES`
  and `TrettelA+2016+eng+JOUR`.

- When using the data, cite `TrettelA+2016+eng+JOUR`
  ([link](https://doi.org/10.1063/1.4942022)).


## Description of columns in global parameter CSV file

1. Originator's identifier: profile identifier in `TrettelA+2016+eng+JOUR`

2. `Ma_bulk`: bulk Mach number

3. `Re_bulk`: bulk Reynolds number

4. `Pr`: Prandtl number

5. `gamma`: heat capacity ratio

6. `R`: specific gas constant

7. `omega`: power-law viscosity exponent

8. `n_x`: number of points in the `x`-direction

9. `n_y`: number of points in the `y`-direction

10. `n_z`: number of points in the `z`-direction

11. `T_w`: wall temperature

12. `rho_w`: wall density

13. `mu_w`: wall dynamic viscosity

14. `tau_w`: mean wall shear stress

15. `u_e`: mean center-line velocity

16. `T_e`: mean center-line temperature

17. `rho_e`: mean center-line density

18. `mu_e`: dynamic viscosity function evaluated at mean center-line
temperature

19. `u_tau`: friction velocity based on wall units

20. `l_nu`: viscous length scale based on wall units

21. `T_tau`: friction temperature based on wall units

22. `B_q`: dimensionless law-of-the-wall heat flux based on wall units

23. `q_w`: wall heat flux

24. `Re_tau`: friction Reynolds number based on wall units

25. `Re_tau*`: semi-local friction Reynolds number

26. `Ma_tau`: friction Mach number based on wall units


## Description of columns in profile CSV files

1. `y`: Wall-normal coordinate

2. `y+`: Wall-normal coordinate, scaled by viscous units

3. `Y+ch`: Wall-normal coordinate, transformed by the Cope and Hartree
transformation (viscous sublayer coordinate transformation)

4. `Y+hw`: Wall-normal coordinate, transformed by the Howarth transformation

5. `Y+tl`: Wall-normal coordinate, transformed by the Trettel-Larsson
transformation (semi-local scaling)

6. `<u>`: Reynolds-averaged streamwise velocity

7. `<u>_f`: Favre-averaged streamwise velocity

8. `u+`: Reynolds-averaged streamwise velocity, scaled by viscous units

9. `U+vd`: Reynolds-averaged streamwise velocity, transformed by the Van Driest
transformation

10. `U+vs`: Reynolds-averaged streamwise velocity, transformed by the viscous
sublayer transformation

11. `U+tl`: Reynolds-averaged streamwise velocity, transformed by the
Trettel-Larsson transformation

12. `<rho>`: Reynolds-averaged density

13. `<P>`: Reynolds-averaged pressure

14. `<T>`: Reynolds-averaged temperature

15. `<T>_f`: Favre-averaged temperature

16. `mu`: Viscosity function evaluated at the Reynolds-averaged temperature

17. `<u''u''>_f`: Favre-averaged streamwise velocity fluctuations squared

18. `<v''v''>_f`: Favre-averaged wall-normal velocity fluctuations squared

19. `<w''w''>_f`: Favre-averaged spanwise velocity fluctuations squared

20. `<u''v''>_f`: Favre-averaged Reynolds shear stress

21. `<rho*u''u''>/tau_w`: Favre-averaged streamwise velocity fluctuations
squared, scaled by Morkovin's scaling

22. `<rho*v''v''>/tau_w`: Favre-averaged wall-normal velocity fluctuations
squared, scaled by Morkovin's scaling

23. `<rho*w''w''>/tau_w`: Favre-averaged spanwise velocity fluctuations
squared, scaled by Morkovin's scaling

24. `<rho*u''v''>/tau_w`: Favre-averaged Reynolds shear stress, scaled by
Morkovin's scaling

25. `<rho'rho'>`: Reynolds-averaged density fluctuations squared

26. `<P'P'>`: Reynolds-averaged pressure fluctuations squared

27. `<T''T''>_f`: Favre-averaged temperature fluctuations squared

28. `<T''v''>_f`: Favre-averaged turbulent heat flux

-------------------------------------------------------------------------------

Copyright © 2020 Andrew Trettel

This file is licensed under the Creative Commons Attribution 4.0 International
license (`CC-BY-4.0`).  For more information, please visit the Creative Commons
website at <https://creativecommons.org/licenses/by/4.0/>.
