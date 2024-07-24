#Import and install the following 
import openmeteo_requests # pip install openmeteo-requests
import requests_cache # pip install requests-cache retry-requests numpy pandas
import pandas as pd # pip install ipympl
import openmeteo_requests # pip install openmeteo-requests
import requests_cache # pip install requests-cache retry-requests numpy pandas
import pandas as pd # pip install ipympl
from retry_requests import retry # pip install retry-requests
import matplotlib.pyplot as plt  # pip install matplotlib
import numpy as np # pip install numpy
import requests # pip install requests
from urllib.parse import quote_plus # pip install urllib3
from timezonefinder import TimezoneFinder # pip install timezonefinder


# these modules don't need to be installed
import sys 
from tkinter import *
import tkinter as tk
from tkinter import ttk  #CH was missing
import tkinter.messagebox as messagebox # needed for error messages
from datetime import datetime 




def select_hourly_variables(hourly_vars, latitude, longitude, timezone): #function to establish variables, scope, location and units of mesaurement and assign them to a single variable, params

	params = {
		"latitude": latitude, # CH was hardcoded
		"longitude": longitude, # CH
		"hourly": hourly_vars, 
		"temperature_unit": "fahrenheit",
		"wind_speed_unit": "mph",
		"timezone": timezone, # CH
		"forecast_days": 7
	}
	
	return params

def select_daily_variables(daily_vars, latitude, longitude, timezone): #function to establish variables, scope, location and units of mesaurement and assign them to a single variable, params

	params = {
		"latitude": latitude, # CH
		"longitude": longitude, # CH
		"daily": daily_vars, 
		"temperature_unit": "fahrenheit",
		"wind_speed_unit": "mph",
		"timezone": timezone, # CH
		"forecast_days": 7
	}
	
	return params

def get_response(params): #sends params to API and gets back a data object (<openmeteo_sdk.WeatherApiResponse.WeatherApiResponse object at 0x14738ce50>)

	# More setup
	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)

	url = "https://api.open-meteo.com/v1/forecast"
	
	responses = openmeteo.weather_api(url, params=params) #returns list of data objects
	response = responses[0] #gets single response from list 

	return response 

def get_location_info(response): #gets whatever variable user selects; results could be shown as output in GUI

	# Process location and get current values.
	info = {}
	info ["Latitude"] = response.Latitude()
	info ["Longitude"] = response.Longitude()
	info ["Elevation"] = response.Elevation()
	info ["Timezone"] = response.Timezone()
	#info ["Timezone_diff"] = response.UtcOffsetSeconds()
	
	return info

# Process hourly data and feed into an array

def process_hourly(response, hourly_vars):
	hourly = response.Hourly() 

	hourly_data = {"date": pd.date_range( #create keys in a dictionary
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True), #check for timezone
		end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}

	for i in range(0, len(hourly_vars)): #creates an array of hourly values for variables (i) 
		ar = hourly.Variables(i).ValuesAsNumpy() 
		key = hourly_vars[i]
		hourly_data[key] = ar

	hourly_dataframe = pd.DataFrame(data = hourly_data)
	return hourly_dataframe

def process_daily(response, daily_vars):
	daily = response.Daily() 

	daily_data = {"date": pd.date_range( #create keys in a dictionary
		start = pd.to_datetime(daily.Time(), unit = "s", utc = True), #check for timezone
		end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = daily.Interval()),
		inclusive = "left"
	)}

	for i in range(0, len(daily_vars)): #creates an array of daily values for variables (i) 
		ar = daily.Variables(i).ValuesAsNumpy() 
		key = daily_vars[i]
		daily_data[key] = ar
	daily_dataframe = pd.DataFrame(data = daily_data)
	return daily_dataframe

#Turn dataframe into a plot
def plot_hourly_data(hourly_dataframe, hourly_var_list):

	p = hourly_dataframe.plot(kind='line',
							x = 'date',
							y = hourly_var_list)
	plt.show()
	
#Turn dataframe into a plot
def plot_daily_data(daily_dataframe, daily_var_list):

	p = daily_dataframe.plot(kind='line',
							x = 'date',
							y = daily_var_list)
	plt.show()

# CH: added this function to get the latitude and longitude from a location address
def get_lat_long(address): # "Marengo, Iowa, USA"
    # URL encode the address
    encoded_address = quote_plus(address)
    # Construct the Nominatim API URL
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_address}"
    # Send the request to the Nominatim API
    response = requests.get(url, headers={'User-Agent': 'Python Geocoding Example'})

    # either the response is not 200 or the response is empty b/c the location was not found
    if response.status_code != 200 or response.json() == []: 
        return None, None

    # Parse the JSON response
    data = response.json()
    # Return the first result (if any)
    if data is not None:
        return data[0].get('lat'), data[0].get('lon')
    else:
        return None, None



#Tkinter for user to input weather variable; implement GUI as a class
class weather_app(tk.Tk): #dervied from Tk class (main class of tkinter module)
    def __init__(self):
        super().__init__() #initiates attributes of parent classdef __init__(self):
        #self.initializeUI()
        self.title("Weather app")
        self.minsize(300, 200)  # width, height)
        self.geometry("400x520+50+50")  # CH made wider and taller b/c of added widgets
        self.setupWindow()

    def setupWindow(self): #Set up the widgets.
        title = Label(self, text="Customize your weather report",
            font=('Helvetica', 20), bd=10)
        title.grid(row=0, column=0, columnspan=2, pady=10)

        line = ttk.Separator(self, orient=HORIZONTAL)
        line.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)

        # CH: I added this entry field to get the location and also another separator
        # also adjusted all the row numbers for the rest of the widgets

        # get location
        self.location_label = Label(self, text="Location:") #Label       
        self.location_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.location_entry = Entry(self) #Entry widget
        self.location_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        line = ttk.Separator(self, orient=HORIZONTAL)
        line.grid(row=3, column=0, columnspan=2, sticky='ew', pady=5)

        order_label = Label(self, text="Choose your variables", bd=10)
        order_label.grid(row=4, column=0, columnspan=2, pady=10)

         # Create a frame to hold the checkbuttons
        checkbox_frame = Frame(self)
        checkbox_frame.grid(row=5, column=0, columnspan=2)

        # CH made this an attribute so I can access it in search_weather
        self.weather_variable_list = ["temperature", "feels like", "rain", "chance of rain", "showers", "snowfall", "wind speed", "wind direction", "sunrise (daily only)", "sunset (daily only)", "UV index (daily only)", "visibility (hourly only)", "humidity (hourly only)", "dewpoint (hourly only)"]
        
        self.var_dict = {}

        # Populate the dictionary with checkbutton widgets and arrage them in a grid
        for  i, weather_var in  enumerate(self.weather_variable_list):

            # Set the text for each checkbutton
            self.var_dict[weather_var] = Checkbutton(checkbox_frame, text=weather_var)

            # Create a new instance of IntVar() for each checkbutton
            self.var_dict[weather_var].var = IntVar()

            # Set the variable parameter of the checkbutton
            self.var_dict[weather_var]['variable'] = self.var_dict[weather_var].var

            # Arrange the checkbutton in the window
            self.var_dict[weather_var].grid(row=i//2, column=i % 2, sticky='w')

        scope_label = Label(checkbox_frame, text="Choose your reporting mode", bd=10)
        scope_label.grid(row=(len(self.weather_variable_list)//2) + 2, column=0, columnspan=2, pady=10)

        # Create integer variable
        self.var = IntVar()
        self.var.set(0)  # Use set() to initialize the variable to hourly
        self.ranges = ["hourly report", "daily summary"]

        for  i, range in  enumerate(self.ranges):
            self.rngs = Radiobutton(checkbox_frame, text=range, variable=self.var, value=i)
            self.rngs.grid(row=(len(self.weather_variable_list)//2) + 5 + i, column=0, sticky='w')

        # Use ttk to add styling to button
        style = ttk.Style()
        style.configure('TButton', bg='skyblue', fg='white')

        # Create button that will call the range to display text and close the program
        search_button = ttk.Button(self, text="Search", command=self.search_weather)
        search_button.grid(row=7, column=0, columnspan=2, pady=10)

    def search_weather(self):
        #use if statement to determine range and create list of selected variables that reflects hourly or daily

        # Get the index of the selected radiobutton
        selected_index = self.var.get()
        # Use the index to get the selected range from self.ranges
        selected_range = self.ranges[selected_index]

        hourly_vars = [] 
        daily_vars = []

        # Get the state of each checkbutton and assemble a list of selected variables
        for weather_var, checkbutton in self.var_dict.items():
            # self.var_dict is a list of checkbutton widgets with the weather variable as the key
            # and the checkbutton widget as the value (e.g. "temperature":  <checkbutton widget> )

            # Check if the checkbox widgets IntVar (stored in checkbutton.var) == 1 (selected)
            if checkbutton.var.get() == 1:
                if selected_range == "hourly report":   
                    if weather_var in ["sunrise (daily only)", "sunset (daily only)", "UV index (daily only)"]:
                        continue # skip those daily only vars
                    hourly_vars.append(weather_var)
                else:  # if "daily" was selected
                    if weather_var in ["visibility (hourly only)", "humidity (hourly only)", "dewpoint (hourly only)"]:
                        continue # skip hourly only vars
                    daily_vars.append(weather_var)
        
        # error out if none of the checkboxes were selected
        if hourly_vars == [] and daily_vars == []:
            messagebox.showerror("Error", "Please select at least one valid weather variable")
            return


        # convert weather_variable_list to strings that Openmeteo uses
        openmeteo_vars = {
            "temperature": "temperature_2m",
            "feels like": "apparent_temperature",
            "rain": "precipitation",
            "chance of rain": "precipitation_probability",
            "showers": "showers",
            "snowfall": "snowfall",
            "wind speed": "wind_speed_10m",
            "wind direction": "wind_direction_10m",
            "sunrise (daily only)": "sunrise",
            "sunset (daily only)": "sunset",
            "UV index (daily only)": "uv_index_max",
            "visibility (hourly only)": "visibility",
            "humidity (hourly only)": "relative_humidity_2m",
            "dewpoint (hourly only)": "dewpoint_2m"
        }

        # convert hourly_vars to strings that Openmeteo uses
        hourly_vars = [openmeteo_vars[w] for w in hourly_vars]

        # convert daily_vars to strings that Openmeteo uses
        daily_vars = [openmeteo_vars[w] for w in daily_vars]

        # CH many vars (e.g. temperature_2m) are not in the list of hourly_vars or daily_vars
        # so we need to convert them to a reasonable equivalent (e.g. temperature)
        if daily_vars != []:
                daily_openmeteo_vars = {
                    "temperature_2m": "temperature_2m_max",
                    "apparent_temperature": "apparent_temperature_max",
                    "precipitation": "rain_sum",
                    "precipitation_probability": "precipitation_probability_max",
                    "showers": "showers_sum",
                    "snowfall": "snowfall_sum",
                    "wind_speed_10m": "wind_speed_10m_max",
                    "wind_direction_10m": "wind_direction_10m_dominant",

                    # these were correct but it's easier to just set them to the same value
                    # than having to detect if they are in the list of daily vars
                    "uv_index_max": "uv_index_max",
                    "sunrise": "sunrise",
                    "sunset": "sunset",
                }   

                # convert the hourly flavor of a var to the daily flavor
                daily_vars = [daily_openmeteo_vars[w] for w in daily_vars]

        # debug
        print("hourly_vars:", hourly_vars, " daily_vars:", daily_vars)

        # Get the location from the entry widget
        location = self.location_entry.get()

        if location == "":
            messagebox.showerror("Error", "Please enter a location")
            return

        # Get the latitude and longitude
        lat, long = get_lat_long(location) # will be strings!

        if lat is None:
            messagebox.showerror("Error", "Location not found")
            return

        tf = TimezoneFinder()
        # Find the timezone
        timezone = tf.timezone_at(lat=float(lat), lng=float(long))

        # debug
        print("lat:", lat, " long:", long, " timezone:", timezone)


        #send list to process_hourly or process_daily

        if selected_range == "hourly report":
            # get lat long via location lookup based on GUI
            p = select_hourly_variables(hourly_vars, lat, long, timezone)
            resp = get_response(p)
            local_info  = get_location_info(resp)
            print("local info", local_info)
            hf = process_hourly(resp, hourly_vars)
            plot_hourly_data(hf, hourly_vars)
        else:
            p = select_daily_variables(daily_vars, lat, long, timezone)
            resp = get_response(p)
            local_info  = get_location_info(resp)
            print("local info", local_info)
            df = process_daily(resp, daily_vars)
            plot_daily_data(df, daily_vars)



if  __name__  ==  "__main__":
    app = weather_app()
    app.mainloop()



