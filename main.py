import requests
import telebot
import datetime
from telebot import types
from datetime import datetime

TG_TOKEN = "6083614335:AAGQC665fJ929K5uhIyUGO3e6dwIcYe-23Y"
bot = telebot.TeleBot(TG_TOKEN)

API_POSITION = "http://api.open-notify.org/iss-now.json"
API_ASTRO = "http://api.open-notify.org/astros.json"

WEATHER_TOKEN = "f564a6066176291403f48b3ea6d04bd7"

CRIPTO_COIN_TOKEN = "93C627B9-9D03-4108-84AC-0CDB7C5DD74A"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Welcome to ISS command center!')
    menu(message)


def menu(message):
    menu_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)

    button_iss_position = types.KeyboardButton("🛰")
    button_astros = types.KeyboardButton("👨‍🚀")
    button_weather = types.KeyboardButton("🌦")
    button_currency = types.KeyboardButton("💸")
    button_restart_bot = types.KeyboardButton("🔄")

    menu_buttons.add(button_iss_position, button_astros, button_weather, button_currency, button_restart_bot)

    bot.send_message(message.chat.id, 'Please, choose option ⬇️', reply_markup=menu_buttons)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.text == "🛰":
        mks_position(message)
    if message.text == "👨‍🚀":
        mks_squad(message)
    if message.text == "🌦":
        get_agreement(message)
    if message.text == "💸":
        get_cripto_coin_name(message)
    if message.text == "🔄":
        menu(message)


@bot.message_handler(commands=['mksPosition'])
def mks_position(message):
    request = requests.get(url=API_POSITION)
    response = request.json()

    timestamp = response['timestamp']
    cur_time = (datetime.utcfromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S'))

    longitude_r = response['iss_position']['longitude']
    latitude_r = response['iss_position']['latitude']

    bot.send_message(message.chat.id, f"Longitude: {longitude_r},\n"
                                      f"Latitude: {latitude_r},\n"
                                      f"Online time: {cur_time}")

    bot.send_location(message.chat.id, longitude=longitude_r, latitude=latitude_r)


@bot.message_handler(commands=['mksSquad'])
def mks_squad(message):
    request = requests.get(url=API_ASTRO)
    response = request.json()

    for item in response['people']:
        bot.send_message(message.chat.id, "🚀: {} | 🧑‍🚀: {}".format(item['craft'], item['name']))

    bot.send_message(message.chat.id, f"Total amount of 👨‍🚀 in space ➡️ {response['number']}❕")


@bot.message_handler(commands=['weather'])
def get_agreement(message):
    message_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)

    request_yes = types.KeyboardButton("🟢")
    request_no = types.KeyboardButton("🔴")

    message_buttons.add(request_yes, request_no)

    message_from_bot = bot.send_message(message.chat.id, "Do you request weather information?",
                                        reply_markup=message_buttons)
    bot.register_next_step_handler(message_from_bot, say_yes_no)


def say_yes_no(message):
    if message.text == "🟢":
        message_from_bot = bot.send_message(message.chat.id, "🏢 Write the name of сity: ")
        bot.register_next_step_handler(message_from_bot, get_weather)
    elif message.text == "🔴":
        bot.send_message(message.chat.id, "📛 Process has been stoped! 📛")
        menu(message)
    elif message.text != "🟢" or message.text != "🔴":
        bot.send_message(message.chat.id, "⛔️ Incorrect input! ⛔ \n"
                                          "Press 🟢 or 🔴 only!")
        get_agreement(message)


def get_weather(message):
    try:
        request = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={WEATHER_TOKEN}&units=metric"
        )
        response = request.json()

        name_of_city = response["name"]
        curr_temperature = response["main"]["temp"]
        temp_feels_like = response["main"]["feels_like"]
        humidity = response["main"]['humidity']
        speed_of_wind = response["wind"]["speed"]
        sunrise = response["sys"]["sunrise"]
        sunrise_timestamp = (datetime.utcfromtimestamp(sunrise).strftime('%H:%M'))
        sunset = response["sys"]["sunset"]
        sunset_timestamp = (datetime.utcfromtimestamp(sunset).strftime('%H:%M'))
        date_time = response["dt"]
        date_time_timestamp = (datetime.utcfromtimestamp(date_time).strftime('%d-%m-%Y %H:%M:%S'))

        bot.send_message(message.chat.id, f"⏰ {date_time_timestamp} \n"
                                          f"🏢 City: {name_of_city} \n"
                                          f"🌡 Current temperature: {curr_temperature}°C \n"
                                          f"🌬 Feels like: {temp_feels_like}°C \n"
                                          f"💧 Humidity: {humidity}% \n"
                                          f"💨 Wind speed: {speed_of_wind} m/s \n"
                                          f"🌇 Sunrise: {sunrise_timestamp} \n"
                                          f"🌃 Sunset: {sunset_timestamp} \n\n"
                                          f"Have a great day! 😎☀️")
        menu(message)
    except Exception as _error:
        error_on_city_r = bot.send_message(message.chat.id, "⛔️ City not found! ⛔️\nWrite city name again: ")
        bot.register_next_step_handler(error_on_city_r, get_weather)


@bot.message_handler(commands=['cripto'])
def get_cripto_coin_name(message):
    message_from_bot = bot.send_message(message.chat.id, 'Write  🪙<b>CRYPTOCURRENCY  NAME</b> and 🇪🇺🇺🇸🇷🇺<b>CURRENCY</b> separated by <b>SPACE</b> (example "btc usd")', parse_mode='HTML')
    bot.register_next_step_handler(message_from_bot, send_result)


@bot.message_handler(func=lambda message: True)
def send_result(message):
    # Получаем текст сообщения
    text = message.text.upper()

    # Разбиваем текст на части
    parts = text.split(' ')

    # Получаем название криптовалюты и валюты, в которой нужно вывести курс
    cripto_currency = parts[0]
    quote_currency = parts[1] if len(parts) > 1 else 'USD'

    # Формируем URL для запроса к API
    url = f'https://rest.coinapi.io/v1/exchangerate/{cripto_currency}/{quote_currency}?apikey={CRIPTO_COIN_TOKEN}'

    # Получаем данные о курсе монеты
    response = requests.get(url).json()

    # Проверяем, есть ли в ответе данные о курсе монеты
    if 'rate' in response:
        # Получаем данные о курсе монеты
        rate = response['rate']
        time_str = response['time']

        # преобразование времени из формата "2023-04-11T22:04:52.0000000Z" в формат "день.месяц.год часы:минуты"
        time = datetime.strptime(time_str[:-2], '%Y-%m-%dT%H:%M:%S.%f')
        time_str_formatted = time.strftime('%d-%m-%Y %H:%M:%S')

        # Формируем сообщение с курсом
        bot.send_message(message.chat.id, f"⏰ {time_str_formatted}\n"
                                          f"🪙 Crypto Coin: {cripto_currency}\n"
                                          f"💸 Currency: {quote_currency}\n"
                                          f"⚖️ Price: {rate:.4f}\n")
        menu(message)
    else:
        # Если курс не найден, отправляем соответствующее сообщение
        bot.reply_to(message, f'❗️ Requested cryptocurrency not found ❗️')
        get_cripto_coin_name(message)


bot.polling(none_stop=True)
