import time

class ListeningState:
    def __init__(self):
        self.listening = False
        self.words = []
        self.last_word_time = None
        self.last_result_time = time.perf_counter()
    
    def set_state(self,args):
        if len(args) == 3:
            self.listening = args[0]
            self.words = args[1]
            self.last_word_time = args[2]
        elif len(args) == 2:
            self.words.append(args[0])
            self.last_word_time = args[1]
        else:
            self.last_result_time = args[0]