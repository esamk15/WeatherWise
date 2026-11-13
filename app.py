
from flask import Flask, render_template, request
import requests
import sqlite3
import os
from datetime import datetime, timezone

from config import API_KEY, BASE_URL, FORECAST_URL

app = Flask(__name__)

# Database file
DATABASE = os.path.join(app.root_path, "weatherwise.db")

# Air Pollution API
AIR_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


# --------------------------------
# DATABASE FUNCTIONS
# --------------------------------

def init_db():

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            country TEXT,
            searched_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_search(city, country):

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        INSERT INTO search_history (city, country, searched_at)
        VALUES (?, ?, ?)
    """, (
        city,
        country,
        datetime.now().strftime("%d %b %Y, %I:%M %p")
    ))

    # Keep only the latest 10 searches
    conn.execute("""
        DELETE FROM search_history
        WHERE id NOT IN (
            SELECT id FROM search_history
            ORDER BY id DESC
            LIMIT 10
        )
    """)

    conn.commit()
    conn.close()


def get_history():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    history = conn.execute("""
        SELECT * FROM search_history
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return history


# --------------------------------
# WEATHER DATA FUNCTION
# --------------------------------

def get_weather_data(params):

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10
    )

    if response.status_code == 404:
        raise ValueError("City or location not found.")

    if response.status_code == 401:
        raise ValueError("Invalid API key or API key not activated.")

    response.raise_for_status()

    data = response.json()

    weather = {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": round(data["main"]["temp"]),
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"],
        "pressure": data["main"]["pressure"],
        "icon": data["weather"][0]["icon"]
    }

    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]

    city_timezone = data.get("timezone", 0)

    forecast_params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }

    # --------------------------------
    # 5-DAY FORECAST
    # --------------------------------

    forecast_response = requests.get(
        FORECAST_URL,
        params=forecast_params,
        timeout=10
    )

    forecast_response.raise_for_status()

    forecast_data = forecast_response.json()

    daily_data = {}

    for item in forecast_data["list"]:

        local_time = datetime.fromtimestamp(
            item["dt"] + city_timezone,
            tz=timezone.utc
        )

        date = local_time.strftime("%Y-%m-%d")

        if date not in daily_data:
            daily_data[date] = (local_time, item)

        elif local_time.hour == 12:
            daily_data[date] = (local_time, item)

    forecast = []

    for local_time, item in list(daily_data.values())[:5]:

        forecast.append({
            "day": local_time.strftime("%A"),
            "date": local_time.strftime("%d %b"),
            "temperature": round(item["main"]["temp"]),
            "description": item["weather"][0]["description"],
            "icon": item["weather"][0]["icon"]
        })

    # --------------------------------
    # HOURLY FORECAST
    # --------------------------------

    hourly = []

    for item in forecast_data["list"][:8]:

        local_time = datetime.fromtimestamp(
            item["dt"] + city_timezone,
            tz=timezone.utc
        )

        hourly.append({
            "time": local_time.strftime("%I:%M %p"),
            "temperature": round(item["main"]["temp"]),
            "description": item["weather"][0]["description"],
            "icon": item["weather"][0]["icon"],
            "humidity": item["main"]["humidity"],
            "wind": item["wind"]["speed"]
        })

    # --------------------------------
    # AIR QUALITY INDEX
    # --------------------------------

    air_quality = None

    try:

        air_params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY
        }

        air_response = requests.get(
            AIR_URL,
            params=air_params,
            timeout=10
        )

        air_response.raise_for_status()

        air_data = air_response.json()

        air_item = air_data["list"][0]

        aqi_value = air_item["main"]["aqi"]

        aqi_status = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }

        aqi_colors = {
            1: "good",
            2: "fair",
            3: "moderate",
            4: "poor",
            5: "very-poor"
        }

        components = air_item["components"]

        air_quality = {
            "aqi": aqi_value,
            "status": aqi_status.get(aqi_value, "Unknown"),
            "color": aqi_colors.get(aqi_value, "moderate"),
            "pm2_5": round(components["pm2_5"], 2),
            "pm10": round(components["pm10"], 2),
            "co": round(components["co"], 2),
            "no2": round(components["no2"], 2),
            "o3": round(components["o3"], 2)
        }

    except (
        requests.exceptions.RequestException,
        KeyError,
        IndexError
    ):
        air_quality = None

    return weather, forecast, hourly, air_quality


# --------------------------------
# HOME PAGE
# --------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    forecast = None
    hourly = None
    air_quality = None
    error = None

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        latitude = request.form.get("latitude", "").strip()

        longitude = request.form.get("longitude", "").strip()

        if not API_KEY:

            error = "API key is missing. Check your .env file."

        else:

            try:

                # GPS location search
                if latitude and longitude:

                    lat = float(latitude)
                    lon = float(longitude)

                    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                        raise ValueError("Invalid location coordinates.")

                    params = {
                        "lat": lat,
                        "lon": lon,
                        "appid": API_KEY,
                        "units": "metric"
                    }

                # City search
                elif city:

                    params = {
                        "q": city,
                        "appid": API_KEY,
                        "units": "metric"
                    }

                else:

                    raise ValueError(
                        "Enter a city or use your current location."
                    )

                (
                    weather,
                    forecast,
                    hourly,
                    air_quality
                ) = get_weather_data(params)

                # Save successful search in SQLite
                save_search(
                    weather["city"],
                    weather["country"]
                )

            except ValueError as e:

                error = str(e)

            except requests.exceptions.RequestException:

                error = "Unable to connect to the weather service."

            except (KeyError, IndexError):

                error = "Unable to process weather information."

    # Get recent searches
    history = get_history()

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        hourly=hourly,
        air_quality=air_quality,
        history=history,
        error=error
    )


# --------------------------------
# START APPLICATION
# --------------------------------

init_db()

if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
