import time
from vosk import SetLogLevel
import sounddevice as sd

from audio.audio_stream import create_stream, q
from audio.recognizer import Recognizer
from commands.commands import *
from config import *
from state.state import ListeningState
from utils.find_command import find_command

commands = {"сверни все окна" : MinimizeAllWindows(),
            "запиши в файл" : WriteToFile(),
            "сделай скриншот" : TakeScreenshot(),
            "создай файл" : CreateFile(),
            "открой браузер" : OpenBroser(),
            "найди документ" : FindDocument(),
            "создай напоминание" : CreateReminder(),
            "напиши" : WriteToConsole(),
            "найди" : FindInBrowser()}

def process_command(words):
    name, args = find_command(words)
    if name in commands:
        commands[name].execute(args)
    else:
        print("Неизвестная команда")
    
def main():
    SetLogLevel(-1)
    device_info = sd.query_devices(DEVICE, "input")
    samplerate = int(device_info["default_samplerate"])

    recognizer = Recognizer(samplerate,MODEL_PATH)
    state = ListeningState()

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
                            state = ListeningState()
                            continue
                        state.words.append(word)
                        state.last_word_time = end
                    state.last_result_time = time.perf_counter()
                else:
                    if state.listening:
                        partial = recognizer.get_partial()
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
                            state = ListeningState()
                            
    except KeyboardInterrupt:
        print("\nDone")
    except Exception as e:
        print(type(e).__name__ + ": " + str(e))

if __name__ == "__main__":
    main()