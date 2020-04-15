A taxonomy of simple fluid flows
================================


Note
----

This taxonomy is in draft form.  This database will only use the final classes
under the shear layer category, but I wanted to provide a more general taxonomy
to better organize the data in the first place.


Classes
-------

All classes:

- Class `B` = boundary layers
- Class `D` = duct flows
- Class `E` = external flows
- Class `F` = free shear flows
- Class `G` = isotropic flows
- Class `H` = homogeneous flows
- Class `I` = internal flows
- Class `J` = (free) jets
- Class `K` = wall jets
- Class `M` = mixing layers
- Class `N` = inhomogeneous flows
- Class `R` = flows with relative motion of the boundaries
- Class `S` = shear layers
- Class `U` = flows
- Class `W` = wakes

Taxonomy:

- `U` = flows

    - `H` = homogeneous flows

        - `G` = isotropic flows

    - `N` = inhomogeneous flows

        - `S` = shear layers

            - `F` = free shear flows

                - `J` = (free) jets

                - `M` = mixing layers

                - `W` = wakes

            - `E` = external flows

                - `B` = boundary layers

                - `K` = wall jets

            - `I` = internal flows

                - `D` = duct flows

                - `R` = flows with relative motion of the boundaries

Tree diagram:

          - H ----- G
         /
        /                        -- J
       /                        /
    U -                   - F ----- M
       \                 /      \
        \               /        -- W
         \             /
          - N ----- S ----- E ----- B
                       \        \
                        \        -- K
                         \
                          - I ----- D
                                \
                                 -- R

Codes reserved for future discussion:

- `A` = acoustic waves

- `C` = cavity flows

- `O` = waves (from "onde")

- `P` = plumes

- `T` = transverse jets

- `V` = vortices

- `X` = shock waves (from "explosion")

- Unused: `L`, `Q`, `Y`, `Z`


Principles of this taxonomy
---------------------------

Any practical taxonomy should organize information in a useful manner.  This
project tries to organize a wide variety of data from different shear layers
into a unified framework, so it requires some means to distinguish between
different kinds of flows.  Previous classification systems have tended to be
too complex, with too many classes and too much ambiguity.  A simpler
classification scheme with a limited number of classes will be much easier to
use.  To achieve this goal, this taxonomy follows 5 principles (language
following RFC 2119):

1. *Each flow class MUST be identified by a single letter related to the flow's
name.*

This principle limits the maximum number of classes to 26 and creates a simple
and obvious code to identify a data set's class.  Moreover, using letters for
the code allows changes to the taxonomy much more readily than using
hierarchical information for the code (the location of the class in the
taxonomy).  The choice of letters means that if the taxonomy needs to be
changed, it can be changed without having to update the codes.

A brief explanation of unexpected codes:

- `G` for isotropic flows from "grid turbulence".

- `K` for wall jets since it is the next letter after `J`.

- `N` for inhomogeneous flows from its second letter.

- `U` for flows from "unclassified" flows.

2. *Individual data sets MUST belong to a single class.*

For example, suppose that there are two classes for boundary layers: attached
boundary layers and separated boundary layers.  It is possible that a single
data set contains a series of boundary layer profiles that separate and then
reattach.  Should the entire series of profiles be classified as separated even
though only some are?  Should each profile be classified individually instead?
No, the simplest solution is to create only one class for boundary layers.
This choice makes classifying a given data set much easier.

3. *Each flow class MUST work for all coordinate systems.*

This principle prevents additional classes being created for each coordinate
system.  For example, both round jets and plane jets are jets first and
foremost, so there is no need for an additional class for each.  Similarly,
both pipe flows and rectangular duct flows are classified as duct flows since
they are duct flows first and foremost.  Additional fields should specify the
coordinate system and geometry of the boundaries, to keep track of this
information outside of the taxonomy itself.

4. *The differences between classes SHOULD be intrinsically discrete and
unquantifiable.*

For example, there should be a single class for boundary layers, and not
multiple classes (incompressible laminar boundary layers, incompressible
turbulent boundary layers, compressible laminar boundary layers, and
compressible turbulent boundary layers).  In each case, the difference between
those classes can be largely quantified with the Reynolds and Mach numbers, so
there is no need to create additional classes when the effect can be quantified
continuously using an additional variable rather than discretely with a
different class.

By this principle, a plume (buoyant jet) is classified under class `J` (jets).
Buoyancy is quantifiable and therefore a plume, as a type of jet, does not
receive a separate class.

Note that internal flows violate this principle since the amount of relative
motion can in fact be quantified, but I split internal flows into two classes
(`D` and `R`) anyway.  In this case, most internal flows do not have both a
pressure gradient and relative motion of the boundaries, so it is more
practical to divide internal flows this way.

5. *The taxonomy SHOULD emphasize differences in flow pattern and geometry over
differences in flow mechanism and physics.*

This principle guides the large-scale structure of the taxonomy more than
small-scale structure.  The point is that the taxonomy divides flows up more by
their flow pattern (homogeneity, kinematics, and presence of boundaries) than
by the specific physics driving the flow (the flow mechanism) or especially the
types of additional physics in the flow (shock waves, separation, cavitation,
free-stream turbulence, ...).

The overall structure of the tree diagram emphasizes this principle by
immediately considering homogeneity (geometry), then shear (kinematics), and
then the influence of boundaries (geometry again).  Indeed, no class is defined
exclusively by the presence of additional physics.


-------------------------------------------------------------------------------

Copyright © 2020 Andrew Trettel

This file is licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.  You may
obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
