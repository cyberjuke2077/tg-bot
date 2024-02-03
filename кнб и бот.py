import os 
import time 

import requests 
# pip install requests

# pip install python-dotenv
from dotenv import load_dotenv

#pip install python-telegram-bot==13.7
from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters

import random 

load_dotenv()
ТОКЕН = os.getenv("токен")

бот = Bot(ТОКЕН)

def проверить_входящие(айди=None):
    while True:
        try:
            обновления = бот.get_updates()
        except:
            time.sleep(1) #ждать одну секунду
            continue
        if len(обновления) == 0:
            time.sleep(1)
            continue

        последнее_сообщение = обновления[-1]
        # если айди не было передано, значит возвращаем последнее сообщение
        if айди == None:
            return последнее_сообщение  

        # проверяем айди и сравниваем его с тем который пришел с сообщением
        отправитель = последнее_сообщение.message.chat_id
        if айди == отправитель:
            return последнее_сообщение


def запросить_информацию(сообщение):
    ответ_пользователя = input(сообщение)
    return ответ_пользователя

def отправить_информацию(сообщение):
    print(сообщение)

def кнб():
    class Игрок:
        def __init__(self, имя):
            self.имя = имя
            self.счет = 0
            self.ход = ""

    юзер = Игрок(запросить_информацию("Введите своё имя: "))
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
            отправить_информацию("Ничья!")
        else:
            отправить_информацию(f"Победил {победитель.имя} со счётом {победитель.счет}/{проигравший.счет}")

    while True:
        if комп.счет == 2 or юзер.счет == 2:
            выход()
            return
        команда = запросить_информацию("Введите команду: ").lower()
        if команда not in ДОПУСТИМЫЕ_КОМАНДЫ:
            continue 
        if команда == "в":
            выход()
            return
        if команда == "с":
            комп.счет = 0
            юзер.счет = 0
            отправить_информацию("Счет сброшен")  
            continue
        юзер.ход = команда
        комп.ход = ['к','н','б'][random.randint(0,2)]

        if юзер.ход == комп.ход:
            ход = СЛОВАРЬ_ЗНАЧЕНИЙ.get(юзер.ход)
            отправить_информацию(f"{ход}/{ход} - Ничья!")
            continue
        победитель = ВАРИАНТЫ_ПОБЕДЫ.get(юзер.ход + комп.ход)
        победитель.счет += 1
        отправить_информацию(f"{СЛОВАРЬ_ЗНАЧЕНИЙ.get(юзер.ход)}/{СЛОВАРЬ_ЗНАЧЕНИЙ.get(комп.ход)} - победил {победитель.имя}. Счёт {юзер.счет}/{комп.счет}")


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

def запустить_бота():
    проверить_входящие(813531325)
    

запустить_бота()