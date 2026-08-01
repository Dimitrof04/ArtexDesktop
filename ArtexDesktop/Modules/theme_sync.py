import os
import time
import subprocess
from pathlib import Path
from PyQt6.QtCore import QSettings

CONFIG_PATH = str(Path.home() / ".config" / "Desktop.conf")
SIGNAL_FILE = "/tmp/desktop_theme.signal"

def set_system_theme(theme_mode: str, colortheme: str = None):
    """Atualiza o Desktop.conf, notifica o GTK/Firefox/Discord e envia sinal pros menus."""
    is_dark = theme_mode.capitalize() == "Dark"
    
    # 1. Atualiza o arquivo Desktop.conf
    settings = QSettings(CONFIG_PATH, QSettings.Format.IniFormat)
    settings.beginGroup("theme")
    settings.setValue("theme", "Dark" if is_dark else "Light")
    if colortheme:
        settings.setValue("colortheme", colortheme)
    settings.endGroup()
    settings.sync()

    # 2. Muda o tema Global do Sistema (Firefox, Discord, GTK Apps)
    scheme = "prefer-dark" if is_dark else "prefer-light"
    subprocess.Popen(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", scheme], stderr=subprocess.DEVNULL)
    subprocess.Popen(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Adwaita-dark" if is_dark else "Adwaita"], stderr=subprocess.DEVNULL)

    # 3. Notifica o outro app atualizando o timestamp do arquivo de sinal
    with open(SIGNAL_FILE, "w") as f:
        f.write(str(time.time()))