# 1956, Hans Reichardt of MPI für Strömungsforschung, Couette flow experiment

- The experiments are described in `ReichardtH+1956+deu+JOUR` and
  `ReichardtH+1959+deu+RPRT`.

    - The data include both laminar and turbulent flows.

    - Tabulated data are given in the 1959 report.

- The experimental setup is also described in `ReichardtH+1954+deu+RPRT`.

- When using the data, please cite `ReichardtH+1956+deu+JOUR`:

    > Reichardt, H. (1956). “Über die Geschwindigkeitsverteilung in einer
    > geradlinigen turbulenten Couetteströmung”. German. In: *Zeitschrift für
    > Angewandte Mathematik und Mechanik* 36.S1, S26– S29. ISSN: `1521-4001`.
    > DOI: `10.1002/zamm.19560361311`.


## CSV files

- All units are either dimensionless or SI.

- `series_1_normalized.csv`, `series_2_normalized.csv`, and
  `series_4_station_4_normalized.csv`

    - These files include the wall points.

    - The velocity is transformed such that the center-line is stationary (see
      figure 9 of the 1959 report).

- `series_3_*.csv`

    - These files exclude the upper and lower wall points.

    - The velocity is transformed such that the center-line is stationary (see
      figure 15 of the 1959 report).

- `series_4_station_1.csv` to `series_4_station_3.csv`

    - These files exclude the upper and lower wall points.

    - The velocity is transformed such that the lower wall is stationary (see
      figure 8 of the 1959 report).

-------------------------------------------------------------------------------

Copyright © 2020-2021 Andrew Trettel

SPDX-License-Identifier: CC-BY-4.0
