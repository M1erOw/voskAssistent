import json
from multiprocessing import Process
import os
import subprocess
import time
import webbrowser
import pyautogui
from pycaw.pycaw import AudioUtilities


from commands.base import Command
from widget.dialog import CustomDialog

class MinimizeAllWindows(Command):
    def execute(self,args):
        pyautogui.hotkey('win','d')

class TakeScreenshot(Command):
    def execute(self,args):
        screenshot = pyautogui.screenshot()
        screenshot.save('screenshot.png')

class CreateFile(Command):
    def execute(self,args):
        if args:
            if os.path.isfile(args[0] + '.txt'):
                print("Файл уже существует")
            else:
                with open(args[0] + '.txt','w',encoding='utf-8'):
                    pass

class OpenBroser(Command):
    def execute(self,args):
        webbrowser.open("https://www.google.com/", new=2)

class FindInBrowser(Command):
    def execute(self,args):
        webbrowser.open("https://www.google.com/search?q=" + " ".join(args), new=2)

class WriteToConsole(Command):
    def execute(self,args):
        print(" ".join(args))

class WriteToFile(Command):
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

mapping = {'один': 1, 'два': 2, 'три': 3, 'четыре': 4, 'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10, 'одиннадцать': 11,
               'двенадцать': 12, 'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15, 'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19,
               'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50, 'шестьдесят': 60, 'семдесят': 70, 'восемдесят': 80, 'девяносто': 90 ,'сто': 100}

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
    def execute(self,args):
        proc = Process(target=createReminder,args=(args,))
        proc.start()

class CreateAlias(Command):
    def execute(self,args):
        dialog = CustomDialog()
        dialog.exec()

class ShowWeather(Command):
    def execute(self,args):
        webbrowser.open("https://www.gismeteo.by/", new=2)
    
class StartApp(Command):
    def execute(self,args):
        if args:
            with open('data.json','r', encoding = "utf-8") as file:
                data = json.load(file)
                name = args[0]
                if name in data:
                    subprocess.Popen([data[name]])

class StopApp(Command):
    def execute(self,args):
        if args:
            with open('data.json','r', encoding = "utf-8") as file:
                data = json.load(file)
                name = args[0]
                if name in data:
                    os.system("taskkill /im " + '"' + data[name].split("/")[-1] + '"')

class SetVolume(Command):
    def execute(self,args):
        loudness = 0
        for i, word in enumerate(args):
            if word in mapping:
                loudness += mapping[word]
            else:
                break
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        volume.SetMasterVolumeLevelScalar(loudness / 100, None)

class VolumeUp(Command):
    def execute(self,args):
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(1.0, current_volume + 0.1), None)
        
class VolumeDown(Command):
    def execute(self,args):
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(max(0.0, current_volume - 0.1), None)

class Mute(Command):
    def execute(self,args):
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        if volume.getMute():
            print("Already muted")
        else:
            volume.setMute(1,None)

class Unmute(Command):
    def execute(self,args):
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        if not volume.getMute():
            print("Already unmuted")
        else:
            volume.setMute(0,None)

class FindDocument(Command):
    def execute(self,args):
        pass