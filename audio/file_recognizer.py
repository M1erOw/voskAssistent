import json
import sys
import time
import wave
from vosk import SetLogLevel
from PyQt5.QtCore import QThread, pyqtSignal

from audio.recognizer import Recognizer
from config import *
from state.state import ListeningState
from utils.commands import find_command
    
class FileRecognizerWorker(QThread):
    show_signal = pyqtSignal()
    text_signal = pyqtSignal(str)
    command_signal = pyqtSignal(bool,str,list,bool)

    def run(self):
        SetLogLevel(LOG_LEVEL)

        wf = wave.open(FILENAME, "rb")

        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            sys.exit(1)

        recognizer = Recognizer(wf.getframerate(), MODEL_PATH)
        state = ListeningState()

        blank_counter = 0

        try:
            print("#" * 80)
            print(f"Trigger word: '{TRIGGER}'")
            print("#" * 80)
            flag = True
            while True:
                time.sleep(0.1)
                data = wf.readframes(4000)
                if len(data) == 0:
                    result = json.loads(recognizer.rec.FinalResult())
                    text = result.get('text', '')
                    if blank_counter:
                        print(f"{blank_counter} blank lines")
                        blank_counter = 0
                    if text:
                        print("FinalRes:",text)
                    else:
                        print("Blank FinalRes")
                    words = text.split()
                    # if not words:
                    #     break
                    idx = 0
                    if not state.listening:
                        if TRIGGER in words:
                            state.listening = True
                            state.words = []
                            self.show_signal.emit()
                            idx = words.index(TRIGGER) + 1

                    state.words += words[idx:]
                    state.last_result_time = time.perf_counter()

                    name, args = find_command(state.words)
                    command = " ".join(state.words)
                    if name:
                        self.text_signal.emit(command)
                        # self.command_signal.emit(True, name, args, False)
                        self.command_signal.emit(True, name, args, False)
                        state = ListeningState()
                    else:
                        self.text_signal.emit(command)
                        self.command_signal.emit(False, "", [], (False if command else True))
                        
                        if state.words:
                            state = ListeningState()
                            state.listening = True
                        else:
                            state = ListeningState()

                    break
                if recognizer.accept(data):
                    result = recognizer.get_result()
                    text = result.get('text', '')
                    if blank_counter:
                        print(f"{blank_counter} blank lines")
                        blank_counter = 0
                    if text:
                        print("Res:",text)
                    else:
                        print("Blank Res")
                    words = text.split()
                    if not words:
                        continue
                    idx = 0
                    if not state.listening:
                        if TRIGGER in words:
                            state.listening = True
                            state.words = []
                            self.show_signal.emit()
                            idx = words.index(TRIGGER) + 1

                    state.words += words[idx:]
                    state.last_result_time = time.perf_counter()
                else:
                    partial = recognizer.get_partial()
                    pText = partial.get('partial', '')
                    if pText:
                        if blank_counter:
                            print(f"{blank_counter} blank lines")
                            blank_counter = 0
                        print("Part:",pText)
                    else:
                        blank_counter += 1
                    # pWords = pText.split()
                    if state.listening:
                        start = time.perf_counter()
                        end = state.last_result_time
                        if start - end > SILENCE + (0.0 if state.words else 3.0):
                            name, args = find_command(state.words)
                            command = " ".join(state.words)
                            if name:
                                self.text_signal.emit(command)
                                # self.command_signal.emit(True, name, args, False)
                                self.command_signal.emit(True, name, args, False)
                                state = ListeningState()
                            else:
                                self.text_signal.emit(command)
                                self.command_signal.emit(False, "", [], (False if command else True))
                                
                                if state.words:
                                    state = ListeningState()
                                    self.listening = True
                                else:
                                    state = ListeningState()

                        elif pText:
                            state.last_result_time = start
                            self.text_signal.emit(" ".join(state.words) + ("\n" if state.words else "") + pText)

                    elif TRIGGER in pText:
                        self.show_signal.emit()
                        text = pText[pText.find(TRIGGER) + len(TRIGGER) + 1:]
                        if text:
                            self.text_signal.emit(" ".join(state.words) + ("\n" if state.words else "") + text)

        except Exception as e:
            print("Worker error:", e)