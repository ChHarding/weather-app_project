# Weather app project
HCI 584 project

## Setup ##

### API ###
Weather-App uses the following open source APIs, neither of which require a key:
- [Open-Meteo](https://open-meteo.com/)
- [Nominatim](https://nominatim.org/release-docs/latest/)

### Packages ###
You’ll need to install the following code packages before running this app:
- from tkinter import ttk, messagebox
- import pandas as pd  # pip install pandas
- import matplotlib.pyplot as plt  # pip install matplotlib
- import numpy as np  # pip install numpy
- import requests  # pip install requests
- from urllib.parse import quote_plus
- from timezonefinder import TimezoneFinder  # pip install timezonefinder
- import openmeteo_requests  # pip install openmeteo-requests
- import requests_cache  # pip install requests-cache
- from retry_requests import retry  # pip install retry-requests

## Walkthrough ##

### Instructions ###
1. Go to run-app.py
2. Press **Run Python file** icon to the upper right and the weather app will appear
<br><img width="399" alt="Screenshot 2024-07-27 at 1 57 33 PM" src="https://github.com/user-attachments/assets/bbb50f76-3ead-4a48-8d4d-25932f303b0b"> <br>
3. Enter the name of your city or ZIP code
4. Select the weather variable(s) you'd like to get the forecast on
5. Choose whether you'd like an hourly report or daily summary
<br><img width="399" alt="Screenshot 2024-07-27 at 2 12 23 PM" src="https://github.com/user-attachments/assets/8bfde770-5e13-4dd8-889c-478eca93ffc5"><br>
6. Select **Search**
<br><img width="638" alt="Screenshot 2024-07-29 at 4 03 06 PM" src="https://github.com/user-attachments/assets/2ec41ded-33e1-4acf-9a30-7dbccbb9edfc">
<br>
   
 ### Error prevention ###
Make sure that you don't select a variable that's incompatible with the time range you've selected. Note that some variables are compatible only with hourly or daily.

## Bugs to be aware of ##
- The app serves an error when a user selects **daily summary**
- When you select **Search**, two windows pop up: figure 1 is empty, figure 2 will have your plot
