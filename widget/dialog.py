from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QDialogButtonBox, QLineEdit
from PyQt5.QtCore import Qt

from utils.add_to_json import add_element_to_json_list

class CustomDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Adding Alias")

        self.setMinimumSize(250,200)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.myAccept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message1 = QLabel("Object name:")
        message2 = QLabel("Alias for object:")
        self.text2 = QLineEdit()
        self.text1 = QLineEdit()
        layout.addWidget(message1)
        layout.addWidget(self.text1)
        layout.addWidget(message2)
        layout.addWidget(self.text2)
        layout.addWidget(self.buttonBox, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #dbcaca;
            }

            QLabel {
                color: black;
                margin-top: 8px;
                font-size: 14px;
            }

            QLineEdit {
                background-color: #e0d5d5;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px;
                color: black;
            }

            QLineEdit:focus {
                border: 1px solid #b88c84;
                background-color: #cfc4c4;
            }

            QPushButton {
                background-color: #9fcafc;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                color: white;
                min-width: 70px;
            }

            QPushButton:hover {
                background-color: #8fc3ff;
            }

            QPushButton:pressed {
                background-color: #2d6396;
            }

            QPushButton[text="Cancel"] {
                background-color: #bcc0c4;
            }

            QPushButton[text="Cancel"]:hover {
                background-color: #9c9ea1;
            }
        """)

    def myAccept(self):
        if self.text1.text() and self.text2.text():
            add_element_to_json_list('data.json',self.text2.text(),self.text1.text())
        else:
            print("Missing values")
        self.accept()