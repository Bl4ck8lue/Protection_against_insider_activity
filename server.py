import socket
import sys

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, \
    QHBoxLayout, QListWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.extension = None
        _signal = pyqtSignal(int)

        self.setWindowTitle("Client-Server for protection")
        self.setFixedSize(460, 300)

        first_layout = QHBoxLayout()
        self.btn_update = QPushButton("Update")
        self.label = QLabel("Device list")
        first_layout.addWidget(self.label)
        first_layout.addWidget(self.btn_update)

        second_layout = QVBoxLayout()
        self.list = QListWidget()
        second_layout.addWidget(self.list)

        main_layout = QVBoxLayout()
        main_layout.addLayout(first_layout)
        main_layout.addLayout(second_layout)

        container = QWidget()

        container.setLayout(main_layout)

        self.setCentralWidget(container)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    server = socket.socket()
    hostname = socket.gethostname()
    port = 123
    server.bind((hostname, port))
    server.listen(5)
    con, addr = server.accept()  # принимаем клиента

    data = con.recv(1024)
    print("connection: ", con)
    print("client address: ", addr)
    print("text: ", data.decode('utf-8'))

    window.show()

    sys.exit(app.exec())
