# modules/system_config.py

import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QListWidget, QComboBox, QSlider
)

class SystemConfigTab(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("<h1>System Config</h1>"))

        # --- WI-FI ---
        layout.addWidget(QLabel("<h2>Rede & Wi-Fi</h2>"))
        self.wifi_toggle = QCheckBox("Habilitar Wi-Fi")
        self.wifi_toggle.stateChanged.connect(self.toggle_wifi)
        layout.addWidget(self.wifi_toggle)

        self.network_status_label = QLabel("<b>Status:</b> Verificando...")
        layout.addWidget(self.network_status_label)

        scan_wifi_btn = QPushButton("Procurar Redes Wi-Fi")
        scan_wifi_btn.clicked.connect(self.scan_wifi_networks)
        layout.addWidget(scan_wifi_btn)

        self.wifi_list = QListWidget()
        self.wifi_list.setFixedHeight(110)
        layout.addWidget(self.wifi_list)

        # --- BLUETOOTH ---
        layout.addWidget(QLabel("<h2>Bluetooth</h2>"))
        self.bt_toggle = QCheckBox("Habilitar Bluetooth")
        self.bt_toggle.stateChanged.connect(self.toggle_bluetooth)
        layout.addWidget(self.bt_toggle)

        # --- SOM ---
        layout.addWidget(QLabel("<h2>Som (PipeWire)</h2>"))
        
        layout.addWidget(QLabel("Volume do Microfone:"))
        mic_slider_layout = QHBoxLayout()
        self.mic_slider = QSlider(Qt.Orientation.Horizontal)
        self.mic_slider.setRange(0, 100)
        self.mic_slider.valueChanged.connect(self.set_mic_volume)
        self.mic_vol_label = QLabel("50%")
        mic_slider_layout.addWidget(self.mic_slider)
        mic_slider_layout.addWidget(self.mic_vol_label)
        layout.addLayout(mic_slider_layout)

        layout.addWidget(QLabel("Volume Principal (Saída):"))
        sink_slider_layout = QHBoxLayout()
        self.sink_slider = QSlider(Qt.Orientation.Horizontal)
        self.sink_slider.setRange(0, 100)
        self.sink_slider.valueChanged.connect(self.set_sink_volume)
        self.sink_vol_label = QLabel("50%")
        sink_slider_layout.addWidget(self.sink_slider)
        sink_slider_layout.addWidget(self.sink_vol_label)
        layout.addLayout(sink_slider_layout)

        self.refresh_system_status()
        layout.addStretch()

    def refresh_system_status(self):
        # 1. Wi-Fi
        try:
            res = subprocess.run(["nmcli", "radio", "wifi"], capture_output=True, text=True)
            self.wifi_toggle.setChecked("enabled" in res.stdout.lower())
        except Exception:
            pass

        # 2. Status Conexão
        try:
            res = subprocess.run(["nmcli", "-t", "-f", "TYPE,STATE", "dev"], capture_output=True, text=True)
            status = "Desconectado"
            for line in res.stdout.splitlines():
                if "ethernet:connected" in line:
                    status = "Conectado via Cabo (Ethernet)"
                    break
                elif "wifi:connected" in line:
                    status = "Conectado via Wi-Fi"
                    break
            self.network_status_label.setText(f"<b>Status:</b> {status}")
        except Exception:
            self.network_status_label.setText("<b>Status:</b> Erro ao obter status")

        # 3. Bluetooth
        try:
            res = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True)
            self.bt_toggle.setChecked("Powered: yes" in res.stdout)
        except Exception:
            pass

        # 4. Som
        try:
            res = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], capture_output=True, text=True)
            vol_float = float(res.stdout.split()[1])
            vol_int = int(vol_float * 100)
            self.sink_slider.setValue(vol_int)
            self.sink_vol_label.setText(f"{vol_int}%")
        except Exception:
            pass

    def toggle_wifi(self, state):
        status = "on" if state == 2 else "off"
        subprocess.run(["nmcli", "radio", "wifi", status], stderr=subprocess.DEVNULL)

    def scan_wifi_networks(self):
        self.wifi_list.clear()
        try:
            subprocess.run(["nmcli", "dev", "wifi", "rescan"], stderr=subprocess.DEVNULL)
            res = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"], capture_output=True, text=True)
            networks = set()
            for line in res.stdout.splitlines():
                parts = line.split(":")
                if len(parts) >= 2 and parts[0].strip():
                    networks.add(f"{parts[0].strip()} ({parts[1].strip()}% Sinal)")

            if networks:
                for net in list(networks)[:8]:
                    self.wifi_list.addItem(net)
            else:
                self.wifi_list.addItem("Nenhuma rede encontrada")
        except Exception:
            self.wifi_list.addItem("Erro ao buscar redes (nmcli não encontrado)")

    def toggle_bluetooth(self, state):
        status = "on" if state == 2 else "off"
        subprocess.run(["bluetoothctl", "power", status], stderr=subprocess.DEVNULL)

    def set_sink_volume(self, value):
        self.sink_vol_label.setText(f"{value}%")
        vol_float = value / 100.0
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{vol_float:.2f}"], stderr=subprocess.DEVNULL)

    def set_mic_volume(self, value):
        self.mic_vol_label.setText(f"{value}%")
        vol_float = value / 100.0
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SOURCE@", f"{vol_float:.2f}"], stderr=subprocess.DEVNULL)