import asyncio
import logging
import re
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from translate import Translator


bot = Bot(token="tg-bot-token")
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class St(StatesGroup):
    city = State()

@dp.message(F.text == "/start")
async def start(message: types.Message, state: FSMContext):
    await message.answer('Отправьте название города, для которого хотите узнать погоду')
    await state.set_state(St.city)


def ya_geocode(city):
    api_key = 'yandex-token'
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={city}&format=json"
    response = requests.get(url)

    # Обработка ответа
    if response.status_code == 200:
        data2 = response.json()
        if data2['response']['GeoObjectCollection']['featureMember']:
            coordinates = data2['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            coordinates = coordinates.split(' ')
            return coordinates


@dp.message(St.city)
async def city(message: types.Message, state: FSMContext):

    try:
        lon, lat = ya_geocode(message.text)
    except Exception as e:
        return await message.answer(f'Ошибка при выполнении запроса к Яндеккс-геокодеру: {e}')
    try:
        resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lon={lon}&lat={lat}&appid=openweathermap-token')
        weather = resp.json()['weather'][0]['description']
        wind = resp.json()['wind']['speed']
        country = resp.json()['sys']['country']

        translator = Translator(from_lang="english", to_lang="russian")
        weather = translator.translate(weather)
        weather =re.sub(r'[^\s\w]', '',weather)
        weather = re.sub(r'\d', '', weather)
        return await message.answer(f'Погода: {weather}\n\nСкорость ветра: {wind} м/с\n\nкод страны: {country}')
    except Exception as e:
        return await message.answer(f'Ошибка при выполнении запроса к погодному сервису: {e}')



if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

