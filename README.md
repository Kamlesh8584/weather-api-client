# Weather Now — Python REST API Web App

A compact Flask website for looking up current weather by city. It calls Open-Meteo's geocoding API to find city coordinates, then its forecast API to retrieve current conditions. No API key is needed.

## Run locally on Windows

```bat
py -m pip install -r requirements.txt
py web_app.py
```

Open **http://127.0.0.1:5000** in your browser. Keep the terminal open while the app is running; press `Ctrl+C` to stop it. Live weather lookups need an internet connection.

## Files

- `web_app.py` — Flask website, form handling, and inline page styling
- `app.py` — API requests, geocoding, weather formatting, and optional command-line client
- `requirements.txt` — Flask dependency
