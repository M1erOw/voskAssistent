import os
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

class CreateReminder(Command):
    def execute(self,args):
        pass

class FindDocument(Command):
    def execute(self,args):
        pass