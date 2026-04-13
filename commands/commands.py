from datetime import datetime
import glob
import json
from multiprocessing import Process
import os
import subprocess
import time
import webbrowser
import pyautogui
from pycaw.pycaw import AudioUtilities

from commands.base import Command
from widgets.dialog import CustomDialog

class MinimizeAllWindows(Command):
    def __init__(self):
        name = "сверни все окна"
        args = "-"
        description = "Отображение/скрытие рабочего стола"
        super().__init__(name, args, description)

    def execute(self,args):
        pyautogui.hotkey('win','d')

class TakeScreenshot(Command):
    def __init__(self):
        name = "сделай скриншот"
        args = "-"
        description = "Создание скриншота с именем \"screenshot[дата,время].png\""
        super().__init__(name, args, description)

    def execute(self,args):
        screenshot = pyautogui.screenshot()
        screenshot.save(f"screenshot{datetime.now().strftime("%Y-%m-%d,%H:%M:%S")}.png")

class CreateFile(Command):
    def __init__(self):
        name = "создай файл"
        args = "создай файл [имя_файла]"
        description = "Создание файла [имя_файла].txt\""
        super().__init__(name, args, description)

    def execute(self,args):
        if args:
            if os.path.isfile(args[0] + '.txt'):
                print("Файл уже существует")
            else:
                with open(args[0] + '.txt','w',encoding='utf-8'):
                    pass

class OpenBroser(Command):
    def __init__(self):
        name = "открой браузер"
        args = "-"
        description = "Открытие новой вкладки в браузере по умолчанию"
        super().__init__(name, args, description)

    def execute(self,args):
        webbrowser.open("https://www.google.com/", new=2)

class FindInBrowser(Command):
    def __init__(self):
        name = "найди"
        args = "найди [запрос]"
        description = "Отрпавка запроса в браузер"
        super().__init__(name, args, description)

    def execute(self,args):
        webbrowser.open("https://www.google.com/search?q=" + " ".join(args), new=2)

class WriteToConsole(Command):
    def __init__(self):
        name = "напиши"
        args = "напиши [текст]"
        description = "Написать продиктованный текст в консоль"
        super().__init__(name, args, description)

    def execute(self,args):
        print(" ".join(args))

class WriteToFile(Command):
    def __init__(self):
        name = "запиши в файл"
        args = "запиши в файл [псевдоним_файла] [текст]"
        description = "Поиск файла по псевдониму и запись текста в его конец(если файл с таким именем не существует, он будет создан)"
        super().__init__(name, args, description)

    def execute(self,args):
        if args:
            with open('data.json','r', encoding = "utf-8") as file:
                data = json.load(file)
                name = args[0]
                if name in data:
                    if os.path.isfile(data[name]):
                        with open(data[name],'a',encoding='utf-8') as f:
                            f.write(" ".join(args[1:]))
                    else:
                        with open(data[name],'w',encoding='utf-8') as f:
                            f.write(" ".join(args[1:]))

mapping = {'ноль': 0, 'один': 1, 'два': 2, 'три': 3, 'четыре': 4, 'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10, 'одиннадцать': 11,
               'двенадцать': 12, 'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15, 'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19,
               'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50, 'шестьдесят': 60, 'семьдесят': 70, 'восемьдесят': 80, 'девяносто': 90 ,'сто': 100}

def createReminder(timeAndText):
    vremes = 0
    for i, word in enumerate(timeAndText):
        if word in mapping:
            vremes += mapping[word]
        else:
            break
    text = timeAndText[i:]
    time.sleep(vremes)
    pyautogui.alert(text=" ".join(text), title='Reminder', button='OK')

class CreateReminder(Command):
    def __init__(self):
        name = "создай напоминание"
        args = "создай напоминание [время_в_минутах] [текст_напоминания]"
        description = "Вывод окна с текстом напоминания через указанное кол-во времени"
        super().__init__(name, args, description)

    def execute(self,args):
        proc = Process(target=createReminder,args=(args,))
        proc.start()

class CreateAlias(Command):
    def __init__(self):
        name = "создай псевдоним"
        args = "-"
        description = "Вызов диалогового окна для добавления записи в формате \"псевдоним\" : \"имя\""
        super().__init__(name, args, description)

    def execute(self,args):
        dialog = CustomDialog()
        dialog.exec()

class ShowWeather(Command):
    def __init__(self):
        name = "покажи погоду"
        args = "-"
        description = "Открытие в браузере сайта с погодой"
        super().__init__(name, args, description)

    def execute(self,args):
        webbrowser.open("https://www.gismeteo.by/", new=2)
    
class StartApp(Command):
    def __init__(self):
        name = "запусти приложение"
        args = "запусти приложение [псевдоним]"
        description = "Поиск исполняемого файла по его псевдониму и его запуск"
        super().__init__(name, args, description)

    def execute(self,args):
        if args:
            with open('data.json','r', encoding = "utf-8") as file:
                data = json.load(file)
                name = args[0]
                if name in data:
                    subprocess.Popen([data[name]])

class StopApp(Command):
    def __init__(self):
        name = "останови приложение"
        args = "останови приложение [псевдоним]"
        description = "Поиск программы по псевдониму и ее завершение"
        super().__init__(name, args, description)

    def execute(self,args):
        if args:
            with open('data.json','r', encoding = "utf-8") as file:
                data = json.load(file)
                name = args[0]
                if name in data:
                    os.system("taskkill /im " + '"' + data[name].split("/")[-1] + '"')

class SetVolume(Command):
    def __init__(self):
        name = "установи громкость"
        args = "установи громкость [значение]"
        description = "Изменяет громкость на указанную"
        super().__init__(name, args, description)
    
    def execute(self,args):
        loudness = 0
        for i, word in enumerate(args):
            if word in mapping:
                loudness += mapping[word]
            else:
                break
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        volume.SetMasterVolumeLevelScalar(loudness / 100.0, None)

class VolumeUp(Command):
    def __init__(self):
        name = "сделай громче"
        args = "-"
        description = "Увеличение громкости на 10 едениц"
        super().__init__(name, args, description)

    def execute(self,args):
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(1.0, current_volume + 0.1), None)
        
class VolumeDown(Command):
    def __init__(self):
        name = "сделай тише"
        args = "-"
        description = "Уменьшение громкости на 10 едениц"
        super().__init__(name, args, description)
    
    def execute(self,args):
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(max(0.0, current_volume - 0.1), None)

class Mute(Command):
    def __init__(self):
        name = "выключи звук"
        args = "-"
        description = "Отключение звука"
        super().__init__(name, args, description)
    
    def execute(self,args):
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        if volume.GetMute():
            print("Already muted")
        else:
            volume.SetMute(1,None)

class Unmute(Command):
    def __init__(self):
        name = "включи звук"
        args = "-"
        description = "Включение звука"
        super().__init__(name, args, description)
    
    def execute(self,args):
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        if not volume.GetMute():
            print("Already unmuted")
        else:
            volume.SetMute(0,None)

class Run(Command):
    def __init__(self):
        name = "запусти"
        args = "запусти [псевдоним]"
        description = "Открытие ссылки в браузере по ее псевдониму"
        super().__init__(name, args, description)
    
    def execute(self,args):
        if args:
            with open('data.json','r', encoding = "utf-8") as file:
                data = json.load(file)
                name = args[0]
                if name in data:
                    webbrowser.open(data[name], new=2)

class Find(Command):
    def __init__(self):
        name = "найди файл"
        args = "найди файл [псевдоним]"
        description = "Поиск файла во всех каталогах"
        super().__init__(name, args, description)
    
    def execute(self,args):
        if args:
            with open('data.json','r', encoding = "utf-8") as file:
                data = json.load(file)
                name = args[0]
                if name in data:
                    for drive in os.listdrives():
                        files = glob.glob(f'{drive}**\\{data[name]}', recursive=True)
                        for file in files:
                            print(file)