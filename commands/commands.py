from multiprocessing import Process
import os
import time
import webbrowser
import pyautogui

from commands.base import Command

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
                with open(args[0] + '.txt','w'):
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
            if os.path.isfile(args[0] + '.txt'):
                with open(args[0] + '.txt','a') as f:
                    f.write(" ".join(args[1:]))
            else:
                with open(args[0] + '.txt','w'):
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

class FindDocument(Command):
    def execute(self,args):
        pass