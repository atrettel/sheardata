Shear layer data compilation
============================

Flow data from shear layer experiments and simulations presented in an open,
modern, and unified format.


Goals
-----

- Single SQLite database as primary output file.

- Python module to load and use SQLite database.

- Documentation also serves as a data and literature review for different flow
  classes (for use in meta-analyses and other work).

- CSV files as input files.  SQLite database file and PDF documentation file as
  output files.

- Uncertainty quantification and data validation for as many cases as possible.

- Emphasis on archival quality and long-term access.

    - [Library of Congress recommended formats statement](https://www.loc.gov/preservation/resources/rfs/)


Previous tabulated data compilations
------------------------------------

I have already conducted a literature search to identify relevant individual
studies to include in the database.  However, many previous data compilations
already exist and provide an extensive amount of data in an already processed
format that is ready for both reference and study.  All of these compilations
are older and presented in tabulated form, which requires digitization for use.
I identify several of these previous data compilations below.

Note that some of these data compilations provided data in a digital form
distributed with the reports, not as printed tables.

- Koo, Eugene Chen 1932, "Mechanisms of isothermal and non-isothermal flow of
  fluids in pipes".  Massachusetts Institute of Technology Ph.D. thesis.

    - [MIT](http://hdl.handle.net/1721.1/61824)

    - Global and profile data.

- Peterson, J. B. Jr. 1963, "A comparison of experimental and theoretical
  results for compressible turbulent-boundary-layer skin friction with zero
  pressure gradient".  NASA-TN-D-1795.

    - [HathiTrust](https://hdl.handle.net/2027/uiug.30112008542125?urlappend=%3Bseq=373)

    - Global data only.

- Chi, S. W. 1965, "Friction and Heat Transfer in a Compressible Turbulent
  Boundary Layer on a Smooth Flat Plate".  Imperial College London Ph.D.
  thesis.

    - [Imperial College London](http://hdl.handle.net/10044/1/15754)

    - Global data only.

    - Additional commentary available in archival journal article below.

        - Spalding, D. B. and Chi, S. W. 1964, "The drag of a compressible
          turbulent boundary layer on a smooth flat plate with and without heat
          transfer".  Journal of Fluid Mechanics, v. 18, n. 1, pp. 117-143.

            - [Journal of Fluid Mechanics](https://doi.org/10.1017/S0022112064000088)

- Coles, D. E. and Hirst, E. A. 1969.  *Computation of Turbulent Boundary
  layers—1968 AFOSR-IFP-Stanford Conference*, Volume 2, "Compiled Data".

    - [DTIC (abstract only)](https://apps.dtic.mil/sti/citations/AD0696082)

    - [NTIS (abstract only)](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/AD696082.xhtml)

    - [WorldCat](https://www.worldcat.org/title/computation-of-turbulent-boundary-layers-1968-afosr-ifp-stanford-conference-proceedings/oclc/561999041)

    - This compilation is unavailable online.

- Zwarts, F. J. 1970, "The compressible turbulent boundary layer in a pressure
  gradient".  McGill University Ph.D. thesis.

    - [McGill University](https://escholarship.mcgill.ca/concern/theses/xs55mc623)

    - Global data only.

- Wheeler, A. J. and Johnston, J. P. 1972, "Three dimensional turbulent
  boundary layers: Data sets for two-space coordinate flows", Stanford
  University Thermosciences Report MD-32, NASA-CR-138962.

    - This compilation is a continuation of the compilation by Coles and Hirst,
      but for three-dimensional boundary layers.  However, the identifier
      system is different.

    - [NASA](https://ntrs.nasa.gov/citations/19740021540)

    - [NTIS (abstract only)](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/N7429653.xhtml)

- Birch, S. F. and Eggers, J. M. 1973.  *Free Turbulent Shear Flows*, Volume 2,
  "Summary of Data".  NASA-SP-321.

    - [NASA](https://ntrs.nasa.gov/search.jsp?R=19730018486)

- Fernholz, H. H. and Finley, P. J. 1977.  *A Critical Compilation of
  Compressible Turbulent Boundary Layer Data*.  AGARD-AG-223.

    - [DTIC](https://apps.dtic.mil/sti/citations/ADA045367)

    - [NATO](https://www.sto.nato.int/publications/AGARD/Forms/AGARD%20Document%20Set/docsethomepage.aspx?ID=9138&FolderCTID=0x0120D5200078F9E87043356C409A0D30823AFA16F60B00B8BCE98BB37EB24A8258823D6B11F157&List=03e8ea21-64e6-4d37-8235-04fb61e122e9&RootFolder=%2Fpublications%2FAGARD%2FAGARD%2DAG%2D223)

    - [NTIS](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA045367.xhtml)

- AGARD Fluid Dynamics Panel Working Group 4 (1979), *Experimental Data Base
  for Computer Program Assessment*, AGARD-AR-138.

    - [DTIC](https://apps.dtic.mil/sti/citations/ADA073982)

    - [NATO](https://www.sto.nato.int/publications/AGARD/Forms/AGARD%20Document%20Set/docsethomepage.aspx?ID=8802&FolderCTID=0x0120D5200078F9E87043356C409A0D30823AFA16F60B00B8BCE98BB37EB24A8258823D6B11F157&List=03e8ea21-64e6-4d37-8235-04fb61e122e9&RootFolder=https://www.sto.nato.int/publications/AGARD/AGARD-AR-138)

    - [NTIS](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA073982.xhtml)

- Fernholz, H. H. and Finley, P. J. 1980.  *A Critical Commentary on Mean Flow
  Data for Two-Dimensional Compressible Turbulent Boundary Layers*.
  AGARD-AG-253.

    - [DTIC](https://apps.dtic.mil/sti/citations/ADA087704)

    - [NTIS](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA087704.xhtml)

- Complex Turbulent Flows (and later Collaborative Testing of Turbulence
  Models)

    - [DTIC, volume 1](https://apps.dtic.mil/sti/citations/ADA135569)

    - [DTIC, volume 2](https://apps.dtic.mil/sti/citations/ADA135570)

    - [DTIC, volume 3](https://apps.dtic.mil/sti/citations/ADA136034)

    - [NASA, data files](https://turbmodels.larc.nasa.gov/bradshaw.html)

- Fernholz, H. H. and Finley, P. J. and Mikulla, V. 1981.  *A Further
  Compilation of Compressible Boundary Layer Data with a Survey of Turbulence
  Data*.  AGARD-AG-263.

    - [DTIC](https://apps.dtic.mil/sti/citations/ADA111638)

    - [NTIS](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA111638.xhtml)

    - [NATO](https://www.sto.nato.int/publications/AGARD/Forms/AGARD%20Document%20Set/docsethomepage.aspx?ID=9062&FolderCTID=0x0120D5200078F9E87043356C409A0D30823AFA16F60B00B8BCE98BB37EB24A8258823D6B11F157&List=03e8ea21-64e6-4d37-8235-04fb61e122e9&RootFolder=%2Fpublications%2FAGARD%2FAGARD%2DAG%2D263)

- AGARD Fluid Dynamics Panel Working Group 4 (1984), *Experimental Data Base
  for Computer Program Assessment.  Addendum*, AGARD-AR-138-ADDENDUM.

    - [DTIC](https://apps.dtic.mil/sti/citations/ADA147197)

    - [NTIS](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA147197.xhtml)

- Fernholz, H. H. and Finley, P. J. and Dussauge, J. P. and Smits, A. J. 1989.
  *Survey of Measurements and Measuring Techniques in Rapidly Distorted
  Compressible Turbulent Boundary Layers*.  AGARD-AG-315.

    - [DTIC](https://apps.dtic.mil/sti/citations/ADA211107)

    - [NTIS](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA211107.xhtml)

- Settles, G. S. and Dodson, L. J. 1991, *Hypersonic Shock/Boundary-Layer
  Interaction Database*.  NASA-CR-177577.

    - [NTIS](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/N9115986.xhtml)

    - [Internet Archive](https://archive.org/details/nasa_techdoc_19930015337)

- Settles, G. S. and Dodson, L. J. 1993, *Hypersonic Turbulent Boundary-Layer
  and Free Shear Database Datasets*.  NASA-CR-177610.

    - These are dataset files.

    - [NASA (abstract and request link)](https://ntrs.nasa.gov/search.jsp?R=20100019476)

    - [HathiTrust (abstract only)](https://hdl.handle.net/2027/uva.x004872560?urlappend=%3Bseq=74)

- Settles, G. S. and Dodson, L. J. 1994, *Hypersonic Shock/Boundary-Layer
  Interaction Database: New and Corrected Data*.  NASA-CR-177638.

    - [Internet Archive](https://archive.org/details/nasa_techdoc_19940032012)

- AGARD Fluid Dynamics Panel Working Group 4 (1994), *A selection of
  experimental test cases for the validation of CFD codes*, AGARD-AR-303.

    - [DTIC, volume 1](https://apps.dtic.mil/sti/citations/ADA286061)

    - [DTIC, volume 2](https://apps.dtic.mil/sti/citations/ADA286216)

    - [NTIS, volume 1](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA286061.xhtml)

    - [NTIS, volume 2](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/ADA286216.xhtml)

    - The data is not tabulated in the volumes but was (at one point) available
      on 9 floppy disks.  However, I have been unable to locate a copy.

- AGARD Fluid Dynamics Panel Working Group 21 (1998), *A selection of test
  cases for the validation of large-eddy simulations of turbulent flows*,
  AGARD-AR-345.

    - [AGARD-AR-345 database](https://torroja.dmt.upm.es/turbdata/agard/)

    - [DTIC, CD-ROM (abstract only)](https://apps.dtic.mil/sti/citations/ADM000830)

    - [NATO](https://www.sto.nato.int/publications/AGARD/Forms/AGARD%20Document%20Set/docsethomepage.aspx?ID=8659&FolderCTID=0x0120D5200078F9E87043356C409A0D30823AFA16F60B00B8BCE98BB37EB24A8258823D6B11F157&List=03e8ea21-64e6-4d37-8235-04fb61e122e9&RootFolder=https://www.sto.nato.int/publications/AGARD/AGARD-AR-345)


Links to other online databases
-------------------------------

Here is a list of several other notable online databases with shear flow data.
Much of this data is available as plain text files or CSV files, but some data
is only available in other formats.

- [Center for Turbulence Research data](https://ctr.stanford.edu/research-data)
  (Stanford University)

- [Computational Turbulence Laboratory data](https://larsson.umd.edu/data/)
  (University of Maryland, Larsson group)

- [DNS database of turbulent flows](http://newton.dma.uniroma1.it/database/)
  (University of Rome data, Pirozzoli group)

- [ERCOFTAC Classic Collection](http://cfd.mace.manchester.ac.uk/ercoftac/)

- [FDY Turbulence DNS data
  base](https://www.fdy.tu-darmstadt.de/fdyresearch/dns/direkte_numerische_simulation.en.jsp)

- [Fluid Dynamics Group UPV](http://personales.upv.es/serhocal/)

- [Gas Dynamics Lab data sets](https://smits.princeton.edu/data-sets/)
  (Princeton University, Smits group)

- [Johns Hopkins Turbulence Databases](http://turbulence.pha.jhu.edu/)

- [NASA LaRC Turbulence Modeling
  Resource](https://turbmodels.larc.nasa.gov/index.html)

- [Oden Institute turbulence file server](https://turbulence.oden.utexas.edu/)
  (University of Texas, Moser group)

- [Pedro Volpiani's DNS database](https://www.psvolpiani.com/dns-database)

- [Schlatter group boundary layer DNS/LES
  data](https://www.mech.kth.se/~pschlatt/DATA/) (KTH Royal Institute of
  Technology)

- [Turbulent Database Madrid](https://torroja.dmt.upm.es/turbdata/) (University
  of Madrid, Jimenez group)

- [UK Turbulence Consortium
  database](https://www.ukturbulence.co.uk/database.html)


Licenses for the shear layer data compilation
---------------------------------------------

The nature of the project requires two different licenses: one for data and
another for the source code and documentation.  The data is located in the
`data` directory.  All files in the `data` directory are licensed under the
Creative Commons Attribution 4.0 International license (`CC-BY-4.0`).  All
other files are licensed under the MIT License (`MIT`).

A copy of the Creative Commons Attribution 4.0 International license
(`CC-BY-4.0`) is located at `data/LICENSE.txt`.  A copy of the MIT License
(`MIT`) is located at `LICENSE.txt`.


-------------------------------------------------------------------------------

Copyright © 2020-2021 Andrew Trettel

SPDX-License-Identifier: MIT
