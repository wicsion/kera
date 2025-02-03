from fastapi import FastAPI, HTTPException
import httpx
from datetime import datetime, timedelta

app = FastAPI()

# Хранение данных о городах и пользователях
cities_data = {}
user_cities = {}
update_interval = timedelta(minutes=15)


async def fetch_weather_data(lat: float, lon: float) -> dict:
    """
    Получает данные о погоде для заданных координат.

    :param lat: Широта города.
    :param lon: Долгота города.
    :return: Данные о текущей погоде.
    :raises HTTPException: Если не удалось получить данные о погоде.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail="Error fetching weather data")


@app.get("/weather")
async def get_weather(lat: float, lon: float):
    """
    Возвращает текущую погоду для заданных координат.

    :param lat: Широта города.
    :param lon: Долгота города.
    :return: Данные о текущей погоде.
    """
    weather_data = await fetch_weather_data(lat, lon)
    current_weather = weather_data['current_weather']
    return {
        "temperature": current_weather['temperature'],
        "windspeed": current_weather['windspeed'],
        "pressure": current_weather['pressure']
    }


@app.post("/add_city")
async def add_city(city_name: str, lat: float, lon: float, user_id: int):
    """
    Добавляет город для указанного пользователя.

    :param city_name: Название города.
    :param lat: Широта города.
    :param lon: Долгота города.
    :param user_id: Идентификатор пользователя.
    :return: Сообщение об успешном добавлении.
    """
    user_cities.setdefault(user_id, []).append({"name": city_name, "lat": lat, "lon": lon})
    cities_data[(city_name, user_id)] = {"lat": lat, "lon": lon, "last_updated": datetime.now()}
    return {"message": f"City {city_name} added for user {user_id}"}


@app.get("/cities")
async def get_cities(user_id: int):
    """
    Возвращает список городов, добавленных пользователем.

    :param user_id: Идентификатор пользователя.
    :return: Список городов.
    """
    return user_cities.get(user_id, [])


@app.get("/weather_at_time")
async def get_weather_at_time(city_name: str, time: str, user_id: int, parameters: str):
    """
    Возвращает данные о погоде в заданный момент времени для указанного города.

    :param city_name: Название города.
    :param time: Время в формате ISO.
    :param user_id: Идентификатор пользователя.
    :param parameters: Запрашиваемые параметры погоды, разделенные запятыми.
    :return: Запрашиваемые данные о погоде.
    :raises HTTPException: Если город не найден для пользователя.
    """
    city_key = (city_name, user_id)
    if city_key not in cities_data:
        raise HTTPException(status_code=404, detail="City not found for user")

    city_info = cities_data[city_key]
    lat, lon = city_info['lat'], city_info['lon']
    target_time = datetime.fromisoformat(time)
    current_time = datetime.now()

    # Проверка необходимости обновления данных
    if current_time - city_info['last_updated'] > update_interval:
        weather_data = await fetch_weather_data(lat, lon)
        cities_data[city_key]['last_updated'] = current_time
    else:
        weather_data = await fetch_weather_data(lat, lon)

    # Возврат запрашиваемых параметров
    response = {}
    current_weather = weather_data['current_weather']
    for param in parameters.split(','):
        if param in current_weather:
            response[param] = current_weather[param]

    return response


# Запуск приложения
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
