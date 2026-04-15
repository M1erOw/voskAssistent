from commands.commands import *
from commands.info import Info
from utils.similarity import checkSimilar

def find_command(words):    
    best_match = None
    best_score = 0.0

    for com in commands:
        score = checkSimilar(" ".join(words[:(com.count(" ") + 1)]),com)
        if score > best_score:
            best_score = score
            best_match = com
    if best_score > 0.8:
        return best_match, words[(best_match.count(" ") + 1):]
    return None, []

commands = {"сверни все окна" : MinimizeAllWindows(),
            "запиши в файл" : WriteToFile(),
            "сделай скриншот" : TakeScreenshot(),
            "создай псевдоним" : CreateAlias(),
            "создай файл" : CreateFile(),
            "сделай громче" : VolumeUp(),
            "сделай тише" : VolumeDown(),
            "установи громкость" : SetVolume(),
            "включи звук" : Unmute(),
            "выключи звук" : Mute(),
            "запусти приложение" : StartApp(),
            "останови приложение" : StopApp(),
            "найди файл" : Find(),
            "покажи погоду" : ShowWeather(),
            "открой браузер" : OpenBroser(),
            "создай напоминание" : CreateReminder(),
            "запусти" : Run(),
            "напиши" : WriteToConsole(),
            "найди" : FindInBrowser(),
            "справка" : Info()
            }

def process_command(name, args, execute = True):
    if execute:
        commands[name].execute(args)
    else:
        return