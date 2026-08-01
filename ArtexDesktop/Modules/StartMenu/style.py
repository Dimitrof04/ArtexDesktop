from PyQt6.QtCore import QSettings

def get_stylesheet(config_path: str) -> tuple[str, str, str, str, str]:
    """Lê as configurações do Desktop.conf e gera o CSS dinâmico."""
    settings = QSettings(config_path, QSettings.Format.IniFormat)
    
    settings.beginGroup("theme")
    accent_color = str(settings.value("colortheme", "#0cb6ff")).strip()
    theme_mode = str(settings.value("theme", "Dark")).strip().capitalize()
    settings.endGroup()

    if theme_mode == "Light":
        bg_color = "#eff1f5"
        card_bg = "#e6e9ef"
        btn_bg = "#dce0e8"
        text_color = "#4c4f69"
        border_color = "#bcc0cc"
    else:  # Dark
        bg_color = "#11111b"
        card_bg = "#181825"
        btn_bg = "#1e1e2e"
        text_color = "#cdd6f4"
        border_color = "#313244"

    qss = f"""
        QWidget#HyprMenuWindow {{
            background-color: {bg_color};
            border: 2px solid {accent_color};
            border-radius: 12px;
        }}
        QTabWidget::pane {{
            border: none;
            background: transparent;
        }}
        QTabBar::tab {{
            background: {btn_bg};
            color: {text_color};
            padding: 8px 16px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background: {accent_color};
            color: #11111b;
            font-weight: bold;
        }}
        
        /* ScrollArea e QScrollBar Estilizada */
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        QScrollArea > QWidget > QWidget {{
            background: transparent;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 0px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {accent_color};
            min-height: 20px;
            border-radius: 4px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

        /* App Cards */
        QFrame#AppCard {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
        }}
        QFrame#AppCard:hover {{
            background-color: {btn_bg};
            border-color: {accent_color};
        }}
        
        QLabel#IconLabel {{
            background-color: {bg_color};
            border: 1px solid {accent_color};
            border-radius: 6px;
        }}

        QLineEdit {{
            background-color: {card_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 6px 10px;
        }}
    """
    return qss, accent_color, theme_mode, btn_bg, text_color