# server.py
import socket
import select
import sys
import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QListWidget, QWidget,
    QListWidgetItem, QDialog, QTextEdit
)


class MainWindow(QMainWindow):
    def __init__(self, host='0.0.0.0', port=50000):
        super().__init__()
        self.setWindowTitle("Client-Server for protection")
        self.setFixedSize(600, 400)

        # clients: mapping "ip:port" -> payload (dict or raw str)
        self.clients = {}

        # UI
        first_layout = QHBoxLayout()
        self.btn_update = QPushButton("Update")
        self.btn_update.clicked.connect(self.on_update)
        self.label = QLabel("Available clients")
        first_layout.addWidget(self.label)
        first_layout.addStretch()
        first_layout.addWidget(self.btn_update)

        second_layout = QVBoxLayout()
        self.list_widget = QListWidget()
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
        self.server.listen(10)
        self.server.setblocking(False)

        # show listening info
        self.add_status_item(f"Listening on {host}:{port}")

    def add_status_item(self, text: str):
        """Добавить простую строку статуса в список."""
        item = QListWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        widget = QLabel(text)
        widget.setWordWrap(True)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

    def add_client_row(self, key: str):
        """Добавляет в QListWidget строку с IP и кнопкой 'Get info'."""
        item = QListWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        row_widget = QWidget()
        h = QHBoxLayout()
        lbl = QLabel(key)
        lbl.setMinimumWidth(300)
        btn = QPushButton("Get info")
        btn.clicked.connect(lambda _, k=key: self.show_info(k))
        h.addWidget(lbl)
        h.addStretch()
        h.addWidget(btn)
        h.setContentsMargins(5, 3, 5, 3)
        row_widget.setLayout(h)
        item.setSizeHint(row_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, row_widget)

    def on_update(self):
        """Проверяем ожидающие подключения — если есть, принимаем и сохраняем payload."""
        try:
            ready, _, _ = select.select([self.server], [], [], 0)
            if ready:
                conn, addr = self.server.accept()
                with conn:
                    # читаем данные (предполагаем, что клиент один send)
                    chunks = []
                    try:
                        while True:
                            chunk = conn.recv(65536)
                            if not chunk:
                                break
                            chunks.append(chunk)
                            # если меньше чем размер буфера — возможно конец (простая эвристика)
                            if len(chunk) < 65536:
                                break
                    except BlockingIOError:
                        pass
                    data = b"".join(chunks)
                    key = f"{addr[0]}:{addr[1]}"
                    if not data:
                        self.clients[key] = None
                        self.add_status_item(f"{key} connected but sent empty payload")
                        self.add_client_row(key)
                        try:
                            conn.sendall(b'OK')
                        except Exception:
                            pass
                        return

                    text = data.decode('utf-8', errors='replace')
                    # попробуем распарсить JSON
                    payload = None
                    try:
                        payload = json.loads(text)
                    except Exception:
                        payload = text  # сохраняем необработанную строку

                    # сохраняем, но не показываем содержимое
                    self.clients[key] = payload
                    self.add_status_item(f"Stored payload from {key}")
                    self.add_client_row(key)

                    # ответ клиенту
                    try:
                        conn.sendall(b'OK')
                    except Exception:
                        pass
            else:
                self.add_status_item("No incoming connection at the moment.")
        except Exception as e:
            self.add_status_item(f"Error accepting connection: {e}")

    def show_info(self, key: str):
        """Открывает окно с красиво отформатированной информацией из self.clients[key]."""
        payload = self.clients.get(key)
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Info from {key}")
        dlg.setMinimumSize(500, 400)
        layout = QVBoxLayout()

        if payload is None:
            text = "No payload received (empty or not parsed)."
        elif isinstance(payload, dict):
            # форматируем красиво: CPU, GPU, RAM, Disk count и Programs — отдельные секции
            pretty = json.dumps(payload, ensure_ascii=False, indent=2)
            # используем QTextEdit для удобного просмотра
            text = pretty
        else:
            # строка
            text = str(payload)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(text)
        layout.addWidget(text_edit)

        dlg.setLayout(layout)
        dlg.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(host='0.0.0.0', port=50000)
    window.show()
    sys.exit(app.exec())
