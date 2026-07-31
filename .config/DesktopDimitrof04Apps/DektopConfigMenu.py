#!/usr/bin/env python3

import sys
import subprocess
import random
import os
from pathlib import Path
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QListWidget, QStackedWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QFileDialog, QColorDialog
)

class SettingsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurações do Desktop")
        self.resize(780, 500)

        # Caminho do arquivo de configuração (~/.config/Desktop.conf)
        config_path = str(Path.home() / ".config" / "Desktop.conf")
        self.settings = QSettings(config_path, QSettings.Format.IniFormat)

        # Layout Principal (Horizontal: Menu Esquerda | Conteúdo Direita)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 1. Menu Lateral
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItem("Personalizacao")
        self.sidebar.addItem("Rede & Bluetooth")
        self.sidebar.addItem("Info")

        # 2. Área de Conteúdo (Páginas sobrepostas)
        self.content_area = QStackedWidget()

        # Adiciona as páginas
        self.content_area.addWidget(self.create_theme_page())
        self.content_area.addWidget(self.create_network_page())
        self.content_area.addWidget(self.create_info_page())

        # Conecta o clique do menu à troca de página
        self.sidebar.currentRowChanged.connect(self.content_area.setCurrentIndex)

        # Adiciona ao Layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

        self.sidebar.setCurrentRow(0)  # Seleciona a primeira opção por padrão
        self.load_settings()           # Carrega as configurações (já chama o apply_styles)

    def select_wallpaper_file(self):
        """Abre o seletor de arquivos para escolher uma imagem."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Wallpaper",
            str(Path.home()),
            "Imagens (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if file_path:
            self.wallpaper_path_input.setText(file_path)

    def select_wallpaper_folder(self):
        """Abre o seletor de diretórios para escolher a pasta de wallpapers."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Wallpapers",
            str(Path.home())
        )
        if folder_path:
            self.wallpaper_folder_input.setText(folder_path)

    def create_theme_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<h1>Personalização</h1>"))

        # --- TEMA DO SISTEMA ---
        layout.addWidget(QLabel("<h2>Tema do Sistema</h2>"))
        
        layout.addWidget(QLabel("Modo Escuro / Claro:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        layout.addWidget(self.theme_combo)

        layout.addWidget(QLabel("Cor de Destaque (HEX):"))
        color_layout = QHBoxLayout()
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("#89b4fa")
        
        pick_color_btn = QPushButton("Escolher Cor")
        pick_color_btn.clicked.connect(self.select_theme_color)

        color_layout.addWidget(self.color_input)
        color_layout.addWidget(pick_color_btn)
        layout.addLayout(color_layout)

        # --- CONFIGURAÇÕES DO HYPRLAND ---
        layout.addWidget(QLabel("<h2>Hyprland</h2>"))

        # Arredondamento
        layout.addWidget(QLabel("Arredondamento de Borda (Rounding):"))
        self.hypr_rounding_input = QLineEdit()
        self.hypr_rounding_input.setPlaceholderText("10")
        layout.addWidget(self.hypr_rounding_input)

        # Espessura
        layout.addWidget(QLabel("Espessura da Borda (Border Size):"))
        self.hypr_border_size_input = QLineEdit()
        self.hypr_border_size_input.setPlaceholderText("2")
        layout.addWidget(self.hypr_border_size_input)

        # Cor da Borda Ativa com Color Picker
        layout.addWidget(QLabel("Cor da Borda Ativa:"))
        border_color_layout = QHBoxLayout()
        self.hypr_active_border_input = QLineEdit()
        self.hypr_active_border_input.setPlaceholderText("0xff89b4fa")

        pick_border_color_btn = QPushButton("Escolher Cor da Borda")
        pick_border_color_btn.clicked.connect(self.select_active_border_color)

        border_color_layout.addWidget(self.hypr_active_border_input)
        border_color_layout.addWidget(pick_border_color_btn)
        layout.addLayout(border_color_layout)

        # --- WALLPAPER ---
        layout.addWidget(QLabel("<h2>Wallpaper</h2>"))

        layout.addWidget(QLabel("Caminho do Wallpaper Atual:"))
        file_layout = QHBoxLayout()
        self.wallpaper_path_input = QLineEdit()
        browse_file_btn = QPushButton("Procurar...")
        browse_file_btn.clicked.connect(self.select_wallpaper_file)
        file_layout.addWidget(self.wallpaper_path_input)
        file_layout.addWidget(browse_file_btn)
        layout.addLayout(file_layout)

        layout.addWidget(QLabel("Pasta de Wallpapers:"))
        folder_layout = QHBoxLayout()
        self.wallpaper_folder_input = QLineEdit()
        browse_folder_btn = QPushButton("Procurar...")
        browse_folder_btn.clicked.connect(self.select_wallpaper_folder)
        folder_layout.addWidget(self.wallpaper_folder_input)
        folder_layout.addWidget(browse_folder_btn)
        layout.addLayout(folder_layout)

        layout.addWidget(QLabel("Tipo de Transição (awww):"))
        self.awww_translate_options = QComboBox()
        self.awww_translate_options.addItems([
            "none", "fade", "wipe", "wave", 
            "grow", "center", "any", "outer", "random"
        ])
        layout.addWidget(self.awww_translate_options)

        # --- BOTÕES DE AÇÃO ---
        save_btn = QPushButton("Salvar Configurações")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        RandomWallpaper_btn = QPushButton("Wallpaper Aleatório")
        RandomWallpaper_btn.clicked.connect(self.GetRandowWallpaper)
        layout.addWidget(RandomWallpaper_btn)

        layout.addStretch()
        return page

    def select_theme_color(self):
        """Abre a janela de seleção de cor para o Tema do Sistema"""
        color = QColorDialog.getColor()
        if color.isValid():
            # color.name() retorna uma string como "#89b4fa"
            self.color_input.setText(color.name())
    
    def select_active_border_color(self):
        """Abre a janela de seleção de cor para a Borda Ativa do Hyprland"""
        color = QColorDialog.getColor()
        if color.isValid():
            # Converte a cor selecionada para o formato do Hyprland (ex: "ff89b4fa" ou "0xff89b4fa")
            hex_color = color.name().lstrip("#")
            # Adicionamos "ff" na frente para a opacidade (100% visível)
            hypr_color = f"0xff{hex_color}"
            self.hypr_active_border_input.setText(hypr_color)

    def create_network_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("<h2>Rede & Conexões</h2>"))
        layout.addWidget(QLabel("<b>Wi-Fi / Ethernet:</b> Conectado"))
        layout.addWidget(QLabel("<b>Bluetooth:</b> Ativo"))

        layout.addStretch()
        return page

    def create_info_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("<h2>Informações do Sistema</h2>"))
        layout.addWidget(QLabel("<b>Versão:</b> 0.0.1"))
        layout.addWidget(QLabel("<b>Configuração:</b> ~/.config/Desktop.conf"))

        layout.addStretch()
        return page

    def set_wallpaper(self, image_path: str):
        """Executa o comando para trocar o wallpaper via awww com os parâmetros configurados."""
        if image_path and os.path.exists(image_path):
            transition_type = self.awww_translate_options.currentText()
            cmd = [
                "awww", "img",
                "--transition-type", transition_type,
                "--transition-duration", "3",
                "--transition-fps", "60",
                image_path
            ]
            try:
                subprocess.run(cmd, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Erro ao trocar o wallpaper: {e}")

    def load_settings(self):
        # 1. Carrega Tema
        self.settings.beginGroup("theme")
        self.theme_combo.setCurrentText(str(self.settings.value("theme", "Dark")))
        self.color_input.setText(str(self.settings.value("colortheme", "#89b4fa")))
        self.settings.endGroup()

        # 2. Carrega opções do Hyprland
        self.settings.beginGroup("Hyprland")
        self.hypr_rounding_input.setText(str(self.settings.value("rounding", "10")))
        self.hypr_border_size_input.setText(str(self.settings.value("border_size", "2")))
        self.hypr_active_border_input.setText(str(self.settings.value("active_border", "0xffffffff")))
        self.settings.endGroup()

        # 3. Carrega Wallpapers
        self.settings.beginGroup("Wallpapers")
        self.wallpaper_path_input.setText(str(self.settings.value("Wallpaper", "")))
        self.wallpaper_folder_input.setText(
            str(self.settings.value("WallpapersFolder", str(Path.home() / "Pictures/Wallpapers")))
        )
        self.awww_translate_options.setCurrentText(str(self.settings.value("awww_transition", "random")))
        self.settings.endGroup()

        self.apply_styles()

    def save_settings(self):
        selected_theme = self.theme_combo.currentText()
        accent_color = self.color_input.text().strip() or "#89b4fa"
        
        rounding = self.hypr_rounding_input.text().strip() or "10"
        border_size = self.hypr_border_size_input.text().strip() or "2"
        active_border = self.hypr_active_border_input.text().strip() or "0xffffffff"

        # Garante formatação válida pro Hyprland caso a pessoa tenha digitado #89b4fa direto
        if active_border.startswith("#"):
            active_border = "0xff" + active_border.lstrip("#")

        # 1. Grava no arquivo ~/.config/Desktop.conf
        self.settings.beginGroup("theme")
        self.settings.setValue("theme", selected_theme)
        self.settings.setValue("colortheme", accent_color)
        self.settings.endGroup()

        self.settings.beginGroup("Hyprland")
        self.settings.setValue("rounding", rounding)
        self.settings.setValue("border_size", border_size)
        self.settings.setValue("active_border", active_border)
        self.settings.endGroup()

        self.settings.beginGroup("Wallpapers")
        self.settings.setValue("Wallpaper", self.wallpaper_path_input.text())
        self.settings.setValue("WallpapersFolder", self.wallpaper_folder_input.text())
        self.settings.setValue("awww_transition", self.awww_translate_options.currentText())
        self.settings.endGroup()

        self.settings.sync()
        self.apply_styles()

        # 2. Aplica em tempo real no Hyprland (usando a nova sintaxe eval)
        try:
            # Seta o arredondamento (decoration.rounding)
            subprocess.run(["hyprctl", "eval", f"hl.config({{ decoration = {{ rounding = {rounding} }} }})"], stderr=subprocess.DEVNULL)
            
            # Seta a espessura da borda (general.border_size)
            subprocess.run(["hyprctl", "eval", f"hl.config({{ general = {{ border_size = {border_size} }} }})"], stderr=subprocess.DEVNULL)
            
            # Seta a cor da borda ativa (general.col.active_border)
            # Como active_border espera uma tabela no formato do seu lua: { colors = { "0xff89b4fa", "0xff89b4fa" } }
            lua_color_cmd = f'hl.config({{ general = {{ col = {{ active_border = {{ colors = {{ "{active_border}", "{active_border}" }} }} }} }} }})'
            subprocess.run(["hyprctl", "eval", lua_color_cmd], stderr=subprocess.DEVNULL)

        except Exception as e:
            print(f"Erro ao aplicar via hyprctl eval: {e}")

        # 3. Wallpaper
        wallpaper_path = self.wallpaper_path_input.text().strip()
        self.set_wallpaper(wallpaper_path)

    def GetRandowWallpaper(self):
        folder_path = self.wallpaper_folder_input.text()

        if not os.path.exists(folder_path):
            print("A pasta especificada não existe!")
            return

        # Lista imagens suportadas na pasta
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
        wallpapers = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]

        if wallpapers:
            wallpaper_escolhido = random.choice(wallpapers)
            location_wallpaper = os.path.join(folder_path, wallpaper_escolhido)

            # Atualiza o campo na interface
            self.wallpaper_path_input.setText(location_wallpaper)

            # Aplica o wallpaper e salva as configurações
            self.save_settings()

    def apply_styles(self):
        """Aplica personalização visual moderna com fundo claro/escuro e cor de destaque."""
        is_light = hasattr(self, 'theme_combo') and self.theme_combo.currentText() == "Light"
        
        accent_color = getattr(self, 'color_input', None)
        color = accent_color.text().strip() if accent_color and accent_color.text().strip() else "#89b4fa"

        bg_main = "#eff1f5" if is_light else "#1e1e2e"
        bg_sidebar = "#e6e9ef" if is_light else "#181825"
        bg_input = "#ccd0da" if is_light else "#313244"
        bg_hover = "#bcc0cc" if is_light else "#45475a"
        text_main = "#4c4f69" if is_light else "#cdd6f4"
        text_muted = "#6c6f85" if is_light else "#a6adc8"
        border_color = "#bcc0cc" if is_light else "#45475a"

        style = f"""
        QWidget {{
            background-color: {bg_main};
            color: {text_main};
            font-family: 'Segoe UI', Ubuntu, sans-serif;
            font-size: 13px;
        }}

        QListWidget {{
            background-color: {bg_sidebar};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 8px;
            outline: 0;
        }}

        QListWidget::item {{
            height: 38px;
            padding-left: 10px;
            border-radius: 6px;
            color: {text_muted};
        }}

        QListWidget::item:hover {{
            background-color: {bg_input};
            color: {text_main};
        }}

        QListWidget::item:selected {{
            background-color: {color};
            color: #11111b;
            font-weight: bold;
        }}

        QLineEdit, QComboBox {{
            background-color: {bg_input};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 6px 10px;
            color: {text_main};
        }}

        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {color};
        }}

        QPushButton {{
            background-color: {bg_input};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 6px 14px;
            color: {text_main};
            font-weight: 500;
        }}

        QPushButton:hover {{
            background-color: {bg_hover};
        }}

        QPushButton:pressed {{
            background-color: {border_color};
        }}

        QPushButton#PrimaryButton {{
            background-color: {color};
            color: #11111b;
            border: none;
            font-weight: bold;
        }}

        QPushButton#PrimaryButton:hover {{
            opacity: 0.85;
        }}

        QLabel {{
            background-color: transparent;
        }}
        """
        self.setStyleSheet(style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsApp()
    window.show()
    sys.exit(app.exec())