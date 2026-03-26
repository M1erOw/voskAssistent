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
                                msg = {'show': True}
                                parent_conn.send(msg)
                                state.listening = True
                                state.words = []
                                state.last_word_time = end
                                if not state.send_show:
                                    parent_conn.send({'show': True})
                                    state.send_show = True
                            continue
                        if start - state.last_word_time > SILENCE:
                            name, arg = find_command(state.words)
                            command = " ".join(state.words)
                            if name:
                                parent_conn.send({'text':command,'command': True,'name': name,'args': arg})
                            else:
                                parent_conn.send({'text':command,'command': False})
                            state = ListeningState()
                            continue
                        state.words.append(word)
                        state.last_word_time = end
                    state.last_result_time = time.perf_counter()
                else:
                    partial = recognizer.get_partial()
                    pText = partial.get('partial','')
                    pWords = partial.get('partial_result',[])
                    if state.listening:                    
                        start = 0.0
                        if pWords:
                            start = pWords[0]['start']
                            end = state.last_word_time
                        else:
                            start = time.perf_counter()
                            end = state.last_result_time
                        if start - end > SILENCE + (0.0 if state.words else 3.0):
                            name, arg = find_command(state.words)
                            command = " ".join(state.words)
                            if name:
                                parent_conn.send({'text':command,'command': True,'name': name,'args': arg})
                            else:
                                parent_conn.send({'text':command,'command': False})
                            state = ListeningState()
                        elif pText:
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