from utils.similarity import checkSimilar

def find_command(words):    
    actions = { "сверни все окна" : 3,
                "запиши в файл" : 3,
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