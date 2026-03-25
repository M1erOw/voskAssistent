from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

class MyWindow(QMainWindow):
    def __init__(self,conn):
        super().__init__()
        self.connection = conn
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_pipe)
        self.timer.start(50)
        self.counter = 0
        self.saved_text = ''
        self.setWindowTitle("мега окно распознаватель")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.lab_listener = QLabel(text="Слушаю")
        self.lab_text = QLabel(text = "Распознанный текст:")
        self.lab_is_com = QLabel(text = "#❌Команда не распознана")

        layout.addWidget(self.lab_listener)
        layout.addWidget(self.lab_text)
        layout.addWidget(self.lab_is_com)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def check_pipe(self):
        try:
            if self.connection.poll():
                msg = self.connection.recv()
                if 'text' in msg:
                    self.saved_text = msg['text']
                if 'add_text' in msg:
                    self.lab_text.setText("Распознанный текст:" + self.saved_text + " " + msg['add_text'])
                else:
                    self.lab_text.setText("Распознанный текст:" + self.saved_text)
                if 'command' in msg:
                    self.lab_is_com.setText("✅Распознана команда -> " + msg['command'])
                if 'show' in msg:
                    if msg['show']:
                        self.show()
                        self.activateWindow()
                    else:
                        self.lab_is_com.setText(self.lab_is_com.text() + "\n" + "Команда выполнена✅")
                        QTimer.singleShot(5000, self.hide_window)
                # if 'terminate' in msg:
                #     self.close()
                #     return
            self.lab_listener.setText("Слушаю" + ("." * ((self.counter // 10) % 4)))
            self.counter += 1
        except KeyboardInterrupt:
            self.close()
    
    def hide_window(self):
        self.lab_text.setText("Распознанный текст:")
        self.lab_is_com.setText("❌Команда не распознана")
        self.hide()