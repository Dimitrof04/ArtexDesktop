#!/usr/bin/env python3

import os
import sys
import fcntl
import argparse
import subprocess
from Modules.theme_sync import set_system_theme # Já foi importado aqui!

# --- 1. GARANTE O DIRETÓRIO CORRETO ---
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

def parse_args():
    parser = argparse.ArgumentParser(
        prog="ArtexDesktop",
        description="Thanks for using :3",
        epilog="Criado por Dimitrof04"
    )

    # 1. Flag de Versão
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s v0.0.1"
    )

    # 2. Flags dos Menus
    parser.add_argument(
        "--StartMenu",
        action="store_true", 
        help="Open Menu Launcher"
    )

    parser.add_argument(
        "--Desktop",
        action="store_true", 
        help="Open Desktop Config"
    )

    # 3. Flag de Tema (aceita um valor: Light ou Dark)
    parser.add_argument(
        "--theme",
        type=str,
        help="Altera o tema do sistema (opções: Light, Dark)"
    )

    return parser.parse_args()

# --- TRAVA POR MENU ---
def check_menu_lock(menu_name: str):
    lock_file_path = f"/tmp/ArtexDesktop_{menu_name}.lock"
    lock_file = open(lock_file_path, "w")
    try:
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except IOError:
        return None

# Caminhos dos Scripts
StartMenuPath = os.path.expanduser("~/.local/share/ArtexDesktop/StartMenu.py")
DektopConfigMenuPath = os.path.expanduser("~/.local/share/ArtexDesktop/DektopConfigMenu.py")

def main():
    args = parse_args()

    # 1. Trata o argumento de Tema
    if args.theme:
        # Garante a formatação "Dark" ou "Light" mesmo que a pessoa digite "dark" ou "LIGHT"
        tema_formatado = args.theme.capitalize()

        if tema_formatado in ["Dark", "Light"]:
            set_system_theme(tema_formatado, None)
        else:
            print(f"⚠️ Tema '{args.theme}' inválido! Use apenas 'Dark' ou 'Light'.")

    # 2. Trata a execução dos Menus
    elif args.StartMenu:
        lock = check_menu_lock("StartMenu")
        if not lock:
            print("⚠️ O StartMenu já está em execução!")
            sys.exit(0)
            
        subprocess.run(["python3", StartMenuPath])

    elif args.Desktop:
        lock = check_menu_lock("DesktopConfig")
        if not lock:
            print("⚠️ O DesktopConfig já está em execução!")
            sys.exit(0)

        subprocess.run(["python3", DektopConfigMenuPath])

    else:
        print("Nothing executed. Try using -h or --help")

if __name__ == "__main__":
    main()

# <sudo ln -s /caminho/completo/para/seu/main.py /usr/local/bin/meuapp>