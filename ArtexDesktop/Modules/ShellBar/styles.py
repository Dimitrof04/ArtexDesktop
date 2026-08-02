#!/usr/bin/env python3
import configparser
import os

CONFIG_PATH = os.path.expanduser("~/.config/Desktop.conf")

def load_config():
    """Carrega dados e parâmetros de configuração do Desktop.conf."""
    config = configparser.ConfigParser(strict=False)
    defaults = {
        "menu": "ArtexDesktop --StartMenu",
        "terminal": "kitty",
        "browser": "firefox",
        "filemanager": "dolphin",
        "colortheme": "#26c5ff",
        "bg_color": "#11111b",
        "transparency": "0.75",
        "theme_mode": "auto",
    }

    if os.path.exists(CONFIG_PATH):
        try:
            config.read(CONFIG_PATH)
            bg = (config.get("General", "Color", fallback=None) or 
                  config.get("theme", "bg_color", fallback=defaults["bg_color"]))
            
            mode = (config.get("theme", "mode", fallback=None) or 
                    config.get("General", "theme_mode", fallback=defaults["theme_mode"]))

            return {
                "menu": config.get("Apps", "menu", fallback=defaults["menu"]),
                "terminal": config.get("Apps", "terminal", fallback=defaults["terminal"]),
                "browser": config.get("Apps", "Browser", fallback=defaults["browser"]),
                "filemanager": config.get("Apps", "filemanager", fallback=defaults["filemanager"]),
                "colortheme": config.get("theme", "colortheme", fallback=defaults["colortheme"]),
                "bg_color": bg,
                "transparency": config.get("General", "KittyTransparincy", fallback=defaults["transparency"]),
                "theme_mode": mode,
            }
        except Exception:
            pass
    return defaults


class StyleManager:
    """Gerencia a estilização visual."""

    @staticmethod
    def is_bg_dark(hex_color):
        """Calcula se a cor de fundo hex é escura ou clara (luminância YIQ)."""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])
        if len(hex_color) != 6:
            return True
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
        return yiq < 128

    @staticmethod
    def hex_to_rgba(hex_code, alpha):
        """Converte cor hex para string rgba(...) válida no GTK CSS."""
        hex_code = hex_code.lstrip("#")
        if len(hex_code) == 3:
            hex_code = "".join([c * 2 for c in hex_code])
        if len(hex_code) != 6:
            hex_code = "000000"
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"

    @classmethod
    def generate_css(cls, cfg):
        accent_color = cfg.get("colortheme", "#26c5ff")
        bg_hex = cfg.get("bg_color", "#11111b")
        theme_mode = str(cfg.get("theme_mode", "auto")).lower()

        try:
            alpha = float(cfg.get("transparency", "0.75"))
        except ValueError:
            alpha = 0.75

        # Lógica de Tema Escuro vs Claro
        if theme_mode == "light":
            is_dark = False
        elif theme_mode in ("dark", "black"):
            is_dark = True
        else:
            is_dark = cls.is_bg_dark(bg_hex)

        # Inversão de Cores: Modo Escuro -> Texto Branco / Modo Claro -> Texto Preto
        if is_dark:
            fg_color = "#ffffff"
            inactive_ws = "#a6adc8"
            bg_base = bg_hex if bg_hex != "#ffffff" else "#1e1e2e"
        else:
            fg_color = "#000000"
            inactive_ws = "#5c5f77"
            bg_base = bg_hex if bg_hex != "#000000" else "#eff1f5"

        bar_bg = cls.hex_to_rgba(bg_base, alpha)

        return f"""
        * {{
            padding: 0px;
            margin: 0px;
            border: none;
            outline: none;
            box-shadow: none;
            text-shadow: none;
        }}

        window {{
            background-color: {bar_bg};
            font-family: "JetBrainsMono Nerd Font", "JetBrains Mono", sans-serif;
            font-size: 12px;
        }}

        .bar-container {{
            background-color: transparent;
            padding: 2px 10px;
            margin: 0px;
        }}

        /* Reset global para retirar fundos e sombras de botões */
        button, .button, label {{
            background: none;
            background-color: transparent;
            color: {fg_color};
            border: none;
            box-shadow: none;
        }}

        /* Botão do Arch */
        .arch-btn {{
            color: {fg_color};
            min-width: 26px;
            min-height: 24px;
            padding: 0px 6px;
            font-size: 16px;
        }}
        .arch-btn:hover {{
            color: {accent_color};
        }}

        /* Indicadores de Workspaces */
        .ws-btn {{
            color: {inactive_ws};
            padding: 0px 5px;
            font-size: 11px;
        }}
        .ws-btn.active {{
            color: {fg_color};
            font-weight: bold;
        }}
        .ws-btn:hover {{
            color: {fg_color};
        }}

        /* Relógio central */
        .clock-pill {{
            color: {fg_color};
            padding: 2px 10px;
            font-weight: bold;
            font-size: 0.95rem;
        }}

        /* Botões de Status */
        .status-pill {{
            color: {fg_color};
            padding: 1px 10px;
            min-height: 22px;
            margin: 0px 2px;
            font-size: 11px;
        }}
        .status-pill:hover {{
            color: {accent_color};
        }}
        """