import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
import os,sys
import math
from typing import List, Tuple
import plotly.express as px

# global variables that act as default values for the trap inputs
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


def print_tide_data(tide_values):
        result_min = np.where(tide_values == min(tide_values))
        result_max = np.where(tide_values == max(tide_values))
        print("The lowest tide reaches", min(tide_values)[0],"meters at",result_min[0][0],"hours")
        print("The highest tide reaches", max(tide_values)[0],"meters at",result_max[0][0],"hours")

def create_tide_plot(timeframe="week", day=1):
    """Displays a plot of hourly tide levels for 1 week in May using readings from comox 
    Args:
    
    option: a string containing the word 'day' or 'week'
    if 'day' is passed a plot with a single day tide measurements will be passed
    if 'week' is passed a plot with a week tide measurements will be passed
    
    This function creates an interactive plot indicating min and max tide values,
    as well as the time when they happened.
    
    Raises: ValueError if options not entered correctly
    """

    tide_df = pd.DataFrame(get_tide_values())
    tide_df = tide_df.rename(columns = {0:'tide_level'})
    tide_df['hour'] = tide_df.index
    tide_df["day_hour"] = tide_df["hour"] % 24
    tide_df["day"] = tide_df['hour'] // 24
    try:
        timeframe = timeframe.lower()
        day = round(day)
    except:
        raise ValueError("kwarg 'timeframe' must be 'day' or 'week'.\n kwarg 'day' must be  between 0-6")


    if(timeframe == "week"):
        fig = px.line(tide_df, x="hour", y="tide_level", line_shape='spline')
        fig.update_traces(text= [f'<b>Day</b>: {x}<br><b>Hour</b>: {y}' for x,y in list(zip(tide_df['day'].values, tide_df['day_hour'].values))],
                        hovertemplate='%{text}<br>%{y:}m above sea-level')
        fig.update_layout(title='Measured Tide Readings for Comox Harbour',
                    xaxis_title = 'Time (Days Since Start)',
                    yaxis_title = 'Tide Level (Meters Above Sea Level)',
                    xaxis = dict(tickvals = tide_df.day.unique() * 24,
                                    ticktext = tide_df.day.unique()))
    
    elif(timeframe == "day" and 0 <= day and 6 >= day):
        tide_df = tide_df[tide_df.day == day]
        fig = px.line(tide_df, x="day_hour", y="tide_level", line_shape='spline')
        fig.update_layout(title='Measured Tide Readings for Comox Harbour',
                    xaxis_title = 'Time (Hours)',
                    yaxis_title = 'Tide Level (Meters Above Sea Level)')
        fig.update_traces(text= [f'<b>Day</b>: {x}<br><b>Hour</b>: {y}' for x,y in list(zip(tide_df['day'].values, tide_df['day_hour'].values))],
                        hovertemplate='%{text}<br>%{y:}m above sea-level')
    
    else:
        raise ValueError("kwarg 'timeframe' must be 'day' or 'week'.\n kwarg 'day' must be  between 0-6")

    fig.show()
    print_tide_data(tide_df[["tide_level"]].to_numpy())

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

def run_trap_harvesting(prev_values = [], selected_harvest: int = 0, radius: int = default_radius, height: float = default_height, slope: float = default_slope, delta: int = default_delta, constant_population:bool = True):
    """Runs the model for one harvesting cycle. Where a harvesting cycle is period of time ending in the next low tide in which the trap is closed with fish inside.
    Args:
        prev_values is an array of arrays with:
            [0]: The total number of harvested fish at hour indexed
            [1]: The total number of fish in the trap at hour at hour indexed
            [2]: the total number of fish outside the trap at hour indexed
            [3]: list of the size of all harvests
        The values in this array are the history of the model. if the model is being run from the start, pass in [].
        
        selected_harvest: how many fish will be harvested this cycle. This is to be user selected
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
    perimeter_ratio = (np.pi * radius) / (np.pi * 25)
    tide_values = get_tide_values()
    perimeter = get_perimeter(radius, height, delta, slope)
#TODO
#check that all the user inputs are within reasonable bounds or throw an error if they are not
    if(len(prev_values) == 0):
        #if the model is just starting
        current_free_fish = max_fish
        current_caught_fish = 0
        total_harvested = [0]
        in_trap = [0]
        out_trap = [max_fish]
        catches = []
    
    else:
        #update the model with the harvest the user selected
        total_harvested = prev_values[0]
        in_trap = prev_values[1]
        out_trap = prev_values[2]
        catches = prev_values[3]
        current_free_fish = out_trap[-1]
        current_caught_fish = in_trap[-1]
    
        try:
            selected_harvest = int(selected_harvest)
        except ValueError:
            raise ValueError("selected_harvest must be a positive integer not larger than the number of fish in the trap")

        if(selected_harvest > current_caught_fish or selected_harvest < 0):
            raise ValueError("selected_harvest must be a positive integer not larger than the number of fish in the trap")

        catches.append(selected_harvest)

        level = tide_values[len(in_trap) - 1]
        coverage = get_ratio_of_perimeter_covered(level, perimeter, radius)
        free_to_caught = current_free_fish * coverage * movement_rate * perimeter_ratio
        caught_to_free = current_caught_fish * coverage * movement_rate * perimeter_ratio
        current_caught_fish = current_caught_fish - caught_to_free + free_to_caught
        current_free_fish = current_free_fish + caught_to_free - free_to_caught

        if(constant_population):
            current_free_fish = max_fish
        else:
            current_free_fish = current_free_fish + (current_caught_fish - selected_harvest)

        total_harvested.append(total_harvested[-1] + selected_harvest)
        #empty the traps and record the step after the selected harvest
        current_caught_fish = 0
        in_trap.append(current_caught_fish)
        out_trap.append(current_free_fish)

    #drop tide values already ran
    tide_values = tide_values[len(in_trap) - 1 : len(tide_values)]

    for level in tide_values:
        coverage = get_ratio_of_perimeter_covered(level, perimeter, radius)
        
        if(math.floor(current_caught_fish) != 0 and coverage == 0):
            return [total_harvested, in_trap, out_trap, catches, False]
        
        free_to_caught = current_free_fish * coverage * movement_rate * perimeter_ratio
        caught_to_free = current_caught_fish * coverage * movement_rate * perimeter_ratio
        current_caught_fish = current_caught_fish - caught_to_free + free_to_caught
        current_free_fish = current_free_fish + caught_to_free - free_to_caught
        
        total_harvested.append(total_harvested[-1])
        in_trap.append(current_caught_fish)
        out_trap.append(current_free_fish)
   
    return [total_harvested, in_trap, out_trap, catches, True]


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
    #TODO:
    # Add a new rate out_variable that is dependent on the volume of water in the trap
    # was looking into: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.dblquad.html
    # to calculate the volume but a rough approximation would probably do.
    max_fish = 1000
    current_free_fish = max_fish
    current_caught_fish = 0
    total_harvested = [0]
    in_trap = [0]
    out_trap = [max_fish]
    catches = []
    perimeter_ratio = (np.pi * radius) / (np.pi * 25)
    tide_values = get_tide_values()
   
    perimeter = get_perimeter(radius, height, delta, slope)
    #iterated through all tide levels recorded and run the model
    for level in tide_values:
        coverage = get_ratio_of_perimeter_covered(level, perimeter, radius)
        free_to_caught = current_free_fish * coverage * movement_rate * perimeter_ratio
        #TODO:
        # the caught_to_free variable should depend on the new calculated variable discussed above
        caught_to_free = current_caught_fish * coverage * movement_rate * perimeter_ratio
        current_caught_fish = current_caught_fish - caught_to_free + free_to_caught
        current_free_fish = current_free_fish + caught_to_free - free_to_caught
        
        #if the coverage is >0 then the fish arn't trapped so "nothing" happens
        if(coverage > 0):
            total_harvested.append(total_harvested[-1])
        
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

def plot_values(values):
    """give the data for the trap, create a plot
    Args:
        data_arr is an array of arrays:
            [0]: The total number of harvested fish at hour indexed
            [1]: The total number of fish in the trap at hour at hour indexed
            [2]: the total number of fish outside the trap at hour indexed
    """
    df = pd.DataFrame(values).transpose()
    df.columns=['Total Harvested', 'In Trap', 'Out of Trap', 'harvest_sizes']
    df = df.drop(['harvest_sizes'], axis=1)
    df['hour'] = df.index
    df['In Area'] = df.apply(lambda x: x['In Trap'] + x['Out of Trap'], axis=1)
    df = df.melt(id_vars=['hour'], value_vars = ['In Trap', 'Out of Trap', 'Total Harvested', 'In Area'])
    df['value'] = df['value'].round()
    df = df.rename(columns={"value": "fish", "variable": "category"})

    fig = px.line(df, x='hour', y='fish', color='category', title="Fish Levels Throughout Harvesting")

    fig.update_traces(hovertemplate=None)

    fig.update_layout(hovermode="x",
                  yaxis_title="Number of Fish",
                 xaxis_title="Time(Hours Since Start)")

    fig.show()

def plot_trap(radius: int = default_radius, height: float = default_height, slope: float = default_slope, delta: int = default_delta, constant_population: bool = True):
    """Generates a plot for the fish trap operating over 1 week

    Args:
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: the slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        constant_population: if true the population will reset to max_fish after every harvest, else it will decrease by the number of harvested fish
    """

    values = run_trap(radius, height, slope, delta, constant_population)
    plot_values(values)
