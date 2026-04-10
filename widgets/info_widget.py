from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt5.QtCore import Qt

from utils.commands import commands

class InfoWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Справка")

        self.setMinimumSize(400,200)

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 10, 10, 10)

        headers = ["Команда", "Аргументы", "Описание"]
        for col, text in enumerate(headers):
            label = QLabel(text)
            label.setObjectName("header")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, 0, col)

        for i, command in enumerate(commands):
            name = QLabel(commands[command].name)
            args = QLabel(commands[command].args)
            desc = QLabel(commands[command].description)

            name.setObjectName("cell")
            args.setObjectName("cell")
            desc.setObjectName("cell")

            layout.addWidget(name, i + 1, 0)
            layout.addWidget(args, i + 1, 1)
            layout.addWidget(desc, i + 1, 2)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #e0f1ff;
                font-family: Segoe UI;
            }

            QLabel {
                padding: 8px;
            }

            QLabel#header {
                background-color: #a6d1f5;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }

            QLabel#cell {
                background-color: white;
                border: 1px solid #d0d7de;
                font-size: 13px;
            }

            QLabel#cell:hover {
                background-color: #e3f1fc;
            }
        """)