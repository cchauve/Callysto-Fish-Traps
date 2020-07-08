import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
import os
import math
from typing import List, Tuple

def get_tide_values():
    """Grabs the tide values measured for one week in comox
    Returns:
        a dataframe containing measured tide values for comox"""

    tide_path = os.path.join('resources', 'comox_tide.csv')
    tide_df = pd.read_csv(tide_path)
    tide_df = tide_df.drop(columns = ['PDT'])
    return tide_df.values.flatten()

def create_tide_plot():
    """Displays a plot of hourly tide levels for 1 week in May using readings from comox """
    tide_values = get_tide_values()
    
    seaborn.set()
    plt.style.use('seaborn-deep')
    x = range(len(tide_values))
    plt.plot(x, tide_values)
    plt.ylabel("tide level (m above sea level)")
    plt.xlabel("time (h)")
    plt.title('tide levels for one week in Comox Harbour')
    plt.savefig("tide.png")
    plt.show()

def get_ratio_of_perimeter_covered(tide_level: float, perimeter,  radius: int =  25, delta: int = 5) -> float:
    """Given a tide level and points on the perimeter of a semi-circular trap gives the ratio of the trap under water

    Args:
        tide_level: A tide level reading in meters above sea-level
        perimeter: a list of (x,y,z) floats descriping the top of the semi-circular trap ordered in increasing x values
        radius: the radius of the semi-circular trap created
        delta: how far down the y axis the "center" of the semi-circle is from the origin

    Returns:
        a float in [0,1] that describes the amount of the trap under water.
        This calculated value ignores the warping of the semi-circle caused by the slope in the z-axis.
    """
    x_values = perimeter[0]
    y_values = perimeter[1]
    z_values = perimeter[2]

    # iterated throught the z values to find the first value underwater
    index = -1
    for i in range(len(z_values)):
        if(z_values[i] <= tide_level):
            index = i
            break;
    #if no point is underwater then return a 0 ratio underwater
    if(index == -1):
        return 0
    
    #record the x and y values for the "first" underwater point
    x = x_values[index]
    y = y_values[index]

    #find the lenth of the chord whos endpoints are (0,1) and (x,y)
    length = np.sqrt((x)**2 + (y - radius - delta)**2)
    
    #find the angle between (0,1) and (x,y) using the length of the three sides of the triangle then divide that by a half pi
    #this ratio is the ratio of the trap that is underwater
    angle = math.acos((2 * radius**2 - length**2) / (2 * radius**2))
    coverage  = angle/ (0.5 * np.pi)
    return coverage

def get_perimeter(radius: int = 25, delta: int = 5, height: float = 2, slope: float = 0.17, intercept: float = 6):
    """Creates set of points at the top of the semi-circular trap

    Args:
        radius: an integer value that sets the radius of the trap
        delta: how far down the y-axis the center of the circle is
        slope: the slope of the beach on which the trap is built
        height: the height from the beach surface to the top of the trap
    
    returns:
        the Perimter, a 2d array:
            [0]: x values
            [1]: y values
            [2]: z values
    """
    
    theta = np.linspace(0, np.pi, 100)
    #equation for a circle
    x = r * np.cos(theta)
    y = r * np.sin(theta) + delta
    # equation for a line
    z = intercept + height - (slope * y)

    return [x,y,z]


def run_trap(radius: int = 25, delta: int = 5, harvesting: bool = False):
    """Runs the fish trap model for 1 week.

    Args:
        radius: the radius of the semi-circular trap created
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        harvesting: if true, user is prompted to harvest some fish at each low tide

    Returns:
        An 2d array containing:
            [0]: The total number of harvested fish at hour indexed
            [1]: The total number of fish in the trap at hour at hour indexed
            [2]: the total number of fish outside the trap at hour indexed
    """
    movement_rate = 0.05
    max_fish = 1000
    current_free_fish = max_fish
    current_caught_fish = 0
    total_harvested = [0]
    in_trap = [0]
    out_trap = [max_fish]
    perimieter_ratio = (np.pi * r) / (np.pi * 25)
    tide_values = get_tide_values()
    
    perimeter = get_perimeter()

    for level in tide_values:
        coverage = get_ratio_of_perimeter_covered(level, perimeter, radius = 25)
        free_to_caught = current_free_fish * coverage * alpha * perimeter_ratio
        caught_to_free = current_caught_fish * coverage * alpha * perimeter_ratio
        current_caught_fish = current_caught_fish - caught_to_free + free_to_caught
        current_free_fish = current_free_fish + caught_to_free - free_to_caught

        if(coverage > 0):
            total_harvested.append(total_harvested[-1])

        else:
            total_harvested.append(total_harvested[-1] + current_caught_fish)
            if (current_caught_fish != 0):
                catches.append(current_caught_fish)

            current_caught_fish = 0
            current_free_fish = max_fish

        in_trap.append(current_caught_fish)
        out_trap.append(current_free_fish)

    return [total_harvested, in_trap, out_trap]

#def plot_trap():

