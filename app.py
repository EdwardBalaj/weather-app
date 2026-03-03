#!/usr/bin/env python3
import urllib.request
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

CITY = os.environ.get("CITY", "Berlin")
URL = f"https://wttr.in/{CITY}?format=j1"


def fetch_weather():
    with urllib.request.urlopen(URL, timeout=10) as resp:
        data = json.loads(resp.read())

    current = data["current_condition"][0]
    area = data["nearest_area"][0]
    return {
        "city": area["areaName"][0]["value"],
        "country": area["country"][0]["value"],
        "temp_c": current["temp_C"],
        "temp_f": current["temp_F"],
        "feels_like_c": current["FeelsLikeC"],
        "feels_like_f": current["FeelsLikeF"],
        "humidity": current["humidity"],
        "wind_kmph": current["windspeedKmph"],
        "wind_direction": current["winddir16Point"],
        "condition": current["weatherDesc"][0]["value"],
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

    def log_message(self, format, *args):
        pass  # suppress access logs


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), WeatherHandler)
    print(f"Serving on :8080, CITY={CITY}", flush=True)
    server.serve_forever()
