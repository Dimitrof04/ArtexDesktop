# modules/info.py

import os
import getpass
import socket
from datetime import datetime, timedelta
import psutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer

class InfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def get_iso_info(self) -> str:
        """Tenta detectar a distro Linux/Arch (Arch, CachyOS, BlackArch, etc)."""
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
        layout.setSpacing(10)

        layout.addWidget(QLabel("<h1>Informações do Painel</h1>"))

        # --- INFORMAÇÕES FIXAS ---
        iso_info = self.get_iso_info()
        layout.addWidget(QLabel(f"<b>ISO Info:</b> {iso_info}"))

        user_name = getpass.getuser()
        layout.addWidget(QLabel(f"<b>User:</b> {user_name}"))

        hostname = socket.gethostname()
        layout.addWidget(QLabel(f"<b>Rootname / Host:</b> {hostname}"))

        # Kernel / Arquitetura
        uname = os.uname()
        layout.addWidget(QLabel(f"<b>Kernel:</b> {uname.release} ({uname.machine})"))

        layout.addWidget(QLabel("<h3>Desempenho & Status</h3>"))

        # --- LABELS DINÂMICAS (Atualizadas pelo Timer) ---
        self.time_label = QLabel()
        layout.addWidget(self.time_label)

        self.uptime_label = QLabel()
        layout.addWidget(self.uptime_label)

        self.cpu_label = QLabel()
        layout.addWidget(self.cpu_label)

        self.ram_label = QLabel()
        layout.addWidget(self.ram_label)

        self.disk_label = QLabel()
        layout.addWidget(self.disk_label)

        # Atualiza uma vez na inicialização
        self.update_stats()

        # Timer para atualizar os dados dinamicos a cada segundo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

        # --- CRÉDITOS ---
        layout.addStretch()
        layout.addWidget(QLabel("<b>Criador:</b> Dimitrof04"))

    def update_stats(self):
        # 1. Data / Hora
        now = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        self.time_label.setText(f"<b>Data / Hora:</b> {now}")

        # 2. Tempo de Atividade (Uptime)
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        # Formata tirando os milissegundos
        uptime_str = str(uptime).split('.')[0]
        self.uptime_label.setText(f"<b>Tempo Ligado (Uptime):</b> {uptime_str}")

        # 3. Uso de CPU
        cpu_usage = psutil.cpu_percent()
        cpu_count = psutil.cpu_count(logical=True)
        self.cpu_label.setText(f"<b>Uso de CPU:</b> {cpu_usage}% ({cpu_count} threads)")

        # 4. Uso de Memória RAM
        ram = psutil.virtual_memory()
        ram_used_gb = ram.used / (1024**3)
        ram_total_gb = ram.total / (1024**3)
        self.ram_label.setText(f"<b>Memória RAM:</b> {ram_used_gb:.2f} GB / {ram_total_gb:.2f} GB ({ram.percent}%)")

        # 5. Armazenamento (Disco Principal '/')
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        self.disk_label.setText(f"<b>Armazenamento (/):</b> {disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB ({disk.percent}%)")