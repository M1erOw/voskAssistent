from multiprocessing import Pipe
import sys
import time
from PyQt5.QtWidgets import QApplication
from vosk import SetLogLevel
import sounddevice as sd

from audio.audio_stream import create_stream, q
from audio.recognizer import Recognizer
from commands.commands import *
from config import *
from state.state import ListeningState
from utils.find_command import find_command
from window.window import MyWindow

commands = {"сверни все окна" : MinimizeAllWindows(),
            "запиши в файл" : WriteToFile(),
            "сделай скриншот" : TakeScreenshot(),
            "создай файл" : CreateFile(),
            "открой браузер" : OpenBroser(),
            "найди документ" : FindDocument(),
            "создай напоминание" : CreateReminder(),
            "напиши" : WriteToConsole(),
            "найди" : FindInBrowser()}

def process_command(words, execute = True):
    name, args = find_command(words)
    if name in commands:
        if execute:
            commands[name].execute(args)
        else:
            return name
    else:
        return None

def start_qt(conn):
    app = QApplication(sys.argv)
    window = MyWindow(conn)
    app.exec()

def main():
    SetLogLevel(-1)
    device_info = sd.query_devices(DEVICE, "input")
    samplerate = int(device_info["default_samplerate"])

    recognizer = Recognizer(samplerate,MODEL_PATH)
    state = ListeningState()

    parent_conn, child_conn = Pipe()
    proc = Process(target=start_qt, args=(child_conn,)) 
    proc.start()

    try:
        with create_stream(samplerate,DEVICE):
            print("#" * 80)
            print("Press Ctrl+C to stop the recording")
            print(f"Trigger word: '{TRIGGER}'")
            print("#" * 80)
            while True:
                data = q.get()              
                if recognizer.accept(data):
                    result = recognizer.get_result()
                    text = result.get('text','') 
                    if text:
                        print(text)
                    words = result.get('result',[])
                    if not words:
                        continue
                    for w in words:
                        word = w['word']
                        start = w['start']
                        end = w['end']
                        if not state.listening:
                            if word == TRIGGER:
                                state.listening = True
                                state.words = []
                                state.last_word_time = end
                            continue
                        if start - state.last_word_time > SILENCE:
                            process_command(state.words)
                            msg = {'show': False,'text':" ".join(state.words)}
                            parent_conn.send(msg)
                            state = ListeningState()
                            continue
                        state.words.append(word)
                        state.last_word_time = end
                    state.last_result_time = time.perf_counter()
                else:
                    partial = recognizer.get_partial()
                    pText = partial.get('partial','')
                    if state.listening:
                        msg = {'add_text':pText}
                        pWords = partial.get('partial_result',[])
                        start = 0.0
                        if pWords:
                            start = pWords[0]['start']
                            end = state.last_word_time
                        else:
                            start = time.perf_counter()
                            end = state.last_result_time
                        if start - end > SILENCE:
                            process_command(state.words)
                            msg['show'] = False
                            msg['text'] = " ".join(state.words)
                            state = ListeningState()
                        parent_conn.send(msg)
                    elif TRIGGER in pText:
                        text = pText[pText.find(TRIGGER) + len(TRIGGER):]
                        words = text.split()
                        name = process_command(words,execute = False)
                        msg = {'text' : text}
                        if name:
                            msg['command'] = name
                        parent_conn.send(msg)
                            
    except KeyboardInterrupt:
        print("\nDone")
        # proc.terminate()
        # parent_conn.send({'terminate':True})
    except Exception as e:
        print(type(e).__name__ + ": " + str(e))

if __name__ == "__main__":
    main()