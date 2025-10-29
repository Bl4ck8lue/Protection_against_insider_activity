import socket
import select
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QListWidget, QWidget
)


class MainWindow(QMainWindow):
    def __init__(self, host='0.0.0.0', port=50000):
        super().__init__()
        self.setWindowTitle("Client-Server for protection")
        self.setFixedSize(460, 300)

        # UI
        first_layout = QHBoxLayout()
        self.btn_update = QPushButton("Update")
        self.btn_update.clicked.connect(self.on_update)
        self.label = QLabel("Device list")
        first_layout.addWidget(self.label)
        first_layout.addWidget(self.btn_update)

        second_layout = QVBoxLayout()
        self.list_widget = QListWidget()   # не называем 'list'
        second_layout.addWidget(self.list_widget)

        main_layout = QVBoxLayout()
        main_layout.addLayout(first_layout)
        main_layout.addLayout(second_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(5)
        # делаем неблокирующим — чтобы GUI не зависал
        self.server.setblocking(False)

        self.list_widget.addItem(f"Listening on {host}:{port}")

    def on_update(self):
        try:
            ready, _, _ = select.select([self.server], [], [], 0)
            if ready:
                conn, addr = self.server.accept()
                with conn:
                    data = conn.recv(4096)
                    if not data:
                        self.list_widget.addItem(f"{addr} sent empty payload")
                        return
                    text = data.decode('utf-8', errors='replace')
                    self.list_widget.addItem(f"{addr[0]}:{addr[1]} -> {text}")
                    # отправим подтверждение клиенту
                    try:
                        conn.sendall(b'OK')
                    except Exception:
                        pass
            else:
                self.list_widget.addItem("No incoming connection at the moment.")
        except Exception as e:
            # Показываем ошибку в списке
            self.list_widget.addItem(f"Error accepting connection: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(host='0.0.0.0', port=50000)
    window.show()
    sys.exit(app.exec())
