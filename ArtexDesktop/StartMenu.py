#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

from Modules.StartMenu.style import get_stylesheet
from Modules.StartMenu.apps_tab import AppsTab
from Modules.StartMenu.system_tab import SystemTab

CONFIG_PATH = str(Path.home() / ".config" / "Desktop.conf")
FAVORITES_PATH = str(Path.home() / ".local" / "share" / "ArtexDesktop" / "FavoritesApps")

class HyprMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("HyprMenuWindow")
        self.setFixedSize(450, 420)
        self.setProperty("class", "hypr_menu")

        self.last_config_mtime = 0
        self.init_ui()

        # Timer ultra-leve para checar modificação no Desktop.conf e posição do mouse[cite: 2]
        self.sync_timer = QTimer(self)
        self.sync_timer.setInterval(200) # Checa 5 vezes por segundo (0% uso de RAM/CPU)
        self.sync_timer.timeout.connect(self.on_timer_tick)
        self.sync_timer.start()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        tabs = QTabWidget()

        self.apps_tab = AppsTab(FAVORITES_PATH)
        self.system_tab = SystemTab(CONFIG_PATH, self.update_style)

        tabs.addTab(self.apps_tab, "📱 Apps")
        tabs.addTab(self.system_tab, "⚡ Sistema")

        main_layout.addWidget(tabs)
        self.update_style()

    def update_style(self):
        """Lê as novas cores do Desktop.conf e reaplica na hora."""
        qss, accent_color, theme_mode, btn_bg, text_color = get_stylesheet(CONFIG_PATH)
        self.setStyleSheet(qss)
        self.system_tab.update_styles(btn_bg, text_color)

    def on_timer_tick(self):
        # 1. Checa se o arquivo Desktop.conf foi modificado por qualquer script
        if os.path.exists(CONFIG_PATH):
            mtime = os.path.getmtime(CONFIG_PATH)
            if mtime != self.last_config_mtime:
                self.last_config_mtime = mtime
                self.update_style()

        # 2. Fecha a janela se o mouse sair dos limites[cite: 2]
        cursor_pos = QCursor.pos()
        local_pos = self.mapFromGlobal(cursor_pos)
        if not self.rect().contains(local_pos):
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HyprMenu()
    window.show()
    sys.exit(app.exec())