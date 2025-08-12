from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import os

from db import db_sqlite
from gemini_bot_2.secretary import Secretary
import bot.keyboards as kb

API_KEY = os.getenv('GEMINI_API_KEY')
secretary = Secretary(api_key=API_KEY)

router = Router()


@router.message(Command('start'))
async def send_welcome(message: Message):
    db_sqlite.insert_user(message.chat.id, message.from_user.first_name)
    await message.answer(f"Здравстуйте, {message.from_user.first_name}! Давайте познакомимся, я ваша новая секретутка с искусственным интеллектом. Для вашего удобства я создала несколько кнопок быстрого доступа, но они не обязательны. Вы можете общаться со мной как с настоящим человеком, а я самостоятельно пойму какой тип задачи (Создание напоминания, просмотр своих напоминаний) вы мне отправили.\n\nДавайте начнём с выбора вашего временного пояса, чтобы я могла вовремя отправлять вам напоминания!", reply_markup=kb.main)


@router.message(F.text == 'Создать задачу')
async def create_task_command(message: Message, mode):
    if mode == 0:
        await message.answer("Расскажите о задаче, которую хотите создать.")
    elif mode == 1:
        await message.answer("Поняла, создаю задачу...")
        answer = secretary.do_this(message.text, message.chat.id, task = 'create_task')
        if answer:
            await message.answer(answer)
        else:
            await message.answer("Что-то пошло не так, я не смогла создать задачу. Пожалуйста, попробуйте позже или напишите мне подробнее, что вы хотите сделать.")

@router.message(F.text == 'Мои задачи')
async def my_tasks_command(message: Message, mode):
    if mode == 0:
        await message.answer("Вот список ваших задач:")
        pass
    elif mode == 1:
        await message.answer("Поняла, загружаю ваши задачи...")
        answer = secretary.do_this(message.text, message.chat.id, task = 'view_tasks')
        if answer:
            await message.answer(answer)
        else:
            await message.answer("У вас пока нет задач. Вы можете создать новую задачу, нажав на кнопку 'Создать задачу'.")

@router.message(F.text == 'Изменить задачу')
async def edit_task_command(message: Message, mode):
    if mode == 0:
        await message.answer("Какую задачу вы хотите изменить?")
    elif mode == 1:
        await message.answer("Поняла, изменяю задачу...")
        answer = secretary.do_this(message.text, message.chat.id, task = 'edit_task')
        if answer:
            await message.answer(answer)
        else:
            await message.answer("Что-то пошло не так, я не смогла изменить задачу. Пожалуйста, попробуйте позже или напишите мне подробнее, что вы хотите сделать.")

@router.message(F.text == 'Удалить задачу')
async def delete_task_command(message: Message, mode):
    if mode == 0:
        await message.answer("Какую задачу вы хотите удалить?")
    elif mode == 1:
        await message.answer("Поняла, удаляю задачу...")
        answer = secretary.do_this(message.text, message.chat.id, task = 'delete_task')
        if answer:
            await message.answer(answer)
        else:
            await message.answer("Что-то пошло не так, я не смогла удалить задачу. Пожалуйста, попробуйте позже или напишите мне подробнее, что вы хотите сделать.")


@router.message(F.text == 'Выбрать часовой пояс')
async def select_timezone_command(message: Message, mode):
    if mode == 0:
        await message.answer("Пожалуйста, выберите ваш часовой пояс из списка ниже:", reply_markup=kb.timezone_keyboard)
    elif mode == 1:
        await message.answer("Поняла, настраиваю часовой пояс...")
        answer = secretary.do_this(message.text, message.chat.id, task = 'select_timezone')
        if answer:
            await message.answer(answer)
        else:
            await message.answer("Что-то пошло не так, я не смогла настроить часовой пояс. Пожалуйста, попробуйте позже или напишите мне подробнее, что вы хотите сделать.")

@router.message(F.text == 'Помощь')
async def help_command(message: Message):
    await message.answer("Вот список доступных команд:\n"
                         "/start - Начать работу с ботом\n"
                         "Создать задачу - Создать новую задачу\n"
                         "Мои задачи - Просмотреть свои задачи\n"
                         "Изменить задачу - Изменить существующую задачу\n"
                         "Удалить задачу - Удалить задачу\n"
                         "Выбрать часовой пояс - Настроить часовой пояс\n"
                         "Помощь - Получить помощь по командам")

@router.message(F.text)
async def unknown_command(message: Message):
    await message.answer("Минутку!")
    action = secretary.analyze_message(message.text, message.chat.id)
    if action == 'create_task':
        await create_task_command(message, mode=1)
    elif action == 'view_tasks':
        await my_tasks_command(message, mode=1)
    elif action == 'edit_task':
        await edit_task_command(message, mode=1)
    elif action == 'delete_task':
        await delete_task_command(message, mode=1)
    elif action == 'select_timezone':
        await select_timezone_command(message, mode=1)
    elif action == 'help':
        await help_command(message)
    elif action == 'a_lot_of_tasks':
        await message.answer("Напишите только одну задачу за раз, пожалуйста. Я не могу обработать сразу несколько задач.")
    else:
        await message.answer("Обшибка")
