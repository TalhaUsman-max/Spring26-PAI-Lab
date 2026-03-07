"""
Weather Dashboard - Working Version
"""

from flask import Flask, render_template, request, jsonify
from weather_service import WeatherService

app = Flask(__name__)


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Weather API
@app.route("/api/weather", methods=["POST"])
def get_weather():

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Invalid request"}), 400

    city = data.get("city", "").strip()

    if not city:
        return jsonify({"success": False, "error": "City is required"}), 400

    service = WeatherService()
    success, weather_data, error = service.get_weather(city)

    if not success:
        return jsonify({"success": False, "error": error}), 400

    formatted = service.format_weather_data(weather_data)

    return jsonify({
        "success": True,
        "data": {
            "city": formatted["city"],
            "country": formatted["country"],
            "temperature": formatted["temperature"],
            "description": formatted["description"],
            "humidity": formatted["humidity"],
            "wind_speed": formatted["wind_speed"],
            "pressure": formatted["pressure"],
            "sunrise": formatted["sunrise"].strftime("%H:%M"),
            "sunset": formatted["sunset"].strftime("%H:%M"),
            "icon": formatted["icon"]
        }
    })


if __name__ == "__main__":
    app.run(debug=True)