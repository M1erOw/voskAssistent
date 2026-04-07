from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QDesktopWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor

from utils.commands import process_command

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.setWindowTitle("мега окно распознаватель")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMinimumSize(400,200)
        self.resize(400,200)

        self.lab_text = QLabel(text="Слушаю...")
        self.lab_text.setWordWrap(True)
        self.lab_text.setAlignment(Qt.AlignCenter)
        self.lab_text.setMinimumSize(400,200)
        self.lab_text.setFixedWidth(400)

        font = QFont("Palatino Linotype",16,QFont.Bold)
        self.lab_text.setFont(font)

        self.lab_text.setStyleSheet("""
            QLabel {
                color: black;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e0f1ff,
                    stop:1 #ebf3fa
                );
                border-radius: 20px;
                padding: 15px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(200, 200, 255, 150))
        shadow.setOffset(5, 5)
        self.lab_text.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.addWidget(self.lab_text)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)

        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.listening)
        self.timer.start(330)

        self.processing_command = False

        self.adjust_window_size()
    
    def center(self):
        geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(center_point)
        self.move(geometry.topLeft())

    def listening(self):
        if self.lab_text.text()[0] == "С":
            self.lab_text.setText("Слушаю" + ("." * (self.counter % 4)))
            self.counter += 1

    def show_widget(self):
        self.show()

    def adjust_window_size(self):
        self.lab_text.adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()
        self.center()

    def set_text(self,text):
        if not self.processing_command:
            self.lab_text.setText(text)
            self.adjust_window_size()

    def stop_pr(self):
        self.processing_command = False

    def show_command_result(self, success, name, args, empty):
        self.processing_command = True
        if success:
            self.lab_text.setText(self.lab_text.text() + " ✅")
            QTimer.singleShot(1500, self.hide)
            QTimer.singleShot(1500, lambda: self.lab_text.setText("Слушаю..."))
            QTimer.singleShot(1600, lambda: process_command(name,args))
            QTimer.singleShot(1600, self.stop_pr)
        else:
            self.lab_text.setText(self.lab_text.text() + " ❌")
            if not empty:
                QTimer.singleShot(1000, lambda: self.lab_text.setText("Слушаю..."))
                QTimer.singleShot(1000, self.stop_pr)
            else:
                QTimer.singleShot(1500, self.hide)
                QTimer.singleShot(1500, lambda: self.lab_text.setText("Слушаю..."))
                QTimer.singleShot(1500, self.stop_pr)
        self.adjust_window_size()