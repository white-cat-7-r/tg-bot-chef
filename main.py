import logging
import asyncio
import threading
import json
import os
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# ======= ПРОСТОЙ ВЕБ-СЕРВЕР ДЛЯ ПИНГОВАНИЯ =======
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот жив!", 200

@app.route('/ping')
def ping():
    return "Pong!", 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Запускаем Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

# ======= РЕЦЕПТЫ (из JSON) =======
RECIPES_PATH = os.path.join(os.path.dirname(__file__), "recipes.json")
with open(RECIPES_PATH, "r", encoding="utf-8") as f:
    _data = json.load(f)

BREAKFAST = _data["breakfast"]
SOUPS = _data["soups"]
PASTA = _data["pasta"]
MAIN_DISHES = _data["main_dishes"]
DESSERTS = _data["desserts"]
SALADS = _data["salads"]

# ======= НАСТРОЙКИ БОТА =======
API_TOKEN = "8684451450:AAFJ5eJPtu85Dpd9nrOAl08aQ5etyPLQuqM"

def escape_md(text):
    for ch in ('*', '_', '[', '`'):
        text = text.replace(ch, '\\' + ch)
    return text

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# ======= КНОПКИ =======
def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽️ Завтраки", callback_data="menu_breakfast")],
        [InlineKeyboardButton(text="🥣 Супы", callback_data="menu_soups")],
        [InlineKeyboardButton(text="🍝 Горячее", callback_data="menu_hot")],
        [InlineKeyboardButton(text="🥗 Салаты", callback_data="menu_salads")],
        [InlineKeyboardButton(text="🍰 Десерты", callback_data="menu_desserts")]
    ])

def category_menu_keyboard(category_data, category_name, back_callback="back_to_main", hot_back_callback=None):
    buttons = []
    for name in category_data.keys():
        buttons.append([InlineKeyboardButton(text=name.capitalize(), callback_data=f"{category_name}_{name}")])
    if hot_back_callback:
        buttons.append([InlineKeyboardButton(text="⬅️ Назад в горячее", callback_data=hot_back_callback)])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def hot_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍝 Пасты", callback_data="hot_pasta")],
        [InlineKeyboardButton(text="🥩 Вторые блюда", callback_data="hot_main")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def back_keyboard(back_callback="back_to_hot_menu"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback)]
    ])

# ======= ОБРАБОТЧИКИ =======
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "🍳 Привет! Я твой личный шеф.\n\n"
        "Выбери раздел:",
        reply_markup=main_menu_keyboard()
    )

@dp.callback_query(lambda c: c.data == "menu_breakfast")
async def show_breakfast_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 Меню завтраков:\nВыбери блюдо:",
        reply_markup=category_menu_keyboard(BREAKFAST, "breakfast")
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu_soups")
async def show_soups_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 Меню супов:\nВыбери блюдо:",
        reply_markup=category_menu_keyboard(SOUPS, "soup")
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu_hot")
async def show_hot_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍝 Горячее:\nВыбери подраздел:",
        reply_markup=hot_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "hot_pasta")
async def show_pasta_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 Пасты:\nВыбери блюдо:",
        reply_markup=category_menu_keyboard(PASTA, "pasta", hot_back_callback="back_to_hot_menu")
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "hot_main")
async def show_main_dishes_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 Вторые блюда:\nВыбери блюдо:",
        reply_markup=category_menu_keyboard(MAIN_DISHES, "main", hot_back_callback="back_to_hot_menu")
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu_salads")
async def show_salads_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 Салаты:\nВыбери блюдо:",
        reply_markup=category_menu_keyboard(SALADS, "salad")
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu_desserts")
async def show_desserts_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 Десерты:\nВыбери блюдо:",
        reply_markup=category_menu_keyboard(DESSERTS, "dessert")
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍳 Привет! Я твой личный шеф.\n\n"
        "Выбери раздел:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_hot_menu")
async def back_to_hot_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍝 Горячее:\nВыбери подраздел:",
        reply_markup=hot_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("back_menu_"))
async def back_to_category_menu(callback: CallbackQuery):
    category = callback.data.split("_", 2)[2]
    menus = {
        "breakfast": ("📋 Меню завтраков:\nВыбери блюдо:", BREAKFAST, "breakfast"),
        "soup": ("📋 Меню супов:\nВыбери блюдо:", SOUPS, "soup"),
        "salad": ("📋 Салаты:\nВыбери блюдо:", SALADS, "salad"),
        "dessert": ("📋 Десерты:\nВыбери блюдо:", DESSERTS, "dessert"),
    }
    if category in menus:
        text, data, name = menus[category]
        await callback.message.edit_text(text, reply_markup=category_menu_keyboard(data, name))
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("breakfast_") or c.data.startswith("soup_") or c.data.startswith("pasta_") or c.data.startswith("main_") or c.data.startswith("salad_") or c.data.startswith("dessert_"))
async def show_recipe(callback: CallbackQuery):
    parts = callback.data.split("_", 1)
    category = parts[0]
    recipe_name = parts[1]

    if category == "breakfast":
        recipe = BREAKFAST.get(recipe_name)
    elif category == "soup":
        recipe = SOUPS.get(recipe_name)
    elif category == "pasta":
        recipe = PASTA.get(recipe_name)
    elif category == "main":
        recipe = MAIN_DISHES.get(recipe_name)
    elif category == "salad":
        recipe = SALADS.get(recipe_name)
    elif category == "dessert":
        recipe = DESSERTS.get(recipe_name)
    else:
        recipe = None

    CATEGORY_BACK = {
        "pasta": "hot_pasta",
        "main": "hot_main",
    }

    if recipe:
        answer = f"🍳 *{escape_md(recipe_name.capitalize())}*\n\n📦 Ингредиенты:\n- " + "\n- ".join(escape_md(i) for i in recipe["ингредиенты"])
        answer += f"\n\n👨‍🍳 Приготовление:\n" + "\n".join(escape_md(s) for s in recipe["шаги"])
        back_cb = CATEGORY_BACK.get(category, f"back_menu_{category}")
        await callback.message.edit_text(answer, parse_mode="Markdown", reply_markup=back_keyboard(back_cb))
    else:
        await callback.message.edit_text("❌ Рецепт не найден.", reply_markup=back_keyboard())
    await callback.answer()

# ======= ЗАПУСК =======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())