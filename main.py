import signal
import sys
from PyQt5.QtWidgets import QApplication

from audio.file_recognizer import FileRecognizerWorker
from audio.recognizer import RecognizerWorker
from widget.widget import MyWidget

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MyWidget()
    worker = RecognizerWorker()
    # worker = FileRecognizerWorker()
    
    worker.show_signal.connect(window.show_widget)
    worker.text_signal.connect(window.set_text)
    worker.command_signal.connect(window.show_command_result)

    worker.start()
    sys.exit(app.exec())
        
if __name__ == "__main__":
    main()