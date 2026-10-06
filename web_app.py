from urllib.error import HTTPError, URLError

from flask import Flask, render_template_string, request

from app import find_city, get_weather

web = Flask(__name__)

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Weather Now</title>
<style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 50% 0%,#e2f0e8,transparent 48%),#f5f8f5;color:#18352d;font:16px 'Segoe UI',sans-serif}.page{max-width:760px;margin:auto;padding:34px 28px}.top{display:flex;align-items:center;gap:10px;font-size:12px;font-weight:700;letter-spacing:.14em;color:#31584a}.mark,.sun{display:grid;place-items:center;border-radius:12px;background:#e3f1e8;color:#14815e}.mark{width:36px;height:36px;font-size:21px}.live{margin-left:auto;padding:6px 10px;border:1px solid #d9e5dc;border-radius:30px;font-size:10px}.hero{text-align:center;padding:74px 0 40px}.eyebrow{font-size:11px;font-weight:700;letter-spacing:.15em;color:#16815e}.hero h1{font-size:clamp(38px,7vw,58px);line-height:1.08;letter-spacing:-.05em;margin:17px 0 12px}.intro{color:#72827a;margin-bottom:27px}.search{display:flex;gap:9px;max-width:560px;margin:auto;padding:7px;background:white;border:1px solid #e1e9e3;border-radius:15px;box-shadow:0 12px 35px #284b3610}.search input{flex:1;min-width:0;border:0;outline:0;padding:12px 14px;font:inherit}.search button{border:0;border-radius:10px;padding:0 17px;background:#147b58;color:white;font-weight:600;cursor:pointer}.error{max-width:560px;margin:14px auto 0;padding:12px 15px;border-radius:10px;background:#fff0ec;color:#a33e2b;text-align:left}.result{max-width:560px;margin:auto;background:#fff;border:1px solid #e0e9e2;border-radius:22px;padding:27px 30px;box-shadow:0 18px 45px #284b360a}.head{display:flex;justify-content:space-between;align-items:center}.result h2{font-size:22px;margin:6px 0}.sun{width:48px;height:48px;background:#fff5dc;color:#efa92d;font-size:28px}.condition{color:#63766c;margin:22px 0 0}.temperature{font-size:76px;line-height:1.1;letter-spacing:-.08em}.temperature small{font-size:27px;vertical-align:top;margin-left:5px;letter-spacing:0}.asof,footer{font-size:13px;color:#829087}.asof{margin:4px 0 22px}.details{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid #e7eee8;padding-top:17px;gap:12px}.details div{display:flex;flex-direction:column;gap:6px}.details span{font-size:11px;color:#87958d}.details strong{font-size:14px}footer{text-align:center;margin:39px 0 0}footer a{color:#16815e}@media(max-width:520px){.page{padding:22px 18px}.hero{padding:58px 0 32px}.search{flex-direction:column}.search button{padding:13px}.result{padding:23px 20px}.details{gap:8px}}
</style></head><body><main class="page">
<header class="top"><span class="mark">☀</span><span>WEATHER NOW</span><span class="live">LIVE API</span></header>
<section class="hero"><p class="eyebrow">A LITTLE FORECAST, WHEREVER YOU ARE</p><h1>How’s the weather<br>out there?</h1><p class="intro">Search a city to see current conditions.</p>
<form method="post" class="search"><input name="city" value="{{ city }}" placeholder="Try Ahmedabad or Tokyo" aria-label="City name" required><button>Get weather →</button></form>
{% if error %}<div class="error" role="alert">{{ error }}</div>{% endif %}</section>
{% if weather %}<section class="result" aria-live="polite"><div class="head"><div><p class="eyebrow">CURRENT CONDITIONS</p><h2>{{ weather.location }}</h2></div><div class="sun">☀</div></div>
<p class="condition">{{ weather.condition }}</p><div class="temperature">{{ weather.temperature.split(' ')[0] }}<small>{{ weather.temperature.split(' ')[1] }}</small></div>
<p class="asof">Feels like {{ weather.feels_like }} · {{ weather.local_time }} local time</p><div class="details">
<div><span>Humidity</span><strong>{{ weather.humidity }}</strong></div><div><span>Wind</span><strong>{{ weather.wind }}</strong></div><div><span>Precipitation</span><strong>{{ weather.precipitation }}</strong></div></div></section>{% endif %}
<footer>Weather data by <a href="https://open-meteo.com/">Open-Meteo</a></footer></main></body></html>"""


@web.route("/", methods=["GET", "POST"])
def home():
    weather = None
    error = None
    city = ""
    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if not city:
            error = "Enter a city name to search."
        else:
            try:
                weather = get_weather(find_city(city))
            except ValueError as exc:
                error = str(exc)
            except (HTTPError, URLError, TimeoutError) as exc:
                error = f"Could not reach the weather service. Check your internet connection and try again. ({exc})"
            except (KeyError, OSError) as exc:
                error = f"Weather lookup failed. Please try again. ({exc})"
    return render_template_string(PAGE, weather=weather, error=error, city=city)


if __name__ == "__main__":
    web.run(host="127.0.0.1", port=5000, debug=True)
