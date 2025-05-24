import httpx
from datetime import datetime, timedelta
from config import WEATHER_API_URL
import matplotlib.pyplot as plt
from io import BytesIO
import math

PARAMETER_LABELS = {
    "temperature_2m": "Температура (°C)",
    "precipitation": "Осадки (мм)",
    "visibility": "Видимость (м)",
    "wind_gusts_10m": "Порывы ветра (м/с)",
    "wind_speed_10m": "Скорость ветра (10 м, м/с)",
    "wind_speed_80m": "Скорость ветра (80 м, м/с)",
    "wind_speed_120m": "Скорость ветра (120 м, м/с)",
    "wind_speed_180m": "Скорость ветра (180 м, м/с)",
    "wind_direction_10m": "Направление ветра (°)"
}

async def get_weather(lat: float, lon: float, parameters: list[str]) -> str:
    return "ok"  # заглушка — не используется (бот не отправляет текст)

async def plot_forecast(data: dict, parameters: list[str]) -> list[tuple[str, BytesIO]]:
    images = []
    times = data["hourly"]["time"][:24]
    hours = [t[-5:] for t in times]

    for key in parameters:
        values = data["hourly"].get(key, [])[:24]
        if not values:
            continue

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.set_title(PARAMETER_LABELS.get(key, key))
        ax.set_xlabel("Время")
        ax.grid(True)
        plt.xticks(rotation=45)

        if key == "wind_direction_10m":
            ax.set_ylim(-1, 1)
            ax.set_yticks([])
            x = list(range(24))
            y = [0] * 24
            u = [math.cos(math.radians(270 - d)) for d in values]
            v = [math.sin(math.radians(270 - d)) for d in values]
            ax.quiver(x, y, u, v, scale=10, angles='xy', scale_units='xy')
            ax.set_xticks(x)
            ax.set_xticklabels(hours)
        else:
            ax.plot(hours, values, marker='o')
            ax.set_ylabel("Значение")

        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        images.append((key, buf))
        plt.close()

    return images