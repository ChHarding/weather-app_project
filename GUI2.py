from tkinter import *
from tkinter import ttk
import requests
from urllib.parse import quote_plus

class  weather_app(Tk):

    def __init__(self):
        super().__init__()
        #self.initializeUI()
        self.title("Weather app")
        self.minsize(300, 200)  # width, height
        self.geometry("350x500+50+50")
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

        scope_label = Label(checkbox_frame, text="Choose your time range", bd=10)
        scope_label.grid(row=(len(self.weather_variable_list)//2) + 2, column=0, columnspan=2, pady=10)

        # Create integer variable
        self.mode = IntVar() #memory holder of which of 2 things is currently
        self.mode.set(0)  # Use set() initialize the variable
        self.ranges = ["hourly report", "daily summary"]

        for  i, range in  enumerate(self.ranges):
            self.rngs = Radiobutton(checkbox_frame, text=range, variable=self.mode, value=i)
            self.rngs.grid(row=(len(self.weather_variable_list)//2) + 3 + i, column=0, sticky='w')

        # Use ttk to add styling to button
        style = ttk.Style()
        style.configure('TButton', bg='skyblue', fg='white')

        # Create button that will call the range to display text and close the program
        search_button = ttk.Button(self, text="Search", command=self.search_weather)
        search_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Add a label for displaying the plot
        self.image_label = Label(self)
        self.image_label.grid(row=7, column=0, columnspan=2, pady=5)


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

        for  w in  self.weather_variable_list:

            if self.var_dict[w]['variable'] == 1: 
                if self.mode == 0: #if "hourly" was selected (indicated by 0), place all selected variables in the hourly_vars list and vice versa
                        hourly_vars.append(w)
                else:
                        daily_vars.append(w)

        #send list to process_hourly or process_daily
        #Im not sure how to tell code to choose the populated list
                

      


if  __name__  ==  "__main__":
    app = weather_app()
    app.mainloop()
