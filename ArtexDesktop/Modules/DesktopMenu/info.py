import os
import getpass
import socket
from datetime import datetime
from pathlib import Path
import psutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer, Qt

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

        # --- FOTO DO USUÁRIO (~/.face) E CABEÇALHO ---
        user_header_layout = QHBoxLayout()

        avatar_label = QLabel()
        avatar_label.setFixedSize(80, 80)
        avatar_label.setStyleSheet("border-radius: 40px; border: 2px solid #89b4fa; background-color: #222;")
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Procura por ~/.face ou ~/.face.icon
        home = Path.home()
        face_path = home / ".face"
        if not face_path.exists():
            face_path = home / ".face.icon"

        if face_path.exists():
            pix = QPixmap(str(face_path))
            if not pix.isNull():
                scaled_pix = pix.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                avatar_label.setPixmap(scaled_pix)
            else:
                avatar_label.setText("Sem Foto")
        else:
            avatar_label.setText("Sem Foto")

        user_header_layout.addWidget(avatar_label)

        header_text_layout = QVBoxLayout()
        header_text_layout.addWidget(QLabel("<h1>Informações do Painel</h1>"))
        
        user_name = getpass.getuser()
        hostname = socket.gethostname()
        header_text_layout.addWidget(QLabel(f"<b>Usuário:</b> {user_name} | <b>Host:</b> {hostname}"))
        
        user_header_layout.addLayout(header_text_layout)
        user_header_layout.addStretch()

        layout.addLayout(user_header_layout)

        # --- INFORMAÇÕES FIXAS ---
        iso_info = self.get_iso_info()
        layout.addWidget(QLabel(f"<b>ISO Info:</b> {iso_info}"))

        uname = os.uname()
        layout.addWidget(QLabel(f"<b>Kernel:</b> {uname.release} ({uname.machine})"))

        layout.addWidget(QLabel("<h3>Desempenho & Status</h3>"))

        # --- LABELS DINÂMICAS ---
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

        self.update_stats()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

        layout.addStretch()
        layout.addWidget(QLabel("<b>Criador:</b> Dimitrof04"))

    def update_stats(self):
        now = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        self.time_label.setText(f"<b>Data / Hora:</b> {now}")

        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = str(uptime).split('.')[0]
        self.uptime_label.setText(f"<b>Tempo Ligado (Uptime):</b> {uptime_str}")

        cpu_usage = psutil.cpu_percent()
        cpu_count = psutil.cpu_count(logical=True)
        self.cpu_label.setText(f"<b>Uso de CPU:</b> {cpu_usage}% ({cpu_count} threads)")

        ram = psutil.virtual_memory()
        ram_used_gb = ram.used / (1024**3)
        ram_total_gb = ram.total / (1024**3)
        self.ram_label.setText(f"<b>Memória RAM:</b> {ram_used_gb:.2f} GB / {ram_total_gb:.2f} GB ({ram.percent}%)")

        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        self.disk_label.setText(f"<b>Armazenamento (/):</b> {disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB ({disk.percent}%)")