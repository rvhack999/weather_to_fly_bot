from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command, CommandObject
import asyncio
from datetime import datetime, timedelta

from config import BOT_TOKEN
from forecast_selector import get_parameter_keyboard, toggle_parameter, get_selected_parameters
from weather import plot_forecast, PARAMETER_LABELS
from users import register_user

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_waiting_location = set()

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Запросить прогноз")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет!\n"
        "Я помогу тебе проверить, подходит ли погода для полёта на дроне.\n"
        "Ты можешь выбрать интересующие параметры прогноза — температуру, ветер, осадки, видимость и другие — и отправить свою геолокацию.\n\n"
        "Нажми кнопку \"Запросить прогноз\", чтобы начать.",
        reply_markup=main_menu_kb
    )

@dp.message(lambda m: m.text == "Начать")
async def handle_start_button(message: Message):
    await cmd_start(message)

@dp.message(lambda m: m.text == "Запросить прогноз")
async def handle_weather_button(message: Message):
    await cmd_weather(message, CommandObject(command='weather', args=""))

@dp.message(Command("weather"))
async def cmd_weather(message: Message, command: CommandObject):
    await message.answer("Выбери параметры прогноза:", reply_markup=get_parameter_keyboard(message.from_user.id))

@dp.callback_query(lambda c: c.data.startswith("toggle:"))
async def toggle_param_callback(call: CallbackQuery):
    param_key = call.data.split(":")[1]
    toggle_parameter(call.from_user.id, param_key)
    await call.message.edit_reply_markup(reply_markup=get_parameter_keyboard(call.from_user.id))
    await call.answer("Выбор обновлён.")

@dp.callback_query(lambda c: c.data == "done")
async def done_callback(call: CallbackQuery):
    await call.message.answer(
        "Отправь свою геолокацию:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отправить геолокацию", request_location=True)]],
            resize_keyboard=True
        )
    )
    user_waiting_location.add(call.from_user.id)
    await call.answer()

@dp.message(lambda msg: msg.location is not None)
async def location_received(message: Message):
    if message.from_user.id in user_waiting_location:
        register_user(message.from_user.id)
        user_waiting_location.remove(message.from_user.id)

        lat = message.location.latitude
        lon = message.location.longitude
        parameters = get_selected_parameters(message.from_user.id)

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": ",".join(parameters),
                    "start_date": datetime.utcnow().date().isoformat(),
                    "end_date": (datetime.utcnow() + timedelta(days=1)).date().isoformat(),
                    "timezone": "auto"
                }
            )
            data = response.json()

        charts = await plot_forecast(data, parameters)
        for name, buf in charts:
            label = PARAMETER_LABELS.get(name, name)
            buf.name = f"{name}.png"
            await message.answer_photo(types.BufferedInputFile(buf.read(), filename=buf.name), caption=label)
        await message.answer("Готово. Можешь запросить новый прогноз.", reply_markup=main_menu_kb)
        buf.close()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())