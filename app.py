#!/usr/bin/env python3
import urllib.request
import json
import os
import sys

CITY = os.environ.get("CITY", "London")
URL = f"https://wttr.in/{CITY}?format=j1"

def get_weather():
    try:
        with urllib.request.urlopen(URL, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"Error fetching weather: {e}", file=sys.stderr)
        sys.exit(1)

    current = data["current_condition"][0]
    area = data["nearest_area"][0]
    city_name = area["areaName"][0]["value"]
    country = area["country"][0]["value"]

    print(f"Weather for {city_name}, {country}")
    print(f"  Temp:       {current['temp_C']}°C / {current['temp_F']}°F")
    print(f"  Feels like: {current['FeelsLikeC']}°C / {current['FeelsLikeF']}°F")
    print(f"  Humidity:   {current['humidity']}%")
    print(f"  Wind:       {current['windspeedKmph']} km/h {current['winddir16Point']}")
    print(f"  Condition:  {current['weatherDesc'][0]['value']}")

if __name__ == "__main__":
    get_weather()
