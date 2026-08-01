#!/usr/bin/env python3

import sys
import subprocess
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QListWidget, QStackedWidget,
    QHBoxLayout, QScrollArea, QMainWindow
)
from PyQt6.QtCore import QSettings, QTimer

from Modules.DesktopMenu.Style import get_stylesheet
from Modules.DesktopMenu.personalization import PersonalizationTab
from Modules.DesktopMenu.keybinds import KeybindsTab
from Modules.DesktopMenu.system_config import SystemConfigTab
from Modules.DesktopMenu.info import InfoTab
from Modules.theme_sync import set_system_theme # Já foi importado aqui!

config_path = str(Path.home() / ".config" / "Desktop.conf")

class SettingsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurações do Desktop")
        self.resize(720, 420)
        self.last_config_mtime = 0
        self.setProperty("class", "hypr_menu")

        
        self.settings = QSettings(config_path, QSettings.Format.IniFormat)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Menu Lateral
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(190)
        self.sidebar.addItem("Personalização")
        self.sidebar.addItem("Atalhos & Apps")
        self.sidebar.addItem("Configurações do Sistema")
        self.sidebar.addItem("Info")

        # Área de Conteúdo Modularizada
        self.content_area = QStackedWidget()

        # Inicializa abas
        self.personalization_tab = PersonalizationTab(self)
        self.keybinds_tab = KeybindsTab(self)
        self.system_config_tab = SystemConfigTab(self)
        self.info_tab = InfoTab()

        self.content_area.addWidget(self.make_scrollable(self.personalization_tab))
        self.content_area.addWidget(self.make_scrollable(self.keybinds_tab))
        self.content_area.addWidget(self.make_scrollable(self.system_config_tab))
        self.content_area.addWidget(self.make_scrollable(self.info_tab))

        self.sidebar.currentRowChanged.connect(self.content_area.setCurrentIndex)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

        self.sidebar.setCurrentRow(0)
        self.load_settings()

        # TIMER DE SINCRONIZAÇÃO EM TEMPO REAL
        self.sync_timer = QTimer()
        self.sync_timer.setInterval(200) # Checa a cada 300ms
        self.sync_timer.timeout.connect(self.check_external_theme_change)
        self.sync_timer.start()

        self.reload_theme()

    def check_external_theme_change(self):
        """Verifica se o Desktop.conf mudou (ex: alterado pelo StartMenu) e recarrega."""
        if os.path.exists(config_path):
            mtime = os.path.getmtime(config_path)
            if mtime != self.last_config_mtime:
                self.last_config_mtime = mtime
                self.reload_theme()

    def reload_theme(self):
        """Lê o Desktop.conf e reaplica o tema no próprio DektopConfigMenu."""
        # Se você tiver um método para recarregar o stylesheet do DesktopConfigMenu:
        settings = QSettings(config_path, QSettings.Format.IniFormat)
        settings.beginGroup("theme")
        theme_mode = str(settings.value("theme", "Dark")).strip().capitalize()
        settings.endGroup()

        # Atualiza a ComboBox visual se ela existir no seu menu
        if hasattr(self, 'theme_combo'):
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentText(theme_mode)
            self.theme_combo.blockSignals(False)

        # Re-aplica o estilo da janela (chame sua função de estilo do Modules/DesktopMenu/Style.py)
        # Exemplo: apply_style(self, CONFIG_PATH)
        self.update()
        self.apply_styles()

    def make_scrollable(self, widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def apply_styles(self):
        is_light = self.theme_combo.currentText() == "Light"
        accent_color = self.color_input.text().strip()
        self.setStyleSheet(get_stylesheet(is_light, accent_color))

    def load_settings(self):
        # 1. Tema
        self.settings.beginGroup("theme")
        self.theme_combo.setCurrentText(str(self.settings.value("theme", "Dark")))
        self.color_input.setText(str(self.settings.value("colortheme", "#89b4fa")))
        self.settings.endGroup()

        # 2. Hyprland
        self.settings.beginGroup("Hyprland")
        self.hypr_rounding_input.setText(str(self.settings.value("rounding", "10")))
        self.hypr_border_size_input.setText(str(self.settings.value("border_size", "2")))
        self.hypr_active_border_input.setText(str(self.settings.value("active_border", "0xff89b4fa")))
        self.settings.endGroup()

        # 3. Wallpapers
        self.settings.beginGroup("Wallpapers")
        self.wallpaper_path_input.setText(str(self.settings.value("Wallpaper", "")))
        self.wallpaper_folder_input.setText(
            str(self.settings.value("WallpapersFolder", str(Path.home() / "Pictures/Wallpapers")))
        )
        self.awww_translate_options.setCurrentText(str(self.settings.value("awww_transition", "random")))
        self.settings.endGroup()

        # 4. Apps & Keybinds
        self.settings.beginGroup("Apps")
        self.app_terminal_input.setText(str(self.settings.value("terminal", "kitty")))
        self.app_filemanager_input.setText(str(self.settings.value("filemanager", "dolphin")))
        self.app_menu_input.setText(str(self.settings.value("menu", "hyprlauncher")))
        self.app_Browser_input.setText(str(self.settings.value("Browser", "firefox")))
        self.settings.endGroup()

        self.settings.beginGroup("Keybinds")
        self.key_mod_combo.setCurrentText(str(self.settings.value("main_mod", "SUPER")))
        self.bind_terminal_input.setText(str(self.settings.value("bind_terminal", "Q")))
        self.bind_close_input.setText(str(self.settings.value("bind_close", "C")))
        self.bind_menu_input.setText(str(self.settings.value("bind_menu", "R")))
        self.bind_filemanager_input.setText(str(self.settings.value("bind_filemanager", "E")))
        self.bind_Browser_input.setText(str(self.settings.value("bind_browser", "W")))
        self.bind_ToggleFloting.setText(str(self.settings.value("bind_ToggleFloting", "Space")))
        self.settings.endGroup()

        self.apply_styles()

    def save_settings(self):
        selected_theme = self.theme_combo.currentText()
        accent_color = self.color_input.text().strip() or "#89b4fa"

        # Dispara a atualização global do sistema e notifica o StartMenu
        set_system_theme(selected_theme, accent_color)

        rounding = self.hypr_rounding_input.text().strip()
        border_size = self.hypr_border_size_input.text().strip()
        active_border = self.hypr_active_border_input.text().strip()

        if active_border.startswith("#"):
            active_border = "0xff" + active_border.lstrip("#")

        # Tema
        self.settings.beginGroup("theme")
        self.settings.setValue("theme", selected_theme)
        self.settings.setValue("colortheme", accent_color)
        self.settings.endGroup()

        # Hyprland
        self.settings.beginGroup("Hyprland")
        if rounding: self.settings.setValue("rounding", rounding)
        if border_size: self.settings.setValue("border_size", border_size)
        if active_border: self.settings.setValue("active_border", active_border)
        self.settings.endGroup()

        # Wallpapers
        self.settings.beginGroup("Wallpapers")
        if self.wallpaper_path_input.text():
            self.settings.setValue("Wallpaper", self.wallpaper_path_input.text())
        if self.wallpaper_folder_input.text():
            self.settings.setValue("WallpapersFolder", self.wallpaper_folder_input.text())
        self.settings.setValue("awww_transition", self.awww_translate_options.currentText())
        self.settings.endGroup()

        # Apps & Keybinds
        self.settings.beginGroup("Apps")
        self.settings.setValue("terminal", self.app_terminal_input.text().strip() or "kitty")
        self.settings.setValue("filemanager", self.app_filemanager_input.text().strip() or "dolphin")
        self.settings.setValue("menu", self.app_menu_input.text().strip() or "hyprlauncher")
        self.settings.setValue("Browser", self.app_Browser_input.text().strip() or "firefox")
        self.settings.endGroup()

        self.settings.beginGroup("Keybinds")
        self.settings.setValue("main_mod", self.key_mod_combo.currentText())
        self.settings.setValue("bind_terminal", self.bind_terminal_input.text().strip() or "Q")
        self.settings.setValue("bind_close", self.bind_close_input.text().strip() or "C")
        self.settings.setValue("bind_menu", self.bind_menu_input.text().strip() or "R")
        self.settings.setValue("bind_filemanager", self.bind_filemanager_input.text().strip() or "E")
        self.settings.setValue("bind_browser", self.bind_Browser_input.text().strip() or "W")
        self.settings.setValue("bind_ToggleFloting", self.bind_ToggleFloting.text().strip() or "Space")
        self.settings.endGroup()

        self.settings.sync()
        self.apply_styles()

        selected_theme = self.theme_combo.currentText()
        accent_color = self.color_input.text() if hasattr(self, 'color_input') else "#0cb6ff"
        
        set_system_theme(selected_theme, accent_color)

        # Aplicar no Hyprland
        try:
            subprocess.run(["hyprctl", "eval", f"hl.config({{ decoration = {{ rounding = {rounding} }} }})"], stderr=subprocess.DEVNULL)
            subprocess.run(["hyprctl", "eval", f"hl.config({{ general = {{ border_size = {border_size} }} }})"], stderr=subprocess.DEVNULL)
            lua_color_cmd = f'hl.config({{ general = {{ col = {{ active_border = {{ colors = {{ "{active_border}", "{active_border}" }} }} }} }} }})'
            subprocess.run(["hyprctl", "eval", lua_color_cmd], stderr=subprocess.DEVNULL)
            subprocess.run(["hyprctl", "reload"], stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Erro hyprctl: {e}")

        # Wallpaper
        wp = self.wallpaper_path_input.text().strip()
        if wp and os.path.exists(wp):
            trans = self.awww_translate_options.currentText()
            cmd = ["awww", "img", "--transition-type", trans, "--transition-duration", "3", "--transition-fps", "60", wp]
            try:
                subprocess.run(cmd, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Erro awww: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsApp()
    window.show()
    sys.exit(app.exec())