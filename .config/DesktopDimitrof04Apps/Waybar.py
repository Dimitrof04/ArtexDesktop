import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QTime

class CustomBar(QWidget):
    def __init__(self):
        super().__init__()

        # Configurações de Janela sem bordas e sempre no topo
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Layout da Barra
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 2, 10, 2)

        # Widgets da barra
        self.workspace_label = QLabel("WS: 1")
        self.clock_label = QLabel()

        layout.addWidget(self.workspace_label)
        layout.addStretch()  # Espaçador central
        layout.addWidget(self.clock_label)

        self.setLayout(layout)

        # Timer para o Relógio
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

        # Estilização CSS rápida
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(24, 24, 37, 0.9);
                color: #cdd6f4;
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                border-bottom: 2px solid #89b4fa;
            }
        """)

    def update_clock(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.clock_label.setText(current_time)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    bar = CustomBar()
    
    # Define o tamanho (Largura total, Altura da barra)
    bar.resize(1920, 30)
    bar.show()
    sys.exit(app.exec())