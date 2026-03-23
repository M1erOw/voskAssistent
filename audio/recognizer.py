import json
from vosk import KaldiRecognizer, Model
class Recognizer:
    def __init__(self,samlerate,model_path):
        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model,samlerate)
        self.rec.SetWords(True)
        self.rec.SetPartialWords(True)
    
    def accept(self,data):
        return self.rec.AcceptWaveform(data)
    
    def get_result(self):
        return json.loads(self.rec.Result())
    
    def get_partial(self):
        return json.loads(self.rec.PartialResult())