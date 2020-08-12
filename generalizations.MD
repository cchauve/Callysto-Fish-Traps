# Generalizing The Fish Trap Model

## Issues with generalizing the current model
The current model is a simple model that uses the length ofthe trap 
perimeter covered by water to determine the rate of fish in/out.
Hence, how long and how much of the trap is underwater determines
how many fish are in the trap. It uses simple geometry assuming a 
semi-circular trap to calculate this the length of the trap covered.

### Overcoming these issues using the current code base
The function "get_perimiter()" currently assumes a semicircular trap and
does some simple geometry using the sea level to calculate the area of
the trap under water. Modifying it so it accepts as input the set of
point on the perimeter (x,y,z) and simply compares the z value of each
point to the z-value of the tide would allow the ratio to simply be the
length connecting these points. However, this niave improvement would
nessesitate some control of the user input for the shape or checkin the
the trap is indeed "closed" on low tides.
 
## Another Model
Many of the fish traps described in the literature are not purely semi-
circular. In river-mouths there are chevron and hook shaped traps. The
chevron act to guide the fish into the hook shaped trap. Here, clearly,
other factors than the water level must be considered. We could start a
model using Brownia (random) motion for fish movement and modify it for 
tide, direction of water flow and expected fish behaviour, we could 
obtain a model that is much more sensitive to the shape of the trap and 
be much more appealing to students. In this way the trap acts like a 
mofified game of plinko where the pegs are chevrons directing the 
"randomly" moving fish to the chevron or semicircular trap

[here](https://imgur.com/Io2Mm8G) is a quick example of a prototype for
such a model. This was created using simple object rriented design in
python. It can readily be improved by allowing user to select the shape 
of the trap and by improving the fish "behaviour" or movement. Code for
it is found the the visualizations notebook.

