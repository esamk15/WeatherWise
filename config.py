
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenWeather API key
API_KEY = os.getenv("WEATHER_API_KEY")

# Current weather API
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# 5-day forecast API (3-hour intervals)
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
