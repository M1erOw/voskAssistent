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
from utils.commands import find_command
from widget.widget import MyWindow

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

    blank_counter = 0

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
                        print("Res:",text)
                    else:
                        print("Blank Res")
                    words = text.split()
                    if not words:
                        continue
                    for word in words:
                        if not state.listening:
                            if word == TRIGGER:
                                state.listening = True
                                state.words = []
                                if not state.send_show:
                                    parent_conn.send({'show': True})
                                    state.send_show = True
                            continue

                        state.words.append(word)
                    state.last_result_time = time.perf_counter()
                else:
                    partial = recognizer.get_partial()
                    pText = partial.get('partial','')
                    if pText:
                        if blank_counter:
                            print(f"{blank_counter} blank lines")
                            blank_counter = 0
                        print("Part:",pText)
                    else:
                        blank_counter += 1
                    pWords = pText.split()
                    if state.listening:                    
                        start = time.perf_counter()
                        end = state.last_result_time
                        if start - end > SILENCE + (0.0 if state.words else 3.0):
                            name, arg = find_command(state.words)
                            command = " ".join(state.words)
                            if name:
                                parent_conn.send({'text':command,'command': True,'name': name,'args': arg})
                                state = ListeningState()
                            else:
                                parent_conn.send({'text':command,'command': False,'second_try':state.second_try})
                                if not state.second_try and state.words:
                                    state.words = []
                                    state.second_try = True
                                else:
                                    state = ListeningState()
                            print("Команда:", command)
                        elif pText:
                            state.last_result_time = start
                            parent_conn.send({'add_text':pText})
                    elif TRIGGER in pText:
                        if not state.send_show:   
                            parent_conn.send({'show': True})
                            state.send_show = True
                        text = pText[pText.find(TRIGGER) + len(TRIGGER) + 1:]
                        if text:
                            parent_conn.send({'add_text' : text})
                            
    except KeyboardInterrupt:
        print("\nDone")
    except Exception as e:
        print(type(e).__name__ + ": " + str(e))

if __name__ == "__main__":
    main()