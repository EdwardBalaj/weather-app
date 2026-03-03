#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

CITY = os.environ.get("CITY", "Madrid")

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


def fetch_weather():
    # Step 1: resolve city name to coordinates
    geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
        {"name": CITY, "count": 1, "language": "en", "format": "json"}
    )
    with urllib.request.urlopen(geo_url, timeout=10) as resp:
        geo = json.loads(resp.read())

    if not geo.get("results"):
        raise ValueError(f"City not found: {CITY}")

    result = geo["results"][0]
    lat, lon = result["latitude"], result["longitude"]
    city_name = result["name"]
    country = result.get("country", "")

    # Step 2: fetch current weather
    weather_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        "wind_speed_unit": "kmh",
    })
    with urllib.request.urlopen(weather_url, timeout=10) as resp:
        data = json.loads(resp.read())

    current = data["current"]
    temp_c = current["temperature_2m"]
    temp_f = round(temp_c * 9 / 5 + 32, 1)
    feels_c = current["apparent_temperature"]
    feels_f = round(feels_c * 9 / 5 + 32, 1)

    return {
        "city": city_name,
        "country": country,
        "temp_c": temp_c,
        "temp_f": temp_f,
        "feels_like_c": feels_c,
        "feels_like_f": feels_f,
        "humidity": current["relative_humidity_2m"],
        "wind_kmph": current["wind_speed_10m"],
        "condition": WMO_CODES.get(current["weather_code"], "Unknown"),
    }


class WeatherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/weather":
            try:
                body = json.dumps(fetch_weather()).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), WeatherHandler)
    print(f"Serving on :8080, CITY={CITY}", flush=True)
    server.serve_forever()
