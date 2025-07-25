import telebot
from telebot import types
import datetime
import pytz
from db import db_sqlite

bot = telebot.TeleBot('8007211189:AAHJ0Ae9QufEAgZOlvTdycMjwSzhqLs5rTw')

time = 0

@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Выбрать временной пояс', callback_data='choose_timezone'))

    db_sqlite.insert_user(message.chat.id, message.from_user.first_name)

    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Давайте начнём наше общение с настройки. Укажите свой временной пояс, для того, чтобы я могла ориентироваться в вашем списке дел!', reply_markup=markup)

@bot.message_handler(commands=['create_task'])
def create_task(message):
    bot.send_message(message.chat.id, "Введите название задачи:")
    bot.register_next_step_handler(message, process_task_title)
def process_task_title(message):
    title = message.text
    bot.send_message(message.chat.id, "Введите описание задачи:")
    bot.register_next_step_handler(message, process_task_description, title)
def process_task_description(message, title):
    description = message.text
    bot.send_message(message.chat.id, "Введите дату выполнения задачи (в формате ГГГГ-ММ-ДД):")
    bot.register_next_step_handler(message, process_task_due_date, title, description)
def process_task_due_date(message, title, description):
    due_date_str = message.text
    try:
        due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
        bot.send_message(message.chat.id, "Задача создана!")
        db_sqlite.insert_task(message.chat.id, title, description, due_date) 
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.") 

@bot.message_handler(commands=['user_info'])
def main(message):
    bot.send_message(message.chat.id, message)

@bot.message_handler()
def info(message):
    global time
    if message.text.lower() == 'время':
        now = datetime.datetime.now()
        time = now.strftime('%H:%M:%S')
        bot.reply_to(message, f'Текущее время: {time}')
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'Ваш ID: {message.from_user.id}')
    # Дополнительные команды можно добавить здесь
    else:
        bot.reply_to(message, "Я не понимаю эту команду")
#     if message.text.lower() == 'id':
#         bot.reply_to(message, f'ID = {message.from_user.id}')
#     elif message.text.lower() == 'время':
#         bot.reply_to(message, f'время = {time}')

@bot.callback_query_handler(func=lambda call: call.data == 'choose_timezone')
def callback_timezone(call):
    markup = types.InlineKeyboardMarkup()

    btn01 = types.InlineKeyboardButton('-11:00', callback_data='tz_-11:00')
    btn02 = types.InlineKeyboardButton('-10:00', callback_data='tz_-10:00')
    btn03 = types.InlineKeyboardButton('-9:30', callback_data='tz_-9:30')
    btn04 = types.InlineKeyboardButton('-9:00', callback_data='tz_-9:00')
    
    markup.row(btn01, btn02, btn03, btn04)

    btn11 = types.InlineKeyboardButton('-8:00', callback_data='tz_-8:00')
    btn12 = types.InlineKeyboardButton('-7:00', callback_data='tz_-7:00')
    btn13 = types.InlineKeyboardButton('-6:00', callback_data='tz_-6:00')
    btn14 = types.InlineKeyboardButton('-5:00', callback_data='tz_-5:00')

    markup.row(btn11, btn12, btn13, btn14)
    
    btn21 = types.InlineKeyboardButton('-4:00', callback_data='tz_-4:00')
    btn22 = types.InlineKeyboardButton('-3:30', callback_data='tz_-3:30')
    btn23 = types.InlineKeyboardButton('-3:00', callback_data='tz_-3:00')
    btn24 = types.InlineKeyboardButton('-2:00', callback_data='tz_-2:00')

    markup.row(btn21, btn22, btn23, btn24)
    
    btn31 = types.InlineKeyboardButton('-1:00', callback_data='tz_-1:00')
    btn32 = types.InlineKeyboardButton('+0:00', callback_data='tz_+0:00')
    btn33 = types.InlineKeyboardButton('+1:00', callback_data='tz_+1:00')
    btn34 = types.InlineKeyboardButton('+2:00', callback_data='tz_+2:00')

    markup.row(btn31, btn32, btn33, btn34)
    
    btn41 = types.InlineKeyboardButton('+3:00', callback_data='tz_+3:00')
    btn42 = types.InlineKeyboardButton('+3:30', callback_data='tz_+3:30')
    btn43 = types.InlineKeyboardButton('+4:00', callback_data='tz_+4:00')
    btn44 = types.InlineKeyboardButton('+4:30', callback_data='tz_+4:30')

    markup.row(btn41, btn42, btn43, btn44)

    btn51 = types.InlineKeyboardButton('+5:00', callback_data='tz_+5:00')
    btn52 = types.InlineKeyboardButton('+5:30', callback_data='tz_+5:30')
    btn53 = types.InlineKeyboardButton('+5:45', callback_data='tz_+5:45')
    btn54 = types.InlineKeyboardButton('+6:00', callback_data='tz_+6:00')

    markup.row(btn51, btn52, btn53, btn54)

    btn61 = types.InlineKeyboardButton('+6:30', callback_data='tz_+6:30')
    btn62 = types.InlineKeyboardButton('+7:00', callback_data='tz_+7:00')
    btn63 = types.InlineKeyboardButton('+8:00', callback_data='tz_+8:00')
    btn64 = types.InlineKeyboardButton('+8:45', callback_data='tz_+8:45')

    markup.row(btn61, btn62, btn63, btn64)

    btn71 = types.InlineKeyboardButton('+9:00', callback_data='tz_+9:00')
    btn72 = types.InlineKeyboardButton('+9:30', callback_data='tz_+9:30')
    btn73 = types.InlineKeyboardButton('+10:00', callback_data='tz_+10:00')
    btn74 = types.InlineKeyboardButton('+10:30', callback_data='tz_+10:30')

    markup.row(btn71, btn72, btn73, btn74)

    btn81 = types.InlineKeyboardButton('+11:00', callback_data='tz_+11:00')
    btn82 = types.InlineKeyboardButton('+12:00', callback_data='tz_+12:00')
    btn83 = types.InlineKeyboardButton('+13:00', callback_data='tz_+13:00')
    btn84 = types.InlineKeyboardButton('+14:00', callback_data='tz_+14:00')

    markup.row(btn81, btn82, btn83, btn84)

    bot.send_message(call.message.chat.id, f'Выберете свой часовой пояс. (Например, Москва находится на UTC +3:00)', reply_markup=markup)

@bot.callback_query_handler(lambda call: call.data.startswith('tz_'))
def send_timezone_info(call: types.CallbackQuery):
    timezone_str = call.data.split('_')[1]
    
    # Разбираем строку часового пояса на часы и минуты
    try:
        # Убираем знак и разделяем часы и минуты
        sign = 1 if timezone_str.startswith('+') else -1
        # Заменяем '+' и '-' на пустую строку, чтобы оставить только 'ЧЧ:ММ'
        parts = timezone_str.replace('+', '').replace('-', '').split(':')
        
        hours = int(parts[0])
        minutes = int(parts[1])
        
        # Создаем смещение (timedelta) на основе полученных значений
        offset = datetime.timedelta(hours=hours * sign, minutes=minutes * sign)
        
        # Получаем текущее UTC-время и применяем смещение
        now_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        now_with_offset = now_utc + offset
        
        bot.send_message(call.message.chat.id, f"Текущее время в выбранном часовом поясе ({timezone_str}):\n{now_with_offset.strftime('%H:%M:%S')}")
        bot.answer_callback_query(call.id)
    
    except (ValueError, IndexError):
        # Если что-то пошло не так при разборе строки
        bot.send_message(call.message.chat.id, "Не удалось определить часовой пояс. Попробуйте еще раз.")
        bot.answer_callback_query(call.id)

bot.infinity_polling()