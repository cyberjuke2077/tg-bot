import os 
import time 
import datetime
import pytz 

import requests 
# pip install requests

# pip install python-dotenv
from dotenv import load_dotenv

#pip install python-telegram-bot==13.7
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters

import random 

load_dotenv()
ТОКЕН = os.getenv("токен")

бот = Bot(ТОКЕН)
этот_файл = __file__
эта_папка = os.path.dirname(этот_файл) # функция позволяет узнать родительскую папку

def считать_последний_id():
    if not os.path.exists(f'{эта_папка}\\last_id'):
        return 0 
    with open(f'{эта_папка}\\last_id', 'r', encoding='utf-8') as file:
        return int(file.read())

def проверить_входящие(айди=None):
    if not os.path.exists(f'{эта_папка}\\last_id'):
        while True:
            try:
                обновления = бот.get_updates()
                break
            except:
                continue
        with open(f'{эта_папка}\\last_id', 'w', encoding='utf-8') as file:
            file.write(str(обновления[-1].update_id))    


    сейчас = datetime.datetime.now(pytz.UTC) # важно указать в скобках now временную зону, которую мы берем из модуля pytz
    while True:
        try:
            обновления = бот.get_updates(offset=считать_последний_id() + 1) # аргумент offset позволяет получать только те обновления, которые пришли позже указанного update id. Если его не указать, мы получим слишком большой список обновлений.
        except:
            time.sleep(1) #ждать одну секунду
            continue
        if len(обновления) == 0:
            time.sleep(1)
            continue

        последнее_сообщение = обновления[-1]
        if последнее_сообщение.message.date < сейчас:
            continue
        обновления.reverse()
        for сообщение in обновления:
            if сообщение.message.date < сейчас:
                continue
        # если айди не было передано, значит возвращаем последнее сообщение
            if айди == None:
                with open(f'{эта_папка}\\last_id', 'w', encoding='utf-8') as file:
                    file.write(str(сообщение.update_id))
                return сообщение  

        # проверяем айди и сравниваем его с тем который пришел с сообщением
            отправитель = сообщение.message.chat_id
            if айди == отправитель:
                with open(f'{эта_папка}\\last_id', 'w', encoding='utf-8') as file:
                    file.write(str(сообщение.update_id))
                return сообщение


def отправить_информацию(айди, сообщение, кнопки):
    бот.send_message(chat_id=айди, text=сообщение, reply_markup=кнопки)


def кнб(айди, имя):
    стандартные_кнопки = ReplyKeyboardMarkup([["Камень, Ножницы, Бумага"]], resize_keyboard=True)
    игровые_кнопки = ReplyKeyboardMarkup([
        ["🧱", "✂", "📃",],
        ["Сброс", "Выход"]
    ], resize_keyboard=True)

    class Игрок:
        def __init__(self, имя):
            self.имя = имя
            self.счет = 0
            self.ход = ""
    правила = f"""Игра "Камень, ножницы, бумага!"
Чтобы сделать ход, выберите один из вариантов: 🧱, ✂, или 📃

Компьютер в это время тоже сделает свой ход и напишет результат. Будет считаться накопительный счёт.

Можно сбросить счёт или выйти из игры."""
    
    отправить_информацию(айди, правила, игровые_кнопки )

    юзер = Игрок(имя)
    комп = Игрок("Печка лютая")
    
    ДОПУСТИМЫЕ_КОМАНДЫ = ['к','н','б','с','в']

    ВАРИАНТЫ_ПОБЕДЫ = {
        'кн': юзер,
        'кб': комп,
        'нб': юзер,
        'нк': комп,
        'бк': юзер,
        'бн': комп,
    }

    СЛОВАРЬ_ЗНАЧЕНИЙ = {
        "к": "Камень",
        "н": "Ножницы",
        "б": "Бумага"
    }

    def выход():
        if комп.счет > юзер.счет:
            победитель = комп
            проигравший = юзер
        else:
            победитель = юзер
            проигравший = комп

        if комп.счет == юзер.счет:
            отправить_информацию(айди, "Ничья!", стандартные_кнопки)
        else:
            отправить_информацию(айди, f"Победил {победитель.имя} со счётом {победитель.счет}/{проигравший.счет}", стандартные_кнопки)

    while True:
        if комп.счет == 2 or юзер.счет == 2:
            выход()
            return
        команда = проверить_входящие(айди).effective_message.text.lower()
        команда = команда.replace("🧱", "к")
        команда = команда.replace("✂", "н")
        команда = команда.replace("📃", "б")
        команда = команда.replace("сброс", "с")
        команда = команда.replace("выход", "в")
        if команда not in ДОПУСТИМЫЕ_КОМАНДЫ:
            отправить_информацию(айди, "Команда не распознана, нормально общайся", игровые_кнопки)
            continue 
        if команда == "в":
            выход()
            return
        if команда == "с":
            комп.счет = 0
            юзер.счет = 0
            отправить_информацию(айди, "Счет сброшен", игровые_кнопки)  
            continue
        юзер.ход = команда
        комп.ход = ['к','н','б'][random.randint(0,2)]

        if юзер.ход == комп.ход:
            ход = СЛОВАРЬ_ЗНАЧЕНИЙ.get(юзер.ход)
            отправить_информацию(айди, f"{ход}/{ход} - Ничья!", игровые_кнопки)
            continue
        победитель = ВАРИАНТЫ_ПОБЕДЫ.get(юзер.ход + комп.ход)
        победитель.счет += 1
        отправить_информацию(айди, f"{СЛОВАРЬ_ЗНАЧЕНИЙ.get(юзер.ход)}/{СЛОВАРЬ_ЗНАЧЕНИЙ.get(комп.ход)} - победил {победитель.имя}. Счёт {юзер.счет}/{комп.счет}", игровые_кнопки)


#айди = 813531325
#бот.send_message(chat_id=айди, text = "я тупая корова, привет! мууу!") 

def запарсить_погоду(город):
    ссылка = "https://google.ru/search"
    параметры = {'q': f'погода в городе {город} в градусах Цельсия', 'hl': 'ru'} 
    ответ_сайта = requests.get(ссылка, параметры)
    if ответ_сайта.status_code != 200:
        return 'Сайт недоступен'
    текст = ответ_сайта.text

    старт = текст.find("BNeawe tAd8D AP7Wnd")
    if старт == -1:
        return 'город не распознан'
    старт = текст.find(">", старт)
    старт += 1 
    стоп = текст.find("<", старт)
    город = текст[старт:стоп]

    старт = текст.find("°C", старт)
    if старт == -1:
        return '°C не найдены'
    старт -= 15
    старт = текст.find(">", старт)
    старт += 1
    стоп = текст.find("<", старт)
    градусы = текст[старт:стоп]

    старт = текст.find("BNeawe tAd8D AP7Wnd", старт)
    if старт == -1:
        return 'второй блок не найден'
    старт = текст.find("\n", старт)
    старт += 1
    стоп = текст.find("<", старт)
    состояние_погоды = текст[старт:стоп].lower()
    return f'В {город} сейчас {градусы}, {состояние_погоды}'

def отправить_сообщение(айди, текст):
    бот.send_message(chat_id=айди, text = текст) 

def этот_айди(информация):
    return информация.effective_message.chat_id

def это_имя(информация):
    return информация.effective_message.chat.first_name

def это_сообщение(информация):
    if информация.message.text:
        return информация.effective_message.text


def запустить_бота():
    стандартные_кнопки = ReplyKeyboardMarkup([["Камень, Ножницы, Бумага"]], resize_keyboard=True) # внутри ReplyKeyboardMarkup передаем список всех кнопок. Внутри него будет один или несколько списков - один вложенный список одна строка. Кнопки нужно отправить вместе с сообщением. resize_keyboard=True делает кнопки маленькими.
    while True:
        сообщение = проверить_входящие()
        
        айди_пользователя = этот_айди(сообщение)
        имя_пользователя = это_имя(сообщение)
        if это_сообщение(сообщение) in ["старт", "start", "/start"]:
            отправить_информацию(айди_пользователя, f"Привет, {имя_пользователя}", стандартные_кнопки)
        elif это_сообщение(сообщение) == "Камень, Ножницы, Бумага":
            кнб(айди_пользователя, имя_пользователя )
        else:
            запарсить_погоду(это_сообщение(сообщение))

запустить_бота()