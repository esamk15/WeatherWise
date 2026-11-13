# 🌦️ WeatherWise – Weather Forecasting Web Application

WeatherWise is a Python Flask-based weather forecasting web application that provides real-time weather information, air quality updates, hourly forecasts, and a five-day weather forecast using the OpenWeather API.

The application also supports GPS-based location detection and maintains a recent search history.

## 🚀 Features

- **Real-Time Weather:** Displays current temperature, weather conditions, humidity, and wind speed.
- **GPS Location Detection:** Automatically detects the user's current location.
- **Air Quality Index (AQI):** Displays air quality information and pollutant levels.
- **Hourly Forecast:** Shows upcoming weather conditions and temperature changes.
- **5-Day Forecast:** Provides weather predictions for the next five days.
- **Temperature Chart:** Visualizes temperature changes using Chart.js.
- **Recent Search History:** Stores the latest 10 city searches using SQLite.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| HTML5 | Web page structure |
| CSS3 | Styling and design |
| JavaScript | Interactive functionality |
| OpenWeather API | Weather and air quality data |
| SQLite | Search history database |
| Chart.js | Temperature visualization |

## 📁 Project Structure

```text
WeatherWise/
│
├── app.py
├── config.py
├── requirements.txt
├── .gitignore
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
└── weatherwise.db
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/esamk15/WeatherWise.git
```

### 2. Open the project directory

```bash
cd WeatherWise
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment (Windows)

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the API key

Create a `.env` file in the project root directory and add your OpenWeather API key:

```text
WEATHER_API_KEY=your_api_key_here
```

Get your API key from: https://openweathermap.org/api

### 7. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## 🔑 API Integration

WeatherWise uses the OpenWeather API to retrieve:

- Current weather information
- Five-day weather forecasts
- Air pollution and air quality data

The API key is stored securely in an environment variable rather than directly in the source code.

## 🎯 Project Objective

The objective of WeatherWise is to build a user-friendly weather forecasting application that combines real-time weather information, air quality monitoring, location detection, and data visualization in one platform.

## 👨‍💻 Developer

**Esam Khalid**  
BTech – Computer Science and Engineering  
SOA University, ITER

## 📌 Future Enhancements

- Weather alerts and notifications
- Improved mobile responsiveness
- Interactive weather maps
- Extended weather forecasting
