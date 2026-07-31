# modules/info.py

import os
import getpass
import socket
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer

class InfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def get_iso_info(self) -> str:
        """Tenta detectar a distro Arch (Arch, CachyOS, BlackArch, etc)."""
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith("PRETTY_NAME="):
                            return line.split("=")[1].strip().strip('"')
        except Exception:
            pass
        return "Arch Linux / Base System"

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("<h1>Informações do Painel</h1>"))

        # 1. ISO Info
        iso_info = self.get_iso_info()
        layout.addWidget(QLabel(f"<b>ISO Info:</b> {iso_info}"))

        # 2. User
        user_name = getpass.getuser()
        layout.addWidget(QLabel(f"<b>User:</b> {user_name}"))

        # 3. Rootname (Hostname)
        hostname = socket.gethostname()
        layout.addWidget(QLabel(f"<b>Rootname / Host:</b> {hostname}"))

        # 4. Time / Data (com atualização em tempo real)
        self.time_label = QLabel()
        layout.addWidget(self.time_label)
        self.update_time()

        # Timer para atualizar a data/hora a cada segundo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # 5. Creator (Permanente Dimitrof04)
        layout.addWidget(QLabel("<b>Criador:</b> Dimitrof04"))

        layout.addStretch()

    def update_time(self):
        now = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        self.time_label.setText(f"<b>Data / Hora:</b> {now}")