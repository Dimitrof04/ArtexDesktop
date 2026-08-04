import subprocess
import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QListWidget, QComboBox, QSlider
)

class SystemConfigTab(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        self.sinks_map = {}
        self.sources_map = {}
        self.bt_map = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("<h1>System Config</h1>"))

        # --- REDE & CONECTIVIDADE (CABO + WI-FI) ---
        layout.addWidget(QLabel("<h2>Rede (Cabo & Wi-Fi)</h2>"))
        self.net_toggle = QCheckBox("Habilitar Rede (Geral)")
        self.net_toggle.stateChanged.connect(self.toggle_network)
        layout.addWidget(self.net_toggle)

        self.network_status_label = QLabel("<b>Status:</b> Verificando...")
        layout.addWidget(self.network_status_label)

        scan_wifi_btn = QPushButton("Procurar Redes Wi-Fi")
        scan_wifi_btn.clicked.connect(self.scan_wifi_networks)
        layout.addWidget(scan_wifi_btn)

        self.wifi_list = QListWidget()
        self.wifi_list.setFixedHeight(100)
        layout.addWidget(self.wifi_list)

        # --- BLUETOOTH ---
        layout.addWidget(QLabel("<h2>Bluetooth</h2>"))
        self.bt_toggle = QCheckBox("Habilitar Bluetooth")
        self.bt_toggle.stateChanged.connect(self.toggle_bluetooth)
        layout.addWidget(self.bt_toggle)

        layout.addWidget(QLabel("Dispositivo Bluetooth:"))
        bt_select_layout = QHBoxLayout()
        self.bt_combo = QComboBox()
        connect_bt_btn = QPushButton("Conectar / Selecionar")
        connect_bt_btn.clicked.connect(self.set_default_bluetooth_device)
        bt_select_layout.addWidget(self.bt_combo)
        bt_select_layout.addWidget(connect_bt_btn)
        layout.addLayout(bt_select_layout)

        # --- SOM (PIPEWIRE) ---
        layout.addWidget(QLabel("<h2>Som (PipeWire)</h2>"))
        
        # Dispositivo de Saída (Speakers/Headphones)
        layout.addWidget(QLabel("Saída de Áudio Padrão:"))
        sink_select_layout = QHBoxLayout()
        self.sink_combo = QComboBox()
        set_sink_btn = QPushButton("Definir Padrão")
        set_sink_btn.clicked.connect(self.set_default_sink)
        sink_select_layout.addWidget(self.sink_combo)
        sink_select_layout.addWidget(set_sink_btn)
        layout.addLayout(sink_select_layout)

        layout.addWidget(QLabel("Volume Principal (Saída):"))
        sink_slider_layout = QHBoxLayout()
        self.sink_slider = QSlider(Qt.Orientation.Horizontal)
        self.sink_slider.setRange(0, 100)
        self.sink_slider.valueChanged.connect(self.set_sink_volume)
        self.sink_vol_label = QLabel("50%")
        sink_slider_layout.addWidget(self.sink_slider)
        sink_slider_layout.addWidget(self.sink_vol_label)
        layout.addLayout(sink_slider_layout)

        # Dispositivo de Entrada (Microfone)
        layout.addWidget(QLabel("Entrada de Áudio Padrão (Microfone):"))
        source_select_layout = QHBoxLayout()
        self.source_combo = QComboBox()
        set_source_btn = QPushButton("Definir Padrão")
        set_source_btn.clicked.connect(self.set_default_source)
        source_select_layout.addWidget(self.source_combo)
        source_select_layout.addWidget(set_source_btn)
        layout.addLayout(source_select_layout)

        layout.addWidget(QLabel("Volume do Microfone:"))
        mic_slider_layout = QHBoxLayout()
        self.mic_slider = QSlider(Qt.Orientation.Horizontal)
        self.mic_slider.setRange(0, 100)
        self.mic_slider.valueChanged.connect(self.set_mic_volume)
        self.mic_vol_label = QLabel("50%")
        mic_slider_layout.addWidget(self.mic_slider)
        mic_slider_layout.addWidget(self.mic_vol_label)
        layout.addLayout(mic_slider_layout)

        self.refresh_system_status()
        layout.addStretch()

    def refresh_system_status(self):
        # 1. Status Geral da Rede (Cabo + Wi-Fi)
        try:
            res = subprocess.run(["nmcli", "networking"], capture_output=True, text=True)
            self.net_toggle.setChecked("enabled" in res.stdout.lower())
        except Exception:
            pass

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

        # 2. Bluetooth (Habilitar + Dispositivos)
        try:
            # Define um timeout de 1 segundo para não travar o boot da janela
            res = subprocess.run(
                ["bluetoothctl", "show"], 
                capture_output=True, 
                text=True, 
                timeout=1
            )
            if res.returncode == 0 and "Powered: yes" in res.stdout:
                # Bluetooth está ligado
                if hasattr(self, 'bt_status_label'):
                    self.bt_status_label.setText("Bluetooth: Ativado")
            else:
                if hasattr(self, 'bt_status_label'):
                    self.bt_status_label.setText("Bluetooth: Desativado / Offline")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            if hasattr(self, 'bt_status_label'):
                self.bt_status_label.setText("Bluetooth: Inacessível")
        except Exception as e:
            print(f"Erro ao checar bluetooth: {e}")
    
            # 3. Som (Dispositivos + Volume)
            self.load_audio_devices()
    
        try:
            res = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], capture_output=True, text=True)
            vol_float = float(res.stdout.split()[1])
            vol_int = int(vol_float * 100)
            self.sink_slider.setValue(vol_int)
            self.sink_vol_label.setText(f"{vol_int}%")
        except Exception:
            pass

    def toggle_network(self, state):
        status = "on" if state == 2 else "off"
        subprocess.run(["nmcli", "networking", status], stderr=subprocess.DEVNULL)

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

    def load_bluetooth_devices(self):
        self.bt_combo.clear()
        self.bt_map.clear()
        try:
            res = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                parts = line.split(" ", 2)
                if len(parts) >= 3:
                    mac = parts[1]
                    name = parts[2]
                    self.bt_map[name] = mac
                    self.bt_combo.addItem(name)
        except Exception:
            pass

    def set_default_bluetooth_device(self):
        name = self.bt_combo.currentText()
        mac = self.bt_map.get(name)
        if mac:
            subprocess.run(["bluetoothctl", "connect", mac], stderr=subprocess.DEVNULL)

    def load_audio_devices(self):
        self.sink_combo.clear()
        self.source_combo.clear()
        self.sinks_map.clear()
        self.sources_map.clear()

        try:
            res = subprocess.run(["wpctl", "status"], capture_output=True, text=True)
            lines = res.stdout.splitlines()

            current_section = None
            for line in lines:
                if "Sinks:" in line:
                    current_section = "sinks"
                    continue
                elif "Sources:" in line:
                    current_section = "sources"
                    continue
                elif "Filters:" in line or "Streams:" in line:
                    current_section = None

                if current_section:
                    match = re.search(r"(\*?)\s*(\d+)\.\s+(.*?)\[", line)
                    if match:
                        is_default = match.group(1) == "*"
                        node_id = match.group(2)
                        name = match.group(3).strip()

                        label = f"{'* ' if is_default else ''}{name} (ID: {node_id})"
                        
                        if current_section == "sinks":
                            self.sinks_map[label] = node_id
                            self.sink_combo.addItem(label)
                            if is_default:
                                self.sink_combo.setCurrentText(label)
                        elif current_section == "sources":
                            self.sources_map[label] = node_id
                            self.source_combo.addItem(label)
                            if is_default:
                                self.source_combo.setCurrentText(label)
        except Exception:
            pass

    def set_default_sink(self):
        label = self.sink_combo.currentText()
        node_id = self.sinks_map.get(label)
        if node_id:
            subprocess.run(["wpctl", "set-default", node_id], stderr=subprocess.DEVNULL)

    def set_default_source(self):
        label = self.source_combo.currentText()
        node_id = self.sources_map.get(label)
        if node_id:
            subprocess.run(["wpctl", "set-default", node_id], stderr=subprocess.DEVNULL)

    def set_sink_volume(self, value):
        self.sink_vol_label.setText(f"{value}%")
        vol_float = value / 100.0
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{vol_float:.2f}"], stderr=subprocess.DEVNULL)

    def set_mic_volume(self, value):
        self.mic_vol_label.setText(f"{value}%")
        vol_float = value / 100.0
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SOURCE@", f"{vol_float:.2f}"], stderr=subprocess.DEVNULL)