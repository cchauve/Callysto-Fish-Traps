from __future__ import print_function
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
import os,sys
import math
from typing import List, Tuple
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import plotly.graph_objs as go
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets


# global variables that act as default values for the trap inputs
default_slope = 0.17
default_inter = 6
default_radius = 25
default_height = 2
default_delta = 5

def get_tide_values():
    """Grabs the tide values measured for one week in comox
    Returns:
        a listcontaining measured tide values for comox"""

    tide_path = os.path.join('resources', 'comox_tide.csv')
    tide_df = pd.read_csv(tide_path)
    tide_df = tide_df.drop(columns = ['PDT'])
    return tide_df.values.flatten()


def print_tide_data(tide_values):
        result_min = np.where(tide_values == min(tide_values))
        result_max = np.where(tide_values == max(tide_values))
        print("The lowest tide reaches", min(tide_values)[0],"meters on day",result_min[0][0]//24,"at",result_min[0][0]%24,"hours")
        print("The highest tide reaches",max(tide_values)[0],"meters on day",result_min[0][0]//24,"at",result_max[0][0]%24,"hours")

def create_tide_plot(timeframe="week", day=1):
    """Displays a plot of hourly tide levels for 1 week in May using readings from comox
    Args:
    
    timeframe: a string containing the word 'day' or 'week'
    if 'day' is passed a plot with a single day tide measurements will be passed
    if 'week' is passed a plot with a week tide measurements will be passed

    day: an int between 0 and 6 to select what single day will be displayed if timeframe = 'day'
    
    display: boolean, if false will return the plotly fig object. If True will display the plot and print high, low tide

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

    return fig

def get_ratio_of_perimeter_covered(tide_level, perimeter,  radius=  25, delta= 5):
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

def get_perimeter(radius= default_radius, height= default_height, delta= default_delta, slope= default_slope, intercept= default_inter):
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

def run_trap_harvesting(prev_values = [], selected_harvest= 0, radius= default_radius, height= default_height, slope= default_slope, delta= default_delta, constant_population= True):
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

    movement_rate = 0.025
    max_fish = 1000
    perimeter_ratio = (np.pi * radius) / (np.pi * 25)
    tide_values = get_tide_values()
    perimeter = get_perimeter(radius, height, delta, slope)
    height_adjustment =1 /  min(1, height / 4)
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
        caught_to_free = current_caught_fish * coverage * movement_rate * perimeter_ratio * height_adjustment
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


def run_trap(radius= default_radius, height= default_height, slope= default_slope, delta= default_delta, constant_population= True):
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
    movement_rate = 0.025
    max_fish = 1000
    current_free_fish = max_fish
    current_caught_fish = 0
    total_harvested = [0]
    in_trap = [0]
    out_trap = [max_fish]
    catches = []
    perimeter_ratio = (np.pi * radius) / (np.pi * 25)
    height_adjustment = 1 / min(1, height / 4)
    tide_values = get_tide_values()
   
    perimeter = get_perimeter(radius, height, delta, slope)
    #iterated through all tide levels recorded and run the model
    for level in tide_values:
        coverage = get_ratio_of_perimeter_covered(level, perimeter, radius)
        free_to_caught = current_free_fish * coverage * movement_rate * perimeter_ratio
        caught_to_free = current_caught_fish * coverage * movement_rate * perimeter_ratio * height_adjustment
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


def generate_df_from_simulation(fish_simulation):
    
    """give the data for the trap, create a plot
    Args:
        fish_simulation is a dictionary with three keys for fish which are either harvested, in the trap 
        and out of the trap, whose values are arrays from our simulation
        
    fish_simulation = {"Total harvested fish":current_results[0],
    "Total fish in the trap":current_results[1],
    "Total fish outside the trap":current_results[2]}
    
    Usage generate_df_from_simulation(fish_simulation)
    """
    df = pd.DataFrame(fish_simulation)
    
    df.columns=['Total Harvested', 'In Trap', 'Out of Trap']
    df['hour'] = df.index
    df['In Area'] = df.apply(lambda x: x['In Trap'] + x['Out of Trap'], axis=1)

    df['day'] = df['hour']//24
    df['day_hour'] = df['hour']%24
    df['In Trap'] = df['In Trap'].round()
    return df

def plot_values(fish_simulation):
    
    """give the data for the trap, create a plot
    Args:
        fish_simulation is a dictionary with three keys for fish which are either harvested, in the trap 
        and out of the trap, whose values are arrays from our simulation
        
    fish_simulation = {"Total harvested fish":current_results[0],
    "Total fish in the trap":current_results[1],
    "Total fish outside the trap":current_results[2]}
    
    Usage plot_values(fish_simulation)
    """
    
    df = generate_df_from_simulation(fish_simulation)
    # Manipulate DF a bit more
    df = df.melt(id_vars=['hour'], value_vars = ['In Trap', 'Out of Trap', 'Total Harvested', 'In Area'])
    df['value'] = df['value'].round()
    df = df.rename(columns={"value": "fish", "variable": "category"})

    fig = px.line(df, x='hour', y='fish', color='category', title="Fish Levels Throughout Harvesting")

    fig.update_traces(hovertemplate=None)

    fig.update_layout(hovermode="x",
                  yaxis_title="Number of Fish",
                 xaxis_title="Time(Days Since Start)",
                 xaxis = dict(tickvals = (df.hour // 24).unique() * 24,
                              ticktext = (df.hour // 24).unique()))

    return fig
    
def plot_caught_fish(fish_simulation):
    """Creates a plotly object displaying the fish in the trap
    Args:
        fish_simulation: a dictionary object showing the fish data to be plotted
    Returns:
        fig: a plotly figure object. Use 'fig.show()' to display plotly plot
    """
    df = generate_df_from_simulation(fish_simulation)
    
    fig = px.line(df, x="hour", y="In Trap", line_shape='spline')

    fig.update_traces(text= [f'<b>Day</b>: {x}<br><b>Hour</b>: {y}' for x,y in list(zip(df['day'].values, df['day_hour'].values))],
                            hovertemplate='%{text}<br>%{y:} fish caught')
    fig.update_layout(title='Number of Fish Trapped using circular trap model at Comox Harbour',
                        xaxis_title = 'Time (Days Since Start)',
                        yaxis_title = 'Number of trapped fish',
                        xaxis = dict(tickvals = df.day.unique() * 24,
                                        ticktext = df.day.unique()))
    
    return fig

def plot_trap(radius= default_radius, height= default_height, slope= default_slope, delta= default_delta, constant_population= True):
    """Generates a plot for the fish trap operating over 1 week

    Args:
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: the slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        constant_population: if true the population will reset to max_fish after every harvest, else it will decrease by the number of harvested fish
    """

    values = run_trap(radius, height, slope, delta, constant_population)
    
    ## Build data structure
    fish_simulation = {"Total harvested fish":values[0],
                        "Total fish in the trap":values[1],
                        "Total fish outside the trap":values[2]}
    
    return plot_values(fish_simulation)
    
def plot_interactive_map(latitude, longitude, tag="Comox Valley Harbour"):
    """Creates and displays interactive plot of the area surrounnding our trap location.
        Args:
            latitude: the latitude of the center of the map
            longitude: the longtitude of the center of the map
            tag: the label given to the icon at the center of the map
    """
    # Initial coordinates
    SC_COORDINATES = [latitude, longitude]

    # Create a map using our initial coordinates
    map_osm=folium.Map(location=SC_COORDINATES, zoom_start=10, tiles='stamenterrain')

    marker_cluster = MarkerCluster().add_to(map_osm)
    folium.Marker(location = [SC_COORDINATES[0],SC_COORDINATES[1]],
                      # Add tree name
                      popup=folium.Popup(tag,sticky=True),
                        tooltip='Click here to hide/reveal name',
                      #Make color/style changes here
                      icon=folium.Icon(color='red', icon='anchor', prefix='fa'),
                      # Make sure our trees cluster nicely!
                      clustered_marker = True).add_to(marker_cluster)

    # Show the map
    display(map_osm)

def create_tide_plot_grade6(radius= default_radius, height= default_height, delta= default_delta,
                            slope= default_slope, intercept= default_inter, filename = None,
                            timeframe= 'day', day= 3):
    """Create a plot of the tide for a week superimposed with a horizontal line representing the low point of a trap.
    
    Args:
        radius: the radius of the semi-circular trap created
        height: the height of the trap
        slope: the slope of the beach
        delta: how far down the y axis the "center" of the semi-circle is from the origin
        intercept: the intercept for the eqation of the slope of the beach (y=mx+b)
        filename: if a string is entered will save the plot with the filename specified
        timeframe: if 'week' will plot for a week, if 'day' will plot for day specified
        day: an int between 0 and 6 which speficies the day to be ploted

    Returns:
        a plotly fig object.
    """

    fig = create_tide_plot(timeframe, day)

    low_point = min(get_perimeter(radius, height, delta, slope, intercept)[2])

    fig['data'][0]['showlegend']=True
    fig['data'][0]['name']='Tide Level'

    # add line to show low point of the trap
    x = fig['data'][0]['x']
    y = np.full(len(x), low_point)
    fig.add_scatter(x= x, y= y, name= "low point of the trap", hovertemplate=' %{y:.3f}m')

    # add text at intersection points
    fig.add_trace(go.Scatter(
        x=[8.2, 19.6],
        y=[low_point, low_point],
        mode="markers+text",
        name="Fish become trapped",
        text=["Trap Closed", "Trap Closed"],
        textposition="top right",
        hovertemplate = 'The water level is now below the trap.<br> This means fish can now be harvested.'
    ))

    fig.add_trace(go.Scatter(
        x=[13],
        y=[low_point],
        mode="markers+text",
        name="No fish are trapped",
        text=["Trap Open"],
        textposition="top right",
        hovertemplate = 'The water level is now above the trap.<br> This means fish can swim in and out of it.'
    ))

    if(isinstance(filename, str)):
        fig.write_image(filename + ".jpeg")
    elif(filename is not None):
        raise(TypeError("filename must be a string"))

    return(fig)

from plotly.subplots import make_subplots

def run(radius=25, height=2, location=5, slope=0.17):
    
    var = create_tide_plot_grade6(radius, height, location, slope, timeframe= 'week')
    var2 = plot_trap(radius, height, slope, location, False)
    
    fish_simulation = run_trap(radius= default_radius, 
         height= height, 
         slope= slope, 
         delta= default_delta, 
         constant_population= False)

    fish_simulation = {"Total harvested fish":fish_simulation[0],
        "Total fish in the trap":fish_simulation[1],
        "Total fish outside the trap":fish_simulation[2]}
    
    df = generate_df_from_simulation(fish_simulation)
    
    
    total = var2['data'][2]['y'][-1]
    labels = ['Harvested Fish', 'Surviving Fish in Area']
    values = [int(total), 1000 - int(total)]

    
    fig = make_subplots(rows=1, cols=2,specs=[[{"type": "scatter"}, {"type": "pie"}]])

    fig.add_trace(
        go.Pie(labels=labels, values=values),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(x=df["hour"], y=df["In Trap"],name='Fish in Trap'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df["hour"], y=df["Total Harvested"],name='Total harvested'),
        row=1, col=1
    )
    
#     fig.add_trace(
#         go.Scatter(x=df["hour"], y=df["Out of Trap"],name='Fish Out of Trap',fillcolor='blue'),
#         row=1, col=1
#     )

    fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")
    fig.show()
    
    

#     #lines below disable the annotations included in fig
#     fig['data'][2]['y'] = None
#     fig['data'][2]['x'] = None
#     fig['data'][3]['y'] = None
#     fig['data'][3]['x'] = None
#     fig.show()
    
    
#     fig3 = go.Figure(data=[go.Pie(labels=labels, values=values)])
#     fig3.update_layout(title_text="Results of Harvesting")
#     fig3.show()


    
    
        
    
