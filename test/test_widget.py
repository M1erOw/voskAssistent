import signal
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGraphicsDropShadowEffect, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("мега окно распознаватель")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        rect = QDesktopWidget().availableGeometry() 
        w,h = rect.width() // 5,rect.height() // 5
        self.resize(w,h)

        self.center()

        self.lab_text = QLabel(text="Слушаю...")
        self.lab_text.setAlignment(Qt.AlignCenter)

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
    
    def center(self):
        geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(center_point)
        self.move(geometry.topLeft())

    def set_text(self,text):
        self.lab_text.setText(text)
        self.center()
    
def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    window = MyWidget()

    window.set_text("Случайный текст для окна")
    
    window.show()
    app.exec()

if __name__ == "__main__":
    main()