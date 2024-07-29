from tkinter import *
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from urllib.parse import quote_plus
from timezonefinder import TimezoneFinder #%pip install timezonefinder
import openmeteo_requests #pip install openmeteo-requests
import requests_cache #pip install requests-cache retry-requests numpy pandas
from retry_requests import retry # pip install retry-requests 
import pytz # pip install pytz

class weather_app(Tk): 
    def __init__(self): #Here we're setting up the user interface of weather_app
        super().__init__()
        self.title("Weather app")
        self.minsize(300, 200)
        self.geometry("400x500+50+50")
        self.setupWindow()

    def setupWindow(self): #Next we set up the widgets
        title = Label(self, text="Customize your weather report",
                      font=('Helvetica', 20), bd=10)
        title.grid(row=0, column=0, columnspan=2, pady=10)

        line = ttk.Separator(self, orient=HORIZONTAL)
        line.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)

        self.label = Label(self, text="Location (city or ZIP code):")
        self.label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry = Entry(self)
        self.entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        order_label = Label(self, text="Choose your variables", bd=10)
        order_label.grid(row=3, column=0, columnspan=2, pady=10)

        checkbox_frame = Frame(self)
        checkbox_frame.grid(row=4, column=0, columnspan=2)

        self.weather_variable_list = ["temperature", "feels like", "rain", "chance of rain", "showers", "snowfall", "wind speed", "wind direction", "sunrise (daily only)", "sunset (daily only)", "UV index (daily only)", "visibility (hourly only)", "humidity (hourly only)", "dewpoint (hourly only)"]
        self.checkbox_state = {}

        for i, weather_var in enumerate(self.weather_variable_list): #iterate over each variable
            var = IntVar() #this object keeps track of the state of the checkbutton
            var.set(0) #this sets the initial value to 0 or unchecked
            Checkbutton(checkbox_frame, text=weather_var, variable=var).grid(row=i//2, column=i % 2, sticky='w') #this is our checkbutton widget
            self.checkbox_state[weather_var] = var #this adds the state of each checkbutton to a dictionary

        scope_label = Label(checkbox_frame, text="Choose your time range", bd=10)
        scope_label.grid(row=(len(self.weather_variable_list)//2) + 2, column=0, columnspan=2, pady=10)

        self.time_mode = IntVar() #holds state of radio button
        self.time_mode.set(0) #keeps track of the state of the checkbutton
        self.ranges = ["hourly report", "daily summary"]

        for i, range in enumerate(self.ranges):
            self.rngs = Radiobutton(checkbox_frame, text=range, variable=self.time_mode, value=i)
            self.rngs.grid(row=(len(self.weather_variable_list)//2) + 3 + i, column=0, sticky='w')

        style = ttk.Style()
        style.configure('TButton', bg='skyblue', fg='white')

        search_button = ttk.Button(self, text="Search", command=self.search_weather)
        search_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.hourly_plot = Label(self)
        self.hourly_plot.grid(row=7, column=0, columnspan=2, pady=5)
        self.daily_plot = Label(self)
        self.daily_plot.grid(row=8, column=0, columnspan=2, pady=5)

    def process_hourly(self, response, hourly_vars): #sets date range (24 hours), populates date range with variables, then returns the data as a dataframe.
        hourly = response.Hourly()
        tz_corr = response.UtcOffsetSeconds()

        hourly_data = {"date": pd.date_range( #create keys in a dictionary
            start=pd.to_datetime(hourly.Time() - tz_corr, unit="s", utc=True), #check for timezone
            end=pd.to_datetime(hourly.TimeEnd() - tz_corr, unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}

        for i in range(0, len(hourly_vars)): #iterates over variables and creates an array 
            ar = hourly.Variables(i).ValuesAsNumpy()
            key = hourly_vars[i]
            hourly_data[key] = ar

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        return hourly_dataframe

    def process_daily(self, response, daily_vars): #sets date range (7 days), populates date range with variables, then returns the data as a dataframe.
        daily = response.Daily()
        tz_str = response.Timezone()

        try:
            timezone = pytz.timezone(tz_str)
        except pytz.UnknownTimeZoneError:
            print(f"Unknown timezone: {tz_str}")
            timezone = pytz.UTC  # Default to UTC or handle as needed

        daily_data = {"date": pd.date_range( #create keys in a dictionary
            start=pd.to_datetime(daily.Time(), unit="s", utc=True).tz_convert(timezone), #check for timezone
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True).tz_convert(timezone),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )}
        for i in range(0, len(daily_vars)): #iterates over variables and creates an array 
            ar = daily.Variables(i).ValuesAsNumpy()
            key = daily_vars[i]
            daily_data[key] = ar

        daily_dataframe = pd.DataFrame(data=daily_data)
        return daily_dataframe

    def get_lat_long(self, address): #sends city or ZIP code user entered to API which either returns the latitude and longitude or serves a None
        encoded_address = quote_plus(address) # URL encode the address
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_address}"  # Construct the Nominatim API URL
        response = requests.get(url, headers={'User-Agent': 'Python Geocoding Example'}) # Send the request to the Nominatim API
        data = response.json()
        if data: # Return the first result (if any)
            return data[0].get('lat'), data[0].get('lon')
        else:
            return None, None

    def search_weather(self): #sends the location, selected weather variables and time range to API and gets back a list that the app then plots
        location = self.entry.get()
        if not location: #catches error
            messagebox.showerror("Error", "Please enter a location.") 
            return

        lat, long = self.get_lat_long(location)
        if lat is None or long is None: #catches error
            messagebox.showerror("Error", "Invalid location. Please enter a valid location.") 
            return

        hourly_vars = []
        daily_vars = []

        for w in self.weather_variable_list: #iterates through all the weather variables that were selected (indicated by 1) and adds them to either an hourly or dailys vars list depending on what the user selected
            if self.checkbox_state[w].get() == 1:
                if self.time_mode.get() == 0:
                    if w in ["sunrise (daily only)", "sunset (daily only)", "UV index (daily only)"]:
                        continue
                    hourly_vars.append(w)
                else:
                    if w in ["visibility (hourly only)", "humidity (hourly only)", "dewpoint (hourly only)"]:
                        continue
                    daily_vars.append(w)

        if not hourly_vars and not daily_vars: #catches error
            messagebox.showerror("Error", "Please select at least one weather variable.")
            return

        #Convert weather_variable_list to strings that Openmeteo uses. Openmeteo has different variables depending on if they're hourly or daily, so we need two different dictionaries.
        hourly_mappings = {
            "temperature": "temperature_2m",
            "feels like": "apparent_temperature",
            "rain": "precipitation",
            "chance of rain": "precipitation_probability",
            "showers": "showers",
            "snowfall": "snowfall",
            "wind speed": "wind_speed_10m",
            "wind direction": "wind_direction_10m",
            "visibility (hourly only)": "visibility",
            "humidity (hourly only)": "relative_humidity_2m",
            "dewpoint (hourly only)": "dewpoint_2m"
        }

        daily_mappings = {
            "temperature": ["temperature_2m_max", "temperature_2m_min"],
            "feels like": "apparent_temperature_max",
            "rain": "precipitation_sum",
            "chance of rain": "precipitation_probability_mean",
            "showers": "showers_sum",
            "snowfall": "snowfall_sum",
            "wind speed": "windspeed_10m_max",
            "wind direction": "winddirection_10m_dominant",
            "sunrise (daily only)": "sunrise",
            "sunset (daily only)": "sunset",
            "UV index (daily only)": "uv_index_max"
        }

        #checks whether the user has selected an hourly report or a daily summary and convert the selected weather variables to the correct API parameters based on the selected time range.
        if self.time_mode.get() == 0:  # hourly report
            selected_vars = [hourly_mappings[w] for w in hourly_vars]
            params = {
                "latitude": lat,
                "longitude": long,
                "hourly": selected_vars,
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": TimezoneFinder().timezone_at(lat=float(lat), lng=float(long)),
                "forecast_days": 1
            }
        else:  # daily summary
            selected_vars = [daily_mappings[w] for w in daily_vars]
            selected_vars = [item for sublist in selected_vars for item in (sublist if isinstance(sublist, list) else [sublist])]
            params = {
                "latitude": lat,
                "longitude": long,
                "daily": selected_vars,
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": TimezoneFinder().timezone_at(lat=float(lat), lng=float(long)),
                "forecast_days": 7
            }

        #TODO figure out why app serves an error when 'daily summary' is selected

        #sets up the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://api.open-meteo.com/v1/forecast"

        try:
            responses = openmeteo.weather_api(url, params=params) #returns list of data objects
            response = responses[0] #gets single response from list
        except Exception as e: #catches error
            messagebox.showerror("Error", f"Failed to retrieve weather data: {e}")
            return

        self.location_info = {
            "Latitude": response.Latitude(),
            "Longitude": response.Longitude(),
            "Elevation": response.Elevation(),
            "Timezone": response.Timezone(),
            "Timezone_diff": response.UtcOffsetSeconds()
        }

        hf = None
        df = None

        #create dataframes
        if len(hourly_vars) > 0:
            hf = self.process_hourly(response, hourly_vars)
        if len(daily_vars) > 0:
            df = self.process_daily(response, daily_vars)
                
        # Create a single figure
        fig, ax = plt.subplots()

        if hf is not None:
            hf.plot(kind='line', x='date', y=hourly_vars, ax=ax)
            plt.show()

        if df is not None:
            ax.clear()  # Clear the current axes
            df.plot(kind='line', x='date', y=daily_vars, ax=ax)
            plt.show()

if __name__ == "__main__":
    app = weather_app()
    app.mainloop()
