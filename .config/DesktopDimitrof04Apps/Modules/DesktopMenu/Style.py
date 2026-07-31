# style.py

def get_stylesheet(is_light: bool, accent_color: str) -> str:
    color = accent_color if accent_color else "#89b4fa"

    bg_main = "#eff1f5" if is_light else "#1e1e2e"
    bg_sidebar = "#e6e9ef" if is_light else "#181825"
    bg_input = "#ccd0da" if is_light else "#313244"
    bg_hover = "#bcc0cc" if is_light else "#45475a"
    text_main = "#4c4f69" if is_light else "#cdd6f4"
    text_muted = "#6c6f85" if is_light else "#a6adc8"
    border_color = "#bcc0cc" if is_light else "#45475a"

    return f"""
    QWidget {{
        background-color: {bg_main};
        color: {text_main};
        font-family: 'Inter', 'Segoe UI', Ubuntu, sans-serif;
        font-size: 13px;
    }}

    QScrollArea {{
        background: transparent;
        border: none;
    }}

    QScrollBar:vertical {{
        border: none;
        background: {bg_sidebar};
        width: 6px;
        border-radius: 3px;
    }}

    QScrollBar::handle:vertical {{
        background: {bg_hover};
        border-radius: 3px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {color};
    }}

    QListWidget {{
        background-color: {bg_sidebar};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 8px;
        outline: 0;
    }}

    QListWidget::item {{
        height: 38px;
        padding-left: 10px;
        border-radius: 8px;
        color: {text_muted};
        font-weight: 500;
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
        border-radius: 8px;
        padding: 8px 12px;
        color: {text_main};
    }}

    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {color};
    }}

    /* Botões Modernos com Animação Visual de Hover/Click */
    QPushButton {{
        background-color: {bg_input};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 8px 16px;
        color: {text_main};
        font-weight: 600;
    }}

    QPushButton:hover {{
        background-color: {bg_hover};
        border-color: {color};
    }}

    QPushButton:pressed {{
        background-color: {color};
        color: #11111b;
    }}

    QPushButton#PrimaryButton {{
        background-color: {color};
        color: #11111b;
        border: none;
        font-weight: bold;
    }}

    QPushButton#PrimaryButton:hover {{
        background-color: {color}dd;
    }}

    QCheckBox {{
        font-weight: 500;
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 5px;S
        border: 1px solid {border_color};
        background: {bg_input};
    }}

    QCheckBox::indicator:checked {{
        background-color: {color};
        border-color: {color};
    }}

    QSlider::groove:horizontal {{
        height: 6px;
        background: {bg_input};
        border-radius: 3px;
    }}

    QSlider::sub-page:horizontal {{
        background: {color};
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: {text_main};
        width: 14px;
        height: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }}
    """