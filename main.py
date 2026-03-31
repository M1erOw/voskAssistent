import signal
import sys
from PyQt5.QtWidgets import QApplication

from audio.recognizer import RecognizerWorker
from commands.commands import *
from config import *
from widget.widget import MyWidget

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
                        
    window = MyWidget()
    worker = RecognizerWorker()
    
    worker.show_signal.connect(window.show_widget)
    worker.text_signal.connect(window.set_text)
    worker.command_signal.connect(window.show_command_result)

    worker.start()
    sys.exit(app.exec())
        
if __name__ == "__main__":
    main()