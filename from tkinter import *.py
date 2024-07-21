from tkinter import *
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from urllib.parse import quote_plus
from timezonefinder import TimezoneFinder # pip install timezonefinder
import openmeteo_requests # pip install openmeteo-requests
import requests_cache # pip install requests-cache 
from retry_requests import retry # pip install retry-requests 

class  weather_app(Tk):

    def __init__(self):
        super().__init__()
        #self.initializeUI()
        self.title("Weather app")
        self.minsize(300, 200)  # width, height
        self.geometry("400x500+50+50")
        self.setupWindow()

    def setupWindow(self): #Set up the widgets.
        title = Label(self, text="Customize your weather report",
            font=('Helvetica', 20), bd=10)
        title.grid(row=0, column=0, columnspan=2, pady=10)

        line = ttk.Separator(self, orient=HORIZONTAL)
        line.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)

        #first widget to get city
        self.label = Label(self, text="Location:") #Label       
        self.label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry = Entry(self) #Entry widget
        self.entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        order_label = Label(self, text="Choose your variables", bd=10)
        order_label.grid(row=3, column=0, columnspan=2, pady=10)

         # Create a frame to hold the checkbuttons
        checkbox_frame = Frame(self)
        checkbox_frame.grid(row=4, column=0, columnspan=2)

        self.weather_variable_list = ["temperature", "feels like", "rain", "chance of rain", "showers", "snowfall", "wind speed", "wind direction", "sunrise (daily only)", "sunset (daily only)", "UV index (daily only)", "visibility (hourly only)", "humidity (hourly only)", "dewpoint (hourly only)"]
        self.checkbox_state = {}

        # Populate the dictionary with checkbutton widgets and arrange them in a grid
        for  i, weather_var in  enumerate(self.weather_variable_list):

            #Create an instance of IntVar()
            var = IntVar()
            var.set(0)

            #Set text for each checkbutton and arrange in window
            Checkbutton(checkbox_frame, text=weather_var, variable=var).grid(row=i//2, column=i % 2, sticky='w')

            #Store IntVar instances that represent the state of the checkbutton
            self.checkbox_state[weather_var] = var

        scope_label = Label(checkbox_frame, text="Choose your time range", bd=10)
        scope_label.grid(row=(len(self.weather_variable_list)//2) + 2, column=0, columnspan=2, pady=10)

        # Create integer variable
        self.time_mode = IntVar() #memory holder of which of 2 things is currently
        self.time_mode.set(0)  # Use set() initialize the variable
        self.ranges = ["hourly report", "daily summary"]

        for  i, range in  enumerate(self.ranges):
            self.rngs = Radiobutton(checkbox_frame, text=range, variable=self.time_mode, value=i)
            self.rngs.grid(row=(len(self.weather_variable_list)//2) + 3 + i, column=0, sticky='w')

        # Use ttk to add styling to button
        style = ttk.Style()
        style.configure('TButton', bg='skyblue', fg='white')

        # Create button that will call the range to display text and close the program
        search_button = ttk.Button(self, text="Search", command=self.search_weather)
        search_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Add a labels for displaying the plot
        self.hourly_plot = Label(self)
        self.hourly_plot.grid(row=7, column=0, columnspan=2, pady=5)
        self.daily_plot = Label(self)
        self.daily_plot.grid(row=8, column=0, columnspan=2, pady=5)

        # Process hourly data and feed into an array

    def process_hourly(self, response, hourly_vars):
        hourly = response.Hourly() 
        tz_corr = response.UtcOffsetSeconds()

        hourly_data = {"date": pd.date_range( #create keys in a dictionary
            start = pd.to_datetime(hourly.Time() - tz_corr, unit = "s", utc = True), #check for timezone
            end = pd.to_datetime(hourly.TimeEnd()- tz_corr, unit = "s", utc = True),
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


    def get_lat_long(self, address): # "Marengo, Iowa, USA"
        # URL encode the address
        encoded_address = quote_plus(address)
        # Construct the Nominatim API URL
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_address}"
        # Send the request to the Nominatim API
        response = requests.get(url, headers={'User-Agent': 'Python Geocoding Example'})
        # Parse the JSON response
        data = response.json()
        # Return the first result (if any)
        if data is not None:
            return data[0].get('lat'), data[0].get('lon')
        else:
            return None, None
        

    def search_weather(self):
        hourly_vars = [] 
        daily_vars = []

        #bail out if we don't have a location or not weather variables are selected

        for w in self.weather_variable_list:

            if self.checkbox_state[w].get() == 1: #get on or off state from weather variable
                if self.time.mode.get() == 0: #if "hourly" was selected (indicated by 0)
                            if w in ["sunrise (daily only)", "sunset(daily only)", "UV index (daily only)"]:
                                 continue #skip those variables
                            hourly_vars.append(w) #place all selected variables in the hourly_vars list
                else: #if "daily" was selected (indicated by 1)
                        if w in ["visibility (houly only)", "humidity (hourly only)", "dewpoint (hourly only)"]:
                             continue
                        daily_vars.append(w)

        #convert weather_variable_list to strings that Openmeteo uses
                        openmeteo_vars = {"temperature":"temperature_2m", 
                                          "feels like": "apparent_temperature", 
                                          "rain": "precipitation", 
                                          "chance of rain": "precipitation probability", 
                                          "showers": "showers", 
                                          "snowfall": "snowfall", 
                                          "wind speed": "wind_speed_10m", 
                                          "wind direction": "wind_direction_10m", 
                                          "sunrise (daily only)": "sunrise", 
                                          "sunset (daily only)": "sunset", 
                                          "UV index (daily only)":"ux_index", 
                                          "visibility (hourly only)": "visibility", 
                                          "humidity (hourly only)": "relative_humidity_2m", 
                                          "dewpoint (hourly only)": "dewpoint_2m"
                                          }
        #convert hourly_vars to strings that Openmeteo uses
        hourly_vars = [openmeteo_vars[w] for w in hourly_vars]
        
        #convert daily_vars to strings that Openmeteo uses
        #daily_vars = [openmeteo_vars[w] for w in daily_vars]

        #get the location from the entry widget
        location = self.entry.get()
        #get the latitude and longitude 
        lat, long= self.entry.get(location)

        tf = TimezoneFinder()
        #find the timezone
        timezone = tf.timezone_at(lat=float(lat), lng=float(long))

        #assemble the parameters for the OpenMeteo API
        params = {
            "latitude": lat,
            "longitude": long,
            "hourly": hourly_vars, 
            #"daily": daily_vars, 
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": timezone
            "forecast_days": 7
	    }

        #Setup the Open-Meteo API client with cache and retry on error

        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        url = "https://api.open-meteo.com/v1/forecast"
        
        try:
            responses = openmeteo.weather_api(url, params=params) #returns list of data objects
            response = responses[0] #gets single response from list 
        except Exception as e:
             print(f"Error: {e}")
             return
        
        #Store location data
        self.location_info = {}
        self.location_info ["Latitude"] = response.Latitude()
        self.location_info ["Longitude"] = response.Longitude()
        self.location_info ["Elevation"] = response.Elevation()
        self.location_info ["Timezone"] = response.Timezone()
        self.location_info ["Timezone_diff"] = response.UtcOffsetSeconds()

        self.hf = None
        self.df = None
        
        #create dataframe
        if len(hourly_vars) > 0:
             hf = self.process_hourly(response, hourly_vars)
        #if len(daily_vars) > 0:
             #hf = self.process_daily(response, daily_vars)
        
        #show plots of data
        if hf is not None:
            p = hf.plot(kind='line',
							x = 'date',
							y = hourly_vars)
            plt.show()

      


if  __name__  ==  "__main__":
    app = weather_app()
    app.mainloop()
