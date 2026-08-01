import subprocess
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QApplication
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

class AppCard(QFrame):
    def __init__(self, name, exec_cmd, icon_name, is_fav, toggle_fav_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("AppCard")
        self.name = name
        self.exec_cmd = exec_cmd
        self.is_fav = is_fav
        self.toggle_fav_callback = toggle_fav_callback

        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Ícone do App em Moldura Quadrada (4x4 Proporcional)
        icon = QIcon.fromTheme(icon_name) if icon_name else QIcon()
        self.icon_label = QLabel()
        self.icon_label.setObjectName("IconLabel")
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(QSize(30, 30)))
        else:
            self.icon_label.setText("📦")
            self.icon_label.setFont(QFont("Sans-Serif", 14))

        # Nome do App
        self.title_label = QLabel(self.name)
        self.title_label.setStyleSheet("font-weight: bold; border: none;")

        # Botão Executar
        self.run_btn = QPushButton("▶")
        self.run_btn.setFixedSize(32, 32)
        self.run_btn.setToolTip("Executar")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1; color: #11111b; border: none; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #94e2d5; }
        """)
        self.run_btn.clicked.connect(self.launch_app)

        # Botão Favorito
        self.fav_btn = QPushButton("★" if self.is_fav else "☆")
        self.fav_btn.setFixedSize(32, 32)
        self.fav_btn.setToolTip("Favorito")
        fav_color = "#f9e2af" if self.is_fav else "#6c7086"
        self.fav_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {fav_color}; border: 1px solid {fav_color}; border-radius: 6px; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #45475a; }}
        """)
        self.fav_btn.clicked.connect(self.on_toggle_fav)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label, 1)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.fav_btn)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.launch_app()

    def launch_app(self):
        cmd = self.exec_cmd
        for placeholder in ['%f', '%F', '%u', '%U', '%d', '%D', '%n', '%N', '%k', '%v', '%m']:
            cmd = cmd.replace(placeholder, '')
        subprocess.Popen(cmd.strip(), shell=True)
        QApplication.quit()

    def on_toggle_fav(self):
        self.is_fav = not self.is_fav
        self.toggle_fav_callback(self.name, self.is_fav)