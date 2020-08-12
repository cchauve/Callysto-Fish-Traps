# Generalizing The Fish Trap Model

## Issues with generalizing the current model
The current model is a simple model that really only uses the length of
the trap covered by water and how long that are is under water as a
factor in determining the rate in/ rate out of fish as they swim in the
vicinity of the trap. It uses simple geometry to calculate this.  Due
to this the shape of the model is almost negligible.

### Overcoming these issues using the current code base
The function "get_perimiter" currently assumes a semicircular trap and
does some simple geometry using the sea level to calculate the area of
the trap under water. Modifying it so it accepts as input the set of
point on the perimeter (x,y,z) and simply compares the z value of each
point to the z-value of the tide would allow the ratio to simply be the
number of points who z value is lower than the tide value divide by the
total number of perimeter points.
 
## Another Model
Many of the fish traps described in the literature are not purely semi-
circular. In river-mouths there are chevron and hook shaped traps. The
chevron act to guide the fish into the hook shaped trap. Here, clearly,
other factors than the water level must be considered. We could start a
model using Brownian or random motion and modify it for tide, direction
of water flow and expected fish behaviour, we could obtain a model that
is much more sensitive to the shape of the trap and be much more
appealing to students.

[here](https://imgur.com/Io2Mm8G) is a quick example of a prototype for
such a model. This was created using simple Object Oriented Design in
python. It can readily be improved by allowing user to select the shape 
of the trap and by improving the fish "behaviour" or movement.

