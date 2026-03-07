import requests
from datetime import datetime


API_KEY = "PASTE_YOUR_API_KEY_HERE"  # 🔥 Yahan apni key likho
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


class WeatherService:

    def get_weather(self, city):

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(BASE_URL, params=params)

        if response.status_code != 200:
            return False, None, response.json().get("message", "Error fetching weather")

        return True, response.json(), None


    @staticmethod
    def format_weather_data(data):

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]),
            "icon": data["weather"][0]["icon"]
        }