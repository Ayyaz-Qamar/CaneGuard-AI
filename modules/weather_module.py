import requests
import random
from datetime import datetime, timedelta

API_KEY  = "15ce7f0ca7b8fbdf9018839b1037f05d"
BASE_URL = "http://api.openweathermap.org/data/2.5"
GEO_URL  = "http://ip-api.com/json"


def get_city_from_ip():
    try:
        resp = requests.get(GEO_URL, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                return {
                    "success": True,
                    "city":    data.get("city", ""),
                    "region":  data.get("regionName", ""),
                    "country": data.get("country", ""),
                    "lat":     data.get("lat"),
                    "lon":     data.get("lon"),
                    "display": f"{data.get('city','')} — {data.get('regionName','')}",
                }
    except Exception:
        pass
    return {"success": False, "city": ""}


def get_weather_forecast(city="Rahim Yar Khan"):
    # Fix common city name issues
    city_map = {
        "Rahim Yar Khan": "Rahimyar Khan",
        "rahim yar khan": "Rahimyar Khan",
        "rahimyarkhan":   "Rahimyar Khan",
    }
    city = city_map.get(city, city)
    try:
        url  = f"{BASE_URL}/forecast?q={city}&appid={API_KEY}&units=metric"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return _process_forecast(resp.json(), city)
        return _demo_weather(city)
    except Exception:
        return _demo_weather(city)


def _process_forecast(data, city):
    daily = {}
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        if date not in daily:
            daily[date] = {"temps":[], "humidity":[], "weather":[], "rain":0}
        daily[date]["temps"].append(item["main"]["temp"])
        daily[date]["humidity"].append(item["main"]["humidity"])
        daily[date]["weather"].append(item["weather"][0]["main"])
        if "rain" in item:
            daily[date]["rain"] += item["rain"].get("3h", 0)

    forecast_days = []
    for date, info in list(daily.items())[:7]:
        avg_temp     = round(sum(info["temps"])    / len(info["temps"]), 1)
        avg_humidity = round(sum(info["humidity"]) / len(info["humidity"]), 1)
        risk = _calculate_risk(avg_temp, avg_humidity, info["rain"])
        forecast_days.append({
            "date":          date,
            "temp":          avg_temp,
            "humidity":      avg_humidity,
            "rain":          round(info["rain"], 1),
            "condition":     info["weather"][0],
            "risk":          risk["level"],
            "risk_label":    risk["label"],
            "risk_label_ur": risk["label_ur"],
            "risk_color":    risk["color"],
        })

    return {
        "city":         city,
        "forecast":     forecast_days,
        "overall_risk": _overall_risk(forecast_days),
        "fetched_at":   datetime.now().strftime("%Y-%m-%d %H:%M"),
        "demo_mode":    False,
    }


def _calculate_risk(temp, humidity, rain):
    score = 0
    if humidity > 80:   score += 3
    elif humidity > 60: score += 1
    if temp > 28:       score += 2
    elif temp > 22:     score += 1
    if rain > 5:        score += 3
    elif rain > 0:      score += 1

    if score >= 5:
        return {"level":"high",   "label":"High Risk",
                "label_ur":"زیادہ خطرہ",   "color":"#ef4444"}
    elif score >= 3:
        return {"level":"medium", "label":"Medium Risk",
                "label_ur":"درمیانہ خطرہ", "color":"#f97316"}
    else:
        return {"level":"low",    "label":"Low Risk",
                "label_ur":"کم خطرہ",      "color":"#22c55e"}


def _overall_risk(forecast_days):
    high_days   = sum(1 for d in forecast_days if d["risk"] == "high")
    medium_days = sum(1 for d in forecast_days if d["risk"] == "medium")
    if high_days >= 3:
        return {"level":"high",
                "label":"High Disease Risk This Week",
                "label_ur":"اس ہفتے بیماری کا زیادہ خطرہ!",
                "color":"#ef4444"}
    elif high_days >= 1 or medium_days >= 3:
        return {"level":"medium",
                "label":"Moderate Risk — Stay Alert",
                "label_ur":"درمیانہ خطرہ — چوکس رہیں",
                "color":"#f97316"}
    else:
        return {"level":"low",
                "label":"Low Risk This Week",
                "label_ur":"اس ہفتے کم خطرہ",
                "color":"#22c55e"}


def _demo_weather(city):
    days = []
    base = datetime.now()
    for i in range(7):
        date     = (base + timedelta(days=i)).strftime("%Y-%m-%d")
        temp     = round(random.uniform(25, 38), 1)
        humidity = round(random.uniform(45, 90), 1)
        rain     = round(random.uniform(0, 12),  1)
        risk     = _calculate_risk(temp, humidity, rain)
        days.append({
            "date":          date,
            "temp":          temp,
            "humidity":      humidity,
            "rain":          rain,
            "condition":     random.choice(["Clear","Clouds","Rain","Haze"]),
            "risk":          risk["level"],
            "risk_label":    risk["label"],
            "risk_label_ur": risk["label_ur"],
            "risk_color":    risk["color"],
        })
    return {
        "city":         city,
        "forecast":     days,
        "overall_risk": _overall_risk(days),
        "fetched_at":   datetime.now().strftime("%Y-%m-%d %H:%M"),
        "demo_mode":    True,
    }


if __name__ == "__main__":
    result = get_weather_forecast("Rahim Yar Khan")
    print(f"City         : {result['city']}")
    print(f"Overall Risk : {result['overall_risk']['label']}")
    print(f"Demo Mode    : {result['demo_mode']}")
    for day in result["forecast"]:
        print(f"  {day['date']} | {day['temp']}C | "
              f"Humidity: {day['humidity']}% | {day['risk_label']}")