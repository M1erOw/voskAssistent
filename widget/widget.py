from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QDesktopWidget
from PyQt5.QtCore import QTimer, Qt

from utils.commands import process_command

class MyWindow(QMainWindow):
    def __init__(self,conn):
        super().__init__()
        self.connection = conn
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_pipe)
        self.timer.start(20)
        self.counter = 0
        self.saved_text = ''
        self.setWindowTitle("мега окно распознаватель")
        
        rect = QDesktopWidget().availableGeometry() 

        w,h = rect.width() // 5,rect.height() // 5

        self.resize(w,h)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        layout = QVBoxLayout()

        self.lab_text = QLabel(text="Слушаю")

        font = self.lab_text.font()
        font.setPointSize(18)
        font.setBold(True)
        self.lab_text.setFont(font)

        self.lab_text.setStyleSheet("""
            color: white;
            background-color: lightblue;
            font-size: 24px;
            font-family: Arial;
            padding: 10px;
            border: 2px solid darkblue;
            border-radius: 50px;
        """)

        layout.addWidget(self.lab_text)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        central_widget.setStyleSheet(
            """
            background:lightgreen;
            border-radius: 50px;
            """
        )
        self.setCentralWidget(central_widget)

    def check_pipe(self):
        try:
            if self.connection.poll():
                msg = self.connection.recv()
                if 'show' in msg:
                    if msg['show']:
                        self.lab_text.setText("Слушаю")
                        self.show()
                        self.activateWindow()
                if 'text' in msg:
                    self.lab_text.setText(msg['text'])
                    self.activateWindow()
                    self.saved_text = ''
                if 'add_text' in msg:
                    if self.saved_text:
                        self.saved_text = self.lab_text.text()
                    self.lab_text.setText(self.saved_text + " " + msg['add_text'])
                if 'command' in msg:
                    if msg['command']:
                        self.lab_text.setText(self.lab_text.text() + "✅")
                        self.activateWindow()
                        QTimer.singleShot(2000, self.hide_window)
                        QTimer.singleShot(2050,lambda: process_command(msg['name'],msg['args'],execute=False))
                    else:
                        self.lab_text.setText(self.lab_text.text() + "❌")
                        self.activateWindow()
                        if not msg['second_try'] and msg['text']:
                            QTimer.singleShot(500, lambda: self.lab_text.setText("Попробуйте еще раз"))
                        else:
                            QTimer.singleShot(2000, self.hide_window)
                if 'close' in msg:
                    QTimer.singleShot(5000, self.close)
            if self.lab_text.text()[0] == "С":
                self.lab_text.setText("Слушаю" + ("." * ((self.counter // 10) % 4)))
            self.counter += 1
        except KeyboardInterrupt:
            self.close()
    
    def hide_window(self):
        self.hide()