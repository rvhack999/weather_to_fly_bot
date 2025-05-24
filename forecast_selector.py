from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

PARAMETER_OPTIONS = {
    "temperature_2m": "Температура",
    "precipitation": "Осадки",
    "visibility": "Видимость",
    "wind_gusts_10m": "Порывы ветра",
    "wind_speed_10m": "Ветер (10м)",
    "wind_speed_80m": "Ветер (80м)",
    "wind_speed_120m": "Ветер (120м)",
    "wind_speed_180m": "Ветер (180м)",
    }

user_param_selection = {}

def get_parameter_keyboard(user_id: int):
    selected = user_param_selection.get(user_id, set())
    kb = InlineKeyboardBuilder()
    for key, name in PARAMETER_OPTIONS.items():
        checked = "✅" if key in selected else "❌"
        kb.button(text=f"{checked} {name}", callback_data=f"toggle:{key}")
    kb.button(text="Готово", callback_data="done")
    kb.adjust(2)
    return kb.as_markup()

def toggle_parameter(user_id: int, key: str):
    selection = user_param_selection.setdefault(user_id, set())
    if key in selection:
        selection.remove(key)
    else:
        selection.add(key)

def get_selected_parameters(user_id: int) -> list[str]:
    return list(user_param_selection.get(user_id, set()))