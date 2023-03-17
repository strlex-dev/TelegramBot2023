import requests
import telebot
import datetime
from telebot import types
from datetime import datetime

TG_TOKEN = '6083614335:AAGQC665fJ929K5uhIyUGO3e6dwIcYe-23Y'
bot = telebot.TeleBot(TG_TOKEN)

API_POSITION = "http://api.open-notify.org/iss-now.json"
API_ASTRO = "http://api.open-notify.org/astros.json"

WEATHER_TOKEN = "f564a6066176291403f48b3ea6d04bd7"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Welcome to ISS command center!')
    menu(message)

@bot.message_handler(commands=['menu'])
def menu(message):
    menu_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)

    button_iss_position = types.KeyboardButton("🛰")
    button_astros = types.KeyboardButton("👨‍🚀")
    button_weather = types.KeyboardButton("🌦")
    button_restart_bot = types.KeyboardButton("🔄")

    menu_buttons.add(button_iss_position, button_astros, button_weather, button_restart_bot)

    bot.send_message(message.chat.id, 'Choose option ⬇️', reply_markup=menu_buttons)

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.text == "🛰":
        bot.send_message(message.chat.id, mks_position(message))
    if message.text == "👨‍🚀":
        bot.send_message(message.chat.id, mks_squad(message))
    if message.text == "🌦":
        bot.send_message(message.chat.id, get_agreement(message))
    if message.text == "🔄":
        bot.send_message(message.chat.id, menu(message))

@bot.message_handler(commands=['mksPosition'])
def mks_position(message):
    request = requests.get(url=API_POSITION)
    response = request.json()

    timestamp = response['timestamp']
    cur_time = (datetime.utcfromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S'))

    bot.send_message(message.chat.id, f"Longitude: {response['iss_position']['longitude']},\n"
                                      f"Latitude: {response['iss_position']['latitude']},\n"
                                      f"Online time: {cur_time}")

    bot.send_location(message.chat.id, longitude={response['iss_position']['longitude']}, latitude={response['iss_position']['latitude']})

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

    request_yes = types.KeyboardButton("✅")
    request_no = types.KeyboardButton("⛔️")

    message_buttons.add(request_yes, request_no)

    message_from_bot = bot.send_message(message.chat.id, "Do you request weather information?", reply_markup=message_buttons)
    bot.register_next_step_handler(message_from_bot, say_yes_no)

def say_yes_no(message):
    if message.text == "✅":
        message_from_bot = bot.send_message(message.chat.id, "🏢 Write the name of сity ➡️")
        bot.register_next_step_handler(message_from_bot, get_weather)
    elif message.text == "⛔️":
        bot.send_message(message.chat.id, "Process finished!")
        menu(message)

def get_weather(message):
    city = message.text

    request = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_TOKEN}&units=metric"
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

bot.polling(none_stop=True)