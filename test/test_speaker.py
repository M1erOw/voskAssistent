#!/usr/bin/env python3

import os
import queue
import sys
import json
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SpkModel, SetLogLevel

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

def cosine_dist(x, y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)

# spk_sig = [-1.0282366666666667, 0.21803366666666668, 0.6835, 0.8318716666666667, -1.911747, -0.31986966666666666, 0.554145, 0.08019733333333333, 1.4430420000000002, 0.012200333333333332, 0.8905553333333334, 0.22557999999999997, -1.2508626666666667, -1.0810513333333334, 0.08664966666666667, -0.10926033333333333, -0.2836099999999999, -0.668727, 1.290918, -1.9153563333333334, -0.8640263333333333, -0.38509400000000005, 0.08712466666666667, 1.3066226666666665, -0.026470666666666667, 0.7810916666666667, 0.491169, -2.5569953333333335, 0.555836, -0.31840199999999996, -0.21329866666666672, -0.32648866666666665, -0.7213026666666668, -0.148083, -0.7159186666666667, 1.3454300000000001, 0.29017633333333337, 0.3646133333333333, 1.2113613333333333, -0.14408033333333337, -0.8467763333333332, 0.6562043333333333, 0.2536673333333333, -0.6537556666666666, 1.1723299999999999, -0.2637633333333333, -0.7636553333333334, 0.9273516666666667, 0.9344446666666667, 1.160255, -0.5086893333333334, 0.05754233333333336, 0.7981506666666666, -0.027424666666666653, 0.3717133333333334, -0.6444493333333333, 0.5330093333333333, -0.665394, 0.32790233333333335, 0.8758726666666666, 0.25169366666666665, 0.04603533333333332, -0.44470933333333335, 0.03523900000000002, 0.743188, -1.3919506666666666, 0.49580533333333326, 0.5962826666666667, -1.2712993333333333, -0.5041473333333333, -0.8831129999999999, -0.9486880000000001, 0.6734923333333334, 0.5258250000000001, 0.5600933333333332, 1.9549839999999998, -1.1239333333333335, -0.9920473333333334, -0.7717303333333333, 0.6503393333333334, -0.514474, -1.063498, 0.16581333333333334, -0.7471800000000001, -0.14787999999999998, 1.3199500000000002, -0.873698, -0.45356, 0.13699633333333336, -0.7788726666666667, 0.04518399999999997, -1.748458, -0.6541116666666666, 0.7667243333333333, 0.0066083333333333645, -0.7445510000000001, 0.281978, -0.07990333333333333, 0.37628599999999995, 0.08786, -0.5768953333333333, -0.748758, -0.3693233333333334, 1.3656730000000001, 0.1723423333333333, -0.5474420000000001, 0.9845703333333332, 1.053503, -1.771816, 0.14148866666666662, -1.1467990000000001, 1.7664373333333334, 0.591096, 0.12238333333333333, 0.031134333333333337, -0.11663199999999997, 0.621572, -0.304096, -0.13491733333333336, 0.8993576666666666, -0.35983433333333337, -0.062258, 0.594766, -0.7599093333333333, -0.9505106666666666, 0.15459366666666666, -0.09106766666666666, 0.5656733333333334]

if __name__ == '__main__':
    SetLogLevel(-2)

    SPK_MODEL_PATH = "C:/Users/user/.cache/vosk/vosk-model-spk-0.4"
    # SPK_MODEL_PATH = "model-spk"

    if not os.path.exists(SPK_MODEL_PATH):
        print("Please download the speaker model from "
            "https://alphacephei.com/vosk/models and unpack as {SPK_MODEL_PATH} "
            "in the current folder.")
        sys.exit(1)

    try:
        device = None
        device_info = sd.query_devices(device, "input")
        samplerate = int(device_info["default_samplerate"])

        model = Model(model_name="vosk-model-small-ru-0.22")
        spk_model = SpkModel(SPK_MODEL_PATH)

        with sd.RawInputStream(samplerate=samplerate, blocksize=4000, device=device,
                            dtype="int16", channels=1, callback=callback):
            print("#" * 80)
            print("Press Ctrl+C to stop the recording")
            print("#" * 80)

            rec = KaldiRecognizer(model, samplerate)
            rec.SetSpkModel(spk_model)

            signatures = {}
            counter = 0

            while True:
                data = q.get()
                            
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text','')
                    if text:
                        print("Text:",text)
                    if "spk" in result:
                        if result["spk_frames"] > 100:
                            min_dist = 2.0
                            speaker_sig = None
                            for sig in signatures:
                                dist = cosine_dist(result["spk"],sig)
                                if dist < min_dist:
                                    min_dist = dist
                                    speaker_sig = sig
                            if min_dist < 0.6: # побробовать разный порог
                                print(f"Говорит спикер №{signatures[speaker_sig]}, cosine_dist = {min_dist:.6f}")
                                signatures[result["spk"]] = signatures[speaker_sig] # или удаление старой записи 
                                                                                    # и создание новой с усредненной сигнатурой
                            else:
                                signatures[result["spk"]] = counter
                                counter += 1
                                print("Добавлен новый спикер")
                        else:
                            print("недостаточно фреймов")        

    except KeyboardInterrupt:
        print("\nDone")
    except Exception as e:
        print(type(e).__name__ + ": " + str(e))