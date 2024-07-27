# jollian_project
HCI 584 project

## Setup ##

### API ###
Weather-App uses Open-Meteo, which is an open source API and doesn’t require a key.

### Packages ###
You’ll need to install the following code packages before running this app:
1. openmeteo-requests
2. Requests-cache 
3. retry-requests 
4. numpy pandas
5. ipympl
6. timezonefinder

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
<br> <img width="636" alt="Screenshot 2024-07-27 at 2 12 36 PM" src="https://github.com/user-attachments/assets/09170b2b-5517-4ebb-9f61-013e1dc20f75"><br>
   
 ### Error prevention ###
Make sure that you don't select a variable that's incompatible with the time range you've selected. Note that some variables are compatible only with hourly or daily.

## Bugs to be aware of ##
- The app serves an error when a user selects **daily summary**
- When you select **Search**, two windows pop up: figure 1 is empty, figure 2 will have your plot
