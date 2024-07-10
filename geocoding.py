import requests
from urllib.parse import quote_plus

def get_lat_long(address): # "Marengo, Iowa, USA"
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

# Example usage
address = "Marengo, Iowa, USA"
lat, lon = get_lat_long(address)

# Print the result
print(f"Coords result for '{address}': {lat}, {lon}")
