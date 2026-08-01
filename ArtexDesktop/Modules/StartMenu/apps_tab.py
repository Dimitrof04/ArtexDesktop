import os
import glob
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QScrollArea
from Modules.StartMenu.app_card import AppCard

class AppsTab(QWidget):
    def __init__(self, favorites_path):
        super().__init__()
        self.favorites_path = favorites_path
        self.favorites = set()
        self.load_favorites()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 10, 5, 5)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar aplicativo...")
        self.search_bar.textChanged.connect(self.filter_apps)
        layout.addWidget(self.search_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(270)  # Limite ~5 itens visíveis

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(6)
        self.scroll_layout.setContentsMargins(0, 5, 5, 5)

        self.load_applications()
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

    def load_favorites(self):
        if os.path.exists(self.favorites_path):
            try:
                with open(self.favorites_path, "r", encoding="utf-8") as f:
                    self.favorites = set(line.strip() for line in f if line.strip())
            except Exception as e:
                print(f"Erro ao carregar favoritos: {e}")

    def save_favorites(self):
        os.makedirs(os.path.dirname(self.favorites_path), exist_ok=True)
        try:
            with open(self.favorites_path, "w", encoding="utf-8") as f:
                for app in self.favorites:
                    f.write(f"{app}\n")
        except Exception as e:
            print(f"Erro ao salvar favoritos: {e}")

    def load_applications(self):
        self.apps_data = []
        desktop_dirs = ["/usr/share/applications", str(Path.home() / ".local/share/applications")]
        
        for d in desktop_dirs:
            if not os.path.exists(d):
                continue
            for filepath in glob.glob(os.path.join(d, "*.desktop")):
                app_info = self.parse_desktop_file(filepath)
                if app_info and app_info['name'] and app_info['exec']:
                    if not any(a['name'] == app_info['name'] for a in self.apps_data):
                        self.apps_data.append(app_info)

        self.render_apps()

    def parse_desktop_file(self, path):
        name, exec_cmd, icon, no_display = None, None, None, False
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.startswith("Name=") and not name:
                        name = line.split("=", 1)[1].strip()
                    elif line.startswith("Exec=") and not exec_cmd:
                        exec_cmd = line.split("=", 1)[1].strip()
                    elif line.startswith("Icon=") and not icon:
                        icon = line.split("=", 1)[1].strip()
                    elif line.startswith("NoDisplay=true"):
                        no_display = True
        except Exception:
            return None

        if no_display:
            return None

        return {"name": name, "exec": exec_cmd, "icon": icon}

    def render_apps(self, filter_text=""):
        for i in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.itemAt(i).widget()
            if child:
                child.deleteLater()

        filtered = [a for a in self.apps_data if filter_text.lower() in a['name'].lower()]

        sorted_apps = sorted(
            filtered,
            key=lambda x: (x['name'] not in self.favorites, x['name'].lower())
        )

        for app in sorted_apps:
            is_fav = app['name'] in self.favorites
            card = AppCard(
                name=app['name'],
                exec_cmd=app['exec'],
                icon_name=app['icon'],
                is_fav=is_fav,
                toggle_fav_callback=self.toggle_favorite
            )
            self.scroll_layout.addWidget(card)

        self.scroll_layout.addStretch()

    def toggle_favorite(self, app_name, is_fav):
        if is_fav:
            self.favorites.add(app_name)
        else:
            self.favorites.discard(app_name)
        self.save_favorites()
        self.render_apps(self.search_bar.text())

    def filter_apps(self, text):
        self.render_apps(text)