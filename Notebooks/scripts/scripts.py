import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
import os
import math
from typing import List, Tuple

def create_tide_plot():
    """Displays a plot of hourly tide levels for 1 week in May using readings from comox """
    tide_path = os.path.join('..', 'resources', 'comox_tide.csv')
    tide_df = pd.read_csv(tide_path)
    tide_df = tide_df.drop(columns = ['PDT'])
    tide_values = tide_df.values.flatten()
    
    seaborn.set()
    plt.style.use('seaborn-deep')
    x = range(len(tide_values))
    plt.plot(x, tide_values)
    plt.ylabel("tide level (m above sea level)")
    plt.xlabel("time (h)")
    plt.title('tide levels for one week in Comox Harbour')
    plt.savefig("tide.png")
    plt.show()

def get_ratio_of_perimeter_covered(tide_level: float, perimeter,  radius: int, delta = 5: int) -> float:
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


