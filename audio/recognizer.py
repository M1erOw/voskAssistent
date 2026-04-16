import json
import time
from vosk import KaldiRecognizer, Model, SetLogLevel
from PyQt5.QtCore import QThread, pyqtSignal
import sounddevice as sd

from audio.audio_stream import create_stream, q
from config import *
from state.state import ListeningState
from utils.commands import find_command

class Recognizer:
    def __init__(self,samlerate,model_path):
        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model,samlerate)
        # self.rec.SetWords(True)
        # self.rec.SetPartialWords(True)
    
    def accept(self,data):
        return self.rec.AcceptWaveform(data)
    
    def get_result(self):
        return json.loads(self.rec.Result())
    
    def get_partial(self):
        return json.loads(self.rec.PartialResult())
    
class RecognizerWorker(QThread):
    show_signal = pyqtSignal()
    text_signal = pyqtSignal(str)
    command_signal = pyqtSignal(bool,str,list,bool)

    def run(self):
        SetLogLevel(LOG_LEVEL)
        device_info = sd.query_devices(DEVICE, "input")
        samplerate = int(device_info["default_samplerate"])

        recognizer = Recognizer(samplerate, MODEL_PATH)
        state = ListeningState()

        blank_counter = 0

        try:
            with create_stream(samplerate, DEVICE):
                print("#" * 80)
                print("Press Ctrl+C to stop the recording")
                print(f"Trigger word: '{TRIGGER}'")
                print("#" * 80)
                while True:
                    data = q.get()
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
                        if state.listening:
                            state.words += words[idx:]
                        if state.words and state.listening:
                            self.text_signal.emit(" ".join(state.words))
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
                                    
                                    if command:
                                        state = ListeningState()
                                        state.listening = True
                                    else:
                                        state = ListeningState()

                            elif pText:
                                state.last_result_time = start
                                self.text_signal.emit(" ".join(state.words) + (" " if state.words else "") + pText)

                        elif TRIGGER in pText:
                            self.show_signal.emit()
                            text = pText[pText.find(TRIGGER) + len(TRIGGER) + 1:]
                            if text:
                                self.text_signal.emit(text)

        except Exception as e:
            print("Worker error:", e)