from commands.commands import *
from utils.similarity import checkSimilar

def find_command(words):    
    actions = { "сверни все окна" : 3,
                "запиши в файл" : 3,
                "создай псевдоним" : 2,
                "сделай скриншот" : 2,
                "создай файл" : 2, 
                "открой браузер" : 2, 
                "найди документ" : 2, 
                "создай напоминание" : 2,
                "напиши" : 1, 
                "найди" : 1}
    # res = [sorted(actions.keys(),key = lambda x: checkSimilar(" ".join(words[:actions[x]]),x))]
    # if res[0] > 0.8:
    #     return res[0],words[actions[res[0]]:]

    best_match = None
    best_score = 0.0

    for action,count in actions.items():
        score = checkSimilar(" ".join(words[:count]), action)
        if score > best_score:
            best_score = score
            best_match = action
    if best_score > 0.8:
        return best_match, words[actions[best_match]:]

    return None, []

commands = {"сверни все окна" : MinimizeAllWindows(),
            "запиши в файл" : WriteToFile(),
            "сделай скриншот" : TakeScreenshot(),
            "создай псевдоним" : CreateAlias(),
            "создай файл" : CreateFile(),
            "открой браузер" : OpenBroser(),
            "найди документ" : FindDocument(),
            "создай напоминание" : CreateReminder(),
            "напиши" : WriteToConsole(),
            "найди" : FindInBrowser()}

def process_command(name, args, execute = True):
    if execute:
        commands[name].execute(args)
    else:
        return