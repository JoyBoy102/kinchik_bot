from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from parser import get_cinema_names, get_info_about_cinema, get_info_about_films, get_all_theaters, get_all_films
from keyboards import ikb_sorts, ikb_categories, ikb_times, menu_kb
import requests
from io import BytesIO
from PIL import Image
import json, pickle

TOKEN_API = "7301050546:AAHSpfj_d89qYrxNWn_NfivibVbNj5zRBi4"
Description = """
Добро пожаловать в kinchik2024_bot!
Этот бот помогает вам быстро узнать актуальное расписание фильмов в кинотеатрах Уфы.
Просто выберите интересующий вас кинотеатр и получите список фильмов с указанием времени сеансов, категории и другой полезной информации.
Бот предоставляет удобный интерфейс с постоянными кнопками для навигации, чтобы вы могли легко найти нужные данные. 
Будьте в курсе всех киноновинок и не пропустите любимые фильмы!
/start - запустить бота
/check_schedule - посмотреть расписание фильмов
"""
bot = Bot(token=TOKEN_API)
dp = Dispatcher(bot)
categories = ["анимация", "боевик", "военный", "детектив", "документальный", "драма", "комедия", "криминал", "приключения",
              "семейный", "сказка", "триллер", "ужасы", "фантастика", "фэнтэзи"]
times = ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00",
         "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30",
         "23:00", "23:30", "24:00"]


@dp.message_handler(commands=["start"])
async def vote_callback(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=Description,
                           reply_markup=menu_kb)


@dp.callback_query_handler(lambda callback: callback.data in categories)
async def vote_callback_categ(callback: types.CallbackQuery):
    all_info = {}
    message_rasp = ""
    with open('all_info.json', 'r', encoding='utf-8') as file:
        all_info = json.load(file)
    all_categories = sort_categories(all_info, callback.data)
    if all_categories!=None:
        message_rasp = get_message(all_categories)

    else:
        message_rasp = "Данный жанр отсутствует в выбранном кинотеатре"
    await bot.send_message(chat_id=callback.from_user.id,
                           text=message_rasp,
                           parse_mode=types.ParseMode.MARKDOWN,
                           reply_markup=ikb_sorts)


@dp.callback_query_handler(lambda callback: callback.data in times)
async def vote_callback_time(callback: types.CallbackQuery):
    all_info = {}
    message_rasp = ""
    with open('all_info.json', 'r', encoding='utf-8') as file:
        all_info = json.load(file)
    all_times = sort_times(all_info, callback.data)
    if all_times != None:
        message_rasp = get_message(all_times)

    else:
        message_rasp = "До этого времени нету фильмов в этом кинотеатре"
    await bot.send_message(chat_id=callback.from_user.id,
                           text=message_rasp,
                           parse_mode=types.ParseMode.MARKDOWN,
                           reply_markup=ikb_times)

@dp.message_handler(commands=["check_schedule"])
async def vote_callback(callback: types.CallbackQuery):
    ikb_actions = InlineKeyboardMarkup(row_width=2)
    ib1_action = InlineKeyboardButton(text="Выбрать кинотеатр", callback_data="choose")
    ib2_action = InlineKeyboardButton(text="Найти кинотеатр по фильму", callback_data="find")
    ikb_actions.add(ib1_action, ib2_action)

    await bot.send_message(chat_id=callback.from_user.id,
                           text="Выберите действие:",
                           reply_markup=ikb_actions)

@dp.callback_query_handler(lambda callback: "find" in callback.data)
async def vote_callback(callback: types.CallbackQuery):
    new_data = callback.data.replace("find", "")
    url = f"https://ufa.kinoafisha.info/cinema/"
    ikb_films = InlineKeyboardMarkup(row_width=5)
    all_films = get_all_films(url)
    buttons = []
    for i in range(len(all_films)):
        ib = InlineKeyboardButton(text=str(i), callback_data="film"+str(i)+new_data)
        buttons.append(ib)
    for i in range(0, len(buttons), 5):
        ikb_films.row(*buttons[i:i + 5])
    message = "Список доступных фильмов в этом городе на сегодня:\n"
    for i in range(len(all_films)):
        message += f"{i} - {all_films[i]}\n"
    message += "Выберите фильм:"
    await bot.send_message(chat_id=callback.from_user.id,
                           text=message,
                           reply_markup=ikb_films)

@dp.callback_query_handler(lambda callback: "film" in callback.data)
async def vote_callback_f(callback: types.CallbackQuery):
    new_data = callback.data.replace("film", "")
    with open('all_films.pkl', 'rb') as f:
        all_films = pickle.load(f)
    index = new_data[0]
    new_data = delete_numbers(new_data)
    url = f"https://ufa.kinoafisha.info/cinema/"
    all_info = get_all_theaters(url)
    ikb_theaters = InlineKeyboardMarkup(row_width=5)
    for key, value in all_info.items():
        if all_films[int(index)] in value["films"]:
            ikb_theaters.add(InlineKeyboardButton(text=key, callback_data=value["link"]))
    await bot.send_message(chat_id=callback.from_user.id,
                           text="Выберите кинотеатр:",
                           reply_markup=ikb_theaters)

@dp.callback_query_handler(lambda callback: "choose" in callback.data)
async def vote_callback_choose(callback: types.CallbackQuery):
    all_info = get_cinema_names(f"https://ufa.kinoafisha.info/cinema/")
    ikb_films = InlineKeyboardMarkup(row_width=len(all_info))
    buttons = []
    for key, item in all_info.items():
        ib_kinoteatr = InlineKeyboardButton(text=key, callback_data=item)
        buttons.append(ib_kinoteatr)
    for i in range(0, len(buttons), 2):
        ikb_films.row(*buttons[i:i + 2])
    await bot.send_message(chat_id=callback.from_user.id,
                           text="Выберите кинотеатр:",
                           reply_markup=ikb_films)

@dp.callback_query_handler(lambda callback: "sort" in callback.data)
async def vote_callback_sort(callback: types.CallbackQuery):
    with open('all_info.json', 'r', encoding='utf-8') as file:
        # Create the inline keyboard with the grouped buttons
        if ("category" in callback.data):
            await bot.send_message(chat_id=callback.from_user.id,
                                   text="Выберите жанр:",
                                   reply_markup=ikb_categories)
        elif ("time" in callback.data):
            await bot.send_message(chat_id=callback.from_user.id,
                                   text="Выберите время:",
                                   reply_markup=ikb_times)


@dp.callback_query_handler(lambda callback: "rasp" not in callback.data)
async def vote_callback(callback: types.CallbackQuery):
    all_info = get_info_about_cinema(callback.data)
    message = f"""
    *Название кинотеатра:* {all_info["Название кинотеатра"]}
*Адрес кинотеатра:* {all_info["Адрес кинотеатра"]}
*Номер телефона:* {all_info["Номер телефона"]}
*О кинотеатре:* {all_info["Отзывы"]}
    """
    ikb_films = InlineKeyboardMarkup(row_width=1)
    ikb_films.add(InlineKeyboardButton(text="Расписание фильмов", callback_data=f"rasp{callback.data}"))
    if all_info["Картинка"]!=None:
        response = requests.get(all_info["Картинка"])
        output_bytes = None
        if response.status_code == 200 and all_info["Картинка"]!=None:
            image_bytes = BytesIO(response.content)
            image = Image.open(image_bytes)
            image = image.convert("RGB")
            resized_image = image.resize((160, 100))
            output_bytes = BytesIO()
            resized_image.save(output_bytes, format='JPEG')
            output_bytes.seek(0)
        if (output_bytes is not None and all_info["Картинка"]!=None):
            await bot.send_photo(chat_id=callback.from_user.id,
                                 photo=output_bytes)
    await bot.send_message(chat_id=callback.from_user.id,
                           text=message,
                           parse_mode=types.ParseMode.MARKDOWN,
                           reply_markup=ikb_films)


@dp.callback_query_handler(lambda callback: "rasp" in callback.data)
async def vote_callback_d(callback: types.CallbackQuery):
    link_film = callback.data[4:]  # Удаляем префикс "rasp"
    link_film = link_film.replace('rasp', '')
    all_info = get_info_about_films(link_film)
    message = get_message(all_info)
    await bot.send_message(chat_id=callback.from_user.id,
                                          text=message,
                                          parse_mode=types.ParseMode.MARKDOWN,
                                          reply_markup=ikb_sorts)


def get_message(all_info):
    message = ""
    for film, value in all_info.items():
        time_and_price = ""
        for i in range(len(value["time_sessions"])):
            try:
                price = value['price_sessions'][i]
            except:
                price = "Цена не указана"
            time_and_price += f"{value['time_sessions'][i]} - {price} \n"
        message += f"""*{film}*
Жанры: {value["categories"]}
Год и страна выпуска: {value["details"]}
Формат фильма: {value["formats"]}
Время начала фильма и стоимость билета: 
{time_and_price} 
"""
    return message

def sort_categories(all_info, category):
    result = {}
    for key, item in all_info.items():
        if category.lower() in item["categories"]:
            result[key] = item
    if len(result) == 0:
        return None
    return result

def sort_times(all_info, time):
    result = {}
    for key, item in all_info.items():
        for j in item["time_sessions"]:
            if get_seconds(j)<get_seconds(time):
                result[key] = item
    if len(result) == 0:
        return None
    return result

def find_place(all_info, film):
    result = []
    for key, item in all_info.items():
        for j in item:
            if j.lower().replace(" ", "") in film:
                result.append(j)
    if len(result) == 0:
        return None
    return result
def get_seconds(time):
    time_list = time.split(":")
    time_list = [0 if i == "00" else int(i) for i in time_list]
    seconds = time_list[0]*3600+time_list[1]*60
    return seconds

def delete_numbers(str):
    new_str = ""
    for i in str:
        if not i.isdigit():
            new_str += i
    return new_str
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
