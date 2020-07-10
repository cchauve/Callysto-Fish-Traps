import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
import os
import math
from typing import List, Tuple


# global variables that act as default values for the trap
default_slope = 0.17
default_inter = 6
default_radius = 25
default_height = 2
default_delta = 5

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

#def get_equation_of_plane(x1,y1, z1, x2, y2, z2, x3, y3, z3):
#    """Takes in three points and calculates the equation of the plane
#
#    returns [e, f, g] where these are the variables of: ex + fy + g = z"""
#
#    # Find two vectors using
#    a1 = x2 - x1
#    b1 = y2 - y1
#    c1 = z2 - z1
#    a2 = x3 - x1
#    b2 = y3 - y1
#    c2 = z3 - z1
#
#   # find a,b,c, d from ax + by + cz = d
#    a = b1 * c2 - b2 * c1
#    b = a2 * c1 - a1 * c2
#    c = a1 * b2 - b1 * a2
#    d = (- a * x1 - b * y1 - c * z1)
#
#    e = a / c
#    f = b / c
#    g = d / c





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

def get_perimeter(radius: int = default_radius, height: float = default_height, delta: int = default_delta, slope: float = default_slope, intercept: float = default_inter):
    """Creates set of points at the top of the semi-circular trap

    Args:
        radius: an integer value that sets the radius of the trap
        height: the height from the beach surface to the top of the trap
        delta: how far down the y-axis the center of the circle is
        slope: the slope of the beach on which the trap is built
        intercept: using mean sea level as zero, the intercept for the equation of the slope of the beac
    
    returns:
        the Perimter, a 2d array:
            [0]: x values
            [1]: y values
            [2]: z values
    """
    
    theta = np.linspace(0, np.pi, 100)
    #equation for a circle
    x = radius * np.cos(theta)
    y = radius * np.sin(theta) + delta
    # equation for a line
    z = intercept + height - (slope * y)

    return [x,y,z]

def get_harvest_input(fish_in_trap: int) -> int:
    """function retrieves user input and checks the value. This number is to represent the number of fish harvested this tide cycle.
    Args:
        fish_in_trap: the current  number of fish in the trap

    Returns:
        a positive integer <= fish_in_trap
    """

    print(math.floor(fish_in_trap), "fish have been trapped.\n how many do you want to harvest? The rest will be released.")
    harvest_raw = input()
    try:
        harvest_int = int(harvest_raw)
        
        if(harvest_int > fish_in_trap):
            print("Enter a number that is no bigger than the number of the fish in the trap")
            return(get_harvest_input(fish_in_trap))

        if(harvest_int < 0):
            print("Enter a non-zero number")
            return(get_harvest_input(fish_in_trap))

        return(harvest_int)

    except ValueError:
        print("Please enter a positive integer, such as:  0,1,2...");
        return(get_harvest_input(fish_in_trap))

def run_trap_harvesting(prev_values, harvesting: int = 0, radius: int = default_radius, height: float = default_height, slope: float = default_slope, delta: int = default_delta, constant_population:bool = True):
    """Runs the model for one harvesting cycle. Where a harvesting cycle is period of time ending in the next low tide in which the trap is closed with fish inside.
    Args:
        prev_values is an array of arrays with:
            [0]: The total number of harvested fish at hour indexed
            [1]: The total number of fish in the trap at hour at hour indexed
            [2]: the total number of fish outside the trap at hour indexed
            [3]: list of the size of all harvests
        The values in this array are the history of the model. if the model is being run from the start, pass in [].
        
        harvesting: how many fish will be harvested this cycle. This is to be user selected
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        constant_population: if true the population will reset to max_fish after every harvest, else it will decrease by the number of harvested fish

    Returns:
        An 2d array containing:
            [0]: The total number of harvested fish at hour indexed
            [1]: The total number of fish in the trap at hour at hour indexed
            [2]: the total number of fish outside the trap at hour indexed
            [3]: list of the size of all harvests
            [4]: a boolean showing if the model is completed
        This returned array is shows one more cycle of harvesting than the inputed one.
        
    Throws:
        ValueError if harvesting is not a positive integer <= the number of the fish in the trap
    """
    movement_rate = 0.05
    max_fish = 1000
    if(len(prev_values) == 0):
        current_free_fish = max_fish
        current_caught_fish = 0
        total_harvested = [0]
        in_trap = [0]
        out_trap = [max_fish]
        catches = []
    else:
        total_harvested = prev_values[0]
        in_trap = prev_values[1]
        out_trap = prev_values[2]
        catches = prev_values[3]
    
    perimeter_ratio = (np.pi * radius) / (np.pi * 25)
    tide_values = get_tide_values()
    perimeter = get_perimeter(radius, height, slope)
    




def run_trap(radius: int = default_radius, height: float = default_height, slope: float = default_slope, delta: int = default_delta, constant_population: bool = True):
    """Runs the fish trap model for 1 week.
    
    Args:
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        constant_population: if true the population will reset to max_fish after every harvest, else it will decrease by the number of harvested fish

    Returns:
        An 2d array containing:
            [0]: The total number of harvested fish at hour indexed
            [1]: The total number of fish in the trap at hour at hour indexed
            [2]: the total number of fish outside the trap at hour indexed
            [3]: list of the size of all harvests
    """
    movement_rate = 0.05
    max_fish = 1000
    current_free_fish = max_fish
    current_caught_fish = 0
    total_harvested = [0]
    in_trap = [0]
    out_trap = [max_fish]
    catches = []
    perimeter_ratio = (np.pi * radius) / (np.pi * 25)
    tide_values = get_tide_values()
   
    perimeter = get_perimeter(radius, height, slope)
    #iterated through all tide levels recorded and run the model
    for level in tide_values:
        coverage = get_ratio_of_perimeter_covered(level, perimeter, radius)
        free_to_caught = current_free_fish * coverage * movement_rate * perimeter_ratio
        caught_to_free = current_caught_fish * coverage * movement_rate * perimeter_ratio
        current_caught_fish = current_caught_fish - caught_to_free + free_to_caught
        current_free_fish = current_free_fish + caught_to_free - free_to_caught
        
        #if the coverage is >0 then the fish arn't trapped so "nothing" happens
        if(coverage > 0):
            total_harvested.append(total_harvested[-1])
        
        else:
            #if harvesting and a whole fish is in the trap the user gets to decide to harvest or not
            if(harvesting and math.floor(current_caught_fish) != 0):
                selected_harvest = get_harvest_input(current_caught_fish)
            else:
                selected_harvest = math.floor(current_caught_fish)
            
            # regardless of if it was automatically selected or user selected we record the harvest level
            total_harvested.append(total_harvested[-1] + selected_harvest)
            
            if(math.floor(current_caught_fish) != 0):
                catches.append(selected_harvest)

            if(constant_population == True):
                current_free_fish = max_fish
            else:
                current_free_fish = current_free_fish + (current_caught_fish - selected_harvest)
            
            # clear the traps
            current_caught_fish = 0
        
        in_trap.append(current_caught_fish)
        out_trap.append(current_free_fish)

    return [total_harvested, in_trap, out_trap, catches]

def plot_trap(radius: int = default_radius, height: float = default_height, slope = default_slope, delta: int = default_delta, constant_population: bool = True):
    """Generates a plot for the fish trap operating over 1 week

    Args:
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: the slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        constant_population: if true the population will reset to max_fish after every harvest, else it will decrease by the number of harvested fish
    """
    seaborn.set()
    plt.style.use('seaborn-deep')

    values = run_trap(radius, height, slope, delta, constant_population)

    x_values = range(len(values[0]))
    plt.plot(x_values, values[1], label = "fish in trap")
    plt.plot(x_values, values[2], label = "fish outside of trap")
    plt.plot(x_values, values[0], label = "total caught")
    plt.ylabel("number of fish")
    plt.xlabel("time (h)")
    plt.title('fish')
    plt.legend()
    plt.show()

