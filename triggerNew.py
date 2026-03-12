#!/usr/bin/env python3

import argparse
import queue
import sys
import json
import time
import sounddevice as sd
import webbrowser
from vosk import Model, KaldiRecognizer, SetLogLevel

q = queue.Queue()
SetLogLevel(-1)

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

def proccessCommand(com):
    if (not com):
        # wake()           # показ окна с текстом + функциями
        return
    command = com.split(maxsplit = 1)
    act = command[0]
    obj = command[1]

    ###############  Определить команды из 1-го слова и 2-ух и больше ###################

    if (checkSimilar(act,"введи") > 0.8): # match/case?
        print(obj)
    elif (checkSimilar(act + " " + obj.split()[0], "открой браузер") > 0.8):
        webbrowser.open("https://www.google.com/", new=2)
    elif (checkSimilar(act, "найди") > 0.8):
        webbrowser.open("https://www.google.com/search?q=" + obj.replace(' ','+'), new=2)
    else:
        print("Неизвестная команда")

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
parser.add_argument(
    "-et", "--endTrig", type=str, default=None,
    help="trigger word or phrase to do task (by default use 5 seconds timer)")
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
        if args.endTrig is not None:
            print(f"End trigger word: '{args.endTrig}'")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)
        rec.SetWords(True)
        rec.SetPartialWords(True)

        command = ""
        commandIsReady = False
        timer = 5.0
        proccessComm = False

        # start = time.perf_counter()

        while True:
            data = q.get()
                        
            if rec.AcceptWaveform(data):
                # end = time.perf_counter()
                # print(f"{end-start:.6f}")
                # start = end
                # print(rec.Result())
                # cprint("###########################")
                result_json = rec.Result()
                result = json.loads(result_json)
                text = result.get('text')
                if text:
                    idx = -1
                    if (not proccessComm):
                        try:
                            idx = text.split().index(args.trigger)
                            proccessComm = True
                            # print(idx)
                        except ValueError:
                            continue
                    if (args.endTrig is None):
                        data = result.get('result','')
                        # print(data)
                        if data:
                            for i in range(idx + 1,len(data)):
                                wordLen = data[i]['end'] - data[i]['start']
                                timer -= wordLen
                                if (timer  > 0):
                                    command += " " + data[i]['word']
                                else:
                                    break
                            if timer > 0:
                                pass
                            else:
                                print(f"Команда: {command}")
                                proccessCommand(command)
                                proccessComm = False
                                timer = 5.0
                    else:
                        newIdx = max(0,idx)
                        # print("newIdx =",newIdx)
                        try:
                            idxOfEnd = text.split()[newIdx:].index(args.endTrig)
                            # print("text =",text)
                            # print(text.split()[newIdx:])
                            # print(idxOfEnd)
                        except ValueError:
                            idxOfEnd = -1
                        if (idxOfEnd != -1):
                            command += " ".join(text.split()[newIdx + (1 if idx >= 0 else 0):idxOfEnd])
                            print(f"Команда: {command}")
                            proccessCommand(command)
                            proccessComm = False
                            command = ""
                        else:
                            command += " ".join(text.split()[newIdx + (1 if idx >= 0 else 0):])
                            command += " "
                else:
                    print("Я всё еще работаю")
            else:
                # print(rec.PartialResult())
                # partial = json.loads(rec.PartialResult())
                # print(partial.get('partial', ''))
                pass

except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))