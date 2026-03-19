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

spk_sig = [-6.94727333e-01,8.05006667e-01,-2.14930333e-01,1.13932833e+00,-8.09158000e-01,-3.97239000e-01,
           2.73436000e-01,1.80585667e-01,1.44789367e+00,8.43977000e-01,1.42144100e+00,-5.57358333e-01,1.69513667e-01,
           -1.32373067e+00,5.33284667e-01,2.46609333e-01,4.47690333e-01,3.65426667e-01,1.54885433e+00,-2.03256833e+00,
           -1.41130167e+00,3.42359000e-01,8.57942667e-01,8.63200333e-01,-7.13758333e-01,1.64330000e+00,2.77569333e-01,
           -1.29548400e+00,2.87020667e-01,-6.74965333e-01,-5.07173000e-01,-8.14965333e-01,-7.05258000e-01,-7.31591333e-01,
           -2.19332067e+00,-3.84938667e-01,1.18398533e+00,-1.49270667e-01,-1.87367000e-01,-5.33153667e-01,-7.66796000e-01,
           -2.91230000e-02,2.27070000e-02,1.11470000e-02,8.05498667e-01,-8.64714667e-01,-5.91025667e-01,-3.42593000e-01,
           1.43026100e+00,1.05467400e+00,-1.39221567e+00,-5.11996667e-02,2.14137000e-01,4.87384333e-01,5.00871333e-01,
           2.66633333e-03,9.69301667e-01,1.10061333e-01,-5.88026667e-01,6.37850667e-01,6.72708333e-01,1.48134700e+00,
           4.83122000e-01,2.29695333e-01,-5.70460333e-01,3.57117000e-01,-6.43227667e-01,1.75260500e+00,-9.36898333e-01,
           -2.87728333e-01,6.19200000e-01,-1.35831900e+00,-1.36962000e-01,-3.53364333e-01,2.80649000e-01,2.80981000e-01,
           -1.02754867e+00,-1.54200567e+00,3.58759333e-01,7.74722000e-01,-5.43133333e-03,-1.35169200e+00,-1.04324767e+00,
           -7.10273667e-01,-1.25241333e+00,8.08710000e-01,-1.42918100e+00,-5.46156667e-02,-9.90879333e-01,5.49269000e-01,
           -1.35196867e+00,-1.02407000e+00,-2.54383333e-02,-3.47483000e-01,8.34632333e-01,-1.03519400e+00,7.01476667e-01,
           1.42674000e+00,4.63431333e-01,2.40388667e-01,-7.32715667e-01,-2.03772833e+00,-4.07422333e-01,-5.33333333e-04,
           -2.93478333e-01,-9.31037333e-01,1.09594567e+00,1.73483500e+00,-6.87970000e-02,2.29382000e-01,-1.44317333e-01,
           -1.25254667e-01,1.57763433e+00,-1.20163167e+00,9.24294333e-01,-2.70763333e-02,-6.47873333e-01,1.45032333e-01,
           -1.28103533e+00,2.75585333e-01,-1.04436033e+00,-7.93336000e-01,4.56101000e-01,-7.54730000e-01,-1.60172667e+00,
           7.63671333e-01,-4.21381333e-01,-8.50410000e-02]

if __name__ == '__main__':
    SetLogLevel(-2)

    # SPK_MODEL_PATH = "C:/Users/user/.cache/vosk/vosk-model-spk-0.4"
    SPK_MODEL_PATH = "model-spk"

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

        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                            dtype="int16", channels=1, callback=callback):
            print("#" * 80)
            print("Press Ctrl+C to stop the recording")
            print("#" * 80)

            rec = KaldiRecognizer(model, samplerate)
            rec.SetSpkModel(spk_model)

            while True:
                data = q.get()
                            
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text','')
                    if text:
                        print("Text:",text)
                    if "spk" in result:
                        dist = cosine_dist(spk_sig, result["spk"])
                        print("Speaker distance:", dist,"based on", result["spk_frames"], "frames")
                        if dist <= 0.15:
                            print("Vitaly")
                                  

    except KeyboardInterrupt:
        print("\nDone")
    except Exception as e:
        print(type(e).__name__ + ": " + str(e))