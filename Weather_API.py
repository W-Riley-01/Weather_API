import requests
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import pytz
import math
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

def get_wind_direction(degrees):
    """Convert wind direction in degrees to compass direction."""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = math.floor((degrees + 11.25) / 22.5) % 16
    return directions[index]


def get_weather():
    """Fetch weather data for the entered city, including all requested details."""
    city = city_entry.get()
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial",  # Default to Fahrenheit for US
    }


    # weather data
    response = requests.get(url, params=params)

    # Check success
    if response.status_code == 200:
        data = response.json()

        # weather data
        city_name = data["city"]["name"]
        timezone_offset = data["city"]["timezone"]

        list_of_forecasts = data["list"]
        current_weather = data["list"][0]

        # sunrise and sunset
        sunrise = datetime.utcfromtimestamp(data["city"]["sunrise"] + timezone_offset)
        sunset = datetime.utcfromtimestamp(data["city"]["sunset"] + timezone_offset)

        # 12-hour AM/PM
        sunrise_local = (sunrise + timedelta(seconds=timezone_offset)).strftime('%I:%M:%S %p')
        sunset_local = (sunset + timedelta(seconds=timezone_offset)).strftime('%I:%M:%S %p')

        # current weather data
        temp = current_weather["main"]["temp"]
        feels_like = current_weather["main"]["feels_like"]
        weather_desc = current_weather["weather"][0]["description"]
        humidity = current_weather["main"]["humidity"]
        cloudiness = current_weather["clouds"]["all"]
        visibility = current_weather["visibility"] / 1609  # Convert to miles
        wind_speed = current_weather["wind"]["speed"]
        wind_gust = current_weather["wind"].get("gust", "N/A")
        wind_degrees = current_weather["wind"]["deg"]
        wind_direction = get_wind_direction(wind_degrees)

        # Prepare data
        forecast_text = f"Weather details for {city_name}:\n"

        # weather data
        forecast_text += f"Temperature: {temp}°F\n"
        forecast_text += f"Feels Like: {feels_like}°F\n"
        forecast_text += f"Weather: {weather_desc}\n"
        forecast_text += f"Humidity: {humidity}%\n"
        forecast_text += f"Cloudiness: {cloudiness}%\n"
        forecast_text += f"Visibility: {visibility:.2f} miles\n"
        forecast_text += f"Wind Speed: {wind_speed} mph\n"
        forecast_text += f"Wind Gust: {wind_gust} mph\n"
        forecast_text += f"Wind Direction: {wind_direction} ({wind_degrees}°)\n"

        # sunrise and sunset
        forecast_text += f"\nSunrise: {sunrise_local}\n"
        forecast_text += f"Sunset: {sunset_local}\n"

        # precipitation probability
        precipitation_probability = "Low"
        for i in range(8):  # Check the next 8 hours
            forecast = list_of_forecasts[i]
            pop = forecast.get("pop", 0)  # (0-1 scale)
            if pop > 0.7:
                precipitation_probability = "High"
            elif pop > 0.4:
                precipitation_probability = "Medium"

        # Convert mm to inches
        forecast_text += f"\nPrecipitation probability for the next 8 hours: {precipitation_probability}\n"
        for i in range(8):
            forecast = list_of_forecasts[i]
            dt = datetime.utcfromtimestamp(forecast["dt"]).strftime('%H:%M')
            precipitation_in_inches = 0  # Default to 0 inches

            if "rain" in forecast:
                precipitation = forecast["rain"].get("3h", 0)  # Precipitation in mm for the past 3 hours
                precipitation_in_inches = round(precipitation / 25.4, 2)
            elif "snow" in forecast:
                precipitation = forecast["snow"].get("3h", 0)  # Snowfall in mm for the past 3 hours
                precipitation_in_inches = round(precipitation / 25.4, 2)

            # hour and precipitation (in inches)
            forecast_text += f"Hour {dt}: {precipitation_in_inches} inches\n"

        # weather warnings or alerts
        alerts = data.get("alerts", [])
        if alerts:
            forecast_text += "\nWeather Alerts:\n"
            for alert in alerts:
                forecast_text += f"Alert: {alert['event']} - {alert['description']}\n"
        else:
            forecast_text += "\nNo weather alerts at this time.\n"

        # weather information in the GUI
        result_label.config(text=forecast_text)
    else:
        # Show an error message
        messagebox.showerror("Error", "City not found or unable to retrieve weather data.")


# Tkinter window
root = tk.Tk()
root.title("Meteo Tempus")
root.geometry("400x700")
root.configure(bg="#ddeeff")

# labels, entry, and buttons
title_label = tk.Label(root, text="Meteo Tempus", font=("Constantia", 16, "bold"), bg="#ddeeff")
title_label.pack(pady=10)

city_label = tk.Label(root, text="Enter City Name:", font=("Constantia", 12), bg="#ddeeff")
city_label.pack()

city_entry = tk.Entry(root, font=("Constantia", 12), width=20)
city_entry.pack(pady=5)

# Bind the Enter key
city_entry.bind("<Return>", lambda event: get_weather())

fetch_button = tk.Button(root, text="Get Weather", font=("Constantia", 12), command=get_weather)
fetch_button.pack(pady=10)

result_label = tk.Label(root, font=("Constantia", 12), bg="#ddeeff", justify="left")
result_label.pack(pady=10)

# main loop
root.mainloop()
