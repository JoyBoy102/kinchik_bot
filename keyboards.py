from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

categories = ["анимация", "боевик", "военный", "детектив", "документальный", "драма", "комедия", "криминал", "приключения",
              "семейный", "сказка", "триллер", "ужасы", "фантастика", "фэнтэзи"]

times = ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
         "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30",
         "23:00", "23:30", "24:00"]



# Создание клавиатуры сортировок
ikb_sorts = InlineKeyboardMarkup(row_width=1)
ib1_sorts = InlineKeyboardButton(text="Найти по жанру", callback_data="sort_category")
ib2_sorts = InlineKeyboardButton(text="Найти по времени начала фильма", callback_data="sort_time")
ikb_sorts.add(ib1_sorts, ib2_sorts)

# Создание клавиатуры категорий
ikb_categories = InlineKeyboardMarkup(row_width=4)
buttons_categories = [InlineKeyboardButton(text=category, callback_data=category) for category in categories]
for i in range(0, len(buttons_categories), 4):
    ikb_categories.row(*buttons_categories[i:i + 4])

# Создание клавиатуры времени
ikb_times = InlineKeyboardMarkup(row_width=4)
buttons_times = [InlineKeyboardButton(text="до "+time, callback_data=time) for time in times]
for i in range(0, len(buttons_times), 4):
    ikb_times.row(*buttons_times[i:i + 4])

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton(text="/check_schedule")
b2 = KeyboardButton(text="/start")

menu_kb.add(b2)
menu_kb.add(b1)
