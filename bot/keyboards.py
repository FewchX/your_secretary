from aiogram.types import (InlineKeyboardMarkup, 
                           InlineKeyboardButton, 
                           ReplyKeyboardMarkup, 
                           KeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Создать задачу')],
                                    [KeyboardButton(text='Просмотреть мои задачи')],
                                    [KeyboardButton(text='Изменить задачу')],
                                    [KeyboardButton(text='Удалить задачу')],
                                    [KeyboardButton(text='Настройки напоминаний')],
                                    [KeyboardButton(text='Выбрать часовой пояс')]],
                                    resize_keyboard=True,
                                    input_field_placeholder="Выберите действие")