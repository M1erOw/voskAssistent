#!/usr/bin/env python3

import argparse
from multiprocessing import Process
import queue
import sys
import json
import time
import pyautogui
import sounddevice as sd
import webbrowser
from vosk import Model, KaldiRecognizer, SetLogLevel

q = queue.Queue()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def checkSimilar(action,template):
    S = (1 << len(action)) - 1
    block = {}
    block_get = block.get
    x = 1
    for ch1 in action:
        block[ch1] = block_get(ch1, 0) | x
        x <<= 1

    for ch2 in template:
        Matches = block_get(ch2, 0)
        u = S & Matches
        S = (S + u) | (S - u)

    res = bin(S)[-len(action) :].count("0")
    maximum = len(action) + len(template)
    dist = maximum - 2 * res
    norm_dist = dist / maximum if maximum else 0
    norm_sim = 1.0 - norm_dist
    return norm_sim

def findMostSimilar(words):
    actions = { 3 : ["сверни все окна", "запиши в файл"],
                2 : ["сделай скриншот", "создай файл", "открой браузер", "найди документ", "создай напоминание"],
                1 : ["напиши", "найди"]}
    for numWords in actions:
        for action in actions[numWords]:
            if checkSimilar(" ".join(words[:numWords]),action) > 0.8:
                return action
    return None

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
    pyautogui.alert(text=text, title='Reminder', button='OK')

def processCommand(words):
    if (not words):
        # wake()           # показ окна с текстом + функциями
        return

    match findMostSimilar(words[:3]):
        case "сверни все окна":
            pyautogui.hotkey('win', 'd')
        # case "запиши в файл":
        #     if len(words) > 3:
        #         with open(words[3] + '.txt','w') as file:
        #             file.write(" ".join(words[4:]))
        case "сделай скриншот":
            screenshot = pyautogui.screenshot()
            screenshot.save('screenshot.png')
        case "создай файл":
            if len(words) > 2:
                with open(words[2] + '.txt','w'):
                    pass
        case "открой браузер":
            webbrowser.open("https://www.google.com/", new=2)
        # case "найди документ":
        #     pass
        # case "создай напоминание":
        #     proc = Process(target=createReminder,args=(words[2:],))
        #     proc.start()
        case "напиши":
            print(" ".join(words[1:]))
        case "найди":
            webbrowser.open("https://www.google.com/search?q=" + " ".join(words[1:]), new=2)
        case _:
            print("Неизвестная команда")

if __name__ == '__main__':
    SetLogLevel(-1)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-l", "--list-devices", action="store_true",
        help="show list of audio devices and exit")
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    parser.add_argument(
        "-d", "--device", type=int_or_str,
        help="input device (numeric ID or substring)")
    parser.add_argument(
        "-r", "--samplerate", type=int, help="sampling rate")
    parser.add_argument(
        "-t", "--trigger", type=str, default="мормышка",
        help="trigger word or phrase to activate (default: 'мормышка')")
    # parser.add_argument(
    #     "-et", "--endTrig", type=str, default=None,
    #     help="trigger word or phrase to do task (by default use 5 seconds timer)")
    args = parser.parse_args(remaining)

    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, "input")
            args.samplerate = int(device_info["default_samplerate"])

        model = Model(model_name="vosk-model-small-ru-0.22")

        with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device,
                            dtype="int16", channels=1, callback=callback):
            print("#" * 80)
            print("Press Ctrl+C to stop the recording")
            print(f"Trigger word: '{args.trigger}'")
            # if args.endTrig is not None:
            #     print(f"End trigger word: '{args.endTrig}'")
            print("#" * 80)

            rec = KaldiRecognizer(model, args.samplerate)
            rec.SetWords(True)
            rec.SetPartialWords(True)

            command_words = []
            silence = 2.0
            listening = False
            last_word_time = None
            last_result_time = time.perf_counter()

            while True:
                data = q.get()
                            
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text','')
                    words = result.get('result',[])
                    if not words: # случай тишины(каждые ~5 секунд тишины rec.Result() возвращает пустую строку)
                        print("тишь да гладь")
                        #################
                        # if listening:
                        #     # По идее сюда никогда не попадем Значит можно убрать
                        #     command = " ".join(command_words)
                        #     print("Команда 1: ",command)
                        #     processCommand(command_words)
                        #     listening = False
                        #     command_words = []
                        #     last_word_time = None
                        #################    
                        continue
                    i = 0
                    while i < len(words):
                        word = words[i]['word']
                        start = words[i]['start']
                        end = words[i]['end']

                        if (not listening):
                            if word == args.trigger:
                                listening = True
                                command_words = []
                                last_word_time = end
                            i += 1
                            continue

                        # if (args.end_trigger and word == args.end_trigger):
                        #     command = " ".join(command_words)
                        #     print("Команда :", command)
                        #     processCommand(command)
                        #     listening = False
                        #     command_words = []
                        #     last_word_time = None
                        #     i += 1
                        #     continue

                        # if not args.end_trigger and last_word_time:
                        # if last_word_time:
                        if start - last_word_time > silence:
                            command = " ".join(command_words)
                            print("Команда 2:", command)
                            processCommand(command_words)
                            listening = False
                            command_words = []
                            last_word_time = None
                            continue

                        command_words.append(word)
                        last_word_time = end
                        i += 1
                    last_result_time = time.perf_counter()
                else:
                    if listening:
                        partial = json.loads(rec.PartialResult())
                        pText = partial.get('partial','')
                        pWords = partial.get('partial_result',[])
                        start = 0.0
                        if pWords:
                            start = pWords[0]['start']
                            end = last_word_time
                        else:
                            start = time.perf_counter()
                            end = last_result_time
                        if start - end > silence:
                            command = " ".join(command_words)
                            print("Команда 3:", command)
                            processCommand(command_words)
                            listening = False
                            command_words = []
                            last_word_time = None              

    except KeyboardInterrupt:
        print("\nDone")
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ": " + str(e))