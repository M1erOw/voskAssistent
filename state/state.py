import time

class ListeningState:
    def __init__(self):
        self.listening = False
        self.words = []
        self.last_word_time = None
        self.last_result_time = time.perf_counter()
        self.send_show = False
        self.second_try = True