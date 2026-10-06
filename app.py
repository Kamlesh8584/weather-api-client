"""A tiny command-line weather app using Open-Meteo's public REST APIs."""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 56: "Light freezing drizzle", 57: "Freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain", 66: "Light freezing rain",
    67: "Freezing rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow",
    77: "Snow grains", 80: "Light rain showers", 81: "Rain showers",
    82: "Heavy rain showers", 85: "Light snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with light hail", 99: "Thunderstorm with heavy hail",
}


def get_json(url, params):
    """Call a JSON REST endpoint and return its decoded response."""
    request = Request(
        f"{url}?{urlencode(params)}",
        headers={"User-Agent": "QuickWeatherPython/1.0", "Accept": "application/json"},
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def find_city(city):
    data = get_json(GEOCODING_URL, {"name": city, "count": 5, "language": "en", "format": "json"})
    matches = data.get("results", [])
    if not matches:
        raise ValueError(f"No matching city found for {city!r}. Try adding a country, e.g. 'Springfield, US'.")
    return matches[0]


def get_weather(place):
    params = {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m",
        "timezone": "auto",
    }
    data = get_json(FORECAST_URL, params)
    current = data["current"]
    units = data.get("current_units", {})
    return {
        "location": ", ".join(filter(None, [place.get("name"), place.get("admin1"), place.get("country")])),
        "local_time": current.get("time"),
        "condition": WEATHER_CODES.get(current.get("weather_code"), "Unknown conditions"),
        "temperature": f"{current.get('temperature_2m')} {units.get('temperature_2m', '°C')}",
        "feels_like": f"{current.get('apparent_temperature')} {units.get('apparent_temperature', '°C')}",
        "humidity": f"{current.get('relative_humidity_2m')} {units.get('relative_humidity_2m', '%')}",
        "wind": f"{current.get('wind_speed_10m')} {units.get('wind_speed_10m', 'km/h')}",
        "precipitation": f"{current.get('precipitation')} {units.get('precipitation', 'mm')}",
    }


def main():
    parser = argparse.ArgumentParser(description="Get current weather for a city (no API key required).")
    parser.add_argument("city", nargs="+", help="City name, optionally followed by country (e.g. Paris France)")
    parser.add_argument("--json", action="store_true", help="Print the result as JSON")
    args = parser.parse_args()
    city = " ".join(args.city)

    try:
        place = find_city(city)
        weather = get_weather(place)
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"Could not reach the weather service: {exc}", file=sys.stderr)
        return 1
    except (ValueError, KeyError) as exc:
        print(f"Weather lookup failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(weather, indent=2, ensure_ascii=False))
    else:
        print(f"\nWeather for {weather['location']}")
        print(f"As of {weather['local_time']} (local time)")
        print(f"\n  {weather['condition']}")
        print(f"  Temperature:   {weather['temperature']}")
        print(f"  Feels like:    {weather['feels_like']}")
        print(f"  Humidity:      {weather['humidity']}")
        print(f"  Wind:          {weather['wind']}")
        print(f"  Precipitation: {weather['precipitation']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
