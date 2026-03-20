import sys
import sounddevice as sd
import queue

q = queue.Queue()

def callback(indata, _frames, _time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def create_stream(samplerate,device):
    return sd.RawInputStream(samplerate, blocksize=8000, device=device, dtype="int16", channels=1, callback=callback)